from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import MenuItem
from app.models.restaurant import Restaurant

PUBLIC_RESTAURANT_STATUS = "APPROVED"


def list_active_restaurants(db: Session) -> list[Restaurant]:
    statement = (
        select(Restaurant)
        .where(
            Restaurant.status == 1,
            Restaurant.restaurant_status == PUBLIC_RESTAURANT_STATUS,
        )
        .order_by(Restaurant.restaurant_name)
    )
    return list(db.scalars(statement).all())


def get_active_restaurant(db: Session, restaurant_id: int) -> Restaurant | None:
    statement = select(Restaurant).where(
        Restaurant.restaurant_id == restaurant_id,
        Restaurant.status == 1,
        Restaurant.restaurant_status == PUBLIC_RESTAURANT_STATUS,
    )
    return db.scalar(statement)


def list_restaurant_menu_items(
    db: Session,
    restaurant_id: int,
) -> list[MenuItem]:
    statement = (
        select(MenuItem)
        .join(Restaurant, Restaurant.restaurant_id == MenuItem.restaurant_id)
        .where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.status == 1,
            Restaurant.status == 1,
            Restaurant.restaurant_status == PUBLIC_RESTAURANT_STATUS,
        )
        .order_by(MenuItem.item_name)
    )
    return list(db.scalars(statement).all())
