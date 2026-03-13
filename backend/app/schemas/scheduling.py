from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    INTAKE = "intake"
    FOLLOW_UP = "follow_up"
    DOCUMENT_REVIEW = "document_review"
    LEGAL_MEETING = "legal_meeting"
    JOB_INTERVIEW_PREP = "job_interview_prep"
    FINANCIAL_COUNSELING = "financial_counseling"
    OTHER = "other"


class ReminderMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"


class AppointmentCreate(BaseModel):
    """Create a new appointment."""

    client_id: UUID
    case_id: UUID | None = None
    staff_id: UUID
    appointment_type: AppointmentType
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = Field(default=None, max_length=255)
    is_virtual: bool = False
    meeting_link: str | None = None

    @model_validator(mode="after")
    def validate_times(self) -> "AppointmentCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AppointmentRead(BaseModel):
    """Appointment read response."""

    id: UUID
    client_id: UUID
    client_name: str | None = None
    case_id: UUID | None = None
    staff_id: UUID
    staff_name: str | None = None
    appointment_type: AppointmentType
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    location: str | None = None
    is_virtual: bool
    meeting_link: str | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentUpdate(BaseModel):
    """Update an appointment."""

    appointment_type: AppointmentType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: AppointmentStatus | None = None
    location: str | None = None
    is_virtual: bool | None = None
    meeting_link: str | None = None
    cancellation_reason: str | None = None


class AvailabilitySlotCreate(BaseModel):
    """Create an availability slot for staff."""

    staff_id: UUID
    day_of_week: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    is_recurring: bool = True
    specific_date: date | None = None

    @model_validator(mode="after")
    def validate_times(self) -> "AvailabilitySlotCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AvailabilitySlotRead(BaseModel):
    """Availability slot read response."""

    id: UUID
    staff_id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    is_recurring: bool
    specific_date: date | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderCreate(BaseModel):
    """Create an appointment reminder."""

    appointment_id: UUID
    remind_at: datetime
    method: ReminderMethod = ReminderMethod.EMAIL
    message: str | None = None


class CalendarQuery(BaseModel):
    """Calendar view query parameters."""

    start_date: date
    end_date: date
    staff_id: UUID | None = None
    client_id: UUID | None = None
    status: AppointmentStatus | None = None
