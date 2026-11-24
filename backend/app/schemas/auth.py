from typing import Annotated

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
)


class RegisterRequest(BaseModel):
    full_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=100,
        ),
    ]
    email: Annotated[EmailStr, Field(max_length=150)]
    phone: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=15,
        ),
    ]
    password: Annotated[SecretStr, Field(min_length=8, max_length=128)]


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(max_length=150)]
    password: SecretStr


class RegisteredCustomer(BaseModel):
    user_id: int
    customer_id: int
    full_name: str
    email: EmailStr


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
