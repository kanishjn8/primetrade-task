"""Pydantic schemas for task request and response payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Payload used to create a new task for the authenticated user."""

    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str | None, Field(max_length=5000)] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        """Trim and validate a task title."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Title must not be empty.")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Trim optional descriptions while preserving null values."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class TaskUpdate(BaseModel):
    """Payload used to update selected task fields."""

    title: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    description: Annotated[str | None, Field(max_length=5000)] = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    @field_validator("title")
    @classmethod
    def normalize_optional_title(cls, value: str | None) -> str | None:
        """Trim and validate an optional title update."""

        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Title must not be empty.")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_optional_description(cls, value: str | None) -> str | None:
        """Trim optional descriptions while preserving explicit null updates."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class TaskRead(BaseModel):
    """Serialized task representation returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
