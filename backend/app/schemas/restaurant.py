from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    restaurant_id: int
    restaurant_name: str
    description: str | None
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    logo_url: str | None
    cover_image: str | None
    average_rating: Decimal | None
    minimum_order_amount: Decimal | None
    estimated_delivery_time: int | None
    is_open: bool | None
    restaurant_status: str | None
