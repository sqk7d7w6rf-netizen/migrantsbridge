"""Tests for app.services.client_service.

These cover client creation (including language associations and duplicate-email
handling), retrieval, updates with schema/model field mapping, soft deletes,
search filtering/pagination, and timeline aggregation.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException, status

from app.core.pagination import PaginationParams
from app.schemas.client import (
    ClientCreate,
    ClientLanguageCreate,
    ClientSearch,
    ClientUpdate,
    ImmigrationStatus,
)
from app.services import client_service

# Run all tests in this module on the shared session-scoped event loop so they
# can use the session-scoped asyncpg engine (see tests/conftest.py).
pytestmark = pytest.mark.asyncio(loop_scope="session")


def _client_create(**overrides) -> ClientCreate:
    data = {"first_name": "Maria", "last_name": "Gomez"}
    data.update(overrides)
    return ClientCreate(**data)


# --------------------------------------------------------------------------- #
# create_client
# --------------------------------------------------------------------------- #


async def test_create_client_minimal(session):
    result = await client_service.create_client(session, _client_create())

    assert result.first_name == "Maria"
    assert result.is_active is True
    assert result.languages == []
    # client_number is derived from the first 8 chars of the UUID, uppercased.
    assert result.client_number == f"CL-{str(result.id)[:8].upper()}"


async def test_create_client_with_languages(session):
    result = await client_service.create_client(
        session,
        _client_create(
            languages=[
                ClientLanguageCreate(language_code="es", proficiency="native", is_primary=True),
                ClientLanguageCreate(language_code="en", proficiency="conversational"),
            ]
        ),
    )

    assert len(result.languages) == 2
    codes = {lang.language_code for lang in result.languages}
    assert codes == {"es", "en"}
    primary = [lang for lang in result.languages if lang.is_primary]
    assert len(primary) == 1
    assert primary[0].language_code == "es"


async def test_create_client_persists_enum_fields(session):
    result = await client_service.create_client(
        session,
        _client_create(immigration_status=ImmigrationStatus.CITIZEN, country_of_origin="Mexico"),
    )
    # Enum is round-tripped back to its string value on read.
    assert result.immigration_status == ImmigrationStatus.CITIZEN
    assert result.country_of_origin == "Mexico"


async def test_create_client_duplicate_email_conflicts(session):
    await client_service.create_client(session, _client_create(email="dup@example.com"))
    with pytest.raises(HTTPException) as exc:
        await client_service.create_client(
            session, _client_create(first_name="Other", email="dup@example.com")
        )
    assert exc.value.status_code == status.HTTP_409_CONFLICT


async def test_create_client_without_email_skips_dup_check(session):
    # Two clients without an email must both be allowed.
    first = await client_service.create_client(session, _client_create())
    second = await client_service.create_client(session, _client_create(first_name="Ana"))
    assert first.id != second.id


# --------------------------------------------------------------------------- #
# get_client
# --------------------------------------------------------------------------- #


async def test_get_client_returns_record(session):
    created = await client_service.create_client(session, _client_create())
    fetched = await client_service.get_client(session, created.id)
    assert fetched.id == created.id


async def test_get_client_missing_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await client_service.get_client(session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------- #
# update_client
# --------------------------------------------------------------------------- #


async def test_update_client_maps_address_fields(session):
    created = await client_service.create_client(session, _client_create())
    updated = await client_service.update_client(
        session,
        created.id,
        ClientUpdate(address_line1="123 Main St", city="Springfield", phone="+15551112222"),
    )
    # Schema's address_line1 maps to the model's address_line_1 column.
    assert updated.address_line1 == "123 Main St"
    assert updated.city == "Springfield"
    assert updated.phone == "+15551112222"


async def test_update_client_missing_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await client_service.update_client(
            session, uuid.uuid4(), ClientUpdate(first_name="Ghost")
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------- #
# delete_client
# --------------------------------------------------------------------------- #


async def test_delete_client_soft_deletes(session):
    created = await client_service.create_client(session, _client_create(email="del@example.com"))
    await client_service.delete_client(session, created.id)

    # Soft-deleted clients are no longer retrievable.
    with pytest.raises(HTTPException) as exc:
        await client_service.get_client(session, created.id)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_client_missing_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await client_service.delete_client(session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------- #
# search_clients
# --------------------------------------------------------------------------- #


async def test_search_clients_by_name_query(session):
    await client_service.create_client(session, _client_create(first_name="Alejandro"))
    await client_service.create_client(session, _client_create(first_name="Beatriz"))

    page = await client_service.search_clients(
        session, ClientSearch(query="alejan"), PaginationParams(page=1, size=20)
    )
    assert page.total == 1
    assert page.items[0].first_name == "Alejandro"


async def test_search_clients_filters_by_active(session):
    active = await client_service.create_client(session, _client_create(first_name="Active"))
    inactive = await client_service.create_client(session, _client_create(first_name="Inactive"))
    await client_service.update_client(session, inactive.id, ClientUpdate(is_active=False))

    page = await client_service.search_clients(
        session, ClientSearch(is_active=True), PaginationParams(page=1, size=20)
    )
    ids = {item.id for item in page.items}
    assert active.id in ids
    assert inactive.id not in ids


async def test_search_clients_pagination(session):
    for i in range(5):
        await client_service.create_client(session, _client_create(first_name=f"Client{i}"))

    page = await client_service.search_clients(
        session, ClientSearch(), PaginationParams(page=1, size=2)
    )
    assert page.total == 5
    assert page.pages == 3
    assert len(page.items) == 2


async def test_search_clients_excludes_soft_deleted(session):
    keep = await client_service.create_client(session, _client_create(first_name="Keep"))
    drop = await client_service.create_client(session, _client_create(first_name="Drop"))
    await client_service.delete_client(session, drop.id)

    page = await client_service.search_clients(
        session, ClientSearch(), PaginationParams(page=1, size=20)
    )
    ids = {item.id for item in page.items}
    assert keep.id in ids
    assert drop.id not in ids


# --------------------------------------------------------------------------- #
# get_client_timeline
# --------------------------------------------------------------------------- #


async def test_timeline_empty_for_new_client(session):
    created = await client_service.create_client(session, _client_create())
    timeline = await client_service.get_client_timeline(session, created.id)
    assert timeline == []


async def test_timeline_missing_client_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await client_service.get_client_timeline(session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
