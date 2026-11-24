from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    JWTConfigurationError,
    create_access_token,
    verify_password,
)
from app.db.session import get_db
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RegisteredCustomer,
    RegisterRequest,
)
from app.services.auth import (
    CustomerRoleNotConfigured,
    EmailAlreadyRegistered,
    PhoneAlreadyRegistered,
    RegistrationConflict,
    get_active_user_by_email,
    register_customer,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisteredCustomer,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Email or phone already registered"},
        503: {"description": "Active Customer role is not configured"},
    },
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisteredCustomer:
    try:
        user, customer = register_customer(
            db,
            full_name=request.full_name.strip(),
            email=str(request.email),
            phone=request.phone.strip(),
            password=request.password.get_secret_value(),
        )
    except EmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from error
    except PhoneAlreadyRegistered as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone already registered",
        ) from error
    except RegistrationConflict as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone already registered",
        ) from error
    except CustomerRoleNotConfigured as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An active Customer role must be configured before registration",
        ) from error

    return RegisteredCustomer(
        user_id=user.user_id,
        customer_id=customer.customer_id,
        full_name=user.full_name,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    responses={401: {"description": "Invalid email or password"}},
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> AccessTokenResponse:
    user = get_active_user_by_email(db, str(request.email))
    if user is None or not verify_password(
        request.password.get_secret_value(),
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        access_token = create_access_token(str(user.user_id))
    except JWTConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    return AccessTokenResponse(
        access_token=access_token,
        token_type="bearer",
    )
