"""Telegram Bot integration using the Bot API over HTTPS."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramBot:
    """Adapter for sending Telegram messages and verifying webhook updates."""

    def __init__(self, token: str | None = None, webhook_secret: str | None = None) -> None:
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.webhook_secret = webhook_secret or settings.TELEGRAM_WEBHOOK_SECRET
        self._client = None

    def _get_client(self):
        """Lazily initialise an async httpx client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(timeout=10.0)
            except ImportError:
                logger.warning("httpx not installed; Telegram sending will be a no-op")
                return None
        return self._client

    def verify_secret_token(self, token_header: str) -> bool:
        """Verify the X-Telegram-Bot-Api-Secret-Token header value."""
        if not self.webhook_secret:
            return True
        return hmac.compare_digest(token_header, self.webhook_secret)

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str = "HTML",
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Send a text message to a Telegram chat."""
        client = self._get_client()
        if client is None or not self.token:
            logger.warning("Telegram message not sent (no client/token): chat_id=%s", chat_id)
            return None

        url = f"{TELEGRAM_API_BASE}{self.token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, **kwargs}

        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Telegram message sent to chat_id=%s, message_id=%s", chat_id, data.get("result", {}).get("message_id"))
            return data.get("result")
        except Exception:
            logger.exception("Failed to send Telegram message to chat_id=%s", chat_id)
            return None

    async def send_bulk(
        self, chat_ids: list[str | int], text: str, **kwargs: Any
    ) -> dict[str, dict[str, Any] | None]:
        """Send the same message to multiple chat IDs."""
        results: dict[str, dict[str, Any] | None] = {}
        for chat_id in chat_ids:
            results[str(chat_id)] = await self.send_message(chat_id, text, **kwargs)
        return results

    async def set_webhook(self, webhook_url: str) -> bool:
        """Register the bot webhook URL with Telegram."""
        client = self._get_client()
        if client is None or not self.token:
            return False

        url = f"{TELEGRAM_API_BASE}{self.token}/setWebhook"
        payload: dict[str, Any] = {"url": webhook_url}
        if self.webhook_secret:
            payload["secret_token"] = self.webhook_secret

        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            ok = bool(result.get("ok"))
            logger.info("Telegram webhook %s: %s", webhook_url, result.get("description"))
            return ok
        except Exception:
            logger.exception("Failed to set Telegram webhook")
            return False

    async def get_webhook_info(self) -> dict[str, Any] | None:
        """Return the current webhook configuration from Telegram."""
        client = self._get_client()
        if client is None or not self.token:
            return None

        url = f"{TELEGRAM_API_BASE}{self.token}/getWebhookInfo"
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json().get("result")
        except Exception:
            logger.exception("Failed to get Telegram webhook info")
            return None

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


telegram_bot = TelegramBot()
