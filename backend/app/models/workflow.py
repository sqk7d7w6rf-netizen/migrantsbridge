import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import (
    WorkflowExecutionStatus,
    WorkflowStepType,
    WorkflowTriggerType,
)
from app.core.database import Base
from app.models.base import TimestampMixin


class Workflow(TimestampMixin, Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[WorkflowTriggerType] = mapped_column(nullable=False, index=True)
    trigger_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_generation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", lazy="selectin",
        order_by="WorkflowStep.step_order",
    )
    executions: Mapped[list["WorkflowExecution"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", lazy="noload"
    )
    created_by: Mapped["User | None"] = relationship(lazy="selectin")  # noqa: F821


class WorkflowStep(TimestampMixin, Base):
    __tablename__ = "workflow_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[WorkflowStepType] = mapped_column(nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    condition: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    on_failure: Mapped[str] = mapped_column(String(50), default="stop", nullable=False)

    workflow: Mapped["Workflow"] = relationship(back_populates="steps")
    logs: Mapped[list["WorkflowStepLog"]] = relationship(
        back_populates="step", cascade="all, delete-orphan", lazy="noload"
    )


class WorkflowExecution(TimestampMixin, Base):
    __tablename__ = "workflow_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[WorkflowExecutionStatus] = mapped_column(
        default=WorkflowExecutionStatus.RUNNING, nullable=False, index=True
    )
    triggered_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    trigger_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="executions", lazy="selectin")
    triggered_by: Mapped["User | None"] = relationship(lazy="selectin")  # noqa: F821
    step_logs: Mapped[list["WorkflowStepLog"]] = relationship(
        back_populates="execution", cascade="all, delete-orphan", lazy="noload"
    )


class WorkflowStepLog(TimestampMixin, Base):
    __tablename__ = "workflow_step_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[WorkflowExecutionStatus] = mapped_column(nullable=False)
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    execution: Mapped["WorkflowExecution"] = relationship(back_populates="step_logs")
    step: Mapped["WorkflowStep"] = relationship(back_populates="logs", lazy="selectin")


class RoutingRule(TimestampMixin, Base):
    __tablename__ = "routing_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    assign_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assign_to_role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    assign_to: Mapped["User | None"] = relationship(lazy="selectin")  # noqa: F821
    assign_to_role: Mapped["Role | None"] = relationship(lazy="selectin")  # noqa: F821
