"""Communication service: templates, rendering, and notification queuing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jinja2 import BaseLoader, Environment, TemplateSyntaxError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ChannelType, NotificationStatus as ModelNotificationStatus
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.communication import MessageLog, MessageTemplate, Notification
from app.models.user import User
from app.schemas.communication import (
    BulkNotificationSend,
    NotificationChannel,
    NotificationRead,
    NotificationSend,
    NotificationStatus,
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
)


_jinja_env = Environment(loader=BaseLoader(), autoescape=True)


def render_template(template_body: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 template string with context variables."""
    try:
        tmpl = _jinja_env.from_string(template_body)
        return tmpl.render(**context)
    except TemplateSyntaxError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template syntax error: {exc.message}",
        )


def _to_template_read(tmpl: MessageTemplate) -> TemplateRead:
    """Map MessageTemplate model to TemplateRead schema."""
    variables = []
    if tmpl.variables:
        if isinstance(tmpl.variables, dict):
            variables = list(tmpl.variables.keys())
        elif isinstance(tmpl.variables, list):
            variables = tmpl.variables

    return TemplateRead(
        id=tmpl.id,
        name=tmpl.name,
        subject=tmpl.subject,
        body=tmpl.body_template,
        channel=tmpl.channel.value,
        language=tmpl.language,
        category=None,
        variables=variables,
        is_active=tmpl.is_active,
        created_at=tmpl.created_at,
        updated_at=tmpl.updated_at,
    )


def _to_notification_read(notif: Notification) -> NotificationRead:
    """Map Notification model to NotificationRead schema."""
    return NotificationRead(
        id=notif.id,
        recipient_id=notif.user_id,
        channel=notif.channel.value,
        subject=notif.title,
        body=notif.message,
        status=notif.status.value,
        template_id=None,
        sent_at=None,
        delivered_at=None,
        read_at=notif.read_at,
        error_message=None,
        created_at=notif.created_at,
    )


# --- Template CRUD ---

async def create_template(session: AsyncSession, payload: TemplateCreate) -> TemplateRead:
    """Create a communication template."""
    # Validate template syntax
    try:
        _jinja_env.from_string(payload.body)
        if payload.subject:
            _jinja_env.from_string(payload.subject)
    except TemplateSyntaxError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template syntax: {exc.message}",
        )

    # Map schema channel to model enum
    channel_map = {
        "email": ChannelType.EMAIL,
        "sms": ChannelType.SMS,
        "in_app": ChannelType.IN_APP,
    }
    model_channel = channel_map.get(payload.channel.value, ChannelType.EMAIL)

    # Store variables as JSONB dict
    variables_dict = {v: "" for v in payload.variables} if payload.variables else None

    template = MessageTemplate(
        name=payload.name,
        subject=payload.subject,
        body_template=payload.body,
        channel=model_channel,
        language=payload.language,
        variables=variables_dict,
        is_active=True,
    )
    session.add(template)
    await session.flush()
    await session.refresh(template)
    return _to_template_read(template)


async def get_template(session: AsyncSession, template_id: UUID) -> TemplateRead:
    """Get a template by ID."""
    result = await session.execute(select(MessageTemplate).where(MessageTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if tmpl is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return _to_template_read(tmpl)


async def list_templates(
    session: AsyncSession,
    pagination: PaginationParams,
    channel: str | None = None,
    language: str | None = None,
    category: str | None = None,
    active_only: bool = True,
) -> PaginatedResponse[TemplateRead]:
    """List templates with optional filters."""
    query = select(MessageTemplate)
    if active_only:
        query = query.where(MessageTemplate.is_active == True)
    if channel:
        try:
            query = query.where(MessageTemplate.channel == ChannelType(channel))
        except ValueError:
            pass
    if language:
        query = query.where(MessageTemplate.language == language)
    query = query.order_by(MessageTemplate.name.asc())
    result = await paginate(session, query, pagination)
    result.items = [_to_template_read(t) for t in result.items]
    return result


async def update_template(
    session: AsyncSession, template_id: UUID, payload: TemplateUpdate
) -> TemplateRead:
    """Update a template."""
    result = await session.execute(select(MessageTemplate).where(MessageTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if tmpl is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Validate template syntax if body changed
    if "body" in update_data and update_data["body"]:
        try:
            _jinja_env.from_string(update_data["body"])
        except TemplateSyntaxError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template syntax: {exc.message}",
            )
        tmpl.body_template = update_data.pop("body")

    if "channel" in update_data and update_data["channel"] is not None:
        channel_map = {"email": ChannelType.EMAIL, "sms": ChannelType.SMS, "in_app": ChannelType.IN_APP}
        tmpl.channel = channel_map.get(update_data.pop("channel").value, ChannelType.EMAIL)

    if "variables" in update_data and update_data["variables"] is not None:
        tmpl.variables = {v: "" for v in update_data.pop("variables")}

    # Set remaining simple fields
    for field in ("name", "subject", "language", "is_active"):
        if field in update_data and update_data[field] is not None:
            setattr(tmpl, field, update_data[field])

    session.add(tmpl)
    await session.flush()
    await session.refresh(tmpl)
    return _to_template_read(tmpl)


async def delete_template(session: AsyncSession, template_id: UUID) -> None:
    """Soft-delete (deactivate) a template."""
    result = await session.execute(select(MessageTemplate).where(MessageTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if tmpl is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    tmpl.is_active = False
    session.add(tmpl)


# --- Notifications ---

async def queue_notification(
    session: AsyncSession, payload: NotificationSend, sender_id: UUID | None = None
) -> NotificationRead:
    """Queue a notification for sending."""
    body = payload.body or ""
    subject = payload.subject or ""

    # If using a template, render it
    if payload.template_id:
        result = await session.execute(
            select(MessageTemplate).where(
                MessageTemplate.id == payload.template_id,
                MessageTemplate.is_active == True,
            )
        )
        tmpl = result.scalar_one_or_none()
        if tmpl is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found or inactive"
            )
        body = render_template(tmpl.body_template, payload.context)
        if tmpl.subject:
            subject = render_template(tmpl.subject, payload.context)

    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification body is required (either directly or via template)",
        )

    # Map schema channel to model ChannelType
    channel_map = {"email": ChannelType.EMAIL, "sms": ChannelType.SMS, "in_app": ChannelType.IN_APP}
    model_channel = channel_map.get(payload.channel.value, ChannelType.IN_APP)

    notification = Notification(
        user_id=payload.recipient_id,
        title=subject or "Notification",
        message=body,
        channel=model_channel,
        status=ModelNotificationStatus.PENDING,
    )
    session.add(notification)
    await session.flush()
    await session.refresh(notification)

    # Dispatch to Celery for actual sending
    _dispatch_notification(str(notification.id), payload.channel.value)

    return _to_notification_read(notification)


def _dispatch_notification(notification_id: str, channel: str) -> None:
    """Dispatch notification to the appropriate Celery task."""
    try:
        if channel == NotificationChannel.EMAIL.value:
            from app.workers.notification_tasks import send_email
            send_email.delay(notification_id)
        elif channel == NotificationChannel.SMS.value:
            from app.workers.notification_tasks import send_sms
            send_sms.delay(notification_id)
        # IN_APP notifications are already persisted
    except Exception:
        import logging
        logging.getLogger(__name__).warning(
            "Could not dispatch notification %s via %s", notification_id, channel
        )


async def queue_bulk_notifications(
    session: AsyncSession, payload: BulkNotificationSend, sender_id: UUID | None = None
) -> list[NotificationRead]:
    """Send the same templated notification to multiple recipients."""
    results: list[NotificationRead] = []
    for recipient_id in payload.recipient_ids:
        single = NotificationSend(
            recipient_id=recipient_id,
            template_id=payload.template_id,
            channel=payload.channel,
            context=payload.context,
        )
        notif = await queue_notification(session, single, sender_id)
        results.append(notif)
    return results


async def get_notification(session: AsyncSession, notification_id: UUID) -> NotificationRead:
    """Get a notification by ID."""
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return _to_notification_read(notif)


async def list_notifications(
    session: AsyncSession,
    pagination: PaginationParams,
    recipient_id: UUID | None = None,
    channel: str | None = None,
    status_filter: str | None = None,
) -> PaginatedResponse[NotificationRead]:
    """List notifications (inbox) with filters."""
    query = select(Notification)
    if recipient_id:
        query = query.where(Notification.user_id == recipient_id)
    if channel:
        try:
            query = query.where(Notification.channel == ChannelType(channel))
        except ValueError:
            pass
    if status_filter:
        try:
            query = query.where(Notification.status == ModelNotificationStatus(status_filter))
        except ValueError:
            pass
    query = query.order_by(Notification.created_at.desc())
    result = await paginate(session, query, pagination)
    result.items = [_to_notification_read(n) for n in result.items]
    return result


async def mark_as_read(session: AsyncSession, notification_id: UUID) -> NotificationRead:
    """Mark a notification as read."""
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    notif.status = ModelNotificationStatus.READ
    notif.read_at = datetime.now(timezone.utc)
    session.add(notif)
    await session.flush()
    return _to_notification_read(notif)
