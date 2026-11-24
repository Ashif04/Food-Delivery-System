from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer
from app.db.session import get_db
from app.models.user import Customer
from app.schemas.coupon import (
    MAX_DATABASE_ID,
    AppliedCouponRead,
    CouponApplyRequest,
    CouponRead,
)
from app.services.coupon import (
    CouponAccountingConflict,
    CouponNotEligible,
    CouponNotFound,
    OrderHasPaymentRecord,
    OrderCouponAlreadyApplied,
    OrderCouponNotFound,
    OrderNotFound,
    apply_coupon_to_order,
    get_available_coupon,
    list_available_coupons,
    remove_coupon_from_order,
)

router = APIRouter(tags=["Coupons"])


def _raise_coupon_error(error: Exception) -> None:
    if isinstance(
        error,
        (CouponNotFound, OrderCouponNotFound, OrderNotFound),
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(
        error,
        (
            CouponAccountingConflict,
            CouponNotEligible,
            OrderHasPaymentRecord,
            OrderCouponAlreadyApplied,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Coupon operation failed",
        ) from error
    raise error


@router.get("/coupons", response_model=list[CouponRead])
def read_coupons(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> list[CouponRead]:
    try:
        return list_available_coupons(db, customer_id=customer.customer_id)
    except SQLAlchemyError as error:
        _raise_coupon_error(error)


@router.get(
    "/coupons/{coupon_id}",
    response_model=CouponRead,
    responses={404: {"description": "Coupon not found or unavailable"}},
)
def read_coupon(
    coupon_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> CouponRead:
    try:
        return get_available_coupon(
            db,
            customer_id=customer.customer_id,
            coupon_id=coupon_id,
        )
    except (CouponNotFound, SQLAlchemyError) as error:
        _raise_coupon_error(error)


@router.post(
    "/orders/{order_id}/coupons",
    response_model=AppliedCouponRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Order or coupon not found"},
        409: {"description": "Coupon is ineligible or already applied"},
    },
)
def apply_order_coupon(
    request: CouponApplyRequest,
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> AppliedCouponRead:
    try:
        return apply_coupon_to_order(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            order_id=order_id,
            coupon_id=request.coupon_id,
        )
    except (
        CouponAccountingConflict,
        CouponNotEligible,
        CouponNotFound,
        OrderHasPaymentRecord,
        OrderCouponAlreadyApplied,
        OrderNotFound,
        SQLAlchemyError,
    ) as error:
        _raise_coupon_error(error)


@router.delete(
    "/orders/{order_id}/coupons/{order_coupon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Order or applied coupon not found"},
        409: {"description": "Coupon cannot be removed from this order"},
    },
)
def delete_order_coupon(
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    order_coupon_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Response:
    try:
        remove_coupon_from_order(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            order_id=order_id,
            order_coupon_id=order_coupon_id,
        )
    except (
        CouponAccountingConflict,
        CouponNotEligible,
        OrderHasPaymentRecord,
        OrderCouponNotFound,
        OrderNotFound,
        SQLAlchemyError,
    ) as error:
        _raise_coupon_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
