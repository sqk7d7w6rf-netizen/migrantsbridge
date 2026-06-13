import { Permission, Role } from "@/types/user";

export const ROLES: Record<Role, { label: string; description: string }> = {
  admin: {
    label: "Administrator",
    description: "Full system access",
  },
  manager: {
    label: "Manager",
    description: "Manage team, clients, and operations",
  },
  caseworker: {
    label: "Caseworker",
    description: "Handle cases and client interactions",
  },
  intake_specialist: {
    label: "Intake Specialist",
    description: "Process new client intakes",
  },
  accountant: {
    label: "Accountant",
    description: "Manage billing and financial records",
  },
  viewer: {
    label: "Viewer",
    description: "Read-only access",
  },
};

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: [
    "clients:read",
    "clients:write",
    "clients:delete",
    "cases:read",
    "cases:write",
    "cases:delete",
    "documents:read",
    "documents:write",
    "documents:delete",
    "appointments:read",
    "appointments:write",
    "appointments:delete",
    "communications:read",
    "communications:write",
    "invoices:read",
    "invoices:write",
    "invoices:delete",
    "tasks:read",
    "tasks:write",
    "tasks:delete",
    "wealth:read",
    "wealth:write",
    "workflows:read",
    "workflows:write",
    "workflows:delete",
    "reports:read",
    "settings:read",
    "settings:write",
    "team:manage",
  ],
  manager: [
    "clients:read",
    "clients:write",
    "cases:read",
    "cases:write",
    "documents:read",
    "documents:write",
    "appointments:read",
    "appointments:write",
    "communications:read",
    "communications:write",
    "invoices:read",
    "invoices:write",
    "tasks:read",
    "tasks:write",
    "wealth:read",
    "wealth:write",
    "workflows:read",
    "workflows:write",
    "reports:read",
    "settings:read",
    "team:manage",
  ],
  caseworker: [
    "clients:read",
    "clients:write",
    "cases:read",
    "cases:write",
    "documents:read",
    "documents:write",
    "appointments:read",
    "appointments:write",
    "communications:read",
    "communications:write",
    "tasks:read",
    "tasks:write",
    "wealth:read",
  ],
  intake_specialist: [
    "clients:read",
    "clients:write",
    "cases:read",
    "cases:write",
    "documents:read",
    "documents:write",
    "appointments:read",
    "appointments:write",
  ],
  accountant: [
    "clients:read",
    "invoices:read",
    "invoices:write",
    "wealth:read",
    "wealth:write",
    "reports:read",
  ],
  viewer: [
    "clients:read",
    "cases:read",
    "documents:read",
    "appointments:read",
    "tasks:read",
    "reports:read",
  ],
};

/**
 * The full set of permissions. `admin` is granted every permission, so its
 * list is the canonical source of truth for "all permissions".
 */
export const ALL_PERMISSIONS: Permission[] = ROLE_PERMISSIONS.admin;

/**
 * Resolve the permissions for a role name as returned by the backend
 * (`/auth/me` sends `role_name`, a plain string).
 *
 * - `admin` always receives every permission (guards against the admin list
 *   drifting out of sync with new permissions).
 * - Unknown / null roles receive no permissions (fail closed) — frontend
 *   checks are a UX layer; the backend remains the real security boundary.
 */
export function getPermissionsForRole(
  role: string | null | undefined
): Permission[] {
  if (!role) return [];
  if (role === "admin") return ALL_PERMISSIONS;
  return ROLE_PERMISSIONS[role as Role] ?? [];
}

/** Pure helper: does this role have the given permission? */
export function roleHasPermission(
  role: string | null | undefined,
  permission: Permission
): boolean {
  return getPermissionsForRole(role).includes(permission);
}
