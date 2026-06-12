"""Zapier integration — outbound webhook triggers and inbound API-key verification."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class ZapierClient:
    """Send data to Zapier Zap webhooks and validate inbound Zapier requests."""

    def __init__(
        self,
        api_key: str | None = None,
        webhook_url: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.ZAPIER_API_KEY
        self.webhook_url = webhook_url or settings.ZAPIER_WEBHOOK_URL
        self._client = None

    def _get_client(self):
        """Lazily initialise an async httpx client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(timeout=15.0)
            except ImportError:
                logger.warning("httpx not installed; Zapier triggers will be a no-op")
                return None
        return self._client

    def verify_api_key(self, provided_key: str) -> bool:
        """Constant-time comparison against the configured API key."""
        if not self.api_key:
            return False
        return hmac.compare_digest(provided_key, self.api_key)

    async def trigger(
        self,
        payload: dict[str, Any],
        webhook_url: str | None = None,
    ) -> bool:
        """POST *payload* to a Zapier catch-hook URL.

        Uses the instance ``webhook_url`` unless an override is passed.
        Returns True on HTTP 2xx, False otherwise.
        """
        client = self._get_client()
        target_url = webhook_url or self.webhook_url
        if client is None or not target_url:
            logger.warning("Zapier trigger skipped (no client or webhook URL)")
            return False

        headers: dict[str, str] = {}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key

        try:
            response = await client.post(target_url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Zapier trigger sent to %s, status=%d", target_url, response.status_code)
            return True
        except Exception:
            logger.exception("Failed to trigger Zapier webhook at %s", target_url)
            return False

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


zapier_client = ZapierClient()
