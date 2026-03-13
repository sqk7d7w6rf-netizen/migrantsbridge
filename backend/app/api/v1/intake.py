"""Intake forms and submissions API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.intake import (
    EligibilityResultRead,
    IntakeFormRead,
    IntakeSubmissionCreate,
    IntakeSubmissionRead,
    IntakeSubmissionUpdate,
)
from app.services import intake_service

router = APIRouter()


@router.get("/forms", response_model=PaginatedResponse[IntakeFormRead])
async def list_forms(
    pagination: PaginationParams = Depends(),
    service_type: str | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    """List available intake forms (public endpoint for portal)."""
    return await intake_service.list_forms(session, pagination, service_type)


@router.get("/forms/{form_id}", response_model=IntakeFormRead)
async def get_form(
    form_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Get a specific intake form definition."""
    return await intake_service.get_form(session, form_id)


@router.post("/submissions", response_model=IntakeSubmissionRead, status_code=201)
async def submit_intake(
    payload: IntakeSubmissionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Submit an intake form (public endpoint for portal)."""
    return await intake_service.create_submission(session, payload)


@router.get("/submissions/{submission_id}", response_model=IntakeSubmissionRead)
async def get_submission(
    submission_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get an intake submission by ID."""
    return await intake_service.get_submission(session, submission_id)


@router.put("/submissions/{submission_id}", response_model=IntakeSubmissionRead)
async def update_submission(
    submission_id: UUID,
    payload: IntakeSubmissionUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update / review an intake submission."""
    return await intake_service.update_submission(
        session, submission_id, payload, reviewer_id=current_user.id
    )


@router.post(
    "/submissions/{submission_id}/assess",
    response_model=EligibilityResultRead,
)
async def assess_eligibility(
    submission_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Trigger an AI eligibility assessment for a submission."""
    return await intake_service.trigger_eligibility_assessment(session, submission_id)


@router.get(
    "/submissions/{submission_id}/eligibility",
    response_model=EligibilityResultRead,
)
async def get_eligibility(
    submission_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get the latest eligibility result for a submission."""
    return await intake_service.get_eligibility(session, submission_id)
