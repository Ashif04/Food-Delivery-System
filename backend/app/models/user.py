
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    Numeric,
    Date,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    text
)
from app.db.base_class import Base
from sqlalchemy.orm import relationship

# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(15), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(String(500), nullable=True)
    email_verified = Column(Boolean, server_default=text("0"))
    phone_verified = Column(Boolean, server_default=text("0"))
    customer = relationship(
        "Customer",
        back_populates="user",
        foreign_keys="Customer.user_id",
        uselist=False
    )
    delivery_partner = relationship(
    "DeliveryPartner",
    back_populates="user",
    foreign_keys="DeliveryPartner.user_id",
    uselist=False
    )
    restaurant_owner = relationship(
    "RestaurantOwner",
    back_populates="user",
    foreign_keys="RestaurantOwner.user_id",
    uselist=False
    )
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        foreign_keys="UserRole.user_id"
    )
    addresses = relationship(
        "Address",
        back_populates="user",
        foreign_keys="Address.user_id"
    )
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))


# 2. ROLES TABLE
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))
    user_roles = relationship("UserRole", back_populates="role")


# 3. USER ROLES TABLE
class UserRole(Base):
    __tablename__ = "user_roles"

    user_role_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    role_id = Column(BigInteger, ForeignKey("roles.role_id"), nullable=False)
    assigned_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))

    __table_args__ = (
        UniqueConstraint("user_id", "role_id"),
    )
    user = relationship(
        "User",
        back_populates="user_roles",
        foreign_keys=[user_id]
    )
    role = relationship("Role", back_populates="user_roles")


# 4. CUSTOMERS TABLE
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    user = relationship(
        "User",
        back_populates="customer",
        foreign_keys=[user_id]
    )
    carts = relationship("Cart", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    restaurant_reviews = relationship(
        "RestaurantReview",
        back_populates="customer"
    )
    food_item_reviews = relationship(
        "FoodItemReview",
        back_populates="customer"
    )
  
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(Integer, nullable=False, server_default=text("1"))


# 5. DELIVERY PARTNERS TABLE
class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    partner_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True)
    vehicle_type = Column(String(50), nullable=True)
    vehicle_number = Column(String(30), nullable=True, unique=True)
    driving_license_number = Column(String(50), nullable=True, unique=True)
    verification_status = Column(String(30), server_default=text("'PENDING'"))
    availability_status = Column(String(30), server_default=text("'AVAILABLE'"))
    current_latitude = Column(Numeric(10, 7), nullable=True)
    current_longitude = Column(Numeric(10, 7), nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    user = relationship(
        "User",
        back_populates="delivery_partner",
        foreign_keys=[user_id]
    )
    delivery_assignments = relationship(
        "DeliveryAssignment",
        back_populates="partner"
    )
    status = Column(Integer, nullable=False, server_default=text("1"))


# 6. RESTAURANT OWNERS TABLE
class RestaurantOwner(Base):
    __tablename__ = "restaurant_owners"

    owner_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True)
    verification_status = Column(String(30), server_default=text("'PENDING'"))

    user = relationship(
        "User",
        back_populates="restaurant_owner",
        foreign_keys=[user_id]
    )

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True, server_default=text("NULL"))
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    restaurants = relationship("Restaurant", back_populates="owner")
    status = Column(Integer, nullable=False, server_default=text("1"))