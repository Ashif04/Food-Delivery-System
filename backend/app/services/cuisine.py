from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Cuisine, RestaurantCuisine
from app.models.restaurant import Restaurant
from app.services.restaurant import PUBLIC_RESTAURANT_STATUS


def list_active_cuisines(db: Session) -> list[Cuisine]:
    statement = (
        select(Cuisine)
        .where(Cuisine.status == 1)
        .order_by(Cuisine.cuisine_name)
    )
    return list(db.scalars(statement).all())


def list_restaurant_cuisines(
    db: Session,
    restaurant_id: int,
) -> list[Cuisine]:
    statement = (
        select(Cuisine)
        .join(
            RestaurantCuisine,
            RestaurantCuisine.cuisine_id == Cuisine.cuisine_id,
        )
        .join(
            Restaurant,
            Restaurant.restaurant_id == RestaurantCuisine.restaurant_id,
        )
        .where(
            RestaurantCuisine.restaurant_id == restaurant_id,
            RestaurantCuisine.status == 1,
            Cuisine.status == 1,
            Restaurant.status == 1,
            Restaurant.restaurant_status == PUBLIC_RESTAURANT_STATUS,
        )
        .distinct()
        .order_by(Cuisine.cuisine_name)
    )
    return list(db.scalars(statement).all())
