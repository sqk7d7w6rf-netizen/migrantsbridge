"""Client management service with search and timeline aggregation."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.client import Client, ClientLanguage
from app.models.case import Case
from app.models.document import Document
from app.models.scheduling import Appointment
from app.schemas.client import (
    ClientCreate,
    ClientRead,
    ClientSearch,
    ClientUpdate,
)


async def create_client(session: AsyncSession, payload: ClientCreate) -> ClientRead:
    """Create a new client record."""
    if payload.email:
        existing = await session.execute(
            select(Client).where(Client.email == payload.email, Client.is_deleted == False)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A client with this email already exists",
            )

    client = Client(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender if payload.gender else None,
        country_of_origin=payload.country_of_origin,
        immigration_status=payload.immigration_status if payload.immigration_status else None,
        address_line_1=payload.address_line1,
        address_line_2=payload.address_line2,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        preferred_language=payload.preferred_language,
        emergency_contact_name=payload.emergency_contact_name,
        emergency_contact_phone=payload.emergency_contact_phone,
        notes=payload.notes,
        is_active=True,
    )
    session.add(client)
    await session.flush()

    # Add languages
    for lang in payload.languages:
        cl = ClientLanguage(
            client_id=client.id,
            language=lang.language_code,
            proficiency=lang.proficiency,
            is_primary=lang.is_primary,
        )
        session.add(cl)

    await session.flush()
    await session.refresh(client, attribute_names=["languages"])

    return _to_client_read(client)


def _to_client_read(client: Client) -> ClientRead:
    """Map Client model to ClientRead schema."""
    from app.schemas.client import ClientLanguageRead

    languages = []
    for lang in (client.languages or []):
        languages.append(ClientLanguageRead(
            id=lang.id,
            language_code=lang.language,
            proficiency=lang.proficiency or "",
            is_primary=lang.is_primary,
        ))

    return ClientRead(
        id=client.id,
        client_number=f"CL-{str(client.id)[:8].upper()}",
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        phone=client.phone,
        date_of_birth=client.date_of_birth,
        gender=client.gender.value if client.gender else None,
        country_of_origin=client.country_of_origin,
        immigration_status=client.immigration_status.value if client.immigration_status else None,
        address_line1=client.address_line_1,
        address_line2=client.address_line_2,
        city=client.city,
        state=client.state,
        zip_code=client.zip_code,
        preferred_language=client.preferred_language,
        emergency_contact_name=client.emergency_contact_name,
        emergency_contact_phone=client.emergency_contact_phone,
        notes=client.notes,
        is_active=client.is_active,
        languages=languages,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


async def get_client(session: AsyncSession, client_id: UUID) -> ClientRead:
    """Get a client by ID."""
    result = await session.execute(
        select(Client)
        .options(selectinload(Client.languages))
        .where(Client.id == client_id, Client.is_deleted == False)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return _to_client_read(client)


async def update_client(
    session: AsyncSession, client_id: UUID, payload: ClientUpdate
) -> ClientRead:
    """Update a client record."""
    result = await session.execute(
        select(Client)
        .options(selectinload(Client.languages))
        .where(Client.id == client_id, Client.is_deleted == False)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Map schema field names to model field names
    field_map = {"address_line1": "address_line_1", "address_line2": "address_line_2"}
    for field, value in update_data.items():
        model_field = field_map.get(field, field)
        setattr(client, model_field, value)

    session.add(client)
    await session.flush()
    await session.refresh(client, attribute_names=["languages"])

    return _to_client_read(client)


async def delete_client(session: AsyncSession, client_id: UUID) -> None:
    """Soft-delete a client."""
    result = await session.execute(
        select(Client).where(Client.id == client_id, Client.is_deleted == False)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    client.is_deleted = True
    client.deleted_at = datetime.now(timezone.utc)
    session.add(client)


async def search_clients(
    session: AsyncSession,
    filters: ClientSearch,
    pagination: PaginationParams,
) -> PaginatedResponse[ClientRead]:
    """Search clients with filters and pagination."""
    query = (
        select(Client)
        .options(selectinload(Client.languages))
        .where(Client.is_deleted == False)
    )

    if filters.query:
        search_term = f"%{filters.query}%"
        query = query.where(
            or_(
                Client.first_name.ilike(search_term),
                Client.last_name.ilike(search_term),
                Client.email.ilike(search_term),
                Client.phone.ilike(search_term),
            )
        )

    if filters.immigration_status:
        query = query.where(Client.immigration_status == filters.immigration_status.value)
    if filters.country_of_origin:
        query = query.where(Client.country_of_origin == filters.country_of_origin)
    if filters.city:
        query = query.where(Client.city.ilike(f"%{filters.city}%"))
    if filters.state:
        query = query.where(Client.state == filters.state)
    if filters.is_active is not None:
        query = query.where(Client.is_active == filters.is_active)
    if filters.preferred_language:
        query = query.where(Client.preferred_language == filters.preferred_language)
    if filters.created_after:
        query = query.where(Client.created_at >= filters.created_after)
    if filters.created_before:
        query = query.where(Client.created_at <= filters.created_before)

    query = query.order_by(Client.created_at.desc())

    return await paginate(session, query, pagination, ClientRead)


async def get_client_cases(
    session: AsyncSession,
    client_id: UUID,
    pagination: PaginationParams,
) -> PaginatedResponse:
    """Get all cases for a client."""
    await get_client(session, client_id)
    query = (
        select(Case)
        .where(Case.client_id == client_id, Case.is_deleted == False)
        .order_by(Case.created_at.desc())
    )
    return await paginate(session, query, pagination)


async def get_client_documents(
    session: AsyncSession,
    client_id: UUID,
    pagination: PaginationParams,
) -> PaginatedResponse:
    """Get all documents for a client."""
    await get_client(session, client_id)
    query = (
        select(Document)
        .where(Document.client_id == client_id, Document.is_deleted == False)
        .order_by(Document.created_at.desc())
    )
    return await paginate(session, query, pagination)


async def get_client_timeline(
    session: AsyncSession, client_id: UUID, limit: int = 50
) -> list[dict]:
    """Get an aggregated activity timeline for a client."""
    await get_client(session, client_id)

    timeline: list[dict] = []

    # Cases
    cases_result = await session.execute(
        select(Case)
        .where(Case.client_id == client_id, Case.is_deleted == False)
        .order_by(Case.created_at.desc())
        .limit(limit)
    )
    for case in cases_result.scalars().all():
        timeline.append({
            "type": "case",
            "id": str(case.id),
            "title": f"Case opened: #{case.case_number}",
            "description": f"Type: {case.case_type.value} - Status: {case.status.value}",
            "timestamp": case.created_at.isoformat(),
            "status": case.status.value,
        })

    # Documents
    docs_result = await session.execute(
        select(Document)
        .where(Document.client_id == client_id, Document.is_deleted == False)
        .order_by(Document.created_at.desc())
        .limit(limit)
    )
    for doc in docs_result.scalars().all():
        timeline.append({
            "type": "document",
            "id": str(doc.id),
            "title": f"Document uploaded: {doc.title}",
            "description": f"Type: {doc.document_type.value}",
            "timestamp": doc.created_at.isoformat(),
            "status": doc.ocr_status.value,
        })

    # Appointments
    appts_result = await session.execute(
        select(Appointment)
        .where(Appointment.client_id == client_id, Appointment.is_deleted == False)
        .order_by(Appointment.created_at.desc())
        .limit(limit)
    )
    for appt in appts_result.scalars().all():
        timeline.append({
            "type": "appointment",
            "id": str(appt.id),
            "title": f"Appointment: {appt.title}",
            "description": f"{appt.appointment_type.value} on {appt.start_time.isoformat()} - {appt.status.value}",
            "timestamp": appt.created_at.isoformat(),
            "status": appt.status.value,
        })

    timeline.sort(key=lambda x: x["timestamp"], reverse=True)
    return timeline[:limit]
