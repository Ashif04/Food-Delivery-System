
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


class Coupon(Base):
    __tablename__ = "coupons"

    coupon_id = Column(BigInteger, primary_key=True, autoincrement=True)

    coupon_code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    discount_type = Column(String(30), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)
    maximum_discount = Column(Numeric(10, 2), nullable=True)
    minimum_order_amount = Column(
        Numeric(10, 2), server_default=text("0.00")
    )

    usage_limit = Column(Integer, nullable=True)
    per_user_limit = Column(Integer, nullable=True)

    valid_from = Column(TIMESTAMP, nullable=True)
    valid_until = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, server_default=text("TRUE"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order_links = relationship("OrderCoupon", back_populates="coupon")


class OrderCoupon(Base):
    __tablename__ = "order_coupons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    coupon_id = Column(
        BigInteger, ForeignKey("coupons.coupon_id"), nullable=False
    )

    discount_amount = Column(Numeric(10, 2), nullable=False)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="coupon_link")
    coupon = relationship("Coupon", back_populates="order_links")

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            name="uq_order_coupons_order"
        ),
    )
