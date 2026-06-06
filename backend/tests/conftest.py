"""Shared pytest fixtures for MigrantsBridge test suite."""

import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.api.router import api_router
from app.core.database import get_async_session
from app.core.security import create_access_token, get_current_user
from app.exceptions import AppException, app_exception_handler, generic_exception_handler


# ---------------------------------------------------------------------------
# Fake user & session
# ---------------------------------------------------------------------------

class FakeRole:
    name = "admin"
    permissions = []


class FakeUser:
    id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    email = "test@migrantsbridge.org"
    is_active = True
    role = FakeRole()


async def _fake_get_current_user():
    return FakeUser()


async def _fake_get_async_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    yield session


# ---------------------------------------------------------------------------
# Test app — uses a no-op lifespan to avoid real DB/Redis at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def _noop_lifespan(app: FastAPI):
    yield


def _create_test_app() -> FastAPI:
    """Minimal FastAPI app wired up identically to production but with no-op lifespan."""
    application = FastAPI(
        title="MigrantsBridge (test)",
        version="0.1.0",
        lifespan=_noop_lifespan,
    )

    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    @application.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy", "app": "MigrantsBridge", "version": "0.1.0"}

    # Dependency overrides
    application.dependency_overrides[get_current_user] = _fake_get_current_user
    application.dependency_overrides[get_async_session] = _fake_get_async_session

    return application


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    return _create_test_app()


@pytest.fixture(scope="session")
def client(app):
    """Test client with auth bypassed — all requests act as authenticated."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="session")
def raw_client():
    """Test client WITHOUT auth override — use to verify 401/403 enforcement."""
    raw_app = FastAPI(
        title="MigrantsBridge (raw test)",
        version="0.1.0",
        lifespan=_noop_lifespan,
    )
    raw_app.add_exception_handler(AppException, app_exception_handler)
    raw_app.add_exception_handler(Exception, generic_exception_handler)
    raw_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    raw_app.include_router(api_router)
    raw_app.dependency_overrides[get_async_session] = _fake_get_async_session

    with TestClient(raw_app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Function-scoped helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_headers():
    token = create_access_token(FakeUser.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake_user():
    return FakeUser()
