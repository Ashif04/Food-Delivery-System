from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.menu import MenuItem
from app.models.order import Order, OrderItem
from app.models.restaurant import Restaurant
from app.models.review import FoodItemReview, RestaurantReview
from app.schemas.review import (
    FoodItemReviewRead,
    RestaurantReviewRead,
    ReviewUpdate,
)


class ReviewError(Exception):
    pass


class ReviewTargetNotFound(ReviewError):
    pass


class PurchaseNotFound(ReviewError):
    pass


class ReviewNotFound(ReviewError):
    pass


class DuplicateReview(ReviewError):
    pass


class ReviewConstraintConflict(ReviewError):
    pass


def list_restaurant_reviews(
    db: Session,
    *,
    restaurant_id: int,
    limit: int,
    offset: int,
) -> list[RestaurantReviewRead]:
    _require_active_restaurant(db, restaurant_id)
    reviews = db.scalars(
        select(RestaurantReview)
        .where(
            RestaurantReview.restaurant_id == restaurant_id,
            RestaurantReview.status == 1,
        )
        .order_by(
            RestaurantReview.created_at.desc(),
            RestaurantReview.review_id.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()
    return [_restaurant_review_response(review) for review in reviews]


def get_restaurant_review(
    db: Session,
    *,
    restaurant_id: int,
    review_id: int,
) -> RestaurantReviewRead:
    _require_active_restaurant(db, restaurant_id)
    review = db.scalar(
        select(RestaurantReview).where(
            RestaurantReview.review_id == review_id,
            RestaurantReview.restaurant_id == restaurant_id,
            RestaurantReview.status == 1,
        )
    )
    if review is None:
        raise ReviewNotFound("Restaurant review not found")
    return _restaurant_review_response(review)


def create_restaurant_review(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    restaurant_id: int,
    order_id: int,
    rating: int,
    review_text: str | None,
) -> RestaurantReviewRead:
    try:
        _require_active_restaurant(db, restaurant_id)
        order = db.scalar(
            select(Order)
            .where(
                Order.order_id == order_id,
                Order.customer_id == customer_id,
                Order.restaurant_id == restaurant_id,
                Order.status == 1,
            )
            .with_for_update()
        )
        if order is None:
            raise PurchaseNotFound(
                "An order for this restaurant was not found"
            )

        existing_review = db.scalar(
            select(RestaurantReview.review_id)
            .where(
                RestaurantReview.order_id == order_id,
                RestaurantReview.customer_id == customer_id,
            )
            .with_for_update()
        )
        if existing_review is not None:
            raise DuplicateReview(
                "A review already exists for this restaurant order"
            )

        review = RestaurantReview(
            order_id=order_id,
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            rating=rating,
            review_text=review_text,
            created_by=user_id,
            status=1,
        )
        db.add(review)
        db.flush()
        db.refresh(review)
        response = _restaurant_review_response(review)
        db.commit()
        return response
    except ReviewError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ReviewConstraintConflict(
            "The restaurant review conflicts with an existing database constraint"
        ) from error
    except SQLAlchemyError:
        db.rollback()
        raise


def update_restaurant_review(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    restaurant_id: int,
    review_id: int,
    update: ReviewUpdate,
) -> RestaurantReviewRead:
    try:
        _require_active_restaurant(db, restaurant_id)
        review = db.scalar(
            select(RestaurantReview)
            .where(
                RestaurantReview.review_id == review_id,
                RestaurantReview.restaurant_id == restaurant_id,
                RestaurantReview.customer_id == customer_id,
                RestaurantReview.status == 1,
            )
            .with_for_update()
        )
        if review is None:
            raise ReviewNotFound("Restaurant review not found")

        if "rating" in update.model_fields_set:
            review.rating = update.rating
        if "review_text" in update.model_fields_set:
            review.review_text = update.review_text
        review.updated_at = _utcnow()
        review.updated_by = user_id
        db.commit()
        return _restaurant_review_response(review)
    except ReviewError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_restaurant_review(
    db: Session,
    *,
    customer_id: int,
    restaurant_id: int,
    review_id: int,
) -> None:
    try:
        _require_active_restaurant(db, restaurant_id)
        review = db.scalar(
            select(RestaurantReview)
            .where(
                RestaurantReview.review_id == review_id,
                RestaurantReview.restaurant_id == restaurant_id,
                RestaurantReview.customer_id == customer_id,
                RestaurantReview.status == 1,
            )
            .with_for_update()
        )
        if review is None:
            raise ReviewNotFound("Restaurant review not found")
        db.delete(review)
        db.commit()
    except ReviewError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def list_food_item_reviews(
    db: Session,
    *,
    item_id: int,
    limit: int,
    offset: int,
) -> list[FoodItemReviewRead]:
    _require_active_menu_item(db, item_id)
    reviews = db.scalars(
        select(FoodItemReview)
        .where(
            FoodItemReview.item_id == item_id,
            FoodItemReview.status == 1,
        )
        .order_by(
            FoodItemReview.created_at.desc(),
            FoodItemReview.review_id.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()
    return [_food_item_review_response(review) for review in reviews]


def get_food_item_review(
    db: Session,
    *,
    item_id: int,
    review_id: int,
) -> FoodItemReviewRead:
    _require_active_menu_item(db, item_id)
    review = db.scalar(
        select(FoodItemReview).where(
            FoodItemReview.review_id == review_id,
            FoodItemReview.item_id == item_id,
            FoodItemReview.status == 1,
        )
    )
    if review is None:
        raise ReviewNotFound("Food item review not found")
    return _food_item_review_response(review)


def create_food_item_review(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    item_id: int,
    order_item_id: int,
    rating: int,
    review_text: str | None,
) -> FoodItemReviewRead:
    try:
        _require_active_menu_item(db, item_id)
        order_item = db.scalar(
            select(OrderItem)
            .join(Order, Order.order_id == OrderItem.order_id)
            .where(
                OrderItem.order_item_id == order_item_id,
                OrderItem.item_id == item_id,
                OrderItem.status == 1,
                Order.customer_id == customer_id,
                Order.status == 1,
            )
            .with_for_update()
        )
        if order_item is None:
            raise PurchaseNotFound(
                "A purchase of this menu item was not found"
            )

        existing_review = db.scalar(
            select(FoodItemReview.review_id)
            .where(
                FoodItemReview.order_item_id == order_item_id,
                FoodItemReview.customer_id == customer_id,
            )
            .with_for_update()
        )
        if existing_review is not None:
            raise DuplicateReview(
                "A review already exists for this purchased menu item"
            )

        review = FoodItemReview(
            order_item_id=order_item_id,
            item_id=item_id,
            customer_id=customer_id,
            rating=rating,
            review_text=review_text,
            created_by=user_id,
            status=1,
        )
        db.add(review)
        db.flush()
        db.refresh(review)
        response = _food_item_review_response(review)
        db.commit()
        return response
    except ReviewError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ReviewConstraintConflict(
            "The food item review conflicts with an existing database constraint"
        ) from error
    except SQLAlchemyError:
        db.rollback()
        raise


def update_food_item_review(
    db: Session,
    *,
    customer_id: int,
    user_id: int,
    item_id: int,
    review_id: int,
    update: ReviewUpdate,
) -> FoodItemReviewRead:
    try:
        _require_active_menu_item(db, item_id)
        review = db.scalar(
            select(FoodItemReview)
            .where(
                FoodItemReview.review_id == review_id,
                FoodItemReview.item_id == item_id,
                FoodItemReview.customer_id == customer_id,
                FoodItemReview.status == 1,
            )
            .with_for_update()
        )
        if review is None:
            raise ReviewNotFound("Food item review not found")

        if "rating" in update.model_fields_set:
            review.rating = update.rating
        if "review_text" in update.model_fields_set:
            review.review_text = update.review_text
        review.updated_at = _utcnow()
        review.updated_by = user_id
        db.commit()
        return _food_item_review_response(review)
    except ReviewError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_food_item_review(
    db: Session,
    *,
    customer_id: int,
    item_id: int,
    review_id: int,
) -> None:
    try:
        _require_active_menu_item(db, item_id)
        review = db.scalar(
            select(FoodItemReview)
            .where(
                FoodItemReview.review_id == review_id,
                FoodItemReview.item_id == item_id,
                FoodItemReview.customer_id == customer_id,
                FoodItemReview.status == 1,
            )
            .with_for_update()
        )
        if review is None:
            raise ReviewNotFound("Food item review not found")
        db.delete(review)
        db.commit()
    except ReviewError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def _require_active_restaurant(db: Session, restaurant_id: int) -> None:
    restaurant_id_found = db.scalar(
        select(Restaurant.restaurant_id).where(
            Restaurant.restaurant_id == restaurant_id,
            Restaurant.status == 1,
        )
    )
    if restaurant_id_found is None:
        raise ReviewTargetNotFound("Restaurant not found")


def _require_active_menu_item(db: Session, item_id: int) -> None:
    item_id_found = db.scalar(
        select(MenuItem.item_id).where(
            MenuItem.item_id == item_id,
            MenuItem.status == 1,
        )
    )
    if item_id_found is None:
        raise ReviewTargetNotFound("Menu item not found")


def _restaurant_review_response(
    review: RestaurantReview,
) -> RestaurantReviewRead:
    return RestaurantReviewRead(
        review_id=review.review_id,
        restaurant_id=review.restaurant_id,
        rating=review.rating,
        review_text=review.review_text,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _food_item_review_response(
    review: FoodItemReview,
) -> FoodItemReviewRead:
    return FoodItemReviewRead(
        review_id=review.review_id,
        item_id=review.item_id,
        rating=review.rating,
        review_text=review.review_text,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
