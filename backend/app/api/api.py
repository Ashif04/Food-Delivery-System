from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.cart import router as cart_router
from app.api.categories import router as categories_router
from app.api.coupons import router as coupons_router
from app.api.cuisines import router as cuisines_router
from app.api.delivery import router as delivery_router
from app.api.food_item_reviews import router as food_item_reviews_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.restaurants import router as restaurants_router
from app.api.restaurant_reviews import router as restaurant_reviews_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(cart_router)
router.include_router(restaurants_router)
router.include_router(categories_router)
router.include_router(coupons_router)
router.include_router(cuisines_router)
router.include_router(restaurant_reviews_router)
router.include_router(food_item_reviews_router)
router.include_router(orders_router)
router.include_router(payments_router)
router.include_router(delivery_router)

@router.get("/")
def home():
    return {"message": "Welcome to Food Delivery API"}