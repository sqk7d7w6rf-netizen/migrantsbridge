"""Tests for Pydantic schema validation rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.auth import ChangePasswordRequest, LoginRequest, UserCreate


def test_login_requires_minimum_password_length():
    with pytest.raises(ValidationError):
        LoginRequest(email="user@example.com", password="short")


def test_login_accepts_valid_payload():
    payload = LoginRequest(email="user@example.com", password="longenough1")
    assert payload.email == "user@example.com"


def test_user_create_requires_uppercase():
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            email="user@example.com",
            password="lowercase1",
            first_name="Ada",
            last_name="Lovelace",
        )
    assert "uppercase" in str(exc.value)


def test_user_create_requires_digit():
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            email="user@example.com",
            password="NoDigitsHere",
            first_name="Ada",
            last_name="Lovelace",
        )
    assert "digit" in str(exc.value)


def test_user_create_accepts_complex_password():
    user = UserCreate(
        email="user@example.com",
        password="ValidPass1",
        first_name="Ada",
        last_name="Lovelace",
    )
    assert user.password == "ValidPass1"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="ValidPass1",
            first_name="Ada",
            last_name="Lovelace",
        )


def test_change_password_enforces_complexity():
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="whatever", new_password="weakpass")
