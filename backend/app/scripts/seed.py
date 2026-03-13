"""Seed the database with an admin role and user."""

import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import select
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import Permission, Role, User


ADMIN_EMAIL = "admin@migrantsbridge.org"
ADMIN_PASSWORD = "Admin123!"  # Change in production

RESOURCES = [
    "clients", "cases", "documents", "billing", "scheduling",
    "communications", "tasks", "workflows", "reports", "settings", "users",
]
ACTIONS = ["create", "read", "update", "delete"]


async def seed() -> None:
    async with async_session_factory() as session:
        # Check if admin already exists
        existing = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        if existing.scalar_one_or_none():
            print(f"Admin user {ADMIN_EMAIL} already exists, skipping seed.")
            return

        # Create permissions
        permissions: list[Permission] = []
        for resource in RESOURCES:
            for action in ACTIONS:
                perm = Permission(resource=resource, action=action, name=f"{resource}.{action}")
                session.add(perm)
                permissions.append(perm)
        await session.flush()

        # Create admin role with all permissions
        admin_role = Role(name="admin", description="Full system administrator")
        admin_role.permissions = permissions
        session.add(admin_role)
        await session.flush()

        # Create staff role with read + limited write
        staff_role = Role(name="staff", description="Staff member")
        staff_perms = [p for p in permissions if p.action in ("create", "read", "update")]
        staff_role.permissions = staff_perms
        session.add(staff_role)
        await session.flush()

        # Create admin user
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin)
        await session.commit()

        print(f"Seeded admin user: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Created roles: admin, staff")
        print(f"Created {len(permissions)} permissions")


if __name__ == "__main__":
    asyncio.run(seed())
