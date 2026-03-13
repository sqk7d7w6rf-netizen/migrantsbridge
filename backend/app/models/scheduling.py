import uuid
from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import AppointmentStatus, AppointmentType, DayOfWeek, ReminderType
from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Appointment(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    appointment_type: Mapped[AppointmentType] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        default=AppointmentStatus.SCHEDULED, nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    client: Mapped["Client"] = relationship(back_populates="appointments", lazy="selectin")  # noqa: F821
    case: Mapped["Case | None"] = relationship(back_populates="appointments", lazy="selectin")  # noqa: F821
    staff: Mapped["User"] = relationship(foreign_keys=[staff_id], lazy="selectin")  # noqa: F821
    cancelled_by: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[cancelled_by_id], lazy="selectin"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="appointment", cascade="all, delete-orphan", lazy="noload"
    )


class StaffAvailability(TimestampMixin, Base):
    __tablename__ = "staff_availability"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821


class Reminder(TimestampMixin, Base):
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reminder_type: Mapped[ReminderType] = mapped_column(nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    appointment: Mapped["Appointment"] = relationship(back_populates="reminders")
