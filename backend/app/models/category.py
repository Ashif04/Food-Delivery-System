
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class FoodCategory(Base):
    __tablename__ = "food_categories"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    restaurants = relationship(
        "RestaurantCategory",
        back_populates="category"
    )
    menu_items = relationship(
        "MenuItem",
        back_populates="category"
    )


class RestaurantCategory(Base):
    __tablename__ = "restaurant_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    category_id = Column(
        BigInteger, ForeignKey("food_categories.category_id"), nullable=False
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    category = relationship(
    "FoodCategory",
    back_populates="restaurants"
    )
    restaurant = relationship(
    "Restaurant",
    back_populates="categories"
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "category_id",
            name="uq_restaurant_categories"
        ),
    )


class Cuisine(Base):
    __tablename__ = "cuisines"

    cuisine_id = Column(BigInteger, primary_key=True, autoincrement=True)
    cuisine_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    restaurants = relationship(
        "RestaurantCuisine",
        back_populates="cuisine"
    )


class RestaurantCuisine(Base):
    __tablename__ = "restaurant_cuisines"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    cuisine_id = Column(
        BigInteger, ForeignKey("cuisines.cuisine_id"), nullable=False
    )
    cuisine = relationship(
    "Cuisine",
    back_populates="restaurants"
    )
    restaurant = relationship(
    "Restaurant",
    back_populates="cuisines"
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "cuisine_id",
            name="uq_restaurant_cuisines"
        ),
    )
