"""Shared pytest fixtures for the backend test suite.

These tests exercise the service layer against a real PostgreSQL database so
they validate the same SQL, enum, and JSONB behavior that runs in production.
Point them at a throwaway database via the ``TEST_DATABASE_URL`` environment
variable; it defaults to a local ``migrantsbridge_test`` database. CI provisions
this with a ``postgres`` service container (see ``.github/workflows/ci.yml``).

Isolation strategy: the schema is created once per session, and every test runs
inside a single outer transaction that is rolled back on teardown. The services
under test only ever ``flush()`` (never ``commit()``), so a rollback fully
restores the database between tests without recreating tables.
"""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import every model module so that ``Base.metadata`` is fully populated before
# we create the schema. Importing the package is enough — ``app/models/__init__.py``
# pulls in all the individual model modules.
import app.models  # noqa: F401
from app.core.database import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/migrantsbridge_test",
)

# asyncpg connections are bound to the event loop that created them, so the
# shared session-scoped ``engine``/``session`` fixtures and every test that uses
# them must run on the same loop. Test modules opt in by re-exporting this as
# their module-level ``pytestmark`` (see the test_services modules).
session_loop = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Session-scoped async engine with a freshly created schema."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=None)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    """Per-test session wrapped in a transaction that is always rolled back."""
    connection = await engine.connect()
    transaction = await connection.begin()
    factory = async_sessionmaker(bind=connection, expire_on_commit=False, class_=AsyncSession)
    db_session = factory()
    try:
        yield db_session
    finally:
        await db_session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
