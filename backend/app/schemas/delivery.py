from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

MAX_DATABASE_ID = 9223372036854775807


class DeliveryTrackingCreate(BaseModel):
    latitude: Decimal = Field(
        ge=Decimal("-90"),
        le=Decimal("90"),
        max_digits=10,
        decimal_places=7,
    )
    longitude: Decimal = Field(
        ge=Decimal("-180"),
        le=Decimal("180"),
        max_digits=10,
        decimal_places=7,
    )


class DeliveryTrackingRead(BaseModel):
    tracking_id: int
    assignment_id: int
    latitude: Decimal
    longitude: Decimal
    recorded_at: datetime | None


class DeliveryAssignmentSummary(BaseModel):
    assignment_id: int
    order_id: int
    order_number: str
    order_status: str | None
    assignment_status: str | None
    assigned_at: datetime | None
    accepted_at: datetime | None
    rejected_at: datetime | None
    picked_up_at: datetime | None
    completed_at: datetime | None


class DeliveryAssignmentDetail(DeliveryAssignmentSummary):
    tracking_points: list[DeliveryTrackingRead]
