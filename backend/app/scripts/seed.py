"""Seed all roles, permissions, and the initial admin user.

Permission naming convention: ``resource:action`` (colon separator, matching
the frontend ``ROLE_PERMISSIONS`` map in ``src/config/roles.ts``).

Actions used:
  read   — view records
  write  — create or update records
  delete — remove records
  manage — higher-level control (currently: team management)

Resources match the frontend domain names (e.g. ``invoices`` not ``billing``,
``appointments`` not ``scheduling``) so that the same strings can be passed to
``require_permission()`` on backend routes without translation.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import select
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import Permission, Role, User


ADMIN_EMAIL = "admin@migrantsbridge.org"
ADMIN_PASSWORD = "Admin123!"  # Change in production


# All unique permissions that exist across any role.
# Format: "resource:action"  (matches frontend ROLE_PERMISSIONS exactly)
ALL_PERMISSIONS: list[tuple[str, str]] = [
    ("clients", "read"),
    ("clients", "write"),
    ("clients", "delete"),
    ("cases", "read"),
    ("cases", "write"),
    ("cases", "delete"),
    ("documents", "read"),
    ("documents", "write"),
    ("documents", "delete"),
    ("appointments", "read"),
    ("appointments", "write"),
    ("appointments", "delete"),
    ("communications", "read"),
    ("communications", "write"),
    ("invoices", "read"),
    ("invoices", "write"),
    ("invoices", "delete"),
    ("tasks", "read"),
    ("tasks", "write"),
    ("tasks", "delete"),
    ("wealth", "read"),
    ("wealth", "write"),
    ("workflows", "read"),
    ("workflows", "write"),
    ("workflows", "delete"),
    ("reports", "read"),
    ("settings", "read"),
    ("settings", "write"),
    ("team", "manage"),
]

# Role definitions mirror frontend src/config/roles.ts ROLE_PERMISSIONS.
# Each value is a list of "resource:action" strings.
ROLE_DEFINITIONS: dict[str, dict] = {
    "admin": {
        "description": "Full system access",
        "permissions": [f"{r}:{a}" for r, a in ALL_PERMISSIONS],
    },
    "manager": {
        "description": "Manage team, clients, and operations",
        "permissions": [
            "clients:read", "clients:write",
            "cases:read", "cases:write",
            "documents:read", "documents:write",
            "appointments:read", "appointments:write",
            "communications:read", "communications:write",
            "invoices:read", "invoices:write",
            "tasks:read", "tasks:write",
            "wealth:read", "wealth:write",
            "workflows:read", "workflows:write",
            "reports:read",
            "settings:read",
            "team:manage",
        ],
    },
    "caseworker": {
        "description": "Handle cases and client interactions",
        "permissions": [
            "clients:read", "clients:write",
            "cases:read", "cases:write",
            "documents:read", "documents:write",
            "appointments:read", "appointments:write",
            "communications:read", "communications:write",
            "tasks:read", "tasks:write",
            "wealth:read",
        ],
    },
    "intake_specialist": {
        "description": "Process new client intakes",
        "permissions": [
            "clients:read", "clients:write",
            "cases:read", "cases:write",
            "documents:read", "documents:write",
            "appointments:read", "appointments:write",
        ],
    },
    "accountant": {
        "description": "Manage billing and financial records",
        "permissions": [
            "clients:read",
            "invoices:read", "invoices:write",
            "wealth:read", "wealth:write",
            "reports:read",
        ],
    },
    "viewer": {
        "description": "Read-only access",
        "permissions": [
            "clients:read",
            "cases:read",
            "documents:read",
            "appointments:read",
            "tasks:read",
            "reports:read",
        ],
    },
}


async def seed() -> None:
    async with async_session_factory() as session:
        # Idempotency guard: bail if the admin user already exists.
        existing = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        if existing.scalar_one_or_none():
            print(f"Admin user {ADMIN_EMAIL} already exists, skipping seed.")
            return

        # 1. Create all permissions.
        perm_map: dict[str, Permission] = {}
        for resource, action in ALL_PERMISSIONS:
            name = f"{resource}:{action}"
            perm = Permission(resource=resource, action=action, name=name)
            session.add(perm)
            perm_map[name] = perm
        await session.flush()

        # 2. Create all roles and assign their permissions.
        role_map: dict[str, Role] = {}
        for role_name, role_def in ROLE_DEFINITIONS.items():
            role = Role(name=role_name, description=role_def["description"])
            role.permissions = [perm_map[p] for p in role_def["permissions"]]
            session.add(role)
            role_map[role_name] = role
        await session.flush()

        # 3. Create the initial admin user.
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            first_name="Admin",
            last_name="User",
            role_id=role_map["admin"].id,
            is_active=True,
        )
        session.add(admin)
        await session.commit()

        print(f"Seeded admin user: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Created {len(ROLE_DEFINITIONS)} roles: {', '.join(ROLE_DEFINITIONS)}")
        print(f"Created {len(perm_map)} permissions")


if __name__ == "__main__":
    asyncio.run(seed())
