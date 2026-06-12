"""Unit tests for the ZapierClient integration adapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.zapier import ZapierClient


@pytest.fixture
def client():
    return ZapierClient(api_key="secret-api-key", webhook_url="https://hooks.zapier.com/hooks/catch/123/abc")


@pytest.fixture
def client_no_key():
    return ZapierClient(api_key="", webhook_url="https://hooks.zapier.com/hooks/catch/123/abc")


# ---------------------------------------------------------------------------
# API key verification
# ---------------------------------------------------------------------------

class TestVerifyApiKey:
    def test_correct_key_accepted(self, client):
        assert client.verify_api_key("secret-api-key") is True

    def test_wrong_key_rejected(self, client):
        assert client.verify_api_key("wrong-key") is False

    def test_empty_provided_key_rejected(self, client):
        assert client.verify_api_key("") is False

    def test_no_api_key_configured_always_fails(self, client_no_key):
        assert client_no_key.verify_api_key("secret-api-key") is False

    def test_constant_time_comparison(self, client):
        # Partial match must still fail
        assert client.verify_api_key("secret-api-ke") is False


# ---------------------------------------------------------------------------
# Lazy client initialisation
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_returns_none_when_httpx_missing(self, client):
        with patch.dict("sys.modules", {"httpx": None}):
            client._client = None
            result = client._get_client()
            assert result is None

    def test_reuses_existing_client(self, client):
        mock_http = MagicMock()
        client._client = mock_http
        assert client._get_client() is mock_http


# ---------------------------------------------------------------------------
# trigger
# ---------------------------------------------------------------------------

class TestTrigger:
    @pytest.mark.asyncio
    async def test_successful_trigger(self, client):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        client._client = mock_http

        ok = await client.trigger({"event": "case_created", "case_id": "abc"})

        assert ok is True
        mock_http.post.assert_called_once()
        call_kwargs = mock_http.post.call_args[1]
        assert call_kwargs["json"] == {"event": "case_created", "case_id": "abc"}
        assert call_kwargs["headers"]["X-Api-Key"] == "secret-api-key"

    @pytest.mark.asyncio
    async def test_trigger_with_override_url(self, client):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        client._client = mock_http

        override = "https://hooks.zapier.com/hooks/catch/999/xyz"
        ok = await client.trigger({"foo": "bar"}, webhook_url=override)
        assert ok is True
        called_url = mock_http.post.call_args[0][0]
        assert called_url == override

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self, client):
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(side_effect=Exception("connection refused"))
        client._client = mock_http

        ok = await client.trigger({"foo": "bar"})
        assert ok is False

    @pytest.mark.asyncio
    async def test_returns_false_without_webhook_url(self):
        c = ZapierClient(api_key="key", webhook_url="")
        ok = await c.trigger({"foo": "bar"})
        assert ok is False

    @pytest.mark.asyncio
    async def test_returns_false_without_http_client(self, client):
        with patch.dict("sys.modules", {"httpx": None}):
            client._client = None
            ok = await client.trigger({"foo": "bar"})
            assert ok is False
