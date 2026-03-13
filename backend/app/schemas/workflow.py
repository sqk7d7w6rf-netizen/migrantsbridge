from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class StepType(str, Enum):
    ACTION = "action"
    CONDITION = "condition"
    NOTIFICATION = "notification"
    APPROVAL = "approval"
    WAIT = "wait"
    AI_DECISION = "ai_decision"
    INTEGRATION = "integration"


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepLogStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TriggerType(str, Enum):
    MANUAL = "manual"
    EVENT = "event"
    SCHEDULE = "schedule"
    CONDITION = "condition"


class WorkflowStepCreate(BaseModel):
    """Create a workflow step."""

    name: str = Field(min_length=1, max_length=255)
    step_type: StepType
    order: int = Field(ge=0)
    config: dict[str, Any] = Field(default_factory=dict)
    condition: dict[str, Any] | None = None
    timeout_seconds: int | None = Field(default=None, ge=0)
    retry_count: int = Field(default=0, ge=0)
    on_failure: str = Field(default="stop", pattern="^(stop|skip|retry)$")


class WorkflowStepRead(BaseModel):
    """Workflow step read response."""

    id: UUID
    workflow_id: UUID
    name: str
    step_type: StepType
    order: int
    config: dict[str, Any]
    condition: dict[str, Any] | None = None
    timeout_seconds: int | None = None
    retry_count: int
    on_failure: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowCreate(BaseModel):
    """Create a new workflow."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: dict[str, Any] = Field(default_factory=dict)
    steps: list[WorkflowStepCreate] = Field(default_factory=list)


class WorkflowRead(BaseModel):
    """Workflow read response."""

    id: UUID
    name: str
    description: str | None = None
    status: WorkflowStatus
    trigger_type: TriggerType
    trigger_config: dict[str, Any]
    steps: list[WorkflowStepRead] = Field(default_factory=list)
    created_by: UUID
    executions_count: int = 0
    last_executed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowUpdate(BaseModel):
    """Update a workflow."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: WorkflowStatus | None = None
    trigger_type: TriggerType | None = None
    trigger_config: dict[str, Any] | None = None


class WorkflowGenerateRequest(BaseModel):
    """Request AI-powered workflow generation."""

    natural_language_description: str = Field(
        min_length=10,
        description="Natural language description of the desired workflow",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context like service_type, client_type, etc.",
    )


class WorkflowExecutionRead(BaseModel):
    """Workflow execution record."""

    id: UUID
    workflow_id: UUID
    workflow_name: str | None = None
    status: ExecutionStatus
    trigger_data: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    current_step: int | None = None

    model_config = {"from_attributes": True}


class StepLogRead(BaseModel):
    """Workflow step execution log."""

    id: UUID
    execution_id: UUID
    step_id: UUID
    step_name: str | None = None
    status: StepLogStatus
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None

    model_config = {"from_attributes": True}


class RoutingRuleCreate(BaseModel):
    """Create a routing rule."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    conditions: dict[str, Any] = Field(description="Conditions to match")
    action: dict[str, Any] = Field(description="Action to take when conditions match")
    priority: int = Field(default=0, ge=0)
    is_active: bool = True


class RoutingRuleRead(BaseModel):
    """Routing rule read response."""

    id: UUID
    name: str
    description: str | None = None
    conditions: dict[str, Any]
    action: dict[str, Any]
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
