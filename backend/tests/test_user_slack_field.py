"""Tests for the slack_user_id field on the User model."""

from __future__ import annotations

from app.models.user import User


def test_user_model_has_slack_user_id_column():
    assert "slack_user_id" in User.__table__.columns


def test_user_slack_user_id_is_nullable_string():
    column = User.__table__.columns["slack_user_id"]
    assert column.nullable is True
    assert column.type.python_type is str
