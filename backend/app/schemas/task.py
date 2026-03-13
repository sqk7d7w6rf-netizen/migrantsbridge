from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    """Create a new task."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    case_id: UUID | None = None
    client_id: UUID | None = None
    assigned_to: UUID | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    estimated_hours: float | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)


class TaskRead(BaseModel):
    """Task read response."""

    id: UUID
    title: str
    description: str | None = None
    case_id: UUID | None = None
    client_id: UUID | None = None
    assigned_to: UUID | None = None
    assigned_to_name: str | None = None
    created_by: UUID
    created_by_name: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None = None
    completed_at: datetime | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    """Update a task."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    estimated_hours: float | None = None
    tags: list[str] | None = None


class TaskAssign(BaseModel):
    """Assign a task to a user."""

    assigned_to: UUID
    note: str | None = None


class TaskCommentCreate(BaseModel):
    """Create a task comment."""

    content: str = Field(min_length=1)


class TaskCommentRead(BaseModel):
    """Task comment read response."""

    id: UUID
    task_id: UUID
    author_id: UUID
    author_name: str | None = None
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskLogHours(BaseModel):
    """Log hours worked on a task."""

    hours: float = Field(gt=0)
    description: str | None = None
    logged_date: datetime | None = None


class WorkloadSummary(BaseModel):
    """Staff workload summary."""

    user_id: UUID
    user_name: str
    total_tasks: int
    open_tasks: int
    overdue_tasks: int
    completed_this_week: int
    estimated_hours_remaining: float
    actual_hours_this_week: float
