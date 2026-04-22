"""Admin-only routes for managing registered users."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.schemas import UserRead, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserRead],
    summary="List all users",
    description="Return every registered user. Accessible only to admins.",
    responses={401: {"description": "Authentication required."}, 403: {"description": "Admin access required."}},
)
async def list_users(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UserRead]:
    """Return all users ordered by creation date descending."""

    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [UserRead.model_validate(user) for user in result.scalars().all()]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by ID",
    description="Return a specific user by identifier. Accessible only to admins.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Admin access required."},
        404: {"description": "User not found."},
    },
)
async def get_user(
    user_id: UUID,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Return one user record or raise 404 if it does not exist."""

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    description="Update an existing user's role or active status. Accessible only to admins.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Admin access required."},
        404: {"description": "User not found."},
        422: {"description": "The request body failed validation."},
    },
)
async def update_user(
    user_id: UUID,
    payload: Annotated[UserUpdate, Body(...)],
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Apply partial admin updates to a user record."""

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Delete an existing user and all of their tasks. Accessible only to admins.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Admin access required."},
        404: {"description": "User not found."},
    },
)
async def delete_user(
    user_id: UUID,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Delete a user record and return an empty 204 response."""

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    await db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
