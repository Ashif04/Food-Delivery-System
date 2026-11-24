from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import FoodCategory, RestaurantCategory
from app.models.restaurant import Restaurant
from app.services.restaurant import PUBLIC_RESTAURANT_STATUS


def list_active_categories(db: Session) -> list[FoodCategory]:
    statement = (
        select(FoodCategory)
        .where(FoodCategory.status == 1)
        .order_by(FoodCategory.category_name)
    )
    return list(db.scalars(statement).all())


def list_restaurant_categories(
    db: Session,
    restaurant_id: int,
) -> list[FoodCategory]:
    statement = (
        select(FoodCategory)
        .join(
            RestaurantCategory,
            RestaurantCategory.category_id == FoodCategory.category_id,
        )
        .join(
            Restaurant,
            Restaurant.restaurant_id == RestaurantCategory.restaurant_id,
        )
        .where(
            RestaurantCategory.restaurant_id == restaurant_id,
            RestaurantCategory.status == 1,
            FoodCategory.status == 1,
            Restaurant.status == 1,
            Restaurant.restaurant_status == PUBLIC_RESTAURANT_STATUS,
        )
        .distinct()
        .order_by(FoodCategory.category_name)
    )
    return list(db.scalars(statement).all())
