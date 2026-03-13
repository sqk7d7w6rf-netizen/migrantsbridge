"""Client management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.client import (
    ClientCreate,
    ClientRead,
    ClientSearch,
    ClientUpdate,
    ImmigrationStatus,
)
from app.schemas.common import SuccessResponse
from app.services import client_service

router = APIRouter()


@router.post("", response_model=ClientRead, status_code=201)
async def create_client(
    payload: ClientCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Register a new client."""
    return await client_service.create_client(session, payload)


@router.get("", response_model=PaginatedResponse[ClientRead])
async def list_clients(
    pagination: PaginationParams = Depends(),
    query: str | None = Query(default=None, description="Search query"),
    immigration_status: ImmigrationStatus | None = None,
    country_of_origin: str | None = None,
    city: str | None = None,
    state: str | None = None,
    is_active: bool | None = None,
    preferred_language: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Search and list clients with filters."""
    filters = ClientSearch(
        query=query,
        immigration_status=immigration_status,
        country_of_origin=country_of_origin,
        city=city,
        state=state,
        is_active=is_active,
        preferred_language=preferred_language,
    )
    return await client_service.search_clients(session, filters, pagination)


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a client by ID."""
    return await client_service.get_client(session, client_id)


@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: UUID,
    payload: ClientUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a client record."""
    return await client_service.update_client(session, client_id, payload)


@router.delete("/{client_id}", response_model=SuccessResponse)
async def delete_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Soft-delete a client."""
    await client_service.delete_client(session, client_id)
    return SuccessResponse(message="Client deleted successfully")


@router.get("/{client_id}/cases", response_model=PaginatedResponse)
async def get_client_cases(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get all cases for a client."""
    return await client_service.get_client_cases(session, client_id, pagination)


@router.get("/{client_id}/documents", response_model=PaginatedResponse)
async def get_client_documents(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get all documents for a client."""
    return await client_service.get_client_documents(session, client_id, pagination)


@router.get("/{client_id}/timeline")
async def get_client_timeline(
    client_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get aggregated activity timeline for a client."""
    return await client_service.get_client_timeline(session, client_id, limit)
