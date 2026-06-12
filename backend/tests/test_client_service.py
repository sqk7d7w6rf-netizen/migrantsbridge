"""Service-layer tests for client_service against a real database."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.constants import Gender, ImmigrationStatus
from app.schemas.client import (
    ClientCreate,
    ClientLanguageCreate,
    ClientUpdate,
)
from app.services import client_service


def _payload(**overrides) -> ClientCreate:
    data = dict(
        first_name="Maria",
        last_name="Garcia",
        email="maria@example.com",
        phone="+15551234567",
    )
    data.update(overrides)
    return ClientCreate(**data)


@pytest_asyncio.fixture
async def created_client(db_session):
    return await client_service.create_client(db_session, _payload())


async def test_create_client_returns_read_with_client_number(db_session):
    client = await client_service.create_client(db_session, _payload())
    assert client.first_name == "Maria"
    assert client.client_number.startswith("CL-")
    assert client.is_active is True


async def test_create_client_persists_languages(db_session):
    payload = _payload(
        languages=[
            ClientLanguageCreate(language_code="es", proficiency="native", is_primary=True),
            ClientLanguageCreate(language_code="en", proficiency="conversational"),
        ]
    )
    client = await client_service.create_client(db_session, payload)
    codes = {lang.language_code for lang in client.languages}
    assert codes == {"es", "en"}


async def test_create_client_roundtrips_enums(db_session):
    payload = _payload(
        email="enums@example.com",
        gender=Gender.FEMALE,
        immigration_status=ImmigrationStatus.REFUGEE,
        date_of_birth=date(1990, 5, 1),
    )
    client = await client_service.create_client(db_session, payload)
    fetched = await client_service.get_client(db_session, client.id)
    assert fetched.gender == Gender.FEMALE
    assert fetched.immigration_status == ImmigrationStatus.REFUGEE
    assert fetched.date_of_birth == date(1990, 5, 1)


async def test_create_client_rejects_duplicate_email(db_session, created_client):
    with pytest.raises(HTTPException) as exc:
        await client_service.create_client(db_session, _payload())
    assert exc.value.status_code == 409


async def test_get_client_missing_404(db_session):
    with pytest.raises(HTTPException) as exc:
        await client_service.get_client(db_session, uuid.uuid4())
    assert exc.value.status_code == 404


async def test_update_client_changes_fields_and_maps_address(db_session, created_client):
    updated = await client_service.update_client(
        db_session,
        created_client.id,
        ClientUpdate(first_name="Mary", address_line1="123 Main St", city="Austin"),
    )
    assert updated.first_name == "Mary"
    assert updated.address_line1 == "123 Main St"
    assert updated.city == "Austin"


async def test_update_client_missing_404(db_session):
    with pytest.raises(HTTPException) as exc:
        await client_service.update_client(
            db_session, uuid.uuid4(), ClientUpdate(first_name="X")
        )
    assert exc.value.status_code == 404


async def test_delete_client_soft_deletes(db_session, created_client):
    await client_service.delete_client(db_session, created_client.id)
    # Soft-deleted clients are no longer retrievable.
    with pytest.raises(HTTPException) as exc:
        await client_service.get_client(db_session, created_client.id)
    assert exc.value.status_code == 404


async def test_delete_client_missing_404(db_session):
    with pytest.raises(HTTPException) as exc:
        await client_service.delete_client(db_session, uuid.uuid4())
    assert exc.value.status_code == 404
