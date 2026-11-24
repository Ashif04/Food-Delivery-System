from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

MAX_DATABASE_ID = 9223372036854775807


class CouponRead(BaseModel):
    coupon_id: int
    coupon_code: str
    description: str | None
    discount_type: str
    discount_value: Decimal
    maximum_discount: Decimal | None
    minimum_order_amount: Decimal | None
    usage_limit: int | None
    per_user_limit: int | None
    valid_from: datetime | None
    valid_until: datetime | None


class CouponApplyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coupon_id: int = Field(gt=0, le=MAX_DATABASE_ID)


class AppliedCouponRead(BaseModel):
    order_coupon_id: int
    order_id: int
    coupon_id: int
    coupon_code: str
    discount_amount: Decimal
    item_discount: Decimal
    total_amount: Decimal
    created_at: datetime | None
