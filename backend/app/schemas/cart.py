from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

MAX_DATABASE_ID = 9223372036854775807
MAX_INTEGER = 2147483647


class CartAddonRequest(BaseModel):
    addon_id: int = Field(gt=0, le=MAX_DATABASE_ID)
    quantity: int = Field(default=1, gt=0, le=MAX_INTEGER)


class CartItemCreate(BaseModel):
    menu_item_id: int = Field(gt=0, le=MAX_DATABASE_ID)
    quantity: int = Field(gt=0, le=MAX_INTEGER)
    variant_id: int | None = Field(default=None, gt=0, le=MAX_DATABASE_ID)
    selected_addons: list[CartAddonRequest] = Field(default_factory=list)


class CartItemQuantityUpdate(BaseModel):
    quantity: int = Field(gt=0, le=MAX_INTEGER)


class CartAddonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    addon_id: int
    addon_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_item_id: int
    menu_item_id: int
    item_name: str
    variant_id: int | None
    variant_name: str | None
    quantity: int
    item_unit_price: Decimal
    selected_addons: list[CartAddonRead]
    line_total: Decimal


class CartRead(BaseModel):
    cart_id: int | None
    restaurant_id: int | None
    items: list[CartItemRead]
    total_amount: Decimal
