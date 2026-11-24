from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer
from app.db.session import get_db
from app.models.user import Customer
from app.schemas.order import (
    OrderCancellationRequest,
    OrderListRead,
    OrderRead,
)
from app.services.order import (
    ActiveCartNotFound,
    CancellationNotAllowed,
    EmptyCart,
    InvalidCartContent,
    MultipleActiveCarts,
    OrderNotFound,
    cancel_order,
    create_order,
    get_order,
    list_customer_orders,
)

router = APIRouter(prefix="/orders", tags=["Orders"])
MAX_DATABASE_ID = 9223372036854775807


def _raise_order_error(error: Exception) -> None:
    if isinstance(error, (ActiveCartNotFound, OrderNotFound)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(
        error,
        (
            CancellationNotAllowed,
            EmptyCart,
            InvalidCartContent,
            MultipleActiveCarts,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order operation failed",
        ) from error
    raise error


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "No active cart found"},
        409: {"description": "Cart is empty or contains unavailable items"},
    },
)
def place_order(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> OrderRead:
    try:
        return create_order(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
        )
    except (
        ActiveCartNotFound,
        EmptyCart,
        InvalidCartContent,
        MultipleActiveCarts,
        SQLAlchemyError,
    ) as error:
        _raise_order_error(error)


@router.get("", response_model=OrderListRead)
def read_orders(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> OrderListRead:
    try:
        return list_customer_orders(
            db,
            customer_id=customer.customer_id,
            limit=limit,
            offset=offset,
        )
    except SQLAlchemyError as error:
        _raise_order_error(error)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    responses={404: {"description": "Order not found"}},
)
def read_order(
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> OrderRead:
    try:
        return get_order(
            db,
            customer_id=customer.customer_id,
            order_id=order_id,
        )
    except (OrderNotFound, SQLAlchemyError) as error:
        _raise_order_error(error)


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderRead,
    responses={
        404: {"description": "Order not found"},
        409: {"description": "Order status does not allow cancellation"},
    },
)
def cancel_customer_order(
    request: OrderCancellationRequest | None = None,
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> OrderRead:
    try:
        return cancel_order(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            order_id=order_id,
            cancellation_reason=(
                request.cancellation_reason if request is not None else None
            ),
        )
    except (
        CancellationNotAllowed,
        OrderNotFound,
        SQLAlchemyError,
    ) as error:
        _raise_order_error(error)
