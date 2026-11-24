from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.menu import MenuItemRead
from app.schemas.restaurant import RestaurantRead
from app.services.restaurant import (
    get_active_restaurant,
    list_active_restaurants,
    list_restaurant_menu_items,
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])
MAX_RESTAURANT_ID = 9223372036854775807


@router.get("", response_model=list[RestaurantRead])
def read_restaurants(db: Session = Depends(get_db)) -> list[RestaurantRead]:
    """Return approved, active restaurants visible to customers."""
    return list_active_restaurants(db)


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantRead,
    responses={404: {"description": "Approved, active restaurant not found"}},
)
def read_restaurant(
    restaurant_id: int = Path(gt=0, le=MAX_RESTAURANT_ID),
    db: Session = Depends(get_db),
) -> RestaurantRead:
    """Return details for one approved, active restaurant."""
    restaurant = get_active_restaurant(db, restaurant_id)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    return restaurant


@router.get(
    "/{restaurant_id}/menu",
    response_model=list[MenuItemRead],
    responses={404: {"description": "Approved, active restaurant not found"}},
)
def read_restaurant_menu(
    restaurant_id: int = Path(gt=0, le=MAX_RESTAURANT_ID),
    db: Session = Depends(get_db),
) -> list[MenuItemRead]:
    """Return active menu items for one approved, active restaurant."""
    if get_active_restaurant(db, restaurant_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    return list_restaurant_menu_items(db, restaurant_id)
