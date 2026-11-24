from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.delivery import DeliveryAssignment, DeliveryTracking
from app.models.order import Order
from app.schemas.delivery import (
    DeliveryAssignmentDetail,
    DeliveryAssignmentSummary,
    DeliveryTrackingCreate,
    DeliveryTrackingRead,
)


class DeliveryError(Exception):
    pass


class AssignmentNotFound(DeliveryError):
    pass


class OrderNotFound(DeliveryError):
    pass


def list_partner_assignments(
    db: Session,
    *,
    partner_id: int,
) -> list[DeliveryAssignmentSummary]:
    assignments = db.scalars(
        select(DeliveryAssignment)
        .join(Order, Order.order_id == DeliveryAssignment.order_id)
        .options(selectinload(DeliveryAssignment.order))
        .where(
            DeliveryAssignment.partner_id == partner_id,
            DeliveryAssignment.status == 1,
            Order.status == 1,
        )
        .order_by(
            DeliveryAssignment.assigned_at.desc(),
            DeliveryAssignment.assignment_id.desc(),
        )
    ).all()
    return [_assignment_summary(assignment) for assignment in assignments]


def get_partner_assignment(
    db: Session,
    *,
    partner_id: int,
    assignment_id: int,
) -> DeliveryAssignmentDetail:
    assignment = db.scalar(
        select(DeliveryAssignment)
        .join(Order, Order.order_id == DeliveryAssignment.order_id)
        .options(selectinload(DeliveryAssignment.order))
        .where(
            DeliveryAssignment.assignment_id == assignment_id,
            DeliveryAssignment.partner_id == partner_id,
            DeliveryAssignment.status == 1,
            Order.status == 1,
        )
    )
    if assignment is None:
        raise AssignmentNotFound("Delivery assignment not found")

    tracking_points = db.scalars(
        select(DeliveryTracking)
        .where(
            DeliveryTracking.assignment_id == assignment.assignment_id,
            DeliveryTracking.status == 1,
        )
        .order_by(
            DeliveryTracking.recorded_at,
            DeliveryTracking.tracking_id,
        )
    ).all()
    return _assignment_detail(assignment, tracking_points)


def add_tracking_point(
    db: Session,
    *,
    partner_id: int,
    user_id: int,
    assignment_id: int,
    request: DeliveryTrackingCreate,
) -> DeliveryTrackingRead:
    try:
        assignment = db.scalar(
            select(DeliveryAssignment)
            .join(Order, Order.order_id == DeliveryAssignment.order_id)
            .where(
                DeliveryAssignment.assignment_id == assignment_id,
                DeliveryAssignment.partner_id == partner_id,
                DeliveryAssignment.status == 1,
                Order.status == 1,
            )
            .with_for_update()
        )
        if assignment is None:
            raise AssignmentNotFound("Delivery assignment not found")

        tracking = DeliveryTracking(
            assignment_id=assignment.assignment_id,
            latitude=request.latitude,
            longitude=request.longitude,
            created_by=user_id,
            status=1,
        )
        db.add(tracking)
        db.flush()
        db.refresh(tracking)
        response = _tracking_response(tracking)
        db.commit()
        return response
    except DeliveryError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def list_customer_order_tracking(
    db: Session,
    *,
    customer_id: int,
    order_id: int,
) -> list[DeliveryTrackingRead]:
    order_exists = db.scalar(
        select(Order.order_id).where(
            Order.order_id == order_id,
            Order.customer_id == customer_id,
            Order.status == 1,
        )
    )
    if order_exists is None:
        raise OrderNotFound("Order not found")

    points = db.scalars(
        select(DeliveryTracking)
        .join(
            DeliveryAssignment,
            DeliveryAssignment.assignment_id == DeliveryTracking.assignment_id,
        )
        .join(Order, Order.order_id == DeliveryAssignment.order_id)
        .where(
            Order.order_id == order_id,
            Order.customer_id == customer_id,
            Order.status == 1,
            DeliveryAssignment.status == 1,
            DeliveryTracking.status == 1,
        )
        .order_by(
            DeliveryTracking.recorded_at,
            DeliveryTracking.tracking_id,
        )
    ).all()
    return [_tracking_response(point) for point in points]


def _assignment_summary(
    assignment: DeliveryAssignment,
) -> DeliveryAssignmentSummary:
    return DeliveryAssignmentSummary(
        assignment_id=assignment.assignment_id,
        order_id=assignment.order_id,
        order_number=assignment.order.order_number,
        order_status=assignment.order.order_status,
        assignment_status=assignment.assignment_status,
        assigned_at=assignment.assigned_at,
        accepted_at=assignment.accepted_at,
        rejected_at=assignment.rejected_at,
        picked_up_at=assignment.picked_up_at,
        completed_at=assignment.completed_at,
    )


def _assignment_detail(
    assignment: DeliveryAssignment,
    tracking_points: list[DeliveryTracking],
) -> DeliveryAssignmentDetail:
    summary = _assignment_summary(assignment)
    return DeliveryAssignmentDetail(
        **summary.model_dump(),
        tracking_points=[_tracking_response(point) for point in tracking_points],
    )


def _tracking_response(point: DeliveryTracking) -> DeliveryTrackingRead:
    return DeliveryTrackingRead(
        tracking_id=point.tracking_id,
        assignment_id=point.assignment_id,
        latitude=point.latitude,
        longitude=point.longitude,
        recorded_at=point.recorded_at,
    )
