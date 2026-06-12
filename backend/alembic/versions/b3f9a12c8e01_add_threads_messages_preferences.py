"""add communication threads, messages, and notification preferences

Revision ID: b3f9a12c8e01
Revises: 078a7feef9ed
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b3f9a12c8e01"
down_revision: Union[str, None] = "078a7feef9ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "communication_threads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column(
            "channel",
            sa.Enum("email", "sms", "in_app", "push", "whatsapp", name="channeltype", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("open", "closed", "archived", name="threadstatus"),
            nullable=False,
        ),
        sa.Column("participants", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("unread_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_threads_client_id", "communication_threads", ["client_id"])
    op.create_index("ix_communication_threads_created_by_id", "communication_threads", ["created_by_id"])
    op.create_index("ix_communication_threads_status", "communication_threads", ["status"])

    op.create_table(
        "communication_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("thread_id", sa.UUID(), nullable=False),
        sa.Column("sender_id", sa.UUID(), nullable=True),
        sa.Column("sender_name", sa.String(length=255), nullable=False),
        sa.Column(
            "sender_type",
            sa.Enum("staff", "client", "system", name="sendertype"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "channel",
            sa.Enum("email", "sms", "in_app", "push", "whatsapp", name="channeltype", create_type=False),
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["communication_threads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_messages_thread_id", "communication_messages", ["thread_id"])
    op.create_index("ix_communication_messages_sender_id", "communication_messages", ["sender_id"])

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sms_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_table("communication_messages")
    op.drop_table("communication_threads")
    op.execute("DROP TYPE IF EXISTS threadstatus")
    op.execute("DROP TYPE IF EXISTS sendertype")
