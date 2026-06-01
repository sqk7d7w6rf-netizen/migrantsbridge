"""Shared pytest fixtures for the MigrantsBridge test suite."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.router import api_router
from app.core.security import get_current_user, hash_password
from app.models.user import Role, User


# ── Mock DB helpers ───────────────────────────────────────────────────────────

def make_db_result(value: Any = None, values: list | None = None) -> MagicMock:
    """Mimic the result object returned by ``await session.execute(stmt)``."""
    rows = values if values is not None else ([] if value is None else [value])
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    r.scalar_one.return_value = value if value is not None else 0
    r.scalars.return_value.all.return_value = rows
    r.scalars.return_value.first.return_value = rows[0] if rows else None
    r.first.return_value = (value,) if value is not None else None
    return r


def make_session(*return_values: Any) -> AsyncMock:
    """Return an AsyncMock session whose execute() yields *return_values* in order."""
    session = AsyncMock()
    session.execute.side_effect = [make_db_result(v) for v in return_values]
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


# ── Domain fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_role() -> Role:
    role = Role(
        id=uuid.uuid4(),
        name="caseworker",
        description="Standard caseworker role",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    role.permissions = []
    role.users = []
    return role


@pytest.fixture
def sample_user(sample_role: Role) -> User:
    user = User(
        id=uuid.uuid4(),
        email="worker@example.com",
        hashed_password=hash_password("Password1!"),
        first_name="Jane",
        last_name="Doe",
        phone="+15551234567",
        is_active=True,
        is_deleted=False,
        role_id=sample_role.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user.role = sample_role
    return user


@pytest.fixture
def inactive_user(sample_role: Role) -> User:
    user = User(
        id=uuid.uuid4(),
        email="inactive@example.com",
        hashed_password=hash_password("Password1!"),
        first_name="Inactive",
        last_name="User",
        is_active=False,
        is_deleted=False,
        role_id=sample_role.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user.role = sample_role
    return user


# ── HTTP fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Minimal FastAPI app (no Redis/DB lifespan) for HTTP-level tests."""
    application = FastAPI()
    application.include_router(api_router)
    return application


@pytest.fixture
async def anon_http(test_app: FastAPI):
    """Unauthenticated HTTP client."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def make_authed_http(test_app: FastAPI):
    """
    Fixture factory.  Call ``await make_authed_http(user)`` to obtain an
    AsyncClient whose ``Authorization`` header carries a valid access token and
    whose ``get_current_user`` dependency is overridden to return *user*.
    """
    from app.core.security import create_access_token

    active_clients: list[AsyncClient] = []

    async def _factory(user: User) -> AsyncClient:
        token = create_access_token(
            user.id, {"role": user.role.name if user.role else None}
        )

        async def _override():
            return user

        test_app.dependency_overrides[get_current_user] = _override

        c = AsyncClient(
            transport=ASGITransport(app=test_app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {token}"},
        )
        active_clients.append(c)
        return c

    yield _factory
    test_app.dependency_overrides.clear()
