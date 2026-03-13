"""Case management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.case import (
    CaseAssignRequest,
    CaseCreate,
    CaseHistoryRead,
    CaseNoteCreate,
    CaseNoteRead,
    CasePriority,
    CaseRead,
    CaseStatus,
    CaseStatusTransition,
    CaseType,
    CaseUpdate,
)
from app.schemas.common import SuccessResponse
from app.services import case_service

router = APIRouter()


@router.post("", response_model=CaseRead, status_code=201)
async def create_case(
    payload: CaseCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a new case."""
    return await case_service.create_case(session, payload, current_user.id)


@router.get("", response_model=PaginatedResponse[CaseRead])
async def list_cases(
    pagination: PaginationParams = Depends(),
    client_id: UUID | None = None,
    status: CaseStatus | None = None,
    case_type: CaseType | None = None,
    assigned_to: UUID | None = None,
    priority: CasePriority | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List cases with filters."""
    filters = {}
    if client_id:
        filters["client_id"] = client_id
    if status:
        filters["status"] = status.value
    if case_type:
        filters["case_type"] = case_type.value
    if assigned_to:
        filters["assigned_to"] = assigned_to
    if priority:
        filters["priority"] = priority.value
    return await case_service.list_cases(session, pagination, **filters)


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(
    case_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a case by ID."""
    return await case_service.get_case(session, case_id)


@router.put("/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: UUID,
    payload: CaseUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a case."""
    return await case_service.update_case(session, case_id, payload, current_user.id)


@router.delete("/{case_id}", response_model=SuccessResponse)
async def delete_case(
    case_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Soft-delete a case."""
    await case_service.delete_case(session, case_id, current_user.id)
    return SuccessResponse(message="Case deleted successfully")


@router.post("/{case_id}/status", response_model=CaseRead)
async def transition_status(
    case_id: UUID,
    payload: CaseStatusTransition,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Transition a case to a new status."""
    return await case_service.transition_status(session, case_id, payload, current_user.id)


@router.post("/{case_id}/assign", response_model=CaseRead)
async def assign_case(
    case_id: UUID,
    payload: CaseAssignRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Assign or reassign a case to a staff member."""
    return await case_service.assign_staff(session, case_id, payload, current_user.id)


@router.post("/{case_id}/notes", response_model=CaseNoteRead, status_code=201)
async def add_note(
    case_id: UUID,
    payload: CaseNoteCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Add a note to a case."""
    return await case_service.add_note(session, case_id, payload, current_user.id)


@router.get("/{case_id}/notes", response_model=PaginatedResponse[CaseNoteRead])
async def list_notes(
    case_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List notes for a case."""
    return await case_service.list_notes(session, case_id, pagination)


@router.get("/{case_id}/history", response_model=PaginatedResponse[CaseHistoryRead])
async def get_history(
    case_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get the audit history for a case."""
    return await case_service.get_history(session, case_id, pagination)
