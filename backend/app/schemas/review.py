from datetime import datetime

from pydantic import BaseModel, Field, model_validator

MIN_DATABASE_INTEGER = -(2**31)
MAX_DATABASE_INTEGER = 2**31 - 1
MAX_DATABASE_ID = 9223372036854775807


class ReviewCreate(BaseModel):
    rating: int = Field(
        strict=True,
        ge=MIN_DATABASE_INTEGER,
        le=MAX_DATABASE_INTEGER,
    )
    review_text: str | None = None


class RestaurantReviewCreate(ReviewCreate):
    order_id: int = Field(gt=0, le=MAX_DATABASE_ID)


class FoodItemReviewCreate(ReviewCreate):
    order_item_id: int = Field(gt=0, le=MAX_DATABASE_ID)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        strict=True,
        ge=MIN_DATABASE_INTEGER,
        le=MAX_DATABASE_INTEGER,
    )
    review_text: str | None = None

    @model_validator(mode="after")
    def require_update_field(self) -> "ReviewUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        if "rating" in self.model_fields_set and self.rating is None:
            raise ValueError("rating cannot be null")
        return self


class RestaurantReviewRead(BaseModel):
    review_id: int
    restaurant_id: int
    rating: int
    review_text: str | None
    created_at: datetime | None
    updated_at: datetime | None


class FoodItemReviewRead(BaseModel):
    review_id: int
    item_id: int
    rating: int
    review_text: str | None
    created_at: datetime | None
    updated_at: datetime | None
