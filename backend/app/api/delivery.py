from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_customer,
    get_current_delivery_partner,
)
from app.db.session import get_db
from app.models.user import Customer, DeliveryPartner
from app.schemas.delivery import (
    MAX_DATABASE_ID,
    DeliveryAssignmentDetail,
    DeliveryAssignmentSummary,
    DeliveryTrackingCreate,
    DeliveryTrackingRead,
)
from app.services.delivery import (
    AssignmentNotFound,
    OrderNotFound,
    add_tracking_point,
    get_partner_assignment,
    list_customer_order_tracking,
    list_partner_assignments,
)

router = APIRouter(tags=["Delivery"])


def _raise_delivery_error(error: Exception) -> None:
    if isinstance(error, (AssignmentNotFound, OrderNotFound)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delivery operation failed",
        ) from error
    raise error


@router.get(
    "/delivery/assignments",
    response_model=list[DeliveryAssignmentSummary],
)
def read_partner_assignments(
    partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db),
) -> list[DeliveryAssignmentSummary]:
    try:
        return list_partner_assignments(db, partner_id=partner.partner_id)
    except SQLAlchemyError as error:
        _raise_delivery_error(error)


@router.get(
    "/delivery/assignments/{assignment_id}",
    response_model=DeliveryAssignmentDetail,
    responses={404: {"description": "Delivery assignment not found"}},
)
def read_partner_assignment(
    assignment_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db),
) -> DeliveryAssignmentDetail:
    try:
        return get_partner_assignment(
            db,
            partner_id=partner.partner_id,
            assignment_id=assignment_id,
        )
    except (AssignmentNotFound, SQLAlchemyError) as error:
        _raise_delivery_error(error)


@router.post(
    "/delivery/assignments/{assignment_id}/tracking",
    response_model=DeliveryTrackingRead,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Delivery assignment not found"}},
)
def create_tracking_point(
    request: DeliveryTrackingCreate,
    assignment_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db),
) -> DeliveryTrackingRead:
    try:
        return add_tracking_point(
            db,
            partner_id=partner.partner_id,
            user_id=partner.user_id,
            assignment_id=assignment_id,
            request=request,
        )
    except (AssignmentNotFound, SQLAlchemyError) as error:
        _raise_delivery_error(error)


@router.get(
    "/orders/{order_id}/tracking",
    response_model=list[DeliveryTrackingRead],
    responses={404: {"description": "Order not found"}},
)
def read_customer_order_tracking(
    order_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> list[DeliveryTrackingRead]:
    try:
        return list_customer_order_tracking(
            db,
            customer_id=customer.customer_id,
            order_id=order_id,
        )
    except (OrderNotFound, SQLAlchemyError) as error:
        _raise_delivery_error(error)
