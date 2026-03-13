import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import CaseStatus, CaseType, Priority
from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin

case_number_seq = Sequence("case_number_seq", start=10001)


class Case(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number: Mapped[int] = mapped_column(
        Integer, case_number_seq, server_default=case_number_seq.next_value(), unique=True, nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_type: Mapped[CaseType] = mapped_column(nullable=False, index=True)
    sub_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[CaseStatus] = mapped_column(default=CaseStatus.INTAKE, nullable=False, index=True)
    priority: Mapped[Priority] = mapped_column(default=Priority.MEDIUM, nullable=False, index=True)
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="cases", lazy="selectin")  # noqa: F821
    assigned_to: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="assigned_cases", foreign_keys=[assigned_to_id], lazy="selectin"
    )
    notes: Mapped[list["CaseNote"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="noload"
    )
    history: Mapped[list["CaseHistory"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="noload"
    )
    assignments: Mapped[list["CaseAssignment"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="noload"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="case", lazy="noload")  # noqa: F821
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="case", lazy="noload")  # noqa: F821
    tasks: Mapped[list["StaffTask"]] = relationship(back_populates="case", lazy="noload")  # noqa: F821


class CaseNote(TimestampMixin, Base):
    __tablename__ = "case_notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_private: Mapped[bool] = mapped_column(default=False, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="notes")
    author: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821


class CaseHistory(TimestampMixin, Base):
    __tablename__ = "case_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="history")
    changed_by: Mapped["User | None"] = relationship(lazy="selectin")  # noqa: F821


class CaseAssignment(TimestampMixin, Base):
    __tablename__ = "case_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    role_in_case: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped["Case"] = relationship(back_populates="assignments")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], lazy="selectin")  # noqa: F821
    assigned_by: Mapped["User | None"] = relationship(foreign_keys=[assigned_by_id], lazy="selectin")  # noqa: F821
