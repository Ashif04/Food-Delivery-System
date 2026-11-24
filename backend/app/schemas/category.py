from pydantic import BaseModel, ConfigDict


class FoodCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    description: str | None
    image_url: str | None
