from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer
from app.db.session import get_db
from app.models.user import Customer
from app.schemas.review import (
    MAX_DATABASE_ID,
    FoodItemReviewCreate,
    FoodItemReviewRead,
    ReviewUpdate,
)
from app.services.review import (
    DuplicateReview,
    PurchaseNotFound,
    ReviewConstraintConflict,
    ReviewNotFound,
    ReviewTargetNotFound,
    create_food_item_review,
    delete_food_item_review,
    get_food_item_review,
    list_food_item_reviews,
    update_food_item_review,
)

router = APIRouter(prefix="/menu-items/{item_id}/reviews", tags=["Reviews"])


def _raise_review_error(error: Exception) -> None:
    if isinstance(error, (PurchaseNotFound, ReviewNotFound, ReviewTargetNotFound)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(error, (DuplicateReview, ReviewConstraintConflict)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Review operation failed",
        ) from error
    raise error


@router.post(
    "",
    response_model=FoodItemReviewRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Menu item or eligible order item not found"},
        409: {"description": "A review already exists for this order item"},
    },
)
def create_review(
    request: FoodItemReviewCreate,
    item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> FoodItemReviewRead:
    try:
        return create_food_item_review(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            item_id=item_id,
            order_item_id=request.order_item_id,
            rating=request.rating,
            review_text=request.review_text,
        )
    except (
        DuplicateReview,
        ReviewConstraintConflict,
        PurchaseNotFound,
        ReviewTargetNotFound,
        SQLAlchemyError,
    ) as error:
        _raise_review_error(error)


@router.get("", response_model=list[FoodItemReviewRead])
def read_reviews(
    item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[FoodItemReviewRead]:
    try:
        return list_food_item_reviews(
            db,
            item_id=item_id,
            limit=limit,
            offset=offset,
        )
    except (ReviewTargetNotFound, SQLAlchemyError) as error:
        _raise_review_error(error)


@router.get(
    "/{review_id}",
    response_model=FoodItemReviewRead,
    responses={404: {"description": "Review or menu item not found"}},
)
def read_review(
    item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    review_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    db: Session = Depends(get_db),
) -> FoodItemReviewRead:
    try:
        return get_food_item_review(
            db,
            item_id=item_id,
            review_id=review_id,
        )
    except (ReviewNotFound, ReviewTargetNotFound, SQLAlchemyError) as error:
        _raise_review_error(error)


@router.patch(
    "/{review_id}",
    response_model=FoodItemReviewRead,
    responses={404: {"description": "Owned review or menu item not found"}},
)
def edit_review(
    request: ReviewUpdate,
    item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    review_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> FoodItemReviewRead:
    try:
        return update_food_item_review(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            item_id=item_id,
            review_id=review_id,
            update=request,
        )
    except (ReviewNotFound, ReviewTargetNotFound, SQLAlchemyError) as error:
        _raise_review_error(error)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Owned review or menu item not found"}},
)
def remove_review(
    item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    review_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Response:
    try:
        delete_food_item_review(
            db,
            customer_id=customer.customer_id,
            item_id=item_id,
            review_id=review_id,
        )
    except (ReviewNotFound, ReviewTargetNotFound, SQLAlchemyError) as error:
        _raise_review_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
