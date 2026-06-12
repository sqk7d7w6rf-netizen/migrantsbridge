"""Communication service: templates, rendering, notification queuing, and threads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jinja2 import BaseLoader, Environment, TemplateSyntaxError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants import ChannelType, NotificationStatus as ModelNotificationStatus
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.communication import (
    Message,
    MessageLog,
    MessageTemplate,
    Notification,
    NotificationPreference,
    SenderType,
    Thread,
    ThreadStatus,
)
from app.models.user import User
from app.schemas.communication import (
    BulkNotificationSend,
    MessageCreate,
    MessageRead,
    NotificationChannel,
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
    NotificationRead,
    NotificationSend,
    NotificationStatus,
    SenderTypeEnum,
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
    ThreadCreate,
    ThreadRead,
    ThreadStatusEnum,
    ThreadWithMessages,
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


# --------------------------------------------------------------------------- #
# Threads & Messages                                                           #
# --------------------------------------------------------------------------- #

_CHANNEL_STR = {ChannelType.EMAIL: "email", ChannelType.SMS: "sms", ChannelType.IN_APP: "in_app"}
_STR_CHANNEL = {v: k for k, v in _CHANNEL_STR.items()}


def _to_message_read(msg: Message) -> MessageRead:
    return MessageRead(
        id=msg.id,
        thread_id=msg.thread_id,
        sender_id=msg.sender_id,
        sender_name=msg.sender_name,
        sender_type=SenderTypeEnum(msg.sender_type.value),
        content=msg.content,
        channel=_CHANNEL_STR.get(msg.channel, "in_app"),
        is_read=msg.is_read,
        metadata=msg.metadata_,
        created_at=msg.created_at,
        updated_at=msg.updated_at,
    )


def _to_thread_read(thread: Thread, last_message: Message | None = None) -> ThreadRead:
    client = thread.client
    client_name = f"{client.first_name} {client.last_name}".strip() if client else "Unknown"
    return ThreadRead(
        id=thread.id,
        subject=thread.subject,
        client_id=thread.client_id,
        client_name=client_name,
        participants=[str(p) for p in (thread.participants or [])],
        status=ThreadStatusEnum(thread.status.value),
        channel=_CHANNEL_STR.get(thread.channel, "in_app"),
        unread_count=thread.unread_count,
        last_message=_to_message_read(last_message) if last_message else None,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
    )


async def list_threads(
    session: AsyncSession,
    pagination: PaginationParams,
    status_filter: str | None = None,
    channel: str | None = None,
    client_id: UUID | None = None,
) -> PaginatedResponse[ThreadRead]:
    query = select(Thread)
    if status_filter:
        try:
            query = query.where(Thread.status == ThreadStatus(status_filter))
        except ValueError:
            pass
    if channel:
        ch = _STR_CHANNEL.get(channel)
        if ch:
            query = query.where(Thread.channel == ch)
    if client_id:
        query = query.where(Thread.client_id == client_id)
    query = query.order_by(Thread.updated_at.desc())
    result = await paginate(session, query, pagination)

    # Load last message for each thread
    thread_ids = [t.id for t in result.items]
    last_messages: dict[UUID, Message] = {}
    if thread_ids:
        msg_result = await session.execute(
            select(Message)
            .where(Message.thread_id.in_(thread_ids))
            .order_by(Message.created_at.desc())
        )
        for msg in msg_result.scalars().all():
            if msg.thread_id not in last_messages:
                last_messages[msg.thread_id] = msg

    result.items = [_to_thread_read(t, last_messages.get(t.id)) for t in result.items]
    return result


async def get_thread(session: AsyncSession, thread_id: UUID) -> ThreadWithMessages:
    result = await session.execute(
        select(Thread)
        .where(Thread.id == thread_id)
        .options(selectinload(Thread.messages))
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    messages = sorted(thread.messages, key=lambda m: m.created_at)
    last_msg = messages[-1] if messages else None
    base = _to_thread_read(thread, last_msg)
    return ThreadWithMessages(**base.model_dump(), messages=[_to_message_read(m) for m in messages])


async def get_thread_messages(session: AsyncSession, thread_id: UUID) -> list[MessageRead]:
    # Verify thread exists
    t_result = await session.execute(select(Thread.id).where(Thread.id == thread_id))
    if t_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    msg_result = await session.execute(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at.asc())
    )
    return [_to_message_read(m) for m in msg_result.scalars().all()]


async def mark_thread_read(session: AsyncSession, thread_id: UUID, user_id: UUID) -> None:
    # Verify thread exists
    t_result = await session.execute(select(Thread).where(Thread.id == thread_id))
    thread = t_result.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    await session.execute(
        update(Message)
        .where(Message.thread_id == thread_id, Message.is_read == False)
        .values(is_read=True)
    )
    thread.unread_count = 0
    session.add(thread)
    await session.flush()


# --------------------------------------------------------------------------- #
# Notification Preferences                                                     #
# --------------------------------------------------------------------------- #

_DEFAULT_EVENTS = [
    ("case_created", "New Case Created"),
    ("case_status_changed", "Case Status Changed"),
    ("document_uploaded", "Document Uploaded"),
    ("appointment_scheduled", "Appointment Scheduled"),
    ("task_assigned", "Task Assigned to You"),
    ("message_received", "New Message Received"),
    ("payment_received", "Payment Received"),
]


async def get_notification_preferences(
    session: AsyncSession, user_id: UUID
) -> list[NotificationPreferenceRead]:
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    saved = {p.event_type: p for p in result.scalars().all()}

    prefs = []
    for event_type, event_label in _DEFAULT_EVENTS:
        pref = saved.get(event_type)
        prefs.append(
            NotificationPreferenceRead(
                event_type=event_type,
                event_label=event_label,
                email_enabled=pref.email_enabled if pref else True,
                sms_enabled=pref.sms_enabled if pref else False,
                in_app_enabled=pref.in_app_enabled if pref else True,
            )
        )
    return prefs


async def update_notification_preferences(
    session: AsyncSession, user_id: UUID, updates: list[NotificationPreferenceUpdate]
) -> list[NotificationPreferenceRead]:
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    saved = {p.event_type: p for p in result.scalars().all()}

    for u in updates:
        pref = saved.get(u.event_type)
        if pref is None:
            pref = NotificationPreference(user_id=user_id, event_type=u.event_type)
            session.add(pref)
        pref.email_enabled = u.email_enabled
        pref.sms_enabled = u.sms_enabled
        pref.in_app_enabled = u.in_app_enabled

    await session.flush()
    return await get_notification_preferences(session, user_id)
