"""Shared pytest fixtures and test configuration.

These tests are designed to run without a live Postgres/Redis instance: they
exercise the security, Claude-client, rate-limiting, and schema logic in
isolation, plus the DB-free ``/health`` endpoint. The settings object is forced
into a safe DEBUG configuration so the production-security guard does not abort
test collection.
"""

from __future__ import annotations

import asyncio
import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings

# Make the singleton settings safe for tests regardless of the host environment.
settings.DEBUG = True
settings.SECRET_KEY = "test-secret-key-not-for-production"


@pytest.fixture
def app():
    """Build the FastAPI app without triggering lifespan (no DB/Redis needed)."""
    from app.main import create_app

    return create_app()


@pytest.fixture
def client(app):
    """A TestClient that does NOT enter the lifespan context.

    Constructing the client without the ``with`` block means startup/shutdown
    hooks (which would try to reach Postgres and Redis) never run, so DB-free
    endpoints like ``/health`` can be tested in isolation.
    """
    from fastapi.testclient import TestClient

    return TestClient(app)


class FakeBlock:
    """Stand-in for an Anthropic content block (text / thinking / tool_use)."""

    def __init__(self, type: str, text: str | None = None) -> None:
        self.type = type
        if text is not None:
            self.text = text


class FakeResponse:
    def __init__(self, blocks: list[FakeBlock]) -> None:
        self.content = blocks


# --- Database fixtures (require Postgres) -------------------------------------
#
# Service-layer tests run against a real Postgres because the models use
# Postgres-specific types (UUID, JSONB, native enums) that SQLite can't emulate.
# Point them at a database with TEST_DATABASE_URL; if it's unreachable the
# DB-backed tests skip rather than fail, so the rest of the suite still runs.

DEFAULT_TEST_DB_URL = "postgresql+asyncpg://postgres@127.0.0.1:5432/migrantsbridge_test"


def _test_db_url() -> str:
    return os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DB_URL)


@pytest.fixture(scope="session")
def db_url():
    """Create the schema once for the session; drop it at the end.

    Uses ``asyncio.run`` so setup/teardown are fully self-contained and don't
    share an event loop with the per-test fixtures.
    """
    import app.models  # noqa: F401 - register all tables on Base.metadata
    from app.core.database import Base

    url = _test_db_url()

    async def _setup() -> None:
        engine = create_async_engine(url)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        finally:
            await engine.dispose()

    try:
        asyncio.run(_setup())
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Test database unavailable: {exc}")

    yield url

    async def _teardown() -> None:
        engine = create_async_engine(url)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        finally:
            await engine.dispose()

    try:
        asyncio.run(_teardown())
    except Exception:  # noqa: BLE001
        pass


@pytest_asyncio.fixture
async def db_session(db_url) -> AsyncSession:
    """Per-test session wrapped in a transaction that is rolled back afterwards.

    Each test gets its own engine on the running loop and a savepoint-joined
    session, so a service calling ``commit()`` won't leak state across tests.
    """
    engine = create_async_engine(db_url)
    conn = await engine.connect()
    trans = await conn.begin()
    session = AsyncSession(
        bind=conn,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()
