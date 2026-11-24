from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY

PASSWORD_HASHER = PasswordHash.recommended()
JWT_ALGORITHM = "HS256"


class JWTConfigurationError(Exception):
    pass


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password, password_hash)
    except PwdlibError:
        return False


def create_access_token(subject: str) -> str:
    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY.encode("utf-8")) < 32:
        raise JWTConfigurationError(
            "Set JWT_SECRET_KEY to a secret containing at least 32 bytes."
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    claims = {"sub": subject, "exp": expires_at}
    return jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
