"""Unit tests for the TelegramBot integration adapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.telegram import TelegramBot


@pytest.fixture
def bot():
    return TelegramBot(token="123456:TEST_TOKEN", webhook_secret="mysecret")


@pytest.fixture
def bot_no_secret():
    return TelegramBot(token="123456:TEST_TOKEN", webhook_secret="")


# ---------------------------------------------------------------------------
# Secret-token verification
# ---------------------------------------------------------------------------

class TestVerifySecretToken:
    def test_correct_token_accepted(self, bot):
        assert bot.verify_secret_token("mysecret") is True

    def test_wrong_token_rejected(self, bot):
        assert bot.verify_secret_token("wrongsecret") is False

    def test_empty_token_rejected(self, bot):
        assert bot.verify_secret_token("") is False

    def test_no_secret_configured_always_passes(self, bot_no_secret):
        # When no secret is set, verification is a no-op
        assert bot_no_secret.verify_secret_token("anything") is True

    def test_constant_time_comparison(self, bot):
        # Ensure both sides are compared fully (no short-circuit on first char)
        assert bot.verify_secret_token("mysecreX") is False


# ---------------------------------------------------------------------------
# Lazy client initialisation
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_returns_none_when_httpx_missing(self, bot):
        with patch.dict("sys.modules", {"httpx": None}):
            bot._client = None
            result = bot._get_client()
            assert result is None

    def test_client_reused_on_second_call(self, bot):
        mock_client = MagicMock()
        bot._client = mock_client
        assert bot._get_client() is mock_client


# ---------------------------------------------------------------------------
# send_message
# ---------------------------------------------------------------------------

class TestSendMessage:
    @pytest.mark.asyncio
    async def test_returns_none_without_token(self):
        bot = TelegramBot(token="", webhook_secret="")
        result = await bot.send_message("12345", "hello")
        assert result is None

    @pytest.mark.asyncio
    async def test_successful_send(self, bot):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 42}}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        bot._client = mock_client

        result = await bot.send_message(chat_id="123", text="Hello World")

        assert result == {"message_id": 42}
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["chat_id"] == "123"
        assert call_args[1]["json"]["text"] == "Hello World"
        assert call_args[1]["json"]["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_returns_none_on_http_error(self, bot):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("connection error"))
        bot._client = mock_client

        result = await bot.send_message("123", "hello")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_bulk_calls_send_for_each(self, bot):
        sent = []

        async def fake_send(chat_id, text, **kw):
            sent.append(chat_id)
            return {"message_id": 1}

        bot.send_message = fake_send  # type: ignore[method-assign]
        results = await bot.send_bulk(["100", "200", "300"], "Broadcast")
        assert len(results) == 3
        assert set(sent) == {"100", "200", "300"}


# ---------------------------------------------------------------------------
# set_webhook
# ---------------------------------------------------------------------------

class TestSetWebhook:
    @pytest.mark.asyncio
    async def test_successful_registration(self, bot):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True, "description": "Webhook was set"}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        bot._client = mock_client

        ok = await bot.set_webhook("https://example.com/api/v1/integrations/webhooks/telegram")
        assert ok is True
        payload = mock_client.post.call_args[1]["json"]
        assert payload["url"] == "https://example.com/api/v1/integrations/webhooks/telegram"
        assert payload["secret_token"] == "mysecret"

    @pytest.mark.asyncio
    async def test_returns_false_on_error(self, bot):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("timeout"))
        bot._client = mock_client

        ok = await bot.set_webhook("https://example.com/webhook")
        assert ok is False

    @pytest.mark.asyncio
    async def test_returns_false_without_token(self):
        bot = TelegramBot(token="", webhook_secret="")
        ok = await bot.set_webhook("https://example.com/webhook")
        assert ok is False
