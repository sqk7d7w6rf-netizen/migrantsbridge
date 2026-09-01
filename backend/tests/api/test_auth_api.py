"""
HTTP-level tests for /api/v1/auth/* endpoints.

The FastAPI app under test is a minimal version (no Redis/DB lifespan).
Service calls are patched so no real database is required.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.core.security import create_access_token, hash_password
from app.models.user import Role, User
from app.schemas.auth import TokenResponse, UserRead

_AUTH = "app.services.auth_service"


def _make_user(email: str = "worker@example.com", is_active: bool = True) -> User:
    role = Role(id=uuid.uuid4(), name="caseworker")
    role.permissions = []
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password("Password1!"),
        first_name="Jane",
        last_name="Doe",
        is_active=is_active,
        is_deleted=False,
        role_id=role.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user.role = role
    return user


def _make_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, {"role": "caseworker"}),
        refresh_token="fake-refresh-token",
        token_type="bearer",
        expires_in=1800,
    )


def _make_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ── POST /auth/login ──────────────────────────────────────────────────────────

class TestLogin:
    async def test_valid_credentials_return_200_with_tokens(self, anon_http, test_app):
        user = _make_user()
        token_response = _make_token_response(user)

        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(f"{_AUTH}.authenticate", new=AsyncMock(return_value=token_response)):
            resp = await anon_http.post(
                "/api/v1/auth/login",
                json={"email": "worker@example.com", "password": "Password1!"},
            )

        test_app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_invalid_credentials_return_401(self, anon_http, test_app):
        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(
            f"{_AUTH}.authenticate",
            new=AsyncMock(
                side_effect=HTTPException(status_code=401, detail="Invalid email or password")
            ),
        ):
            resp = await anon_http.post(
                "/api/v1/auth/login",
                json={"email": "bad@example.com", "password": "WrongPass1!"},
            )

        test_app.dependency_overrides.clear()
        assert resp.status_code == 401

    async def test_missing_fields_return_422(self, anon_http):
        resp = await anon_http.post("/api/v1/auth/login", json={"email": "user@example.com"})
        assert resp.status_code == 422

    async def test_short_password_returns_422(self, anon_http):
        resp = await anon_http.post(
            "/api/v1/auth/login", json={"email": "user@example.com", "password": "short"}
        )
        assert resp.status_code == 422


# ── POST /auth/register ───────────────────────────────────────────────────────

class TestRegister:
    async def test_valid_payload_returns_201(self, anon_http, test_app):
        user = _make_user(email="new@example.com")
        user_read = _make_user_read(user)

        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(f"{_AUTH}.create_user", new=AsyncMock(return_value=user_read)):
            resp = await anon_http.post(
                "/api/v1/auth/register",
                json={
                    "email": "new@example.com",
                    "password": "Password1!",
                    "first_name": "New",
                    "last_name": "User",
                },
            )

        test_app.dependency_overrides.clear()
        assert resp.status_code == 201
        assert resp.json()["email"] == "new@example.com"

    async def test_duplicate_email_returns_409(self, anon_http, test_app):
        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(
            f"{_AUTH}.create_user",
            new=AsyncMock(
                side_effect=HTTPException(
                    status_code=409, detail="A user with this email already exists"
                )
            ),
        ):
            resp = await anon_http.post(
                "/api/v1/auth/register",
                json={
                    "email": "taken@example.com",
                    "password": "Password1!",
                    "first_name": "Dup",
                    "last_name": "User",
                },
            )

        test_app.dependency_overrides.clear()
        assert resp.status_code == 409

    async def test_password_without_uppercase_returns_422(self, anon_http):
        resp = await anon_http.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password1!",  # no uppercase
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert resp.status_code == 422

    async def test_password_without_digit_returns_422(self, anon_http):
        resp = await anon_http.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "PasswordOnly!",  # no digit
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert resp.status_code == 422


# ── GET /auth/me ──────────────────────────────────────────────────────────────

class TestGetMe:
    async def test_authenticated_user_returns_200(self, make_authed_http, sample_user, test_app):
        user_read = _make_user_read(sample_user)

        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(f"{_AUTH}.get_user_by_id", new=AsyncMock(return_value=sample_user)):
            client = await make_authed_http(sample_user)
            async with client:
                resp = await client.get("/api/v1/auth/me")

        test_app.dependency_overrides.pop(get_async_session, None)
        assert resp.status_code == 200
        assert resp.json()["email"] == sample_user.email

    async def test_unauthenticated_returns_401(self, anon_http):
        resp = await anon_http.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ── POST /auth/change-password ────────────────────────────────────────────────

class TestChangePassword:
    async def test_correct_password_returns_200(self, make_authed_http, sample_user, test_app):
        from app.core.database import get_async_session

        async def _fake_session():
            yield AsyncMock()

        test_app.dependency_overrides[get_async_session] = _fake_session

        with patch(f"{_AUTH}.change_password", new=AsyncMock(return_value=None)):
            client = await make_authed_http(sample_user)
            async with client:
                resp = await client.post(
                    "/api/v1/auth/change-password",
                    json={"current_password": "Password1!", "new_password": "NewPass2!"},
                )

        test_app.dependency_overrides.pop(get_async_session, None)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Password changed successfully"

    async def test_unauthenticated_returns_401(self, anon_http):
        resp = await anon_http.post(
            "/api/v1/auth/change-password",
            json={"current_password": "Old1!", "new_password": "New1Password!"},
        )
        assert resp.status_code == 401


# ── RBAC: protected endpoints without auth ────────────────────────────────────

class TestProtectedEndpoints:
    """Spot-check that non-auth endpoints enforce authentication."""

    async def test_clients_list_requires_auth(self, anon_http):
        resp = await anon_http.get("/api/v1/clients/")
        assert resp.status_code == 401

    async def test_workflows_list_requires_auth(self, anon_http):
        resp = await anon_http.get("/api/v1/workflows/")
        assert resp.status_code == 401

    async def test_cases_list_requires_auth(self, anon_http):
        resp = await anon_http.get("/api/v1/cases/")
        assert resp.status_code == 401

    async def test_documents_list_requires_auth(self, anon_http):
        resp = await anon_http.get("/api/v1/documents/")
        assert resp.status_code == 401
