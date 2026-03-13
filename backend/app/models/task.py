import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import Priority, TaskStatus, TaskType
from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class StaffTask(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "staff_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING, nullable=False, index=True)
    priority: Mapped[Priority] = mapped_column(default=Priority.MEDIUM, nullable=False, index=True)
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)

    assigned_to: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="tasks", foreign_keys=[assigned_to_id], lazy="selectin"
    )
    created_by: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[created_by_id], lazy="selectin"
    )
    case: Mapped["Case | None"] = relationship(back_populates="tasks", lazy="selectin")  # noqa: F821
    comments: Mapped[list["TaskComment"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", lazy="noload"
    )
    dependencies: Mapped[list["TaskDependency"]] = relationship(
        back_populates="task",
        foreign_keys="TaskDependency.task_id",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    dependents: Mapped[list["TaskDependency"]] = relationship(
        back_populates="depends_on_task",
        foreign_keys="TaskDependency.depends_on_id",
        lazy="noload",
    )


class TaskComment(TimestampMixin, Base):
    __tablename__ = "task_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    task: Mapped["StaffTask"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821


class TaskDependency(TimestampMixin, Base):
    __tablename__ = "task_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    depends_on_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("staff_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    task: Mapped["StaffTask"] = relationship(foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task: Mapped["StaffTask"] = relationship(foreign_keys=[depends_on_id], back_populates="dependents")

    __table_args__ = (
        UniqueConstraint("task_id", "depends_on_id", name="uq_task_dependency"),
    )
