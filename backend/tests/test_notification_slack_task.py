"""Tests for the send_slack Celery task status transitions."""

from __future__ import annotations

from uuid import uuid4

from app.constants import NotificationStatus
from app.workers import notification_tasks


class _FakeResult:
    def __init__(self, obj):
        self._obj = obj

    def scalar_one_or_none(self):
        return self._obj


class _FakeNotification:
    def __init__(self, user_id):
        self.user_id = user_id
        self.title = "Heads up"
        self.message = "A case needs review"
        self.status = NotificationStatus.PENDING


class _FakeUser:
    def __init__(self):
        self.id = uuid4()


class _FakeSession:
    def __init__(self, notif, user):
        self._results = [notif, user]
        self._idx = 0
        self.committed = False

    async def execute(self, _stmt):
        obj = self._results[self._idx]
        self._idx += 1
        return _FakeResult(obj)

    def add(self, _obj):
        pass

    async def commit(self):
        self.committed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _patch(monkeypatch, notif, user, send_return):
    session = _FakeSession(notif, user)

    def fake_factory():
        return session

    monkeypatch.setattr(
        "app.core.database.async_session_factory", fake_factory, raising=False
    )

    class _FakeAdapter:
        def send(self, text, channel=None, blocks=None):
            return send_return

    monkeypatch.setattr("app.integrations.slack.slack_adapter", _FakeAdapter())

    from app.config import settings

    monkeypatch.setattr(settings, "SLACK_DEFAULT_CHANNEL", "#ops")
    return notif


def test_send_slack_success_marks_sent(monkeypatch):
    user = _FakeUser()
    notif = _FakeNotification(user.id)
    _patch(monkeypatch, notif, user, send_return=True)

    result = notification_tasks.send_slack.run(str(uuid4()))

    assert result["status"] == "sent"
    assert notif.status == NotificationStatus.SENT


def test_send_slack_failure_marks_failed(monkeypatch):
    user = _FakeUser()
    notif = _FakeNotification(user.id)
    _patch(monkeypatch, notif, user, send_return=False)

    result = notification_tasks.send_slack.run(str(uuid4()))

    assert result["status"] == "failed"
    assert notif.status == NotificationStatus.FAILED
