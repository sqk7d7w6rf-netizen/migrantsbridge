"""Tests for app/core/security.py — JWT creation, verification, and permission checking."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    require_permission,
    verify_password,
)


# ── Password hashing ──────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self):
        pw = "MySecurePass1!"
        hashed = hash_password(pw)
        assert verify_password(pw, hashed) is True

    def test_wrong_password_rejected(self):
        hashed = hash_password("correct-horse-battery-1A")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_is_not_plaintext(self):
        pw = "Password1!"
        assert hash_password(pw) != pw

    def test_two_hashes_differ(self):
        pw = "Password1!"
        # bcrypt generates a unique salt each time
        assert hash_password(pw) != hash_password(pw)


# ── Access token ──────────────────────────────────────────────────────────────

class TestCreateAccessToken:
    def test_returns_decodable_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == str(user_id)

    def test_type_claim_is_access(self):
        token = create_access_token(uuid.uuid4())
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["type"] == "access"

    def test_extra_claims_included(self):
        token = create_access_token(uuid.uuid4(), extra_claims={"role": "admin"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["role"] == "admin"

    def test_expiry_in_future(self):
        token = create_access_token(uuid.uuid4())
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp > datetime.now(timezone.utc)

    def test_accepts_string_subject(self):
        token = create_access_token("some-string-id")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "some-string-id"


# ── Refresh token ─────────────────────────────────────────────────────────────

class TestCreateRefreshToken:
    def test_type_claim_is_refresh(self):
        token = create_refresh_token(uuid.uuid4())
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["type"] == "refresh"

    def test_expiry_is_after_access_token(self):
        user_id = uuid.uuid4()
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)

        access_payload = jwt.decode(access, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        refresh_payload = jwt.decode(refresh, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        assert refresh_payload["exp"] > access_payload["exp"]


# ── decode_token ──────────────────────────────────────────────────────────────

class TestDecodeToken:
    def test_valid_token_decoded(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)

    def test_tampered_token_raises_401(self):
        token = create_access_token(uuid.uuid4())
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered)
        assert exc_info.value.status_code == 401

    def test_wrong_secret_raises_401(self):
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_expired_token_raises_401(self):
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_garbage_string_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_token("this.is.not.a.jwt")
        assert exc_info.value.status_code == 401


# ── require_permission ────────────────────────────────────────────────────────

class TestRequirePermission:
    """
    require_permission returns an async dependency function.  We test it by
    calling that inner function with a mocked token resolution path.
    """

    async def test_user_with_permission_passes(self):
        from app.models.user import Permission, User

        mock_perm = MagicMock(spec=Permission)
        mock_perm.name = "clients:write"

        mock_user = MagicMock(spec=User)
        mock_user.role = MagicMock()
        mock_user.role.permissions = [mock_perm]

        with patch(
            "app.dependencies.resolve_current_user_with_permissions",
            new=AsyncMock(return_value=(mock_user, ["clients:write"])),
        ):
            dependency = require_permission("clients:write")
            result = await dependency(token="fake-token")
            assert result is mock_user

    async def test_user_missing_permission_raises_403(self):
        from app.models.user import User

        mock_user = MagicMock(spec=User)

        with patch(
            "app.dependencies.resolve_current_user_with_permissions",
            new=AsyncMock(return_value=(mock_user, ["clients:read"])),
        ):
            dependency = require_permission("clients:write")
            with pytest.raises(HTTPException) as exc_info:
                await dependency(token="fake-token")
            assert exc_info.value.status_code == 403
            assert "clients:write" in exc_info.value.detail

    async def test_multiple_permissions_all_required(self):
        from app.models.user import User

        mock_user = MagicMock(spec=User)

        with patch(
            "app.dependencies.resolve_current_user_with_permissions",
            new=AsyncMock(return_value=(mock_user, ["clients:read"])),
        ):
            dependency = require_permission("clients:read", "clients:write")
            with pytest.raises(HTTPException) as exc_info:
                await dependency(token="fake-token")
            assert exc_info.value.status_code == 403
