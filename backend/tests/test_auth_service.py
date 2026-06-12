"""Service-layer tests for auth_service against a real database."""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.core.security import decode_token, verify_password
from app.models.user import Role, User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    UserCreate,
)
from app.services import auth_service


@pytest_asyncio.fixture
async def role(db_session):
    role = Role(name="caseworker", description="Test role")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest_asyncio.fixture
async def user(db_session, role):
    payload = UserCreate(
        email="worker@example.com",
        password="StrongPass1",
        first_name="Casey",
        last_name="Worker",
        role_id=role.id,
    )
    created = await auth_service.create_user(db_session, payload)
    return created


async def test_create_user_persists_hashed_password(db_session, role):
    payload = UserCreate(
        email="new@example.com",
        password="StrongPass1",
        first_name="New",
        last_name="User",
        role_id=role.id,
    )
    created = await auth_service.create_user(db_session, payload)

    assert created.email == "new@example.com"
    assert created.role_name == "caseworker"

    stored = await db_session.get(User, created.id)
    assert stored.hashed_password != "StrongPass1"
    assert verify_password("StrongPass1", stored.hashed_password)


async def test_create_user_rejects_duplicate_email(db_session, user):
    dup = UserCreate(
        email="worker@example.com",
        password="StrongPass1",
        first_name="Dup",
        last_name="Licate",
    )
    with pytest.raises(HTTPException) as exc:
        await auth_service.create_user(db_session, dup)
    assert exc.value.status_code == 409


async def test_authenticate_success_returns_valid_tokens(db_session, user):
    tokens = await auth_service.authenticate(
        db_session, LoginRequest(email="worker@example.com", password="StrongPass1")
    )
    assert tokens.token_type == "bearer"
    payload = decode_token(tokens.access_token)
    assert payload["sub"] == str(user.id)
    assert payload["role"] == "caseworker"


async def test_authenticate_wrong_password_401(db_session, user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            db_session, LoginRequest(email="worker@example.com", password="WrongPass1")
        )
    assert exc.value.status_code == 401


async def test_authenticate_unknown_email_401(db_session, user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            db_session, LoginRequest(email="ghost@example.com", password="StrongPass1")
        )
    assert exc.value.status_code == 401


async def test_authenticate_inactive_user_403(db_session, user):
    stored = await db_session.get(User, user.id)
    stored.is_active = False
    await db_session.flush()

    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            db_session, LoginRequest(email="worker@example.com", password="StrongPass1")
        )
    assert exc.value.status_code == 403


async def test_authenticate_updates_last_login(db_session, user):
    before = await db_session.get(User, user.id)
    assert before.last_login_at is None
    await auth_service.authenticate(
        db_session, LoginRequest(email="worker@example.com", password="StrongPass1")
    )
    after = await db_session.get(User, user.id)
    assert after.last_login_at is not None


async def test_refresh_token_issues_new_pair(db_session, user):
    tokens = await auth_service.authenticate(
        db_session, LoginRequest(email="worker@example.com", password="StrongPass1")
    )
    refreshed = await auth_service.refresh_token(db_session, tokens.refresh_token)
    assert decode_token(refreshed.access_token)["type"] == "access"


async def test_refresh_rejects_access_token(db_session, user):
    tokens = await auth_service.authenticate(
        db_session, LoginRequest(email="worker@example.com", password="StrongPass1")
    )
    with pytest.raises(HTTPException) as exc:
        await auth_service.refresh_token(db_session, tokens.access_token)
    assert exc.value.status_code == 401


async def test_change_password_success(db_session, user):
    await auth_service.change_password(
        db_session,
        user.id,
        ChangePasswordRequest(current_password="StrongPass1", new_password="BrandNew2"),
    )
    stored = await db_session.get(User, user.id)
    assert verify_password("BrandNew2", stored.hashed_password)


async def test_change_password_wrong_current_400(db_session, user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.change_password(
            db_session,
            user.id,
            ChangePasswordRequest(current_password="Nope0000", new_password="BrandNew2"),
        )
    assert exc.value.status_code == 400


async def test_get_user_by_id_missing_404(db_session):
    with pytest.raises(HTTPException) as exc:
        await auth_service.get_user_by_id(db_session, uuid.uuid4())
    assert exc.value.status_code == 404
