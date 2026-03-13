import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import IntakeSubmissionStatus
from app.core.database import Base
from app.models.base import TimestampMixin


class IntakeForm(TimestampMixin, Base):
    __tablename__ = "intake_forms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    form_schema: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    submissions: Mapped[list["IntakeSubmission"]] = relationship(
        back_populates="form", cascade="all, delete-orphan", lazy="noload"
    )


class IntakeSubmission(TimestampMixin, Base):
    __tablename__ = "intake_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("intake_forms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    submitted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    response_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[IntakeSubmissionStatus] = mapped_column(
        default=IntakeSubmissionStatus.IN_PROGRESS, nullable=False, index=True
    )
    step_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    form: Mapped["IntakeForm"] = relationship(back_populates="submissions", lazy="selectin")
    client: Mapped["Client | None"] = relationship(lazy="selectin")  # noqa: F821
    submitted_by: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[submitted_by_id], lazy="selectin"
    )
    reviewed_by: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[reviewed_by_id], lazy="selectin"
    )
    eligibility_results: Mapped[list["EligibilityResult"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan", lazy="noload"
    )


class EligibilityResult(TimestampMixin, Base):
    __tablename__ = "eligibility_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("intake_submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    program_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_met: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    criteria_not_met: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    submission: Mapped["IntakeSubmission"] = relationship(back_populates="eligibility_results")
