
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False, unique=True)

    customer_id = Column(
        BigInteger, ForeignKey("customers.customer_id"), nullable=False
    )
    restaurant_id = Column(
        BigInteger, ForeignKey("restaurants.restaurant_id"), nullable=False
    )
    address_id = Column(
        BigInteger, ForeignKey("addresses.address_id"), nullable=True
    )

    delivery_address_snapshot = Column(Text, nullable=True)
    delivery_latitude = Column(Numeric(10, 7), nullable=True)
    delivery_longitude = Column(Numeric(10, 7), nullable=True)

    subtotal = Column(Numeric(10, 2), nullable=False)
    item_discount = Column(Numeric(10, 2), server_default=text("0.00"))
    tax_amount = Column(Numeric(10, 2), server_default=text("0.00"))
    delivery_fee = Column(Numeric(10, 2), server_default=text("0.00"))
    platform_fee = Column(Numeric(10, 2), server_default=text("0.00"))
    packaging_fee = Column(Numeric(10, 2), server_default=text("0.00"))
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(
        String(30), server_default=text("'PENDING'")
    )
    order_status = Column(
        String(30), server_default=text("'PLACED'")
    )

    special_instructions = Column(Text, nullable=True)

    placed_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    accepted_at = Column(TIMESTAMP, nullable=True)
    delivered_at = Column(TIMESTAMP, nullable=True)
    cancelled_at = Column(TIMESTAMP, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    address = relationship("Address", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    delivery_assignments = relationship(
        "DeliveryAssignment",
        back_populates="order"
    )
    status_history = relationship("OrderStatusHistory", back_populates="order")
    coupon_link = relationship(
        "OrderCoupon",
        back_populates="order",
        uselist=False
    )
    restaurant_reviews = relationship(
        "RestaurantReview",
        back_populates="order"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    item_id = Column(
        BigInteger, ForeignKey("menu_items.item_id"), nullable=True
    )
    variant_id = Column(
        BigInteger, ForeignKey("item_variants.variant_id"), nullable=True
    )

    item_name = Column(String(150), nullable=False)
    variant_name = Column(String(100), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    variant = relationship("ItemVariant", back_populates="order_items")
    addons = relationship("OrderItemAddon", back_populates="order_item")
    reviews = relationship("FoodItemReview", back_populates="order_item")


class OrderItemAddon(Base):
    __tablename__ = "order_item_addons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_item_id = Column(
        BigInteger, ForeignKey("order_items.order_item_id"), nullable=False
    )
    addon_id = Column(
        BigInteger, ForeignKey("addons.addon_id"), nullable=True
    )

    addon_name = Column(String(100), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text("1"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order_item = relationship("OrderItem", back_populates="addons")
    addon = relationship("Addon", back_populates="order_item_links")
