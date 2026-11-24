
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    payment_method_id = Column(
        BigInteger, primary_key=True, autoincrement=True
    )
    method_name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    payments = relationship("Payment", back_populates="payment_method")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    payment_method_id = Column(
        BigInteger,
        ForeignKey("payment_methods.payment_method_id"),
        nullable=False
    )

    payment_reference = Column(String(100), nullable=True, unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(
        String(30), server_default=text("'PENDING'")
    )
    gateway_transaction_id = Column(String(150), nullable=True)
    paid_at = Column(TIMESTAMP, nullable=True)

    refund_amount = Column(Numeric(10, 2), server_default=text("0.00"))
    refund_status = Column(String(30), nullable=True)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
