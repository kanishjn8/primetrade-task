"""Authentication helpers for password hashing and JWT handling."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from app.schemas.token import TokenPayload


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
REFRESH_COOKIE_NAME = "refresh_token"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def _normalize_password(plain: str) -> str:
    """Normalize arbitrary-length passwords to a bcrypt-safe representation.

    bcrypt only processes the first 72 bytes of input. `passlib` raises a
    ValueError for longer inputs. To support long passphrases without truncation,
    we pre-hash them using SHA-256 and store/verify the resulting hex digest.

    For inputs <= 72 bytes UTF-8, we keep the original value.
    """

    plain_bytes = plain.encode("utf-8")
    if len(plain_bytes) <= 72:
        return plain
    return hashlib.sha256(plain_bytes).hexdigest()


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt."""

    return pwd_context.hash(_normalize_password(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""

    return pwd_context.verify(_normalize_password(plain), hashed)


def _create_token(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    """Create a signed JWT token with standard auth claims."""

    now = datetime.now(UTC)
    payload = {
        **data,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": token_type,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(data: dict[str, Any]) -> str:
    """Create a short-lived access token for API authorization."""

    return _create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type=ACCESS_TOKEN_TYPE,
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a longer-lived refresh token for session renewal."""

    return _create_token(
        data=data,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type=REFRESH_TOKEN_TYPE,
    )


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token into a typed payload object.

    Raises:
        ValueError: If the token is invalid or missing required claims.
    """

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenPayload.model_validate(payload)
    except (JWTError, ValueError) as exc:
        raise ValueError("Invalid or expired token.") from exc


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Validate credentials and return the matching active user if present."""

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_token_subject(user: User) -> dict[str, str]:
    """Return the canonical claims embedded into issued JWTs."""

    return {"sub": str(user.id), "role": user.role.value}
