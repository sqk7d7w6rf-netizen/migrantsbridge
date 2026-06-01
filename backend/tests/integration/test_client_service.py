"""Integration tests for app/services/client_service.py (DB session is mocked)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.constants import Gender, ImmigrationStatus
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientSearch, ClientUpdate
from app.services import client_service
from app.core.pagination import PaginationParams
from tests.conftest import make_db_result, make_session


def _make_client(email: str | None = "client@example.com") -> Client:
    c = Client(
        id=uuid.uuid4(),
        first_name="Maria",
        last_name="Garcia",
        email=email,
        phone="+15551234567",
        gender=Gender.FEMALE,
        country_of_origin="Mexico",
        immigration_status=ImmigrationStatus.REFUGEE,
        preferred_language="es",
        is_active=True,
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    c.languages = []
    return c


# ── create_client ─────────────────────────────────────────────────────────────

class TestCreateClient:
    async def test_creates_client_successfully(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.add = MagicMock()
        # email check → no existing client
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.refresh = AsyncMock()

        payload = ClientCreate(
            first_name="Carlos",
            last_name="Rivera",
            email="carlos@example.com",
        )

        # Intercept the client object that gets added so we can inject languages
        added_objects = []

        def _capture_add(obj):
            if isinstance(obj, Client):
                obj.languages = []
            added_objects.append(obj)

        session.add.side_effect = _capture_add

        result = await client_service.create_client(session, payload)
        assert result.first_name == "Carlos"
        assert result.last_name == "Rivera"
        assert result.email == "carlos@example.com"

    async def test_duplicate_email_raises_409(self):
        existing = _make_client(email="taken@example.com")
        session = make_session(existing)

        payload = ClientCreate(
            first_name="Other",
            last_name="Person",
            email="taken@example.com",
        )
        with pytest.raises(HTTPException) as exc:
            await client_service.create_client(session, payload)
        assert exc.value.status_code == 409

    async def test_no_email_skips_uniqueness_check(self):
        """Clients without email are always allowed regardless of other clients."""
        session = AsyncMock()
        session.flush = AsyncMock()
        session.add = MagicMock()
        session.refresh = AsyncMock()

        added_objects = []

        def _capture(obj):
            if isinstance(obj, Client):
                obj.languages = []
            added_objects.append(obj)

        session.add.side_effect = _capture

        payload = ClientCreate(first_name="Ana", last_name="Lopez")
        result = await client_service.create_client(session, payload)
        assert result.first_name == "Ana"
        # No DB execute call for uniqueness since email is None
        session.execute.assert_not_called()


# ── get_client ────────────────────────────────────────────────────────────────

class TestGetClient:
    async def test_returns_client(self):
        client = _make_client()
        session = make_session(client)
        result = await client_service.get_client(session, client.id)
        assert result.id == client.id
        assert result.first_name == client.first_name

    async def test_not_found_raises_404(self):
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await client_service.get_client(session, uuid.uuid4())
        assert exc.value.status_code == 404

    async def test_client_number_format(self):
        client = _make_client()
        session = make_session(client)
        result = await client_service.get_client(session, client.id)
        # Format: "CL-" + first 8 chars of UUID uppercased
        expected_prefix = f"CL-{str(client.id)[:8].upper()}"
        assert result.client_number == expected_prefix


# ── update_client ─────────────────────────────────────────────────────────────

class TestUpdateClient:
    async def test_updates_fields(self):
        client = _make_client()
        session = make_session(client)
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        payload = ClientUpdate(first_name="Updated", city="Los Angeles")
        result = await client_service.update_client(session, client.id, payload)

        assert client.first_name == "Updated"
        assert client.city == "Los Angeles"

    async def test_not_found_raises_404(self):
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await client_service.update_client(session, uuid.uuid4(), ClientUpdate())
        assert exc.value.status_code == 404


# ── delete_client ─────────────────────────────────────────────────────────────

class TestDeleteClient:
    async def test_soft_deletes_client(self):
        client = _make_client()
        session = make_session(client)
        session.add = MagicMock()

        await client_service.delete_client(session, client.id)

        assert client.is_deleted is True
        assert client.deleted_at is not None

    async def test_soft_delete_preserves_data(self):
        client = _make_client()
        original_name = client.first_name
        session = make_session(client)
        session.add = MagicMock()

        await client_service.delete_client(session, client.id)

        assert client.first_name == original_name

    async def test_already_deleted_raises_404(self):
        """Querying for a deleted client (is_deleted=True) should return 404."""
        # The service filters is_deleted == False, so the mock returns None
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await client_service.delete_client(session, uuid.uuid4())
        assert exc.value.status_code == 404


# ── search_clients ────────────────────────────────────────────────────────────

class TestSearchClients:
    async def test_returns_paginated_results(self):
        clients = [_make_client(email=f"c{i}@example.com") for i in range(3)]

        session = AsyncMock()
        # paginate calls: 1) count query, 2) data query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 3

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = clients

        session.execute.side_effect = [count_result, data_result]

        pagination = PaginationParams(page=1, size=20)
        filters = ClientSearch()
        result = await client_service.search_clients(session, filters, pagination)

        assert result.total == 3
        assert len(result.items) == 3

    async def test_empty_results(self):
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        session.execute.side_effect = [count_result, data_result]

        pagination = PaginationParams(page=1, size=20)
        result = await client_service.search_clients(session, ClientSearch(), pagination)

        assert result.total == 0
        assert result.items == []


# ── _to_client_read (via get_client) ─────────────────────────────────────────

class TestToClientRead:
    async def test_full_address_property(self):
        client = _make_client()
        client.address_line_1 = "123 Main St"
        client.address_line_2 = None
        client.city = "Austin"
        client.state = "TX"
        client.zip_code = "78701"
        session = make_session(client)

        result = await client_service.get_client(session, client.id)
        assert result.full_address == "123 Main St, Austin, TX, 78701"

    async def test_gender_returned_as_value_string(self):
        client = _make_client()
        session = make_session(client)
        result = await client_service.get_client(session, client.id)
        assert result.gender == "female"

    async def test_immigration_status_returned_as_value_string(self):
        client = _make_client()
        session = make_session(client)
        result = await client_service.get_client(session, client.id)
        assert result.immigration_status == "refugee"
