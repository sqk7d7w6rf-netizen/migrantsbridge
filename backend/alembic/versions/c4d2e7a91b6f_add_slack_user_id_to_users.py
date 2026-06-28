"""add slack_user_id to users

Revision ID: c4d2e7a91b6f
Revises: b3f9a12c8e01
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d2e7a91b6f"
down_revision: Union[str, None] = "b3f9a12c8e01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("slack_user_id", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "slack_user_id")
