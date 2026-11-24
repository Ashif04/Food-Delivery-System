from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.coupon import Coupon, OrderCoupon
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.coupon import AppliedCouponRead, CouponRead

ELIGIBLE_ORDER_STATUS = "PLACED"
CENT = Decimal("0.01")
ZERO_AMOUNT = Decimal("0.00")


class CouponError(Exception):
    pass


class CouponNotFound(CouponError):
    pass


class OrderNotFound(CouponError):
    pass


class CouponNotEligible(CouponError):
    pass


class OrderCouponAlreadyApplied(CouponError):
    pass


class OrderCouponNotFound(CouponError):
    pass


class CouponAccountingConflict(CouponError):
    pass


class OrderHasPaymentRecord(CouponError):
    pass


def list_available_coupons(
    db: Session,
    *,
    customer_id: int,
) -> list[CouponRead]:
    now = _utcnow()
    coupons = db.scalars(
        _current_coupon_statement(now).order_by(Coupon.coupon_code)
    ).all()
    global_usage, customer_usage = _coupon_usage_counts(db, customer_id)
    return [
        _coupon_response(coupon)
        for coupon in coupons
        if _within_usage_limits(
            coupon,
            global_usage.get(coupon.coupon_id, 0),
            customer_usage.get(coupon.coupon_id, 0),
        )
    ]


def get_available_coupon(
    db: Session,
    *,
    customer_id: int,
    coupon_id: int,
) -> CouponRead:
    coupon = db.scalar(
        _current_coupon_statement(_utcnow()).where(
            Coupon.coupon_id == coupon_id
        )
    )
    if coupon is None:
        raise CouponNotFound("Coupon not found")

    global_usage, customer_usage = _single_coupon_usage_counts(
        db,
        coupon_id=coupon_id,
        customer_id=customer_id,
    )
    if not _within_usage_limits(coupon, global_usage, customer_usage):
        raise CouponNotFound("Coupon not found")
    return _coupon_response(coupon)


def apply_coupon_to_order(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    order_id: int,
    coupon_id: int,
) -> AppliedCouponRead:
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
        _ensure_order_eligible(order)
        _ensure_no_payment_record(db, order.order_id)

        existing_link = db.scalar(
            select(OrderCoupon.id)
            .where(OrderCoupon.order_id == order.order_id)
            .with_for_update()
        )
        if existing_link is not None:
            raise OrderCouponAlreadyApplied(
                "This order already has a coupon applied"
            )

        coupon = db.scalar(
            _current_coupon_statement(_utcnow())
            .where(Coupon.coupon_id == coupon_id)
            .with_for_update()
        )
        if coupon is None:
            raise CouponNotEligible("Coupon is inactive, invalid, or expired")

        global_usage, customer_usage = _locked_coupon_usage_counts(
            db,
            coupon_id=coupon_id,
            customer_id=customer_id,
        )
        if not _within_usage_limits(coupon, global_usage, customer_usage):
            raise CouponNotEligible("Coupon usage limit has been reached")

        order_total = order.total_amount
        minimum_order_amount = coupon.minimum_order_amount or ZERO_AMOUNT
        if order_total < minimum_order_amount:
            raise CouponNotEligible(
                "Order total does not meet the coupon minimum"
            )
        if order_total < ZERO_AMOUNT:
            raise CouponNotEligible("Order total cannot be negative")

        discount = _calculate_discount(coupon, order_total)
        updated_item_discount = (order.item_discount or ZERO_AMOUNT) + discount
        updated_total = order_total - discount
        if updated_total < ZERO_AMOUNT:
            raise CouponNotEligible("Coupon discount exceeds order total")

        order_coupon = OrderCoupon(
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
            discount_amount=discount,
            created_by=user_id,
            status=1,
        )
        order.item_discount = updated_item_discount
        order.total_amount = updated_total
        order.updated_at = _utcnow()
        order.updated_by = user_id
        db.add(order_coupon)
        db.flush()
        response = AppliedCouponRead(
            order_coupon_id=order_coupon.id,
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
            coupon_code=coupon.coupon_code,
            discount_amount=discount,
            item_discount=updated_item_discount,
            total_amount=updated_total,
            created_at=order_coupon.created_at,
        )
        db.commit()
        return response
    except CouponError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def remove_coupon_from_order(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    order_id: int,
    order_coupon_id: int,
) -> None:
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
        _ensure_order_eligible(order)
        _ensure_no_payment_record(db, order.order_id)

        order_coupon = db.scalar(
            select(OrderCoupon)
            .where(
                OrderCoupon.id == order_coupon_id,
                OrderCoupon.order_id == order.order_id,
                OrderCoupon.status == 1,
            )
            .with_for_update()
        )
        if order_coupon is None:
            raise OrderCouponNotFound("Applied coupon not found")

        current_discount = order.item_discount or ZERO_AMOUNT
        if current_discount < order_coupon.discount_amount:
            raise CouponAccountingConflict(
                "Stored order discount is inconsistent with its coupon"
            )

        order.item_discount = current_discount - order_coupon.discount_amount
        order.total_amount += order_coupon.discount_amount
        order.updated_at = _utcnow()
        order.updated_by = user_id
        db.delete(order_coupon)
        db.commit()
    except CouponError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def _current_coupon_statement(now: datetime):
    return select(Coupon).where(
        Coupon.status == 1,
        Coupon.is_active.is_(True),
        Coupon.discount_type.in_(("PERCENTAGE", "FIXED")),
        Coupon.discount_value >= ZERO_AMOUNT,
        (Coupon.valid_from.is_(None)) | (Coupon.valid_from <= now),
        (Coupon.valid_until.is_(None)) | (Coupon.valid_until >= now),
    )


def _coupon_usage_counts(
    db: Session,
    customer_id: int,
) -> tuple[dict[int, int], dict[int, int]]:
    global_counts = db.execute(
        select(OrderCoupon.coupon_id, func.count(OrderCoupon.id))
        .where(OrderCoupon.status == 1)
        .group_by(OrderCoupon.coupon_id)
    ).all()
    customer_counts = db.execute(
        select(OrderCoupon.coupon_id, func.count(OrderCoupon.id))
        .join(Order, Order.order_id == OrderCoupon.order_id)
        .where(OrderCoupon.status == 1, Order.customer_id == customer_id)
        .group_by(OrderCoupon.coupon_id)
    ).all()
    return dict(global_counts), dict(customer_counts)


def _single_coupon_usage_counts(
    db: Session,
    *,
    coupon_id: int,
    customer_id: int,
) -> tuple[int, int]:
    global_count = db.scalar(
        select(func.count(OrderCoupon.id)).where(
            OrderCoupon.coupon_id == coupon_id,
            OrderCoupon.status == 1,
        )
    ) or 0
    customer_count = db.scalar(
        select(func.count(OrderCoupon.id))
        .join(Order, Order.order_id == OrderCoupon.order_id)
        .where(
            OrderCoupon.coupon_id == coupon_id,
            OrderCoupon.status == 1,
            Order.customer_id == customer_id,
        )
    ) or 0
    return global_count, customer_count


def _locked_coupon_usage_counts(
    db: Session,
    *,
    coupon_id: int,
    customer_id: int,
) -> tuple[int, int]:
    global_usage = db.scalars(
        select(OrderCoupon.id)
        .where(
            OrderCoupon.coupon_id == coupon_id,
            OrderCoupon.status == 1,
        )
        .with_for_update()
    ).all()
    customer_usage = db.scalars(
        select(OrderCoupon.id)
        .join(Order, Order.order_id == OrderCoupon.order_id)
        .where(
            OrderCoupon.coupon_id == coupon_id,
            OrderCoupon.status == 1,
            Order.customer_id == customer_id,
        )
        .with_for_update()
    ).all()
    return len(global_usage), len(customer_usage)


def _within_usage_limits(
    coupon: Coupon,
    global_usage: int,
    customer_usage: int,
) -> bool:
    if coupon.usage_limit is not None and global_usage >= coupon.usage_limit:
        return False
    if (
        coupon.per_user_limit is not None
        and customer_usage >= coupon.per_user_limit
    ):
        return False
    return True


def _ensure_order_eligible(order: Order) -> None:
    if order.order_status != ELIGIBLE_ORDER_STATUS:
        raise CouponNotEligible(
            f"Coupons can only be changed on {ELIGIBLE_ORDER_STATUS} orders"
        )


def _ensure_no_payment_record(db: Session, order_id: int) -> None:
    payment_id = db.scalar(
        select(Payment.payment_id)
        .where(Payment.order_id == order_id)
        .with_for_update()
        .limit(1)
    )
    if payment_id is not None:
        raise OrderHasPaymentRecord(
            "Coupons cannot be changed after a payment record exists for the order"
        )


def _calculate_discount(coupon: Coupon, order_total: Decimal) -> Decimal:
    if coupon.discount_value < ZERO_AMOUNT:
        raise CouponNotEligible("Coupon discount value cannot be negative")

    if coupon.discount_type == "PERCENTAGE":
        discount = order_total * coupon.discount_value / Decimal("100")
        if coupon.maximum_discount is not None:
            if coupon.maximum_discount < ZERO_AMOUNT:
                raise CouponNotEligible("Coupon maximum discount is invalid")
            discount = min(discount, coupon.maximum_discount)
    elif coupon.discount_type == "FIXED":
        discount = coupon.discount_value
    else:
        raise CouponNotEligible("Coupon discount type is not supported")

    discount = min(discount, order_total).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )
    if discount < ZERO_AMOUNT:
        raise CouponNotEligible("Coupon discount cannot be negative")
    return discount


def _coupon_response(coupon: Coupon) -> CouponRead:
    return CouponRead(
        coupon_id=coupon.coupon_id,
        coupon_code=coupon.coupon_code,
        description=coupon.description,
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
        maximum_discount=coupon.maximum_discount,
        minimum_order_amount=coupon.minimum_order_amount,
        usage_limit=coupon.usage_limit,
        per_user_limit=coupon.per_user_limit,
        valid_from=coupon.valid_from,
        valid_until=coupon.valid_until,
    )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
