"""Seed initial data: admin role and first admin user.

Idempotent — safe to run on every deploy:

    python -m app.initial_data

Reads FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD from the environment / .env.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.config import settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import Role, User

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("initial_data")


async def seed() -> None:
    if not settings.FIRST_ADMIN_EMAIL or not settings.FIRST_ADMIN_PASSWORD:
        logger.warning(
            "FIRST_ADMIN_EMAIL / FIRST_ADMIN_PASSWORD not set — skipping admin seed"
        )
        return

    async with async_session_factory() as session:
        # Admin role
        result = await session.execute(select(Role).where(Role.name == "admin"))
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(name="admin", description="Full administrative access")
            session.add(role)
            await session.flush()
            logger.info("Created role 'admin'")

        # First admin user
        result = await session.execute(
            select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                email=settings.FIRST_ADMIN_EMAIL,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                first_name="Admin",
                last_name="User",
                role_id=role.id,
                is_active=True,
            )
            session.add(user)
            logger.info("Created admin user %s", settings.FIRST_ADMIN_EMAIL)
        elif user.role_id is None:
            user.role_id = role.id
            logger.info("Assigned admin role to existing user %s", user.email)
        else:
            logger.info("Admin user %s already exists — nothing to do", user.email)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
