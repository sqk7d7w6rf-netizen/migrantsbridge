"""Slack adapter using the Slack Web API."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SLACK_API_BASE_URL = "https://slack.com/api"


class SlackClient:
    """Slack Web API client for posting messages."""

    def __init__(self, bot_token: str | None = None) -> None:
        self.bot_token = bot_token or settings.SLACK_BOT_TOKEN

    async def post_message(
        self,
        channel: str,
        text: str,
        blocks: list[dict] | None = None,
    ) -> dict:
        """Post a message to a Slack channel via chat.postMessage.

        If no bot token is configured, this is a no-op (logs a warning and
        skips the HTTP call) so local/dev environments without Slack
        configured don't break.
        """
        if not self.bot_token:
            logger.warning(
                "Slack bot token not configured; skipping message to channel=%s: %s",
                channel,
                text[:100],
            )
            return {"ok": False, "skipped": True, "reason": "SLACK_BOT_TOKEN not configured"}

        payload: dict = {"channel": channel, "text": text}
        if blocks is not None:
            payload["blocks"] = blocks

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{SLACK_API_BASE_URL}/chat.postMessage",
                    headers={
                        "Authorization": f"Bearer {self.bot_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            logger.exception("Failed to reach Slack API for channel=%s", channel)
            raise

        if not data.get("ok", False):
            logger.error("Slack API returned an error: %s", data.get("error", "unknown_error"))
            raise ValueError(f"Slack API error: {data.get('error', 'unknown_error')}")

        logger.info("Slack message posted to %s", channel)
        return data


# Singleton instance
slack_client = SlackClient()
