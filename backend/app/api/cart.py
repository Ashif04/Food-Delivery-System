from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_customer
from app.db.session import get_db
from app.models.user import Customer
from app.schemas.cart import CartItemCreate, CartItemQuantityUpdate, CartRead
from app.services.cart import (
    CartItemNotFound,
    CartNotFound,
    CartRestaurantConflict,
    CartStateConflict,
    InvalidCartSelection,
    MenuItemUnavailable,
    add_cart_item,
    clear_customer_cart,
    get_customer_cart,
    remove_cart_item,
    update_cart_item_quantity,
)

router = APIRouter(prefix="/cart", tags=["Cart"])
MAX_DATABASE_ID = 9223372036854775807


def _raise_cart_error(error: Exception) -> None:
    if isinstance(error, (CartItemNotFound, CartNotFound, MenuItemUnavailable)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    if isinstance(
        error,
        (CartRestaurantConflict, CartStateConflict),
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    if isinstance(error, InvalidCartSelection):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    if isinstance(error, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cart operation failed",
        ) from error
    raise error


@router.post(
    "/items",
    response_model=CartRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Menu item not found or unavailable"},
        409: {"description": "Cart contains items from another restaurant"},
        422: {"description": "Invalid variant or add-on selection"},
    },
)
def create_cart_item(
    request: CartItemCreate,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> CartRead:
    try:
        return add_cart_item(
            db,
            customer_id=customer.customer_id,
            user_id=customer.user_id,
            request=request,
        )
    except (CartNotFound, CartRestaurantConflict, CartStateConflict,
            InvalidCartSelection, MenuItemUnavailable, SQLAlchemyError) as error:
        _raise_cart_error(error)


@router.get(
    "",
    response_model=CartRead,
    responses={409: {"description": "Multiple active carts exist"}},
)
def read_cart(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> CartRead:
    try:
        return get_customer_cart(db, customer.customer_id)
    except (CartStateConflict, SQLAlchemyError) as error:
        _raise_cart_error(error)


@router.put(
    "/items/{cart_item_id}",
    response_model=CartRead,
    responses={404: {"description": "Cart item not found"}},
)
def update_cart_item(
    request: CartItemQuantityUpdate,
    cart_item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> CartRead:
    try:
        return update_cart_item_quantity(
            db,
            customer_id=customer.customer_id,
            cart_item_id=cart_item_id,
            quantity=request.quantity,
        )
    except (CartItemNotFound, CartNotFound, CartStateConflict,
            SQLAlchemyError) as error:
        _raise_cart_error(error)


@router.delete(
    "/items/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Cart item not found"}},
)
def delete_cart_item(
    cart_item_id: int = Path(gt=0, le=MAX_DATABASE_ID),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Response:
    try:
        remove_cart_item(
            db,
            customer_id=customer.customer_id,
            cart_item_id=cart_item_id,
        )
    except (CartItemNotFound, CartNotFound, SQLAlchemyError) as error:
        _raise_cart_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
) -> Response:
    try:
        clear_customer_cart(db, customer.customer_id)
    except CartNotFound as error:
        _raise_cart_error(error)
    except SQLAlchemyError as error:
        _raise_cart_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
