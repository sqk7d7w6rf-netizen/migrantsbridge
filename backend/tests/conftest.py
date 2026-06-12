"""Shared pytest fixtures and test configuration.

These tests are designed to run without a live Postgres/Redis instance: they
exercise the security, Claude-client, rate-limiting, and schema logic in
isolation, plus the DB-free ``/health`` endpoint. The settings object is forced
into a safe DEBUG configuration so the production-security guard does not abort
test collection.
"""

from __future__ import annotations

import pytest

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
