"""Pydantic schemas for user request and response payloads."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserRole


PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,128}$")


class UserCreate(BaseModel):
    """Payload used to register a new application user."""

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=100)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        """Lowercase and trim the provided email address."""

        return value.strip().lower()

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        """Trim and validate that the username is not blank."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Username must not be empty.")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Enforce minimum password strength requirements."""

        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be at least 8 characters long and include one uppercase letter and one number."
            )
        return value


class UserUpdate(BaseModel):
    """Admin-only payload for updating user role or activation status."""

    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    """Serialized user representation returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
