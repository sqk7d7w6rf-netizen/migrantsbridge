from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# ---- Thread / Message schemas ----


class ThreadStatusEnum(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class SenderTypeEnum(str, Enum):
    STAFF = "staff"
    CLIENT = "client"
    SYSTEM = "system"


class MessageRead(BaseModel):
    id: UUID
    thread_id: UUID
    sender_id: UUID | None = None
    sender_name: str
    sender_type: SenderTypeEnum
    content: str
    channel: str
    is_read: bool
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreadRead(BaseModel):
    id: UUID
    subject: str
    client_id: UUID
    client_name: str
    participants: list[str]
    status: ThreadStatusEnum
    channel: str
    unread_count: int
    last_message: MessageRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreadWithMessages(ThreadRead):
    messages: list[MessageRead] = []


class ThreadCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=500)
    client_id: UUID
    channel: str = "in_app"
    participants: list[str] = Field(default_factory=list)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    channel: str = "in_app"
    sender_type: SenderTypeEnum = SenderTypeEnum.STAFF


# ---- Notification Preference schemas ----


class NotificationPreferenceRead(BaseModel):
    event_type: str
    event_label: str
    email_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool


class NotificationPreferenceUpdate(BaseModel):
    event_type: str
    email_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool


class NotificationPreferencesUpdate(BaseModel):
    preferences: list[NotificationPreferenceUpdate]


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
