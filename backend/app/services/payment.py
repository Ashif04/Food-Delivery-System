from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order
from app.models.payment import Payment, PaymentMethod
from app.schemas.payment import PaymentMethodRead, PaymentRead


class PaymentError(Exception):
    pass


class OrderNotFound(PaymentError):
    pass


class PaymentMethodNotFound(PaymentError):
    pass


class PaymentNotFound(PaymentError):
    pass


def list_active_payment_methods(db: Session) -> list[PaymentMethodRead]:
    methods = db.scalars(
        select(PaymentMethod)
        .where(PaymentMethod.status == 1)
        .order_by(PaymentMethod.method_name)
    ).all()
    return [
        PaymentMethodRead(
            payment_method_id=method.payment_method_id,
            method_name=method.method_name,
            description=method.description,
        )
        for method in methods
    ]


def create_payment_record(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    order_id: int,
    payment_method_id: int,
) -> PaymentRead:
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

        payment_method = db.scalar(
            select(PaymentMethod)
            .where(
                PaymentMethod.payment_method_id == payment_method_id,
                PaymentMethod.status == 1,
            )
            .with_for_update()
        )
        if payment_method is None:
            raise PaymentMethodNotFound("Active payment method not found")

        payment = Payment(
            order_id=order.order_id,
            payment_method_id=payment_method.payment_method_id,
            amount=order.total_amount,
            payment_status="PENDING",
            status=1,
            created_by=user_id,
        )
        db.add(payment)
        db.commit()
        return get_customer_payment(
            db,
            customer_id=customer_id,
            payment_id=payment.payment_id,
        )
    except PaymentError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def get_customer_payment(
    db: Session,
    *,
    customer_id: int,
    payment_id: int,
) -> PaymentRead:
    payment = db.scalar(
        select(Payment)
        .join(Order, Order.order_id == Payment.order_id)
        .options(selectinload(Payment.payment_method))
        .where(
            Payment.payment_id == payment_id,
            Payment.status == 1,
            Order.customer_id == customer_id,
            Order.status == 1,
        )
    )
    if payment is None:
        raise PaymentNotFound("Payment not found")
    return _payment_response(payment)


def list_order_payments(
    db: Session,
    *,
    customer_id: int,
    order_id: int,
) -> list[PaymentRead]:
    order_exists = db.scalar(
        select(Order.order_id).where(
            Order.order_id == order_id,
            Order.customer_id == customer_id,
            Order.status == 1,
        )
    )
    if order_exists is None:
        raise OrderNotFound("Order not found")

    payments = db.scalars(
        select(Payment)
        .join(Order, Order.order_id == Payment.order_id)
        .options(selectinload(Payment.payment_method))
        .where(
            Payment.order_id == order_id,
            Payment.status == 1,
            Order.customer_id == customer_id,
            Order.status == 1,
        )
        .order_by(Payment.created_at.desc(), Payment.payment_id.desc())
    ).all()
    return [_payment_response(payment) for payment in payments]


def _payment_response(payment: Payment) -> PaymentRead:
    return PaymentRead(
        payment_id=payment.payment_id,
        order_id=payment.order_id,
        payment_method_id=payment.payment_method_id,
        payment_method_name=payment.payment_method.method_name,
        payment_reference=payment.payment_reference,
        amount=payment.amount,
        payment_status=payment.payment_status,
        gateway_transaction_id=payment.gateway_transaction_id,
        paid_at=payment.paid_at,
        refund_amount=payment.refund_amount,
        refund_status=payment.refund_status,
        refund_reason=payment.refund_reason,
        refunded_at=payment.refunded_at,
        created_at=payment.created_at,
    )
