from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.addon import Addon, AddonGroup, MenuItemAddonGroup
from app.models.cart import Cart, CartItem, CartItemAddon
from app.models.history import OrderStatusHistory
from app.models.menu import ItemVariant, MenuItem
from app.models.order import Order, OrderItem, OrderItemAddon
from app.models.restaurant import Restaurant
from app.models.user import Customer
from app.schemas.order import (
    OrderAddonRead,
    OrderItemRead,
    OrderListRead,
    OrderRead,
    OrderSummaryRead,
)

CANCELLABLE_ORDER_STATUS = "PLACED"
CANCELLED_ORDER_STATUS = "CANCELLED"
ZERO_AMOUNT = Decimal("0.00")


class OrderError(Exception):
    pass


class ActiveCartNotFound(OrderError):
    pass


class EmptyCart(OrderError):
    pass


class MultipleActiveCarts(OrderError):
    pass


class InvalidCartContent(OrderError):
    pass


class OrderNotFound(OrderError):
    pass


class CancellationNotAllowed(OrderError):
    pass


def create_order(db: Session, *, customer_id: int, user_id: int) -> OrderRead:
    try:
        customer = db.scalar(
            select(Customer)
            .where(Customer.customer_id == customer_id, Customer.status == 1)
            .with_for_update()
        )
        if customer is None:
            raise InvalidCartContent("The customer is no longer active")

        carts = list(
            db.scalars(
                select(Cart)
                .where(
                    Cart.customer_id == customer_id,
                    Cart.cart_status == "ACTIVE",
                    Cart.status == 1,
                )
                .order_by(Cart.cart_id)
                .with_for_update()
            ).all()
        )
        if not carts:
            raise ActiveCartNotFound("No active cart was found")
        if len(carts) > 1:
            raise MultipleActiveCarts(
                "Multiple active carts exist; resolve them before placing an order"
            )
        cart = carts[0]

        restaurant = db.scalar(
            select(Restaurant)
            .where(
                Restaurant.restaurant_id == cart.restaurant_id,
                Restaurant.status == 1,
            )
            .with_for_update()
        )
        if restaurant is None:
            raise InvalidCartContent("The cart's restaurant is unavailable")

        cart_items = list(
            db.scalars(
                select(CartItem)
                .where(CartItem.cart_id == cart.cart_id, CartItem.status == 1)
                .order_by(CartItem.cart_item_id)
                .with_for_update()
            ).all()
        )
        if not cart_items:
            raise EmptyCart("The active cart is empty")
        if any(item.quantity <= 0 for item in cart_items):
            raise InvalidCartContent("Cart item quantities must be positive")

        cart_item_ids = [item.cart_item_id for item in cart_items]
        cart_addons = list(
            db.scalars(
                select(CartItemAddon)
                .where(
                    CartItemAddon.cart_item_id.in_(cart_item_ids),
                    CartItemAddon.status == 1,
                )
                .order_by(CartItemAddon.id)
                .with_for_update()
            ).all()
        )
        if any(addon.quantity <= 0 for addon in cart_addons):
            raise InvalidCartContent("Add-on quantities must be positive")

        item_ids = sorted({item.item_id for item in cart_items})
        menu_items = list(
            db.scalars(
                select(MenuItem)
                .where(
                    MenuItem.item_id.in_(item_ids),
                    MenuItem.status == 1,
                    MenuItem.is_available.is_(True),
                )
                .order_by(MenuItem.item_id)
                .with_for_update()
            ).all()
        )
        menu_items_by_id = {item.item_id: item for item in menu_items}
        if len(menu_items_by_id) != len(item_ids) or any(
            item.restaurant_id != cart.restaurant_id for item in menu_items
        ):
            raise InvalidCartContent(
                "One or more cart items are no longer available"
            )

        variant_ids = sorted(
            {item.variant_id for item in cart_items if item.variant_id is not None}
        )
        variants = []
        if variant_ids:
            variants = list(
                db.scalars(
                    select(ItemVariant)
                    .where(
                        ItemVariant.variant_id.in_(variant_ids),
                        ItemVariant.status == 1,
                        ItemVariant.is_available.is_(True),
                    )
                    .order_by(ItemVariant.variant_id)
                    .with_for_update()
                ).all()
            )
        variants_by_id = {variant.variant_id: variant for variant in variants}
        for item in cart_items:
            if item.variant_id is not None:
                variant = variants_by_id.get(item.variant_id)
                if variant is None or variant.item_id != item.item_id:
                    raise InvalidCartContent(
                        "A cart item has an unavailable variant"
                    )

        addon_ids = sorted({addon.addon_id for addon in cart_addons})
        addons_by_item_and_id: dict[tuple[int, int], tuple[Addon, AddonGroup]] = {}
        if addon_ids:
            addon_rows = db.execute(
                select(MenuItemAddonGroup.item_id, Addon, AddonGroup)
                .join(
                    AddonGroup,
                    AddonGroup.addon_group_id
                    == MenuItemAddonGroup.addon_group_id,
                )
                .join(Addon, Addon.addon_group_id == AddonGroup.addon_group_id)
                .where(
                    MenuItemAddonGroup.item_id.in_(item_ids),
                    MenuItemAddonGroup.status == 1,
                    AddonGroup.restaurant_id == cart.restaurant_id,
                    AddonGroup.status == 1,
                    Addon.addon_id.in_(addon_ids),
                    Addon.status == 1,
                    Addon.is_available.is_(True),
                )
                .order_by(MenuItemAddonGroup.item_id, Addon.addon_id)
                .with_for_update()
            ).all()
            addons_by_item_and_id = {
                (item_id, addon.addon_id): (addon, group)
                for item_id, addon, group in addon_rows
            }
            required_addon_pairs = {
                (item.item_id, addon.addon_id)
                for item in cart_items
                for addon in cart_addons
                if addon.cart_item_id == item.cart_item_id
            }
            if not required_addon_pairs.issubset(addons_by_item_and_id):
                raise InvalidCartContent(
                    "One or more selected add-ons are no longer available"
                )

        addons_by_cart_item: dict[int, list[CartItemAddon]] = {}
        for addon in cart_addons:
            addons_by_cart_item.setdefault(addon.cart_item_id, []).append(addon)

        subtotal = ZERO_AMOUNT
        item_snapshots = []
        for cart_item in cart_items:
            menu_item = menu_items_by_id[cart_item.item_id]
            variant = (
                variants_by_id.get(cart_item.variant_id)
                if cart_item.variant_id is not None
                else None
            )
            item_unit_price = (
                variant.price if variant is not None else menu_item.base_price
            )
            selected_links = addons_by_cart_item.get(cart_item.cart_item_id, [])
            selected_addons = [
                addons_by_item_and_id[(cart_item.item_id, link.addon_id)][0]
                for link in selected_links
            ]
            selected_addon_total = sum(
                (
                    (addon.additional_price or ZERO_AMOUNT) * link.quantity
                    for link, addon in zip(selected_links, selected_addons)
                ),
                ZERO_AMOUNT,
            )
            line_total = (item_unit_price + selected_addon_total) * cart_item.quantity
            subtotal += line_total
            item_snapshots.append(
                (
                    cart_item,
                    menu_item,
                    variant,
                    item_unit_price,
                    line_total,
                    selected_links,
                    selected_addons,
                )
            )

        order = Order(
            order_number=f"ORD-{uuid4().hex.upper()}",
            customer_id=customer_id,
            restaurant_id=cart.restaurant_id,
            subtotal=subtotal,
            item_discount=ZERO_AMOUNT,
            tax_amount=ZERO_AMOUNT,
            delivery_fee=ZERO_AMOUNT,
            platform_fee=ZERO_AMOUNT,
            packaging_fee=ZERO_AMOUNT,
            total_amount=subtotal,
            payment_status="PENDING",
            order_status="PLACED",
            status=1,
            created_by=user_id,
        )
        db.add(order)
        db.flush()

        for (
            cart_item,
            menu_item,
            variant,
            unit_price,
            line_total,
            selected_links,
            selected_addons,
        ) in item_snapshots:
            order_item = OrderItem(
                order_id=order.order_id,
                item_id=menu_item.item_id,
                variant_id=variant.variant_id if variant else None,
                item_name=menu_item.item_name,
                variant_name=variant.variant_name if variant else None,
                unit_price=unit_price,
                quantity=cart_item.quantity,
                total_price=line_total,
                special_instructions=cart_item.special_instructions,
                status=1,
                created_by=user_id,
            )
            db.add(order_item)
            db.flush()
            db.add_all(
                [
                    OrderItemAddon(
                        order_item_id=order_item.order_item_id,
                        addon_id=addon.addon_id,
                        addon_name=addon.addon_name,
                        unit_price=addon.additional_price or ZERO_AMOUNT,
                        quantity=link.quantity,
                        status=1,
                        created_by=user_id,
                    )
                    for link, addon in zip(selected_links, selected_addons)
                ]
            )

        cart_item_ids_for_cleanup = select(CartItem.cart_item_id).where(
            CartItem.cart_id == cart.cart_id
        )
        db.execute(
            delete(CartItemAddon).where(
                CartItemAddon.cart_item_id.in_(cart_item_ids_for_cleanup)
            )
        )
        db.execute(delete(CartItem).where(CartItem.cart_id == cart.cart_id))
        db.delete(cart)
        db.commit()
        return get_order(db, customer_id=customer_id, order_id=order.order_id)
    except OrderError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def list_customer_orders(
    db: Session,
    *,
    customer_id: int,
    limit: int,
    offset: int,
) -> OrderListRead:
    total = db.scalar(
        select(func.count(Order.order_id)).where(
            Order.customer_id == customer_id,
            Order.status == 1,
        )
    ) or 0
    orders = db.scalars(
        select(Order)
        .options(selectinload(Order.restaurant))
        .where(
            Order.customer_id == customer_id,
            Order.status == 1,
        )
        .order_by(Order.placed_at.desc(), Order.order_id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return OrderListRead(
        items=[_order_summary(order) for order in orders],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_order(db: Session, *, customer_id: int, order_id: int) -> OrderRead:
    statement = (
        select(Order)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items.and_(OrderItem.status == 1)).selectinload(
                OrderItem.addons.and_(OrderItemAddon.status == 1)
            ),
        )
        .where(
            Order.order_id == order_id,
            Order.customer_id == customer_id,
            Order.status == 1,
        )
    )
    order = db.scalar(statement)
    if order is None:
        raise OrderNotFound("Order not found")
    return _order_response(order)


def cancel_order(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    order_id: int,
    cancellation_reason: str | None,
) -> OrderRead:
    try:
        order = db.scalar(
            select(Order)
            .where(
                Order.order_id == order_id,
                Order.customer_id == customer_id,
                Order.status == 1,
            )
            .with_for_update()
        )
        if order is None:
            raise OrderNotFound("Order not found")
        if order.order_status != CANCELLABLE_ORDER_STATUS:
            raise CancellationNotAllowed(
                f"Only {CANCELLABLE_ORDER_STATUS} orders can be cancelled"
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        reason = cancellation_reason.strip() if cancellation_reason else None
        if reason == "":
            reason = None
        old_status = order.order_status
        order.order_status = CANCELLED_ORDER_STATUS
        order.cancelled_at = now
        order.cancellation_reason = reason
        order.updated_at = now
        order.updated_by = user_id
        db.add(
            OrderStatusHistory(
                order_id=order.order_id,
                old_status=old_status,
                new_status=CANCELLED_ORDER_STATUS,
                changed_by=user_id,
                remarks=reason,
                created_by=user_id,
                status=1,
            )
        )
        db.commit()
        return get_order(db, customer_id=customer_id, order_id=order_id)
    except OrderError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def _order_summary(order: Order) -> OrderSummaryRead:
    return OrderSummaryRead(
        order_id=order.order_id,
        order_number=order.order_number,
        restaurant_id=order.restaurant_id,
        restaurant_name=order.restaurant.restaurant_name,
        order_status=order.order_status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        total_amount=order.total_amount,
        placed_at=order.placed_at,
    )


def _order_response(order: Order) -> OrderRead:
    items = []
    for item in order.items:
        addons = [
            OrderAddonRead(
                addon_id=addon.addon_id,
                addon_name=addon.addon_name,
                unit_price=addon.unit_price,
                quantity=addon.quantity,
                total_price=(
                    addon.unit_price * addon.quantity * item.quantity
                ),
            )
            for addon in item.addons
        ]
        items.append(
            OrderItemRead(
                order_item_id=item.order_item_id,
                item_id=item.item_id,
                variant_id=item.variant_id,
                item_name=item.item_name,
                variant_name=item.variant_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price,
                special_instructions=item.special_instructions,
                addons=addons,
            )
        )
    return OrderRead(
        order_id=order.order_id,
        order_number=order.order_number,
        restaurant_id=order.restaurant_id,
        restaurant_name=order.restaurant.restaurant_name,
        address_id=order.address_id,
        delivery_address_snapshot=order.delivery_address_snapshot,
        delivery_latitude=order.delivery_latitude,
        delivery_longitude=order.delivery_longitude,
        subtotal=order.subtotal,
        item_discount=order.item_discount,
        tax_amount=order.tax_amount,
        delivery_fee=order.delivery_fee,
        platform_fee=order.platform_fee,
        packaging_fee=order.packaging_fee,
        total_amount=order.total_amount,
        payment_status=order.payment_status,
        order_status=order.order_status,
        special_instructions=order.special_instructions,
        placed_at=order.placed_at,
        accepted_at=order.accepted_at,
        delivered_at=order.delivered_at,
        cancelled_at=order.cancelled_at,
        cancellation_reason=order.cancellation_reason,
        items=items,
    )
