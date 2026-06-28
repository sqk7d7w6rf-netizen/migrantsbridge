"""Tests for the Slack integration adapter."""

from __future__ import annotations

from app.integrations.slack import SLACK_POST_MESSAGE_URL, SlackAdapter


class _FakeResponse:
    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self._json = json_data
        self.status_code = status_code

    def json(self) -> dict:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_send_with_bot_token_posts_to_chat_postmessage(monkeypatch):
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return _FakeResponse({"ok": True})

    monkeypatch.setattr("app.integrations.slack.httpx.post", fake_post)

    adapter = SlackAdapter(bot_token="xoxb-test", default_channel="#ops")
    result = adapter.send(text="hello", channel="#alerts")

    assert result is True
    assert captured["url"] == SLACK_POST_MESSAGE_URL
    assert captured["headers"]["Authorization"] == "Bearer xoxb-test"
    assert captured["json"]["channel"] == "#alerts"
    assert captured["json"]["text"] == "hello"


def test_send_defaults_to_default_channel(monkeypatch):
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return _FakeResponse({"ok": True})

    monkeypatch.setattr("app.integrations.slack.httpx.post", fake_post)

    adapter = SlackAdapter(bot_token="xoxb-test", default_channel="#ops")
    assert adapter.send(text="hi") is True
    assert captured["json"]["channel"] == "#ops"


def test_send_returns_false_when_slack_reports_not_ok(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse({"ok": False, "error": "channel_not_found"})

    monkeypatch.setattr("app.integrations.slack.httpx.post", fake_post)

    adapter = SlackAdapter(bot_token="xoxb-test", default_channel="#ops")
    assert adapter.send(text="hi") is False


def test_send_via_webhook_fallback(monkeypatch):
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse({}, status_code=200)

    monkeypatch.setattr("app.integrations.slack.httpx.post", fake_post)

    adapter = SlackAdapter(
        bot_token="", default_channel="", webhook_url="https://hooks.slack.com/services/xxx"
    )
    assert adapter.send(text="hi", blocks=[{"type": "section"}]) is True
    assert captured["url"] == "https://hooks.slack.com/services/xxx"
    assert captured["json"]["text"] == "hi"
    assert captured["json"]["blocks"] == [{"type": "section"}]


def test_send_unconfigured_is_noop(monkeypatch):
    def fail_post(*args, **kwargs):  # pragma: no cover - should never be called
        raise AssertionError("httpx.post should not be called when unconfigured")

    monkeypatch.setattr("app.integrations.slack.httpx.post", fail_post)

    adapter = SlackAdapter(bot_token="", default_channel="", webhook_url="")
    assert adapter.send(text="hi") is False
