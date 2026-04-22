"""Shared enumeration types used by ORM models and schemas."""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Supported authorization roles for application users."""

    USER = "user"
    ADMIN = "admin"


class TaskStatus(str, Enum):
    """Lifecycle states available for task records."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Priority levels available for task records."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
