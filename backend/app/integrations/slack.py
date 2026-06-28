"""Slack adapter using httpx."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SLACK_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"


class SlackAdapter:
    """Slack message sending adapter (Bot token or incoming webhook)."""

    def __init__(
        self,
        bot_token: str | None = None,
        default_channel: str | None = None,
        webhook_url: str | None = None,
    ) -> None:
        self.bot_token = bot_token or settings.SLACK_BOT_TOKEN
        self.default_channel = default_channel or settings.SLACK_DEFAULT_CHANNEL
        self.webhook_url = webhook_url or settings.SLACK_WEBHOOK_URL

    def send(
        self,
        text: str,
        channel: str | None = None,
        blocks: list | None = None,
    ) -> bool:
        """Send a message to Slack. Returns True on success."""
        target_channel = channel or self.default_channel

        if self.bot_token:
            payload: dict = {"channel": target_channel, "text": text}
            if blocks:
                payload["blocks"] = blocks
            try:
                response = httpx.post(
                    SLACK_POST_MESSAGE_URL,
                    headers={
                        "Authorization": f"Bearer {self.bot_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=10.0,
                )
                data = response.json()
                if not data.get("ok"):
                    logger.error(
                        "Slack chat.postMessage failed: %s", data.get("error")
                    )
                    return False
                logger.info("Slack message sent to %s", target_channel)
                return True
            except Exception:
                logger.exception("Failed to send Slack message to %s", target_channel)
                return False

        if self.webhook_url:
            payload = {"text": text}
            if blocks:
                payload["blocks"] = blocks
            try:
                response = httpx.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.info("Slack message sent via webhook")
                return True
            except Exception:
                logger.exception("Failed to send Slack message via webhook")
                return False

        logger.warning(
            "Slack message not sent (no bot token or webhook configured): %s",
            text[:50],
        )
        return False


slack_adapter = SlackAdapter()
