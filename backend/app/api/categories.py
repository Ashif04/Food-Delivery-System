from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.category import FoodCategoryRead
from app.services.category import (
    list_active_categories,
    list_restaurant_categories,
)
from app.services.restaurant import get_active_restaurant

router = APIRouter(tags=["Categories"])
MAX_RESTAURANT_ID = 9223372036854775807


@router.get("/categories", response_model=list[FoodCategoryRead])
def read_categories(db: Session = Depends(get_db)) -> list[FoodCategoryRead]:
    """Return all active food categories."""
    return list_active_categories(db)


@router.get(
    "/restaurants/{restaurant_id}/categories",
    response_model=list[FoodCategoryRead],
    responses={404: {"description": "Approved, active restaurant not found"}},
)
def read_restaurant_categories(
    restaurant_id: int = Path(gt=0, le=MAX_RESTAURANT_ID),
    db: Session = Depends(get_db),
) -> list[FoodCategoryRead]:
    """Return active categories for one approved, active restaurant."""
    if get_active_restaurant(db, restaurant_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    return list_restaurant_categories(db, restaurant_id)
