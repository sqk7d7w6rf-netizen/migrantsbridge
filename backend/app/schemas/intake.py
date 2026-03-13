from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class IntakeStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INFO = "needs_info"


class IntakeFormRead(BaseModel):
    """Intake form definition."""

    id: UUID
    name: str
    description: str | None = None
    form_schema: dict[str, Any]
    version: int
    is_active: bool
    service_type: str | None = None  # Not on model; populated manually
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class IntakeSubmissionCreate(BaseModel):
    """Create a new intake submission."""

    form_id: UUID
    client_id: UUID | None = None
    form_data: dict[str, Any]
    preferred_language: str = Field(default="en", max_length=10)


class IntakeSubmissionRead(BaseModel):
    """Intake submission read response."""

    id: UUID
    form_id: UUID
    form_name: str | None = None
    client_id: UUID | None = None
    client_name: str | None = None
    form_data: dict[str, Any]
    status: IntakeStatus
    preferred_language: str
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    reviewer_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntakeSubmissionUpdate(BaseModel):
    """Update an intake submission."""

    form_data: dict[str, Any] | None = None
    status: IntakeStatus | None = None
    reviewer_notes: str | None = None


class EligibilityResultRead(BaseModel):
    """Eligibility assessment result."""

    id: UUID
    submission_id: UUID
    eligible_services: list[str]
    ineligible_services: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    confidence_score: float
    reasoning: str
    assessed_at: datetime
    assessed_by: str = Field(description="'ai' or user UUID")

    model_config = {"from_attributes": True}
