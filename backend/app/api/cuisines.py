from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cuisine import CuisineRead
from app.services.cuisine import (
    list_active_cuisines,
    list_restaurant_cuisines,
)
from app.services.restaurant import get_active_restaurant

router = APIRouter(tags=["Cuisines"])
MAX_RESTAURANT_ID = 9223372036854775807


@router.get("/cuisines", response_model=list[CuisineRead])
def read_cuisines(db: Session = Depends(get_db)) -> list[CuisineRead]:
    """Return all active cuisines."""
    return list_active_cuisines(db)


@router.get(
    "/restaurants/{restaurant_id}/cuisines",
    response_model=list[CuisineRead],
    responses={404: {"description": "Approved, active restaurant not found"}},
)
def read_restaurant_cuisines(
    restaurant_id: int = Path(gt=0, le=MAX_RESTAURANT_ID),
    db: Session = Depends(get_db),
) -> list[CuisineRead]:
    """Return active cuisines for one approved, active restaurant."""
    if get_active_restaurant(db, restaurant_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    return list_restaurant_cuisines(db, restaurant_id)
