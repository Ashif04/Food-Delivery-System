
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    assignment_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_id = Column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    partner_id = Column(
        BigInteger, ForeignKey("delivery_partners.partner_id"), nullable=False
    )

    assignment_status = Column(
        String(30), server_default=text("'ASSIGNED'")
    )

    assigned_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    accepted_at = Column(TIMESTAMP, nullable=True)
    rejected_at = Column(TIMESTAMP, nullable=True)
    picked_up_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    order = relationship("Order", back_populates="delivery_assignments")
    partner = relationship(
        "DeliveryPartner",
        back_populates="delivery_assignments"
    )
    tracking_points = relationship(
        "DeliveryTracking",
        back_populates="assignment"
    )


class DeliveryTracking(Base):
    __tablename__ = "delivery_tracking"

    tracking_id = Column(BigInteger, primary_key=True, autoincrement=True)

    assignment_id = Column(
        BigInteger,
        ForeignKey("delivery_assignments.assignment_id"),
        nullable=False
    )

    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)

    recorded_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    assignment = relationship(
        "DeliveryAssignment",
        back_populates="tracking_points"
    )
