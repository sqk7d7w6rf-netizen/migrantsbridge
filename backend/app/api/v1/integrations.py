"""Integration endpoints: Telegram Bot and Zapier webhooks."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.config import settings
from app.core.security import get_current_user
from app.integrations.telegram import telegram_bot
from app.integrations.zapier import zapier_client
from app.schemas.integrations import (
    IntegrationStatusItem,
    IntegrationStatusResponse,
    TelegramSendRequest,
    TelegramSendResponse,
    TelegramWebhookUpdate,
    ZapierInboundPayload,
    ZapierTriggerRequest,
    ZapierTriggerResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@router.get("/status", response_model=IntegrationStatusResponse)
async def integration_status(current_user=Depends(get_current_user)):
    """Return the configuration status of each integration."""
    items = [
        IntegrationStatusItem(
            name="telegram",
            configured=bool(settings.TELEGRAM_BOT_TOKEN),
            detail="webhook_secret set" if settings.TELEGRAM_WEBHOOK_SECRET else "no webhook_secret",
        ),
        IntegrationStatusItem(
            name="zapier",
            configured=bool(settings.ZAPIER_API_KEY and settings.ZAPIER_WEBHOOK_URL),
            detail=f"webhook_url={'set' if settings.ZAPIER_WEBHOOK_URL else 'not set'}",
        ),
    ]
    return IntegrationStatusResponse(integrations=items)


# ---------------------------------------------------------------------------
# Telegram — outbound
# ---------------------------------------------------------------------------

@router.post("/telegram/send", response_model=TelegramSendResponse, status_code=201)
async def send_telegram_message(
    payload: TelegramSendRequest,
    current_user=Depends(get_current_user),
):
    """Send a Telegram message to a chat_id (authenticated staff endpoint)."""
    result = await telegram_bot.send_message(
        chat_id=payload.chat_id,
        text=payload.text,
        parse_mode=payload.parse_mode,
    )
    return TelegramSendResponse(
        chat_id=payload.chat_id,
        message_id=result.get("message_id") if result else None,
        delivered=result is not None,
    )


# ---------------------------------------------------------------------------
# Telegram — webhook (public, verified via secret-token header)
# ---------------------------------------------------------------------------

@router.post("/webhooks/telegram", status_code=200)
async def telegram_webhook(
    update: TelegramWebhookUpdate,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    """Receive incoming updates from Telegram.

    Telegram delivers updates here when a webhook is registered via
    ``TelegramBot.set_webhook()``.  The ``X-Telegram-Bot-Api-Secret-Token``
    header is checked when TELEGRAM_WEBHOOK_SECRET is configured.
    """
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if not x_telegram_bot_api_secret_token or not telegram_bot.verify_secret_token(
            x_telegram_bot_api_secret_token
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret token")

    logger.info("Telegram update received: update_id=%d", update.update_id)

    if update.message:
        chat_id = update.message.get("chat", {}).get("id")
        text = update.message.get("text", "")
        logger.info("Telegram message from chat_id=%s: %s", chat_id, text[:100])

    return {"ok": True}


# ---------------------------------------------------------------------------
# Zapier — outbound trigger
# ---------------------------------------------------------------------------

@router.post("/zapier/trigger", response_model=ZapierTriggerResponse, status_code=201)
async def zapier_trigger(
    payload: ZapierTriggerRequest,
    current_user=Depends(get_current_user),
):
    """Trigger a Zapier Zap by POSTing to its catch-hook URL."""
    target = payload.webhook_url or settings.ZAPIER_WEBHOOK_URL
    if not target:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Zapier webhook URL configured. Set ZAPIER_WEBHOOK_URL or pass webhook_url.",
        )

    success = await zapier_client.trigger(payload.payload, webhook_url=target)
    return ZapierTriggerResponse(success=success, webhook_url=target)


# ---------------------------------------------------------------------------
# Zapier — inbound webhook (API-key protected)
# ---------------------------------------------------------------------------

@router.post("/webhooks/zapier", status_code=200)
async def zapier_webhook(
    payload: ZapierInboundPayload,
    x_api_key: str | None = Header(default=None),
):
    """Receive inbound data from a Zapier Zap action.

    Authenticate with the ``X-Api-Key`` header matching ``ZAPIER_API_KEY``.
    """
    if not settings.ZAPIER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Zapier integration is not configured on this server.",
        )

    if not x_api_key or not zapier_client.verify_api_key(x_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    logger.info("Zapier inbound event=%s data_keys=%s", payload.event, list(payload.data.keys()))

    return {"received": True, "event": payload.event}
