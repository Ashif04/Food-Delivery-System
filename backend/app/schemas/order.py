from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderAddonRead(BaseModel):
    addon_id: int | None
    addon_name: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal


class OrderItemRead(BaseModel):
    order_item_id: int
    item_id: int | None
    variant_id: int | None
    item_name: str
    variant_name: str | None
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    special_instructions: str | None
    addons: list[OrderAddonRead]


class OrderSummaryRead(BaseModel):
    order_id: int
    order_number: str
    restaurant_id: int
    restaurant_name: str
    order_status: str | None
    payment_status: str | None
    subtotal: Decimal
    total_amount: Decimal
    placed_at: datetime | None


class OrderRead(BaseModel):
    order_id: int
    order_number: str
    restaurant_id: int
    restaurant_name: str
    address_id: int | None
    delivery_address_snapshot: str | None
    delivery_latitude: Decimal | None
    delivery_longitude: Decimal | None
    subtotal: Decimal
    item_discount: Decimal | None
    tax_amount: Decimal | None
    delivery_fee: Decimal | None
    platform_fee: Decimal | None
    packaging_fee: Decimal | None
    total_amount: Decimal
    payment_status: str | None
    order_status: str | None
    special_instructions: str | None
    placed_at: datetime | None
    accepted_at: datetime | None
    delivered_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    items: list[OrderItemRead]


class OrderListRead(BaseModel):
    items: list[OrderSummaryRead]
    total: int
    limit: int
    offset: int


class OrderCancellationRequest(BaseModel):
    cancellation_reason: str | None = None
