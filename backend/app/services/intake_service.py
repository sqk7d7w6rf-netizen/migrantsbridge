"""Intake forms and submissions service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import IntakeSubmissionStatus
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.intake import EligibilityResult, IntakeForm, IntakeSubmission
from app.models.client import Client
from app.schemas.intake import (
    EligibilityResultRead,
    IntakeFormRead,
    IntakeSubmissionCreate,
    IntakeSubmissionRead,
    IntakeSubmissionUpdate,
)


async def list_forms(
    session: AsyncSession,
    pagination: PaginationParams,
    active_only: bool = True,
) -> PaginatedResponse[IntakeFormRead]:
    """List available intake forms."""
    query = select(IntakeForm)
    if active_only:
        query = query.where(IntakeForm.is_active == True)
    query = query.order_by(IntakeForm.name.asc())
    # IntakeFormRead has service_type which doesn't exist on model; paginate without model
    result = await paginate(session, query, pagination)
    result.items = [
        IntakeFormRead(
            id=f.id,
            name=f.name,
            description=f.description,
            form_schema=f.form_schema,
            version=f.version,
            is_active=f.is_active,
            service_type=None,
            created_at=f.created_at,
            updated_at=f.updated_at,
        )
        for f in result.items
    ]
    return result


async def get_form(session: AsyncSession, form_id: UUID) -> IntakeFormRead:
    """Get a single intake form by ID."""
    result = await session.execute(
        select(IntakeForm).where(IntakeForm.id == form_id)
    )
    form = result.scalar_one_or_none()
    if form is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intake form not found")

    return IntakeFormRead(
        id=form.id,
        name=form.name,
        description=form.description,
        form_schema=form.form_schema,
        version=form.version,
        is_active=form.is_active,
        service_type=None,
        created_at=form.created_at,
        updated_at=form.updated_at,
    )


def _build_submission_read(
    submission: IntakeSubmission,
    form_name: str | None = None,
    client_name: str | None = None,
) -> IntakeSubmissionRead:
    """Map an IntakeSubmission model to the read schema."""
    return IntakeSubmissionRead(
        id=submission.id,
        form_id=submission.form_id,
        form_name=form_name or (submission.form.name if submission.form else None),
        client_id=submission.client_id,
        client_name=client_name,
        form_data=submission.response_data,
        status=submission.status.value,
        preferred_language=submission.form.language if submission.form else "en",
        reviewed_by=submission.reviewed_by_id,
        reviewed_at=submission.reviewed_at,
        reviewer_notes=submission.review_notes,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
    )


async def create_submission(
    session: AsyncSession, payload: IntakeSubmissionCreate
) -> IntakeSubmissionRead:
    """Create a new intake submission."""
    # Verify form exists and is active
    form_result = await session.execute(
        select(IntakeForm).where(IntakeForm.id == payload.form_id, IntakeForm.is_active == True)
    )
    form = form_result.scalar_one_or_none()
    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intake form not found or inactive",
        )

    # Verify client if provided
    client_name = None
    if payload.client_id:
        client_result = await session.execute(
            select(Client).where(Client.id == payload.client_id, Client.is_deleted == False)
        )
        client = client_result.scalar_one_or_none()
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        client_name = f"{client.first_name} {client.last_name}"

    submission = IntakeSubmission(
        form_id=payload.form_id,
        client_id=payload.client_id,
        response_data=payload.form_data,
        status=IntakeSubmissionStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )
    session.add(submission)
    await session.flush()
    await session.refresh(submission)

    return _build_submission_read(submission, form_name=form.name, client_name=client_name)


async def get_submission(session: AsyncSession, submission_id: UUID) -> IntakeSubmissionRead:
    """Get an intake submission by ID."""
    result = await session.execute(
        select(IntakeSubmission).where(IntakeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Intake submission not found"
        )

    client_name = None
    if submission.client_id:
        client_result = await session.execute(
            select(Client).where(Client.id == submission.client_id)
        )
        client = client_result.scalar_one_or_none()
        if client:
            client_name = f"{client.first_name} {client.last_name}"

    form_name = submission.form.name if submission.form else None

    return _build_submission_read(submission, form_name=form_name, client_name=client_name)


async def update_submission(
    session: AsyncSession,
    submission_id: UUID,
    payload: IntakeSubmissionUpdate,
    reviewer_id: UUID | None = None,
) -> IntakeSubmissionRead:
    """Update an intake submission (review, status change, etc.)."""
    result = await session.execute(
        select(IntakeSubmission).where(IntakeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Intake submission not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "form_data" in update_data and update_data["form_data"] is not None:
        submission.response_data = update_data.pop("form_data")

    if "status" in update_data and update_data["status"] is not None:
        schema_status = update_data.pop("status")
        # Map schema IntakeStatus to model IntakeSubmissionStatus
        status_map = {
            "draft": IntakeSubmissionStatus.IN_PROGRESS,
            "submitted": IntakeSubmissionStatus.SUBMITTED,
            "under_review": IntakeSubmissionStatus.UNDER_REVIEW,
            "approved": IntakeSubmissionStatus.APPROVED,
            "rejected": IntakeSubmissionStatus.REJECTED,
            "needs_info": IntakeSubmissionStatus.IN_PROGRESS,
        }
        submission.status = status_map.get(schema_status.value, IntakeSubmissionStatus.IN_PROGRESS)

    if "reviewer_notes" in update_data:
        submission.review_notes = update_data.pop("reviewer_notes")

    if reviewer_id and payload.status:
        submission.reviewed_by_id = reviewer_id
        submission.reviewed_at = datetime.now(timezone.utc)

    session.add(submission)
    await session.flush()

    return await get_submission(session, submission_id)


async def trigger_eligibility_assessment(
    session: AsyncSession, submission_id: UUID
) -> list[EligibilityResultRead]:
    """Trigger an AI eligibility assessment for a submission."""
    result = await session.execute(
        select(IntakeSubmission).where(IntakeSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Intake submission not found"
        )

    # Call AI service for eligibility assessment
    from app.services.ai_service import assess_eligibility

    assessment = await assess_eligibility(submission.response_data)

    results: list[EligibilityResultRead] = []

    # Create individual EligibilityResult records for each service
    for service_name in assessment.get("eligible_services", []):
        eligibility = EligibilityResult(
            submission_id=submission_id,
            program_name=service_name,
            is_eligible=True,
            confidence_score=assessment.get("confidence_score"),
            reasoning=assessment.get("reasoning", ""),
            criteria_met=assessment.get("recommendations", []),
        )
        session.add(eligibility)
        await session.flush()
        await session.refresh(eligibility)
        results.append(_to_eligibility_read(eligibility))

    for service_name in assessment.get("ineligible_services", []):
        eligibility = EligibilityResult(
            submission_id=submission_id,
            program_name=service_name,
            is_eligible=False,
            confidence_score=assessment.get("confidence_score"),
            reasoning=assessment.get("reasoning", ""),
            criteria_not_met=assessment.get("risk_factors", []),
        )
        session.add(eligibility)
        await session.flush()
        await session.refresh(eligibility)
        results.append(_to_eligibility_read(eligibility))

    if not results:
        # Create a default result if AI returned no services
        eligibility = EligibilityResult(
            submission_id=submission_id,
            program_name="general",
            is_eligible=False,
            confidence_score=assessment.get("confidence_score", 0.0),
            reasoning=assessment.get("reasoning", "No eligible services found"),
        )
        session.add(eligibility)
        await session.flush()
        await session.refresh(eligibility)
        results.append(_to_eligibility_read(eligibility))

    return results


def _to_eligibility_read(er: EligibilityResult) -> EligibilityResultRead:
    """Map EligibilityResult model to schema."""
    eligible_services = [er.program_name] if er.is_eligible else []
    ineligible_services = [er.program_name] if not er.is_eligible else []
    recommendations = er.criteria_met if isinstance(er.criteria_met, list) else []
    risk_factors = er.criteria_not_met if isinstance(er.criteria_not_met, list) else []

    return EligibilityResultRead(
        id=er.id,
        submission_id=er.submission_id,
        eligible_services=eligible_services,
        ineligible_services=ineligible_services,
        recommendations=recommendations,
        risk_factors=risk_factors,
        confidence_score=er.confidence_score or 0.0,
        reasoning=er.reasoning or "",
        assessed_at=er.created_at,
        assessed_by="ai",
    )


async def get_eligibility(
    session: AsyncSession, submission_id: UUID
) -> EligibilityResultRead:
    """Get the latest eligibility result for a submission."""
    result = await session.execute(
        select(EligibilityResult)
        .where(EligibilityResult.submission_id == submission_id)
        .order_by(EligibilityResult.created_at.desc())
    )
    eligibility = result.scalar_one_or_none()
    if eligibility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No eligibility assessment found for this submission",
        )
    return _to_eligibility_read(eligibility)
