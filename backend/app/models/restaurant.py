
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    Time,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )

    address_type = Column(String(30), nullable=True)
    house_number = Column(String(100), nullable=True)
    street = Column(String(150), nullable=True)
    area = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    landmark = Column(String(150), nullable=True)

    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)

    is_default = Column(Boolean, server_default=text("FALSE"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    user = relationship("User", back_populates="addresses", foreign_keys=[user_id])
    orders = relationship("Order", back_populates="address")


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(BigInteger, primary_key=True, autoincrement=True)

    owner_id = Column(
        BigInteger, ForeignKey("restaurant_owners.owner_id"), nullable=False
    )
    restaurant_hours = relationship(
    "RestaurantHour",
    back_populates="restaurant"
    )
    categories = relationship(
    "RestaurantCategory",
    back_populates="restaurant"
    )
    cuisines = relationship(
    "RestaurantCuisine",
    back_populates="restaurant"
    )
    menu_items = relationship(
        "MenuItem",
        back_populates="restaurant"
    )
    addon_groups = relationship(
        "AddonGroup",
        back_populates="restaurant"
    )
    carts = relationship("Cart", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("RestaurantReview", back_populates="restaurant")

    restaurant_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(15), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)

    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)

    logo_url = Column(String(500), nullable=True)
    cover_image = Column(String(500), nullable=True)

    average_rating = Column(Numeric(3, 2), server_default=text("0.00"))
    minimum_order_amount = Column(Numeric(10, 2), server_default=text("0.00"))
    estimated_delivery_time = Column(Integer, nullable=True)

    is_open = Column(Boolean, server_default=text("TRUE"))
    restaurant_status = Column(
        String(30), server_default=text("'PENDING'")
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    owner = relationship("RestaurantOwner", back_populates="restaurants")
    status = Column(Integer, nullable=False, server_default=text("1"))


class RestaurantHour(Base):
    __tablename__ = "restaurant_hours"

    hours_id = Column(BigInteger, primary_key=True, autoincrement=True)

    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    restaurant = relationship(
        "Restaurant",
        back_populates="restaurant_hours"
    )

    day_of_week = Column(String(20), nullable=False)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    is_closed = Column(Boolean, server_default=text("FALSE"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "day_of_week",
            name="uq_restaurant_hours_day"
        ),
    )
