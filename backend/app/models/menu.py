
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    Text,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    category_id = Column(
        BigInteger, ForeignKey("food_categories.category_id"), nullable=False
    )

    item_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    food_type = Column(String(30), nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, server_default=text("TRUE"))
    preparation_time = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    restaurant = relationship(
    "Restaurant",
    back_populates="menu_items"
    )
    category = relationship(
    "FoodCategory",
    back_populates="menu_items"
    )
    variants = relationship(
    "ItemVariant",
    back_populates="menu_item"
    )
    images = relationship(
        "MenuItemImage",
        back_populates="menu_item"
    )
    cart_items = relationship("CartItem", back_populates="menu_item")
    order_items = relationship("OrderItem", back_populates="menu_item")
    food_item_reviews = relationship(
        "FoodItemReview",
        back_populates="menu_item"
    )
    addon_group_links = relationship(
        "MenuItemAddonGroup",
        back_populates="menu_item"
    )

class ItemVariant(Base):
    __tablename__ = "item_variants"

    variant_id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=False
    )

    variant_name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, server_default=text("TRUE"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    menu_item = relationship(
        "MenuItem",
        back_populates="variants"
    )
    cart_items = relationship("CartItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")


class MenuItemImage(Base):
    __tablename__ = "menu_item_images"

    image_id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=False
    )

    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, server_default=text("FALSE"))
    display_order = Column(Integer, server_default=text("1"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    menu_item = relationship(
        "MenuItem",
        back_populates="images"
    )
