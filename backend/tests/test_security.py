"""Tests for password hashing, JWT handling, and the production-security guard."""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.config import settings
from app.core import security
from app.core.security import (
    INSECURE_SECRET_KEY,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    validate_production_security,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("S3cretPass")
    assert hashed != "S3cretPass"
    assert verify_password("S3cretPass", hashed)
    assert not verify_password("wrong", hashed)


def test_hash_password_is_salted():
    # Two hashes of the same password differ thanks to per-hash salts.
    assert hash_password("samePass1") != hash_password("samePass1")


def test_access_token_roundtrip():
    token = create_access_token("user-123", {"role": "admin"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["role"] == "admin"


def test_refresh_token_type():
    payload = decode_token(create_refresh_token("user-123"))
    assert payload["type"] == "refresh"


def test_decode_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc:
        decode_token("not-a-real-token")
    assert exc.value.status_code == 401


def test_decode_expired_token_raises_401(monkeypatch):
    # Issue a token that is already expired by patching the expiry window.
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    expired = create_access_token("user-123")
    with pytest.raises(HTTPException) as exc:
        decode_token(expired)
    assert exc.value.status_code == 401


def test_token_signed_with_wrong_secret_is_rejected(monkeypatch):
    token = create_access_token("user-123")
    monkeypatch.setattr(settings, "SECRET_KEY", "a-different-secret")
    with pytest.raises(HTTPException):
        decode_token(token)


def test_validate_production_security_allows_safe_secret(monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "SECRET_KEY", "a-strong-random-secret")
    # Should not raise.
    validate_production_security()


def test_validate_production_security_blocks_default_secret_in_production(monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "SECRET_KEY", INSECURE_SECRET_KEY)
    with pytest.raises(RuntimeError):
        validate_production_security()


def test_validate_production_security_warns_in_debug(monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "SECRET_KEY", INSECURE_SECRET_KEY)
    # In DEBUG the insecure default is tolerated (warning only).
    validate_production_security()
