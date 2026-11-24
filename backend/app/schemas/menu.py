from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MenuItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    restaurant_id: int
    category_id: int
    item_name: str
    description: str | None
    food_type: str | None
    base_price: Decimal
    is_available: bool | None
    preparation_time: int | None
