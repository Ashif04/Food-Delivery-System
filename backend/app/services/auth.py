from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import Customer, Role, User, UserRole


class EmailAlreadyRegistered(Exception):
    pass


class PhoneAlreadyRegistered(Exception):
    pass


class CustomerRoleNotConfigured(Exception):
    pass


class RegistrationConflict(Exception):
    pass


def register_customer(
    db: Session,
    *,
    full_name: str,
    email: str,
    phone: str,
    password: str,
) -> tuple[User, Customer]:
    password_hash = hash_password(password)

    try:
        if db.scalar(select(User.user_id).where(User.email == email)) is not None:
            raise EmailAlreadyRegistered

        if db.scalar(select(User.user_id).where(User.phone == phone)) is not None:
            raise PhoneAlreadyRegistered

        customer_role = db.scalar(
            select(Role).where(
                func.lower(Role.role_name) == "customer",
                Role.status == 1,
            )
        )
        if customer_role is None:
            raise CustomerRoleNotConfigured

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            status=1,
        )
        db.add(user)
        db.flush()

        customer = Customer(user_id=user.user_id, status=1)
        user_role = UserRole(
            user_id=user.user_id,
            role_id=customer_role.role_id,
            status=1,
        )
        db.add_all([customer, user_role])
        db.flush()
        db.commit()

    except (EmailAlreadyRegistered, PhoneAlreadyRegistered, CustomerRoleNotConfigured):
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        if db.scalar(select(User.user_id).where(User.email == email)) is not None:
            db.rollback()
            raise EmailAlreadyRegistered from error
        if db.scalar(select(User.user_id).where(User.phone == phone)) is not None:
            db.rollback()
            raise PhoneAlreadyRegistered from error
        db.rollback()
        raise RegistrationConflict from error
    except SQLAlchemyError:
        db.rollback()
        raise

    return user, customer


def get_active_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(
        User.email == email,
        User.status == 1,
    )
    return db.scalar(statement)
