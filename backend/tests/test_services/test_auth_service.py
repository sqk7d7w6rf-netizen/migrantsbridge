"""Tests for app.services.auth_service.

These cover registration, authentication, token refresh, password changes, and
user lookups/updates against a real database session.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException, status

from app.core.security import create_access_token, decode_token, verify_password
from app.models.user import Role, User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    UserCreate,
    UserUpdate,
)
from app.services import auth_service

# Run all tests in this module on the shared session-scoped event loop so they
# can use the session-scoped asyncpg engine (see tests/conftest.py).
pytestmark = pytest.mark.asyncio(loop_scope="session")

VALID_PASSWORD = "Sup3rSecret"
NEW_PASSWORD = "N3wPassword"


def _user_create(**overrides) -> UserCreate:
    data = {
        "email": "newuser@example.com",
        "password": VALID_PASSWORD,
        "first_name": "New",
        "last_name": "User",
    }
    data.update(overrides)
    return UserCreate(**data)


@pytest_asyncio.fixture
async def role(session) -> Role:
    role = Role(name="case_manager", description="Manages cases")
    session.add(role)
    await session.flush()
    return role


@pytest_asyncio.fixture
async def existing_user(session) -> User:
    user = await auth_service.create_user(session, _user_create(email="existing@example.com"))
    return await auth_service.get_user_by_id(session, user.id)


# --------------------------------------------------------------------------- #
# create_user
# --------------------------------------------------------------------------- #


async def test_create_user_persists_hashed_password(session):
    result = await auth_service.create_user(session, _user_create())

    assert result.email == "newuser@example.com"
    assert result.is_active is True
    assert result.role_name is None

    db_user = await auth_service.get_user_by_id(session, result.id)
    # Password must be hashed, never stored in plaintext.
    assert db_user.hashed_password != VALID_PASSWORD
    assert verify_password(VALID_PASSWORD, db_user.hashed_password)


async def test_create_user_with_role_returns_role_name(session, role):
    result = await auth_service.create_user(
        session, _user_create(email="withrole@example.com", role_id=role.id)
    )
    assert result.role_id == role.id
    assert result.role_name == "case_manager"


async def test_create_user_duplicate_email_conflicts(session, existing_user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.create_user(session, _user_create(email=existing_user.email))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


# --------------------------------------------------------------------------- #
# authenticate
# --------------------------------------------------------------------------- #


async def test_authenticate_success_returns_tokens_and_sets_last_login(session, existing_user):
    assert existing_user.last_login_at is None

    tokens = await auth_service.authenticate(
        session, LoginRequest(email=existing_user.email, password=VALID_PASSWORD)
    )

    assert tokens.token_type == "bearer"
    assert tokens.access_token
    assert tokens.refresh_token

    access_payload = decode_token(tokens.access_token)
    assert access_payload["sub"] == str(existing_user.id)
    assert access_payload["type"] == "access"

    # authenticate() mutates last_login_at but relies on the request session to
    # commit; flush so the change reaches the DB, then reload to confirm.
    await session.flush()
    await session.refresh(existing_user)
    assert existing_user.last_login_at is not None


async def test_authenticate_embeds_role_claim(session, role):
    created = await auth_service.create_user(
        session, _user_create(email="claim@example.com", role_id=role.id)
    )
    tokens = await auth_service.authenticate(
        session, LoginRequest(email=created.email, password=VALID_PASSWORD)
    )
    assert decode_token(tokens.access_token)["role"] == "case_manager"


async def test_authenticate_wrong_password_unauthorized(session, existing_user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            session, LoginRequest(email=existing_user.email, password="WrongPass1")
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authenticate_unknown_email_unauthorized(session):
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            session, LoginRequest(email="nobody@example.com", password=VALID_PASSWORD)
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authenticate_inactive_account_forbidden(session, existing_user):
    existing_user.is_active = False
    session.add(existing_user)
    await session.flush()

    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            session, LoginRequest(email=existing_user.email, password=VALID_PASSWORD)
        )
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


async def test_authenticate_ignores_soft_deleted_user(session, existing_user):
    existing_user.is_deleted = True
    session.add(existing_user)
    await session.flush()

    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(
            session, LoginRequest(email=existing_user.email, password=VALID_PASSWORD)
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------- #
# refresh_token
# --------------------------------------------------------------------------- #


async def test_refresh_token_issues_new_pair(session, existing_user):
    tokens = await auth_service.authenticate(
        session, LoginRequest(email=existing_user.email, password=VALID_PASSWORD)
    )
    refreshed = await auth_service.refresh_token(session, tokens.refresh_token)

    assert refreshed.access_token
    payload = decode_token(refreshed.access_token)
    assert payload["sub"] == str(existing_user.id)


async def test_refresh_token_rejects_access_token(session, existing_user):
    access = create_access_token(existing_user.id)
    with pytest.raises(HTTPException) as exc:
        await auth_service.refresh_token(session, access)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "refresh token" in exc.value.detail


async def test_refresh_token_rejects_inactive_user(session, existing_user):
    tokens = await auth_service.authenticate(
        session, LoginRequest(email=existing_user.email, password=VALID_PASSWORD)
    )
    existing_user.is_active = False
    session.add(existing_user)
    await session.flush()

    with pytest.raises(HTTPException) as exc:
        await auth_service.refresh_token(session, tokens.refresh_token)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------- #
# change_password
# --------------------------------------------------------------------------- #


async def test_change_password_updates_hash(session, existing_user):
    await auth_service.change_password(
        session,
        existing_user.id,
        ChangePasswordRequest(current_password=VALID_PASSWORD, new_password=NEW_PASSWORD),
    )
    await session.flush()
    await session.refresh(existing_user)

    assert verify_password(NEW_PASSWORD, existing_user.hashed_password)
    assert not verify_password(VALID_PASSWORD, existing_user.hashed_password)


async def test_change_password_wrong_current_rejected(session, existing_user):
    with pytest.raises(HTTPException) as exc:
        await auth_service.change_password(
            session,
            existing_user.id,
            ChangePasswordRequest(current_password="WrongPass1", new_password=NEW_PASSWORD),
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


async def test_change_password_missing_user_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await auth_service.change_password(
            session,
            uuid.uuid4(),
            ChangePasswordRequest(current_password=VALID_PASSWORD, new_password=NEW_PASSWORD),
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------- #
# get_user_by_id / update_user
# --------------------------------------------------------------------------- #


async def test_get_user_by_id_missing_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await auth_service.get_user_by_id(session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


async def test_update_user_changes_fields(session, existing_user):
    updated = await auth_service.update_user(
        session,
        existing_user.id,
        UserUpdate(first_name="Renamed", phone="+15551234567", is_active=False),
    )
    assert updated.first_name == "Renamed"
    assert updated.phone == "+15551234567"
    assert updated.is_active is False
