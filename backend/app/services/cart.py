from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.addon import Addon, AddonGroup, MenuItemAddonGroup
from app.models.cart import Cart, CartItem, CartItemAddon
from app.models.menu import ItemVariant, MenuItem
from app.models.restaurant import Restaurant
from app.models.user import Customer
from app.schemas.cart import (
    CartAddonRequest,
    CartAddonRead,
    CartItemCreate,
    CartItemRead,
    CartRead,
)


class CartError(Exception):
    pass


class MenuItemUnavailable(CartError):
    pass


class InvalidCartSelection(CartError):
    pass


class CartRestaurantConflict(CartError):
    pass


class CartNotFound(CartError):
    pass


class CartItemNotFound(CartError):
    pass


class CartStateConflict(CartError):
    pass


def get_customer_cart(db: Session, customer_id: int) -> CartRead:
    carts = _get_active_carts(db, customer_id, load_items=True)
    if len(carts) > 1:
        raise CartStateConflict(
            "Multiple active carts exist; clear the carts before continuing"
        )
    if not carts:
        return CartRead(
            cart_id=None,
            restaurant_id=None,
            items=[],
            total_amount=Decimal("0.00"),
        )
    return _cart_response(carts[0])


def add_cart_item(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    request: CartItemCreate,
) -> CartRead:
    try:
        _lock_customer(db, customer_id)

        menu_item = db.scalar(
            select(MenuItem).where(
                MenuItem.item_id == request.menu_item_id,
                MenuItem.status == 1,
                MenuItem.is_available.is_(True),
            )
        )
        if menu_item is None:
            raise MenuItemUnavailable("Menu item is unavailable")

        restaurant = db.scalar(
            select(Restaurant).where(
                Restaurant.restaurant_id == menu_item.restaurant_id,
                Restaurant.status == 1,
            )
        )
        if restaurant is None:
            raise MenuItemUnavailable("Menu item is unavailable")

        variant = None
        if request.variant_id is not None:
            variant = db.scalar(
                select(ItemVariant).where(
                    ItemVariant.variant_id == request.variant_id,
                    ItemVariant.item_id == menu_item.item_id,
                    ItemVariant.status == 1,
                    ItemVariant.is_available.is_(True),
                )
            )
            if variant is None:
                raise InvalidCartSelection(
                    "The selected variant is unavailable for this menu item"
                )

        selected_addons = _get_valid_addons(
            db,
            menu_item.item_id,
            menu_item.restaurant_id,
            request.selected_addons,
        )

        carts = _get_active_carts(db, customer_id)
        if len(carts) > 1:
            raise CartStateConflict(
                "Multiple active carts exist; clear the carts before continuing"
            )
        if carts and carts[0].restaurant_id != menu_item.restaurant_id:
            raise CartRestaurantConflict(
                "A cart can contain items from only one restaurant"
            )
        cart = carts[0] if carts else Cart(
            customer_id=customer_id,
            restaurant_id=menu_item.restaurant_id,
            cart_status="ACTIVE",
            created_by=user_id,
            status=1,
        )
        if not carts:
            db.add(cart)
            db.flush()

        cart_item = CartItem(
            cart_id=cart.cart_id,
            item_id=menu_item.item_id,
            variant_id=variant.variant_id if variant else None,
            quantity=request.quantity,
            created_by=user_id,
            status=1,
        )
        db.add(cart_item)
        db.flush()
        db.add_all(
            [
                CartItemAddon(
                    cart_item_id=cart_item.cart_item_id,
                    addon_id=addon.addon_id,
                    quantity=addon_request.quantity,
                    created_by=user_id,
                    status=1,
                )
                for addon_request, addon in selected_addons
            ]
        )
        db.commit()
        return get_customer_cart(db, customer_id)
    except CartError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def update_cart_item_quantity(
    db: Session,
    *,
    customer_id: int,
    cart_item_id: int,
    quantity: int,
) -> CartRead:
    try:
        _lock_customer(db, customer_id)
        cart_item = _get_owned_cart_item(db, customer_id, cart_item_id)
        if cart_item is None:
            raise CartItemNotFound("Cart item not found")
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.now(timezone.utc)
        cart_item.updated_by = _customer_user_id(db, customer_id)
        db.commit()
        return get_customer_cart(db, customer_id)
    except CartError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def remove_cart_item(
    db: Session,
    *,
    customer_id: int,
    cart_item_id: int,
) -> None:
    try:
        _lock_customer(db, customer_id)
        cart_item = _get_owned_cart_item(db, customer_id, cart_item_id)
        if cart_item is None:
            raise CartItemNotFound("Cart item not found")
        db.execute(
            delete(CartItemAddon).where(
                CartItemAddon.cart_item_id == cart_item.cart_item_id
            )
        )
        db.delete(cart_item)
        db.commit()
    except CartError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def clear_customer_cart(db: Session, customer_id: int) -> None:
    try:
        _lock_customer(db, customer_id)
        carts = _get_active_carts(db, customer_id)
        cart_ids = [cart.cart_id for cart in carts]
        if cart_ids:
            cart_item_ids = select(CartItem.cart_item_id).where(
                CartItem.cart_id.in_(cart_ids)
            )
            db.execute(
                delete(CartItemAddon).where(
                    CartItemAddon.cart_item_id.in_(cart_item_ids)
                )
            )
            db.execute(delete(CartItem).where(CartItem.cart_id.in_(cart_ids)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def _lock_customer(db: Session, customer_id: int) -> None:
    customer = db.scalar(
        select(Customer)
        .where(Customer.customer_id == customer_id, Customer.status == 1)
        .with_for_update()
    )
    if customer is None:
        raise CartNotFound("Customer not found")


def _get_active_carts(
    db: Session,
    customer_id: int,
    *,
    load_items: bool = False,
) -> list[Cart]:
    statement = select(Cart).where(
        Cart.customer_id == customer_id,
        Cart.cart_status == "ACTIVE",
        Cart.status == 1,
    )
    if load_items:
        statement = statement.options(
            selectinload(Cart.items.and_(CartItem.status == 1)).selectinload(
                CartItem.menu_item
            ),
            selectinload(Cart.items.and_(CartItem.status == 1)).selectinload(
                CartItem.variant
            ),
            selectinload(
                Cart.items.and_(CartItem.status == 1)
            ).selectinload(
                CartItem.addons.and_(CartItemAddon.status == 1)
            )
            .selectinload(CartItemAddon.addon),
        )
    return list(db.scalars(statement.order_by(Cart.cart_id)).all())


def _get_valid_addons(
    db: Session,
    item_id: int,
    restaurant_id: int,
    requested_addons: list[CartAddonRequest],
) -> list[tuple[CartAddonRequest, Addon]]:
    addon_ids = [addon.addon_id for addon in requested_addons]
    if len(addon_ids) != len(set(addon_ids)):
        raise InvalidCartSelection("An add-on can only be selected once")
    if not addon_ids:
        _validate_required_addon_groups(db, item_id, restaurant_id, {})
        return []

    rows = db.execute(
        select(Addon, AddonGroup)
        .join(AddonGroup, Addon.addon_group_id == AddonGroup.addon_group_id)
        .join(
            MenuItemAddonGroup,
            MenuItemAddonGroup.addon_group_id == AddonGroup.addon_group_id,
        )
        .where(
            Addon.addon_id.in_(addon_ids),
            Addon.status == 1,
            Addon.is_available.is_(True),
            AddonGroup.status == 1,
            AddonGroup.restaurant_id == restaurant_id,
            MenuItemAddonGroup.item_id == item_id,
            MenuItemAddonGroup.status == 1,
        )
    ).all()
    addons_by_id = {addon.addon_id: (addon, group) for addon, group in rows}
    if set(addons_by_id) != set(addon_ids):
        raise InvalidCartSelection(
            "One or more selected add-ons are unavailable for this menu item"
        )

    selected_counts: dict[int, int] = {}
    for addon, group in addons_by_id.values():
        selected_counts[group.addon_group_id] = (
            selected_counts.get(group.addon_group_id, 0) + 1
        )
    _validate_required_addon_groups(
        db, item_id, restaurant_id, selected_counts
    )

    request_by_id = {addon.addon_id: addon for addon in requested_addons}
    return [
        (request_by_id[addon_id], addons_by_id[addon_id][0])
        for addon_id in addon_ids
    ]


def _validate_required_addon_groups(
    db: Session,
    item_id: int,
    restaurant_id: int,
    selected_counts: dict[int, int],
) -> None:
    groups = db.scalars(
        select(AddonGroup)
        .join(
            MenuItemAddonGroup,
            MenuItemAddonGroup.addon_group_id == AddonGroup.addon_group_id,
        )
        .where(
            MenuItemAddonGroup.item_id == item_id,
            MenuItemAddonGroup.status == 1,
            AddonGroup.status == 1,
            AddonGroup.restaurant_id == restaurant_id,
        )
    ).all()
    for group in groups:
        count = selected_counts.get(group.addon_group_id, 0)
        minimum = group.min_selection or 0
        maximum = group.max_selection
        if (group.is_required and count < max(1, minimum)) or count < minimum:
            raise InvalidCartSelection(
                f"Select at least {max(1, minimum)} add-on(s) from {group.group_name}"
            )
        if maximum is not None and count > maximum:
            raise InvalidCartSelection(
                f"Select no more than {maximum} add-on(s) from {group.group_name}"
            )


def _get_owned_cart_item(
    db: Session,
    customer_id: int,
    cart_item_id: int,
) -> CartItem | None:
    return db.scalar(
        select(CartItem)
        .join(Cart, Cart.cart_id == CartItem.cart_id)
        .where(
            CartItem.cart_item_id == cart_item_id,
            CartItem.status == 1,
            Cart.customer_id == customer_id,
            Cart.cart_status == "ACTIVE",
            Cart.status == 1,
        )
    )


def _customer_user_id(db: Session, customer_id: int) -> int:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise CartNotFound("Customer not found")
    return customer.user_id


def _cart_response(cart: Cart) -> CartRead:
    response_items = []
    total = Decimal("0.00")
    for item in cart.items:
        item_price = (
            item.variant.price
            if item.variant is not None
            else item.menu_item.base_price
        )
        addon_responses = []
        item_total = item_price
        for link in item.addons:
            addon_price = link.addon.additional_price or Decimal("0.00")
            addon_total = addon_price * link.quantity
            item_total += addon_total
            addon_responses.append(
                CartAddonRead(
                    addon_id=link.addon.addon_id,
                    addon_name=link.addon.addon_name,
                    quantity=link.quantity,
                    unit_price=addon_price,
                    total_price=addon_total,
                )
            )
        line_total = item_total * item.quantity
        total += line_total
        response_items.append(
            CartItemRead(
                cart_item_id=item.cart_item_id,
                menu_item_id=item.menu_item.item_id,
                item_name=item.menu_item.item_name,
                variant_id=item.variant.variant_id if item.variant else None,
                variant_name=item.variant.variant_name if item.variant else None,
                quantity=item.quantity,
                item_unit_price=item_price,
                selected_addons=addon_responses,
                line_total=line_total,
            )
        )
    return CartRead(
        cart_id=cart.cart_id,
        restaurant_id=cart.restaurant_id,
        items=response_items,
        total_amount=total,
    )
