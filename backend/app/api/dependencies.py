from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import JWT_SECRET_KEY
from app.core.security import JWT_ALGORITHM
from app.db.session import get_db
from app.models.user import Customer, DeliveryPartner, User

bearer_scheme = HTTPBearer(auto_error=False)
MAX_USER_ID = 9223372036854775807


def get_current_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Customer:
    user_id = _authenticated_user_id(credentials)
    statement = (
        select(Customer)
        .join(User, Customer.user_id == User.user_id)
        .where(
            User.user_id == user_id,
            User.status == 1,
            Customer.status == 1,
        )
    )
    customer = db.scalar(statement)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return customer


def get_current_delivery_partner(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DeliveryPartner:
    user_id = _authenticated_user_id(credentials)
    statement = (
        select(DeliveryPartner)
        .join(User, DeliveryPartner.user_id == User.user_id)
        .where(
            User.user_id == user_id,
            User.status == 1,
            DeliveryPartner.status == 1,
        )
    )
    partner = db.scalar(statement)
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An active delivery partner profile is required",
        )
    return partner


def _authenticated_user_id(
    credentials: HTTPAuthorizationCredentials | None,
) -> int:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication is not configured",
        )

    try:
        claims = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(claims.get("sub", ""))
    except (JWTError, TypeError, ValueError):
        raise unauthorized

    if user_id <= 0 or user_id > MAX_USER_ID:
        raise unauthorized
    return user_id
