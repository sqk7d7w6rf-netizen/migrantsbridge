"""API endpoint tests for /api/v1/integrations."""

from unittest.mock import AsyncMock, patch

import pytest

from app.config import settings


# ---------------------------------------------------------------------------
# GET /api/v1/integrations/status
# ---------------------------------------------------------------------------

class TestIntegrationStatus:
    def test_requires_authentication(self, raw_client):
        resp = raw_client.get("/api/v1/integrations/status")
        assert resp.status_code == 401

    def test_returns_status_for_each_integration(self, client, auth_headers):
        resp = client.get("/api/v1/integrations/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        names = {item["name"] for item in data["integrations"]}
        assert "telegram" in names
        assert "zapier" in names

    def test_telegram_unconfigured_when_no_token(self, client, auth_headers):
        original = settings.TELEGRAM_BOT_TOKEN
        settings.TELEGRAM_BOT_TOKEN = ""
        try:
            resp = client.get("/api/v1/integrations/status", headers=auth_headers)
            items = {i["name"]: i for i in resp.json()["integrations"]}
            assert items["telegram"]["configured"] is False
        finally:
            settings.TELEGRAM_BOT_TOKEN = original


# ---------------------------------------------------------------------------
# POST /api/v1/integrations/telegram/send
# ---------------------------------------------------------------------------

class TestTelegramSend:
    def test_requires_authentication(self, raw_client):
        resp = raw_client.post("/api/v1/integrations/telegram/send", json={"chat_id": "123", "text": "hi"})
        assert resp.status_code == 401

    def test_send_message_delivered(self, client, auth_headers):
        with patch("app.api.v1.integrations.telegram_bot") as mock_bot:
            mock_bot.send_message = AsyncMock(return_value={"message_id": 99})

            resp = client.post(
                "/api/v1/integrations/telegram/send",
                headers=auth_headers,
                json={"chat_id": "123456", "text": "Hello migrant!", "parse_mode": "HTML"},
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["delivered"] is True
        assert body["message_id"] == 99
        assert body["chat_id"] == "123456"

    def test_send_message_not_delivered(self, client, auth_headers):
        with patch("app.api.v1.integrations.telegram_bot") as mock_bot:
            mock_bot.send_message = AsyncMock(return_value=None)

            resp = client.post(
                "/api/v1/integrations/telegram/send",
                headers=auth_headers,
                json={"chat_id": "123", "text": "hi"},
            )

        assert resp.status_code == 201
        assert resp.json()["delivered"] is False

    def test_empty_text_rejected(self, client, auth_headers):
        resp = client.post(
            "/api/v1/integrations/telegram/send",
            headers=auth_headers,
            json={"chat_id": "123", "text": ""},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/integrations/webhooks/telegram
# ---------------------------------------------------------------------------

class TestTelegramWebhook:
    VALID_UPDATE = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "chat": {"id": 111, "type": "private"},
            "text": "Hello bot",
        },
    }

    def test_accepted_without_secret_configured(self, client):
        original = settings.TELEGRAM_WEBHOOK_SECRET
        settings.TELEGRAM_WEBHOOK_SECRET = ""
        try:
            resp = client.post("/api/v1/integrations/webhooks/telegram", json=self.VALID_UPDATE)
            assert resp.status_code == 200
            assert resp.json()["ok"] is True
        finally:
            settings.TELEGRAM_WEBHOOK_SECRET = original

    def test_accepted_with_correct_secret(self, client):
        settings.TELEGRAM_WEBHOOK_SECRET = "tg-secret"
        with patch("app.api.v1.integrations.telegram_bot") as mock_bot:
            mock_bot.verify_secret_token.return_value = True
            mock_bot.webhook_secret = "tg-secret"

            resp = client.post(
                "/api/v1/integrations/webhooks/telegram",
                json=self.VALID_UPDATE,
                headers={"X-Telegram-Bot-Api-Secret-Token": "tg-secret"},
            )
        settings.TELEGRAM_WEBHOOK_SECRET = ""
        assert resp.status_code == 200

    def test_rejected_with_wrong_secret(self, client):
        settings.TELEGRAM_WEBHOOK_SECRET = "tg-secret"
        with patch("app.api.v1.integrations.telegram_bot") as mock_bot:
            mock_bot.verify_secret_token.return_value = False
            mock_bot.webhook_secret = "tg-secret"

            resp = client.post(
                "/api/v1/integrations/webhooks/telegram",
                json=self.VALID_UPDATE,
                headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
            )
        settings.TELEGRAM_WEBHOOK_SECRET = ""
        assert resp.status_code == 403

    def test_missing_secret_header_rejected(self, client):
        settings.TELEGRAM_WEBHOOK_SECRET = "tg-secret"
        with patch("app.api.v1.integrations.telegram_bot") as mock_bot:
            mock_bot.verify_secret_token.return_value = False
            mock_bot.webhook_secret = "tg-secret"

            resp = client.post("/api/v1/integrations/webhooks/telegram", json=self.VALID_UPDATE)
        settings.TELEGRAM_WEBHOOK_SECRET = ""
        assert resp.status_code == 403

    def test_invalid_payload_rejected(self, client):
        settings.TELEGRAM_WEBHOOK_SECRET = ""
        resp = client.post(
            "/api/v1/integrations/webhooks/telegram",
            json={"not_update_id": True},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/integrations/zapier/trigger
# ---------------------------------------------------------------------------

class TestZapierTrigger:
    def test_requires_authentication(self, raw_client):
        resp = raw_client.post("/api/v1/integrations/zapier/trigger", json={"payload": {}})
        assert resp.status_code == 401

    def test_trigger_success(self, client, auth_headers):
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.trigger = AsyncMock(return_value=True)

            resp = client.post(
                "/api/v1/integrations/zapier/trigger",
                headers=auth_headers,
                json={
                    "payload": {"event": "case_created", "case_id": "abc-123"},
                    "webhook_url": "https://hooks.zapier.com/hooks/catch/1/test",
                },
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert "zapier" in body["webhook_url"]

    def test_trigger_failure_propagated(self, client, auth_headers):
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.trigger = AsyncMock(return_value=False)

            resp = client.post(
                "/api/v1/integrations/zapier/trigger",
                headers=auth_headers,
                json={"payload": {"x": 1}, "webhook_url": "https://hooks.zapier.com/hooks/catch/1/test"},
            )

        assert resp.status_code == 201
        assert resp.json()["success"] is False

    def test_no_url_and_no_config_returns_422(self, client, auth_headers):
        original = settings.ZAPIER_WEBHOOK_URL
        settings.ZAPIER_WEBHOOK_URL = ""
        try:
            resp = client.post(
                "/api/v1/integrations/zapier/trigger",
                headers=auth_headers,
                json={"payload": {"x": 1}},
            )
            assert resp.status_code == 422
        finally:
            settings.ZAPIER_WEBHOOK_URL = original


# ---------------------------------------------------------------------------
# POST /api/v1/integrations/webhooks/zapier
# ---------------------------------------------------------------------------

class TestZapierWebhook:
    VALID_PAYLOAD = {"event": "new_intake_submitted", "data": {"client_id": "xyz"}}

    def test_rejected_when_not_configured(self, client):
        original = settings.ZAPIER_API_KEY
        settings.ZAPIER_API_KEY = ""
        try:
            resp = client.post(
                "/api/v1/integrations/webhooks/zapier",
                json=self.VALID_PAYLOAD,
                headers={"X-Api-Key": "any-key"},
            )
            assert resp.status_code == 503
        finally:
            settings.ZAPIER_API_KEY = original

    def test_accepted_with_correct_api_key(self, client):
        settings.ZAPIER_API_KEY = "z-secret"
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.verify_api_key.return_value = True

            resp = client.post(
                "/api/v1/integrations/webhooks/zapier",
                json=self.VALID_PAYLOAD,
                headers={"X-Api-Key": "z-secret"},
            )
        settings.ZAPIER_API_KEY = ""
        assert resp.status_code == 200
        assert resp.json()["received"] is True
        assert resp.json()["event"] == "new_intake_submitted"

    def test_rejected_with_wrong_api_key(self, client):
        settings.ZAPIER_API_KEY = "z-secret"
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.verify_api_key.return_value = False

            resp = client.post(
                "/api/v1/integrations/webhooks/zapier",
                json=self.VALID_PAYLOAD,
                headers={"X-Api-Key": "wrong"},
            )
        settings.ZAPIER_API_KEY = ""
        assert resp.status_code == 401

    def test_missing_api_key_header_rejected(self, client):
        settings.ZAPIER_API_KEY = "z-secret"
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.verify_api_key.return_value = False

            resp = client.post("/api/v1/integrations/webhooks/zapier", json=self.VALID_PAYLOAD)
        settings.ZAPIER_API_KEY = ""
        assert resp.status_code == 401

    def test_missing_event_field_rejected(self, client):
        settings.ZAPIER_API_KEY = "z-secret"
        with patch("app.api.v1.integrations.zapier_client") as mock_zap:
            mock_zap.verify_api_key.return_value = True

            resp = client.post(
                "/api/v1/integrations/webhooks/zapier",
                json={"data": {"foo": "bar"}},
                headers={"X-Api-Key": "z-secret"},
            )
        settings.ZAPIER_API_KEY = ""
        assert resp.status_code == 422
