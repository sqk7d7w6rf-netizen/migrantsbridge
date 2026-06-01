"""Integration tests for app/services/auth_service.py (DB session is mocked)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.security import hash_password, verify_password
from app.models.user import Role, User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    UserCreate,
)
from app.services import auth_service
from tests.conftest import make_db_result, make_session


def _make_user(
    email: str = "test@example.com",
    password: str = "Password1!",
    is_active: bool = True,
    is_deleted: bool = False,
) -> User:
    role = Role(id=uuid.uuid4(), name="staff")
    role.permissions = []
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        first_name="Test",
        last_name="User",
        is_active=is_active,
        is_deleted=is_deleted,
        role_id=role.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    user.role = role
    return user


# ── authenticate ──────────────────────────────────────────────────────────────

class TestAuthenticate:
    async def test_valid_credentials_return_tokens(self):
        user = _make_user()
        session = make_session(user)

        payload = LoginRequest(email=user.email, password="Password1!")
        result = await auth_service.authenticate(session, payload)

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"
        assert result.expires_in > 0

    async def test_wrong_password_raises_401(self):
        user = _make_user(password="CorrectPass1!")
        session = make_session(user)

        payload = LoginRequest(email=user.email, password="WrongPass1!")
        with pytest.raises(HTTPException) as exc:
            await auth_service.authenticate(session, payload)
        assert exc.value.status_code == 401

    async def test_nonexistent_user_raises_401(self):
        session = make_session(None)  # user not found
        payload = LoginRequest(email="nobody@example.com", password="Password1!")
        with pytest.raises(HTTPException) as exc:
            await auth_service.authenticate(session, payload)
        assert exc.value.status_code == 401

    async def test_inactive_user_raises_403(self):
        user = _make_user(is_active=False)
        session = make_session(user)

        payload = LoginRequest(email=user.email, password="Password1!")
        with pytest.raises(HTTPException) as exc:
            await auth_service.authenticate(session, payload)
        assert exc.value.status_code == 403

    async def test_error_message_does_not_differentiate_user_vs_password(self):
        """Prevents user-enumeration: same message for wrong user or wrong password."""
        # Wrong user
        session_no_user = make_session(None)
        try:
            await auth_service.authenticate(
                session_no_user, LoginRequest(email="x@y.com", password="Password1!")
            )
        except HTTPException as exc_no_user:
            pass

        # Wrong password
        user = _make_user()
        session_wrong_pw = make_session(user)
        try:
            await auth_service.authenticate(
                session_wrong_pw, LoginRequest(email=user.email, password="WrongPass1!")
            )
        except HTTPException as exc_wrong_pw:
            pass

        assert exc_no_user.detail == exc_wrong_pw.detail

    async def test_updates_last_login(self):
        user = _make_user()
        session = make_session(user)

        await auth_service.authenticate(session, LoginRequest(email=user.email, password="Password1!"))

        assert user.last_login_at is not None
        session.add.assert_called()


# ── create_user ───────────────────────────────────────────────────────────────

class TestCreateUser:
    async def test_new_user_created_successfully(self):
        session = make_session(None)  # no existing user with same email

        # After flush+refresh, the session.refresh should set user attributes.
        # We need the user object created inside create_user to have its id set.
        # Since User.id has default=uuid.uuid4 (Python-side), it IS set on __init__.
        payload = UserCreate(
            email="new@example.com",
            password="Password1!",
            first_name="New",
            last_name="User",
        )

        # We need to patch get_user_by_id or let session.refresh be a no-op.
        # The user object created inside create_user will have id set via default.
        result = await auth_service.create_user(session, payload)

        assert result.email == "new@example.com"
        assert result.first_name == "New"
        assert result.last_name == "User"

    async def test_duplicate_email_raises_409(self):
        existing_user = _make_user(email="taken@example.com")
        session = make_session(existing_user)  # returns existing user on lookup

        payload = UserCreate(
            email="taken@example.com",
            password="Password1!",
            first_name="Another",
            last_name="User",
        )
        with pytest.raises(HTTPException) as exc:
            await auth_service.create_user(session, payload)
        assert exc.value.status_code == 409

    async def test_password_is_hashed_not_stored_plain(self):
        session = make_session(None)
        payload = UserCreate(
            email="secure@example.com",
            password="Password1!",
            first_name="Sec",
            last_name="User",
        )

        # Capture the User object added to the session
        added_objects = []
        session.add.side_effect = added_objects.append

        await auth_service.create_user(session, payload)

        user_obj = next((o for o in added_objects if isinstance(o, User)), None)
        assert user_obj is not None
        assert user_obj.hashed_password != "Password1!"
        assert verify_password("Password1!", user_obj.hashed_password)


# ── refresh_token ─────────────────────────────────────────────────────────────

class TestRefreshToken:
    async def test_valid_refresh_token_returns_new_pair(self):
        user = _make_user()
        session = make_session(user)

        from app.core.security import create_refresh_token
        token = create_refresh_token(user.id)

        result = await auth_service.refresh_token(session, token)

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"

    async def test_access_token_used_as_refresh_raises_401(self):
        user = _make_user()
        session = make_session(user)

        from app.core.security import create_access_token
        access_token = create_access_token(user.id)

        with pytest.raises(HTTPException) as exc:
            await auth_service.refresh_token(session, access_token)
        assert exc.value.status_code == 401

    async def test_inactive_user_refresh_raises_401(self):
        user = _make_user(is_active=False)
        session = make_session(None)  # is_active=True query returns None

        from app.core.security import create_refresh_token
        token = create_refresh_token(user.id)

        with pytest.raises(HTTPException) as exc:
            await auth_service.refresh_token(session, token)
        assert exc.value.status_code == 401

    async def test_garbage_token_raises_401(self):
        session = make_session()
        with pytest.raises(HTTPException) as exc:
            await auth_service.refresh_token(session, "not.a.real.token")
        assert exc.value.status_code == 401


# ── change_password ───────────────────────────────────────────────────────────

class TestChangePassword:
    async def test_correct_current_password_updates_hash(self):
        user = _make_user(password="OldPass1!")
        session = make_session(user)

        payload = ChangePasswordRequest(
            current_password="OldPass1!", new_password="NewPass2!"
        )
        await auth_service.change_password(session, user.id, payload)

        assert verify_password("NewPass2!", user.hashed_password)

    async def test_wrong_current_password_raises_400(self):
        user = _make_user(password="CorrectPass1!")
        session = make_session(user)

        payload = ChangePasswordRequest(
            current_password="WrongPass1!", new_password="NewPass2!"
        )
        with pytest.raises(HTTPException) as exc:
            await auth_service.change_password(session, user.id, payload)
        assert exc.value.status_code == 400

    async def test_user_not_found_raises_404(self):
        session = make_session(None)
        payload = ChangePasswordRequest(
            current_password="OldPass1!", new_password="NewPass2!"
        )
        with pytest.raises(HTTPException) as exc:
            await auth_service.change_password(session, uuid.uuid4(), payload)
        assert exc.value.status_code == 404
