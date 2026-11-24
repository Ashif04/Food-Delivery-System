from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

MAX_DATABASE_ID = 9223372036854775807


class PaymentMethodRead(BaseModel):
    payment_method_id: int
    method_name: str
    description: str | None


class PaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: int = Field(gt=0, le=MAX_DATABASE_ID)
    payment_method_id: int = Field(gt=0, le=MAX_DATABASE_ID)


class PaymentRead(BaseModel):
    payment_id: int
    order_id: int
    payment_method_id: int
    payment_method_name: str
    payment_reference: str | None
    amount: Decimal
    payment_status: str | None
    gateway_transaction_id: str | None
    paid_at: datetime | None
    refund_amount: Decimal | None
    refund_status: str | None
    refund_reason: str | None
    refunded_at: datetime | None
    created_at: datetime | None
