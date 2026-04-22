"""Pydantic schemas for authentication requests and JWT payloads."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    """Payload used to authenticate an existing user."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        """Normalize email input before querying credentials."""

        return value.strip().lower()


class TokenResponse(BaseModel):
    """Authentication response that contains signed JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload used across dependency and router layers."""

    sub: str
    role: UserRole
    exp: int
    iat: int
    type: str
