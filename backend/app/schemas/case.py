from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    INTAKE = "intake"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_DOCUMENTS = "pending_documents"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DENIED = "denied"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CaseType(str, Enum):
    IMMIGRATION = "immigration"
    LEGAL_AID = "legal_aid"
    JOB_PLACEMENT = "job_placement"
    HOUSING = "housing"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCIAL = "financial"
    COMMUNITY_SUPPORT = "community_support"
    OTHER = "other"


# Valid status transitions
ALLOWED_TRANSITIONS: dict[CaseStatus, list[CaseStatus]] = {
    CaseStatus.INTAKE: [CaseStatus.OPEN, CaseStatus.CLOSED],
    CaseStatus.OPEN: [CaseStatus.IN_PROGRESS, CaseStatus.ON_HOLD, CaseStatus.CLOSED],
    CaseStatus.IN_PROGRESS: [
        CaseStatus.PENDING_DOCUMENTS,
        CaseStatus.PENDING_REVIEW,
        CaseStatus.ON_HOLD,
        CaseStatus.CLOSED,
    ],
    CaseStatus.PENDING_DOCUMENTS: [CaseStatus.IN_PROGRESS, CaseStatus.ON_HOLD, CaseStatus.CLOSED],
    CaseStatus.PENDING_REVIEW: [
        CaseStatus.APPROVED,
        CaseStatus.DENIED,
        CaseStatus.IN_PROGRESS,
        CaseStatus.ON_HOLD,
    ],
    CaseStatus.APPROVED: [CaseStatus.CLOSED, CaseStatus.ARCHIVED],
    CaseStatus.DENIED: [CaseStatus.IN_PROGRESS, CaseStatus.CLOSED, CaseStatus.ARCHIVED],
    CaseStatus.ON_HOLD: [CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.CLOSED],
    CaseStatus.CLOSED: [CaseStatus.ARCHIVED, CaseStatus.OPEN],
    CaseStatus.ARCHIVED: [],
}


class CaseCreate(BaseModel):
    """Create a new case."""

    client_id: UUID
    case_type: CaseType
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: CasePriority = CasePriority.MEDIUM
    assigned_to: UUID | None = None
    due_date: datetime | None = None


class CaseRead(BaseModel):
    """Case read response."""

    id: UUID
    case_number: str
    client_id: UUID
    client_name: str | None = None
    case_type: CaseType
    title: str
    description: str | None = None
    status: CaseStatus
    priority: CasePriority
    assigned_to: UUID | None = None
    assigned_to_name: str | None = None
    due_date: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseUpdate(BaseModel):
    """Case update payload."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: CasePriority | None = None
    case_type: CaseType | None = None
    due_date: datetime | None = None


class CaseNoteCreate(BaseModel):
    """Create a case note."""

    content: str = Field(min_length=1)
    is_internal: bool = False


class CaseNoteRead(BaseModel):
    """Case note read response."""

    id: UUID
    case_id: UUID
    author_id: UUID
    author_name: str | None = None
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseHistoryRead(BaseModel):
    """Case history / audit entry."""

    id: UUID
    case_id: UUID
    user_id: UUID | None = None
    user_name: str | None = None
    action: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseAssignRequest(BaseModel):
    """Assign case to staff."""

    assigned_to: UUID
    note: str | None = None


class CaseStatusTransition(BaseModel):
    """Request a case status transition."""

    new_status: CaseStatus
    reason: str | None = None
