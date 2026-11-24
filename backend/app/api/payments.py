from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer
from app.db.session import get_db
from app.models.user import Customer
from app.schemas.payment import (
    MAX_DATABASE_ID,
    PaymentCreate,
    PaymentMethodRead,
    PaymentRead,
)
from app.services.payment import (
    OrderNotFound,
    PaymentMethodNotFound,
    PaymentNotFound,
    create_payment_record,
    get_customer_payment,
    list_active_payment_methods,
    list_order_payments,
)

router = APIRouter(tags=["Payments"])


def _raise_payment_error(error: Exception) -> None:
    if isinstance(error, (OrderNotFound, PaymentMethodNotFound, PaymentNotFound)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment record operation failed",
        ) from error
    raise error


@router.get("/payment-methods", response_model=list[PaymentMethodRead])
def read_payment_methods(
    db: Session = Depends(get_db),
) -> list[PaymentMethodRead]:
    try:
        return list_active_payment_methods(db)
    except SQLAlchemyError as error:
        _raise_payment_error(error)


@router.post(
    "/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Order or active payment method not found"},
    },
)
def create_payment(
    request: PaymentCreate,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> PaymentRead:
    try:
        return create_payment_record(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            order_id=request.order_id,
            payment_method_id=request.payment_method_id,
        )
    except (
        OrderNotFound,
        PaymentMethodNotFound,
        SQLAlchemyError,
    ) as error:
        _raise_payment_error(error)


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentRead,
    responses={404: {"description": "Payment not found"}},
)
def read_payment(
    payment_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> PaymentRead:
    try:
        return get_customer_payment(
            db,
            customer_id=customer.customer_id,
            payment_id=payment_id,
        )
    except (PaymentNotFound, SQLAlchemyError) as error:
        _raise_payment_error(error)


@router.get(
    "/orders/{order_id}/payments",
    response_model=list[PaymentRead],
    responses={404: {"description": "Order not found"}},
)
def read_order_payments(
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    try:
        return list_order_payments(
            db,
            customer_id=customer.customer_id,
            order_id=order_id,
        )
    except (OrderNotFound, SQLAlchemyError) as error:
        _raise_payment_error(error)
