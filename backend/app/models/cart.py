
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(
        BigInteger, ForeignKey("customers.customer_id"), nullable=False
    )
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    cart_status = Column(String(30), server_default=text("'ACTIVE'"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    customer = relationship("Customer", back_populates="carts")
    restaurant = relationship("Restaurant", back_populates="carts")
    items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    cart_id = Column(
        BigInteger, ForeignKey("carts.cart_id"), nullable=False
    )
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=False
    )
    variant_id = Column(
        BigInteger, ForeignKey("item_variants.variant_id"), nullable=True
    )

    quantity = Column(Integer, nullable=False, server_default=text("1"))
    special_instructions = Column(Text, nullable=True)
    added_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    cart = relationship("Cart", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="cart_items")
    variant = relationship("ItemVariant", back_populates="cart_items")
    addons = relationship("CartItemAddon", back_populates="cart_item")


class CartItemAddon(Base):
    __tablename__ = "cart_item_addons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cart_item_id = Column(
        BigInteger, ForeignKey("cart_items.cart_item_id"), nullable=False
    )
    addon_id = Column(
        BigInteger, ForeignKey("addons.addon_id"), nullable=False
    )

    quantity = Column(Integer, nullable=False, server_default=text("1"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    cart_item = relationship("CartItem", back_populates="addons")
    addon = relationship("Addon", back_populates="cart_item_links")
