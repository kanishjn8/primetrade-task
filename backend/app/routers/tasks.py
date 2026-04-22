"""Task CRUD routes for authenticated users and admins."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TaskCreate, TaskRead, TaskUpdate
from app.services import create_task, delete_task, get_task_by_id, get_tasks, update_task


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=list[TaskRead],
    summary="List tasks",
    description="Return tasks visible to the authenticated user. Admins receive all tasks.",
    responses={401: {"description": "Authentication required."}},
)
async def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TaskRead]:
    """List tasks accessible to the current user."""

    tasks = await get_tasks(db, current_user)
    return [TaskRead.model_validate(task) for task in tasks]


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Create a new task owned by the authenticated user.",
    responses={401: {"description": "Authentication required."}, 422: {"description": "Validation failed."}},
)
async def create_task_endpoint(
    payload: Annotated[TaskCreate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    """Create a task for the current user and return its serialized representation."""

    task = await create_task(db, current_user.id, payload)
    return TaskRead.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a task by ID",
    description="Return one task if it belongs to the caller or the caller is an admin.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Access to this task is forbidden."},
        404: {"description": "Task not found."},
    },
)
async def get_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    """Fetch a single task that the current user may access."""

    task = await get_task_by_id(db, task_id, current_user)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Update a task if it belongs to the caller or the caller is an admin.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Access to this task is forbidden."},
        404: {"description": "Task not found."},
        422: {"description": "Validation failed."},
    },
)
async def update_task_endpoint(
    task_id: UUID,
    payload: Annotated[TaskUpdate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    """Update a task and return the saved representation."""

    task = await update_task(db, task_id, current_user, payload)
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task if it belongs to the caller or the caller is an admin.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Access to this task is forbidden."},
        404: {"description": "Task not found."},
    },
)
async def delete_task_endpoint(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Delete a task and return an empty 204 response."""

    await delete_task(db, task_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
