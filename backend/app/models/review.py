
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class RestaurantReview(Base):
    __tablename__ = "restaurant_reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    customer_id = Column(
        BigInteger, ForeignKey("customers.customer_id"), nullable=False
    )
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )

    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="restaurant_reviews")
    customer = relationship("Customer", back_populates="restaurant_reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "customer_id",
            name="uq_restaurant_reviews"
        ),
    )


class FoodItemReview(Base):
    __tablename__ = "food_item_reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_item_id = Column(
        BigInteger, ForeignKey("order_items.order_item_id"), nullable=False
    )
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=False
    )
    customer_id = Column(
        BigInteger, ForeignKey("customers.customer_id"), nullable=False
    )

    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order_item = relationship("OrderItem", back_populates="reviews")
    menu_item = relationship("MenuItem", back_populates="food_item_reviews")
    customer = relationship("Customer", back_populates="food_item_reviews")

    __table_args__ = (
        UniqueConstraint(
            "order_item_id",
            "customer_id",
            name="uq_food_item_reviews"
        ),
    )
