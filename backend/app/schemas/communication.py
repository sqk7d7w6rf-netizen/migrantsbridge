from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class TemplateCreate(BaseModel):
    """Create a communication template."""

    name: str = Field(min_length=1, max_length=255)
    subject: str | None = Field(default=None, max_length=500)
    body: str = Field(min_length=1)
    channel: NotificationChannel
    language: str = Field(default="en", max_length=10)
    category: str | None = Field(default=None, max_length=100)
    variables: list[str] = Field(default_factory=list, description="Template variable names")


class TemplateRead(BaseModel):
    """Template read response."""

    id: UUID
    name: str
    subject: str | None = None
    body: str
    channel: NotificationChannel
    language: str
    category: str | None = None
    variables: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateUpdate(BaseModel):
    """Update a template."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = None
    body: str | None = None
    channel: NotificationChannel | None = None
    language: str | None = None
    category: str | None = None
    variables: list[str] | None = None
    is_active: bool | None = None


class NotificationSend(BaseModel):
    """Send a notification."""

    recipient_id: UUID
    template_id: UUID | None = None
    channel: NotificationChannel
    subject: str | None = None
    body: str | None = None
    context: dict[str, Any] = Field(default_factory=dict, description="Template rendering context")
    scheduled_at: datetime | None = None


class BulkNotificationSend(BaseModel):
    """Send notifications to multiple recipients."""

    recipient_ids: list[UUID] = Field(min_length=1)
    template_id: UUID
    channel: NotificationChannel
    context: dict[str, Any] = Field(default_factory=dict)


class NotificationRead(BaseModel):
    """Notification read response."""

    id: UUID
    recipient_id: UUID
    channel: NotificationChannel
    subject: str | None = None
    body: str
    status: NotificationStatus
    template_id: UUID | None = None
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
