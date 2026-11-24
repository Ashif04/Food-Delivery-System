
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class AddonGroup(Base):
    __tablename__ = "addon_groups"

    addon_group_id = Column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )

    group_name = Column(String(100), nullable=False)
    is_required = Column(Boolean, server_default=text("FALSE"))
    min_selection = Column(Integer, server_default=text("0"))
    max_selection = Column(Integer, server_default=text("1"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    addons = relationship(
        "Addon",
        back_populates="addon_group"
    )
    restaurant = relationship(
        "Restaurant",
        back_populates="addon_groups"
    )
    menu_item_links = relationship(
        "MenuItemAddonGroup",
        back_populates="addon_group"
    )


class Addon(Base):
    __tablename__ = "addons"

    addon_id = Column(BigInteger, primary_key=True, autoincrement=True)
    addon_group_id = Column(
        BigInteger, ForeignKey("addon_groups.addon_group_id"), nullable=False
    )

    addon_name = Column(String(100), nullable=False)
    additional_price = Column(Numeric(10, 2), server_default=text("0.00"))
    is_available = Column(Boolean, server_default=text("TRUE"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    addon_group = relationship(
        "AddonGroup",
        back_populates="addons"
    )
    cart_item_links = relationship("CartItemAddon", back_populates="addon")
    order_item_links = relationship("OrderItemAddon", back_populates="addon")


class MenuItemAddonGroup(Base):
    __tablename__ = "menu_item_addon_groups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=False
    )
    addon_group_id = Column(
        BigInteger, ForeignKey("addon_groups.addon_group_id"), nullable=False
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    menu_item = relationship(
        "MenuItem",
        back_populates="addon_group_links"
    )
    addon_group = relationship(
        "AddonGroup",
        back_populates="menu_item_links"
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "addon_group_id",
            name="uq_menu_item_addon_groups"
        ),
    )
