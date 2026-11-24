
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


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    history_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)

    changed_by = Column(
        BigInteger, ForeignKey("users.user_id"), nullable=True
    )
    remarks = Column(Text, nullable=True)
    changed_at = Column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="status_history")
