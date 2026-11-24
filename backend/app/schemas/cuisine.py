from pydantic import BaseModel, ConfigDict


class CuisineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cuisine_id: int
    cuisine_name: str
    description: str | None
