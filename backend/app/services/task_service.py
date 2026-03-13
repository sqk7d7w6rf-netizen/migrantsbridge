"""Task management service."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Priority, TaskStatus as ModelTaskStatus, TaskType
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.task import StaffTask, TaskComment
from app.models.user import User
from app.schemas.task import (
    TaskAssign,
    TaskCommentCreate,
    TaskCommentRead,
    TaskCreate,
    TaskLogHours,
    TaskRead,
    TaskStatus,
    TaskUpdate,
    WorkloadSummary,
)


async def _get_task_or_404(session: AsyncSession, task_id: UUID) -> StaffTask:
    result = await session.execute(
        select(StaffTask).where(StaffTask.id == task_id, StaffTask.is_deleted == False)
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _build_task_read(task: StaffTask) -> TaskRead:
    """Map StaffTask model to TaskRead schema using selectin-loaded relationships."""
    assigned_name = None
    if task.assigned_to:
        assigned_name = f"{task.assigned_to.first_name} {task.assigned_to.last_name}"

    created_name = None
    if task.created_by:
        created_name = f"{task.created_by.first_name} {task.created_by.last_name}"

    actual_hours = float(task.actual_hours) if task.actual_hours else None

    # Map model TaskStatus to schema TaskStatus
    status_map = {
        ModelTaskStatus.PENDING: TaskStatus.TODO,
        ModelTaskStatus.IN_PROGRESS: TaskStatus.IN_PROGRESS,
        ModelTaskStatus.BLOCKED: TaskStatus.BLOCKED,
        ModelTaskStatus.COMPLETED: TaskStatus.COMPLETED,
        ModelTaskStatus.CANCELLED: TaskStatus.CANCELLED,
    }
    schema_status = status_map.get(task.status, TaskStatus.TODO)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        case_id=task.case_id,
        client_id=None,
        assigned_to=task.assigned_to_id,
        assigned_to_name=assigned_name,
        created_by=task.created_by_id or task.assigned_to_id or UUID("00000000-0000-0000-0000-000000000000"),
        created_by_name=created_name,
        status=schema_status,
        priority=task.priority.value,
        due_date=datetime.combine(task.due_date, datetime.min.time()) if task.due_date else None,
        completed_at=task.completed_at,
        estimated_hours=float(task.estimated_hours) if task.estimated_hours else None,
        actual_hours=actual_hours,
        tags=[],
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


async def create_task(
    session: AsyncSession, payload: TaskCreate, created_by: UUID
) -> TaskRead:
    """Create a new task."""
    # Map schema priority to model Priority
    try:
        model_priority = Priority(payload.priority.value)
    except ValueError:
        model_priority = Priority.MEDIUM

    task = StaffTask(
        title=payload.title,
        description=payload.description,
        case_id=payload.case_id,
        assigned_to_id=payload.assigned_to,
        created_by_id=created_by,
        task_type=TaskType.OTHER,
        status=ModelTaskStatus.PENDING,
        priority=model_priority,
        due_date=payload.due_date.date() if payload.due_date else None,
        estimated_hours=Decimal(str(payload.estimated_hours)) if payload.estimated_hours else None,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return _build_task_read(task)


async def get_task(session: AsyncSession, task_id: UUID) -> TaskRead:
    """Get a task by ID."""
    task = await _get_task_or_404(session, task_id)
    return _build_task_read(task)


async def list_tasks(
    session: AsyncSession,
    pagination: PaginationParams,
    assigned_to: UUID | None = None,
    case_id: UUID | None = None,
    client_id: UUID | None = None,
    status_filter: str | None = None,
    priority: str | None = None,
) -> PaginatedResponse[TaskRead]:
    """List tasks with filters."""
    query = select(StaffTask).where(StaffTask.is_deleted == False)

    if assigned_to:
        query = query.where(StaffTask.assigned_to_id == assigned_to)
    if case_id:
        query = query.where(StaffTask.case_id == case_id)
    if status_filter:
        # Map schema status values to model status
        status_map = {
            "todo": ModelTaskStatus.PENDING,
            "in_progress": ModelTaskStatus.IN_PROGRESS,
            "blocked": ModelTaskStatus.BLOCKED,
            "in_review": ModelTaskStatus.IN_PROGRESS,
            "completed": ModelTaskStatus.COMPLETED,
            "cancelled": ModelTaskStatus.CANCELLED,
        }
        model_status = status_map.get(status_filter)
        if model_status:
            query = query.where(StaffTask.status == model_status)
    if priority:
        try:
            query = query.where(StaffTask.priority == Priority(priority))
        except ValueError:
            pass

    query = query.order_by(StaffTask.created_at.desc())
    result = await paginate(session, query, pagination)
    result.items = [_build_task_read(task) for task in result.items]
    return result


async def update_task(
    session: AsyncSession, task_id: UUID, payload: TaskUpdate
) -> TaskRead:
    """Update a task."""
    task = await _get_task_or_404(session, task_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        schema_status = update_data.pop("status")
        status_map = {
            TaskStatus.TODO: ModelTaskStatus.PENDING,
            TaskStatus.IN_PROGRESS: ModelTaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED: ModelTaskStatus.BLOCKED,
            TaskStatus.COMPLETED: ModelTaskStatus.COMPLETED,
            TaskStatus.CANCELLED: ModelTaskStatus.CANCELLED,
        }
        task.status = status_map.get(schema_status, ModelTaskStatus.PENDING)

        # Auto-set completed_at
        if schema_status == TaskStatus.COMPLETED and task.completed_at is None:
            task.completed_at = datetime.now(timezone.utc)
        elif schema_status != TaskStatus.COMPLETED:
            task.completed_at = None

    if "priority" in update_data and update_data["priority"] is not None:
        try:
            task.priority = Priority(update_data.pop("priority").value)
        except (ValueError, AttributeError):
            update_data.pop("priority", None)

    if "due_date" in update_data:
        due = update_data.pop("due_date")
        task.due_date = due.date() if due and hasattr(due, "date") else due

    if "estimated_hours" in update_data:
        eh = update_data.pop("estimated_hours")
        task.estimated_hours = Decimal(str(eh)) if eh is not None else None

    # Set remaining simple fields (title, description)
    for field in ("title", "description"):
        if field in update_data and update_data[field] is not None:
            setattr(task, field, update_data[field])

    session.add(task)
    await session.flush()
    await session.refresh(task)
    return _build_task_read(task)


async def delete_task(session: AsyncSession, task_id: UUID) -> None:
    """Soft-delete a task."""
    task = await _get_task_or_404(session, task_id)
    task.is_deleted = True
    task.deleted_at = datetime.now(timezone.utc)
    session.add(task)


async def assign_task(
    session: AsyncSession, task_id: UUID, payload: TaskAssign
) -> TaskRead:
    """Assign a task to a staff member."""
    task = await _get_task_or_404(session, task_id)

    # Verify user exists
    user_result = await session.execute(
        select(User).where(User.id == payload.assigned_to, User.is_active == True)
    )
    if user_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive"
        )

    task.assigned_to_id = payload.assigned_to
    session.add(task)

    if payload.note:
        comment = TaskComment(
            task_id=task.id,
            author_id=payload.assigned_to,
            content=f"Task assigned. Note: {payload.note}",
        )
        session.add(comment)

    await session.flush()
    await session.refresh(task)
    return _build_task_read(task)


async def get_my_tasks(
    session: AsyncSession, user_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[TaskRead]:
    """Get all tasks assigned to the current user."""
    return await list_tasks(session, pagination, assigned_to=user_id)


# --- Comments ---

async def add_comment(
    session: AsyncSession, task_id: UUID, payload: TaskCommentCreate, author_id: UUID
) -> TaskCommentRead:
    """Add a comment to a task."""
    await _get_task_or_404(session, task_id)

    comment = TaskComment(
        task_id=task_id,
        author_id=author_id,
        content=payload.content,
    )
    session.add(comment)
    await session.flush()
    await session.refresh(comment)

    author_name = None
    if comment.author:
        author_name = f"{comment.author.first_name} {comment.author.last_name}"

    return TaskCommentRead(
        id=comment.id,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author_name=author_name,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


async def list_comments(
    session: AsyncSession, task_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[TaskCommentRead]:
    """List comments for a task."""
    await _get_task_or_404(session, task_id)
    query = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
    )
    result = await paginate(session, query, pagination)
    result.items = [
        TaskCommentRead(
            id=c.id,
            task_id=c.task_id,
            author_id=c.author_id,
            author_name=f"{c.author.first_name} {c.author.last_name}" if c.author else None,
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in result.items
    ]
    return result


# --- Time Logging ---

async def log_hours(
    session: AsyncSession, task_id: UUID, payload: TaskLogHours, user_id: UUID
) -> dict:
    """Log hours worked on a task by updating actual_hours."""
    task = await _get_task_or_404(session, task_id)

    current_hours = task.actual_hours or Decimal("0.00")
    task.actual_hours = current_hours + Decimal(str(payload.hours))
    session.add(task)

    # Also add a comment to track the log
    if payload.description:
        comment = TaskComment(
            task_id=task_id,
            author_id=user_id,
            content=f"Logged {payload.hours}h: {payload.description}",
        )
        session.add(comment)

    await session.flush()

    return {
        "task_id": str(task.id),
        "hours_logged": payload.hours,
        "total_actual_hours": float(task.actual_hours),
        "description": payload.description,
    }


# --- Workload ---

async def compute_workload(session: AsyncSession, user_id: UUID) -> WorkloadSummary:
    """Compute workload summary for a staff member."""
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_name = f"{user.first_name} {user.last_name}"

    # Total tasks
    total_result = await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.assigned_to_id == user_id, StaffTask.is_deleted == False
        )
    )
    total_tasks = total_result.scalar_one()

    # Open tasks (not completed/cancelled)
    open_result = await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.assigned_to_id == user_id,
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([ModelTaskStatus.COMPLETED, ModelTaskStatus.CANCELLED]),
        )
    )
    open_tasks = open_result.scalar_one()

    # Overdue tasks
    today = date.today()
    overdue_result = await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.assigned_to_id == user_id,
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([ModelTaskStatus.COMPLETED, ModelTaskStatus.CANCELLED]),
            StaffTask.due_date < today,
        )
    )
    overdue_tasks = overdue_result.scalar_one()

    # Completed this week
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    completed_result = await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.assigned_to_id == user_id,
            StaffTask.is_deleted == False,
            StaffTask.status == ModelTaskStatus.COMPLETED,
            StaffTask.completed_at >= week_start,
        )
    )
    completed_this_week = completed_result.scalar_one()

    # Estimated hours remaining
    est_result = await session.execute(
        select(func.coalesce(func.sum(StaffTask.estimated_hours), Decimal("0.00"))).where(
            StaffTask.assigned_to_id == user_id,
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([ModelTaskStatus.COMPLETED, ModelTaskStatus.CANCELLED]),
        )
    )
    estimated_hours_remaining = float(est_result.scalar_one())

    # Actual hours this week (from actual_hours on completed tasks this week)
    hours_result = await session.execute(
        select(func.coalesce(func.sum(StaffTask.actual_hours), Decimal("0.00"))).where(
            StaffTask.assigned_to_id == user_id,
            StaffTask.is_deleted == False,
            StaffTask.completed_at >= week_start,
        )
    )
    actual_hours_this_week = float(hours_result.scalar_one())

    return WorkloadSummary(
        user_id=user_id,
        user_name=user_name,
        total_tasks=total_tasks,
        open_tasks=open_tasks,
        overdue_tasks=overdue_tasks,
        completed_this_week=completed_this_week,
        estimated_hours_remaining=estimated_hours_remaining,
        actual_hours_this_week=actual_hours_this_week,
    )
