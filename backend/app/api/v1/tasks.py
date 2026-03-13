"""Task management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.task import (
    TaskAssign,
    TaskCommentCreate,
    TaskCommentRead,
    TaskCreate,
    TaskLogHours,
    TaskRead,
    TaskUpdate,
    WorkloadSummary,
)
from app.services import task_service

router = APIRouter()


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a new task."""
    return await task_service.create_task(session, payload, current_user.id)


@router.get("", response_model=PaginatedResponse[TaskRead])
async def list_tasks(
    pagination: PaginationParams = Depends(),
    assigned_to: UUID | None = None,
    case_id: UUID | None = None,
    client_id: UUID | None = None,
    status: str | None = None,
    priority: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List tasks with filters."""
    return await task_service.list_tasks(
        session, pagination, assigned_to, case_id, client_id, status, priority
    )


@router.get("/my-tasks", response_model=PaginatedResponse[TaskRead])
async def get_my_tasks(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get all tasks assigned to the current user."""
    return await task_service.get_my_tasks(session, current_user.id, pagination)


@router.get("/workload/{user_id}", response_model=WorkloadSummary)
async def get_workload(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get workload summary for a staff member."""
    return await task_service.compute_workload(session, user_id)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a task by ID."""
    return await task_service.get_task(session, task_id)


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a task."""
    return await task_service.update_task(session, task_id, payload)


@router.delete("/{task_id}", response_model=SuccessResponse)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Soft-delete a task."""
    await task_service.delete_task(session, task_id)
    return SuccessResponse(message="Task deleted successfully")


@router.post("/{task_id}/assign", response_model=TaskRead)
async def assign_task(
    task_id: UUID,
    payload: TaskAssign,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Assign a task to a staff member."""
    return await task_service.assign_task(session, task_id, payload)


@router.post("/{task_id}/comments", response_model=TaskCommentRead, status_code=201)
async def add_comment(
    task_id: UUID,
    payload: TaskCommentCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Add a comment to a task."""
    return await task_service.add_comment(session, task_id, payload, current_user.id)


@router.get("/{task_id}/comments", response_model=PaginatedResponse[TaskCommentRead])
async def list_comments(
    task_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List comments for a task."""
    return await task_service.list_comments(session, task_id, pagination)


@router.post("/{task_id}/log-hours")
async def log_hours(
    task_id: UUID,
    payload: TaskLogHours,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Log hours worked on a task."""
    return await task_service.log_hours(session, task_id, payload, current_user.id)
