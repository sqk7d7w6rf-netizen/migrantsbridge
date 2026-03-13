"""Communication API routes: templates, notifications, inbox."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.communication import (
    BulkNotificationSend,
    NotificationRead,
    NotificationSend,
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
)
from app.services import communication_service

router = APIRouter()


# --- Templates ---

@router.post("/templates", response_model=TemplateRead, status_code=201)
async def create_template(
    payload: TemplateCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a communication template."""
    return await communication_service.create_template(session, payload)


@router.get("/templates", response_model=PaginatedResponse[TemplateRead])
async def list_templates(
    pagination: PaginationParams = Depends(),
    channel: str | None = None,
    language: str | None = None,
    category: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List communication templates."""
    return await communication_service.list_templates(
        session, pagination, channel, language, category
    )


@router.get("/templates/{template_id}", response_model=TemplateRead)
async def get_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a template by ID."""
    return await communication_service.get_template(session, template_id)


@router.put("/templates/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: UUID,
    payload: TemplateUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a template."""
    return await communication_service.update_template(session, template_id, payload)


@router.delete("/templates/{template_id}", response_model=SuccessResponse)
async def delete_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Deactivate a template."""
    await communication_service.delete_template(session, template_id)
    return SuccessResponse(message="Template deactivated successfully")


# --- Notifications ---

@router.post("/send", response_model=NotificationRead, status_code=201)
async def send_notification(
    payload: NotificationSend,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Send a notification to a recipient."""
    return await communication_service.queue_notification(session, payload, current_user.id)


@router.post("/bulk-send", response_model=list[NotificationRead], status_code=201)
async def bulk_send(
    payload: BulkNotificationSend,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Send notifications to multiple recipients."""
    return await communication_service.queue_bulk_notifications(
        session, payload, current_user.id
    )


@router.get("/inbox", response_model=PaginatedResponse[NotificationRead])
async def get_inbox(
    pagination: PaginationParams = Depends(),
    channel: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get the current user's notification inbox."""
    return await communication_service.list_notifications(
        session, pagination, recipient_id=current_user.id, channel=channel, status_filter=status
    )


@router.get("/notifications/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a notification by ID."""
    return await communication_service.get_notification(session, notification_id)


@router.post("/notifications/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Mark a notification as read."""
    return await communication_service.mark_as_read(session, notification_id)
