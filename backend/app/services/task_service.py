"""Business logic for task CRUD with ownership enforcement."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, owner_id: UUID, payload: TaskCreate) -> Task:
    """Create and persist a task owned by the provided user."""

    task = Task(owner_id=owner_id, **payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(db: AsyncSession, user: User) -> list[Task]:
    """Return tasks visible to the current user, ordered newest first."""

    statement = select(Task).order_by(Task.created_at.desc())
    if user.role != UserRole.ADMIN:
        statement = statement.where(Task.owner_id == user.id)
    result = await db.execute(statement)
    return list(result.scalars().unique().all())


async def get_task_by_id(db: AsyncSession, task_id: UUID, user: User) -> Task:
    """Return a task if it exists and the user is allowed to access it."""

    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    if user.role != UserRole.ADMIN and task.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this task.")
    return task


async def update_task(db: AsyncSession, task_id: UUID, user: User, payload: TaskUpdate) -> Task:
    """Apply partial updates to a task visible to the current user."""

    task = await get_task_by_id(db, task_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: UUID, user: User) -> None:
    """Delete a task after confirming the caller may access it."""

    task = await get_task_by_id(db, task_id, user)
    await db.delete(task)
    await db.commit()
