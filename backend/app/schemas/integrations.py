"""Pydantic schemas for Telegram and Zapier integration endpoints."""

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

class TelegramSendRequest(BaseModel):
    chat_id: str = Field(..., description="Telegram chat_id or @username")
    text: str = Field(..., min_length=1, max_length=4096)
    parse_mode: str = Field("HTML", description="HTML or Markdown")


class TelegramSendResponse(BaseModel):
    chat_id: str
    message_id: int | None = None
    delivered: bool


class TelegramWebhookUpdate(BaseModel):
    """Minimal subset of a Telegram Update object used for routing."""

    update_id: int
    message: dict[str, Any] | None = None
    callback_query: dict[str, Any] | None = None
    inline_query: dict[str, Any] | None = None

    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# Zapier
# ---------------------------------------------------------------------------

class ZapierTriggerRequest(BaseModel):
    payload: dict[str, Any] = Field(..., description="Arbitrary data to POST to the Zapier hook")
    webhook_url: str | None = Field(None, description="Override the default ZAPIER_WEBHOOK_URL")


class ZapierTriggerResponse(BaseModel):
    success: bool
    webhook_url: str


class ZapierInboundPayload(BaseModel):
    """Generic inbound payload from a Zapier Zap action."""

    event: str = Field(..., description="Event name sent by the Zap")
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

class IntegrationStatusItem(BaseModel):
    name: str
    configured: bool
    detail: str | None = None


class IntegrationStatusResponse(BaseModel):
    integrations: list[IntegrationStatusItem]
