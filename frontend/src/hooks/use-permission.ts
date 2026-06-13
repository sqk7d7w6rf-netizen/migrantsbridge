"use client";

import { useCallback, useMemo } from "react";
import { useAuthStore } from "@/stores/use-auth-store";
import { getPermissionsForRole } from "@/config/roles";
import { Permission } from "@/types/user";

/**
 * Permission hook — the real RBAC enforcement layer the app was missing.
 *
 * Permissions are derived from the current user's `role_name` (returned by
 * `/auth/me`) using the ROLE_PERMISSIONS map. Note this is a UX convenience:
 * it hides/disables controls the user can't use. The backend still enforces
 * every permission on the API — never treat the frontend as the security
 * boundary.
 */
export function usePermission() {
  const user = useAuthStore((state) => state.user);

  const permissions = useMemo(
    () => getPermissionsForRole(user?.role_name),
    [user?.role_name]
  );

  const permissionSet = useMemo(() => new Set(permissions), [permissions]);

  /** True if the user has the given permission. */
  const can = useCallback(
    (permission: Permission) => permissionSet.has(permission),
    [permissionSet]
  );

  /** True if the user has at least one of the given permissions. */
  const canAny = useCallback(
    (perms: Permission[]) => perms.some((p) => permissionSet.has(p)),
    [permissionSet]
  );

  /** True if the user has all of the given permissions. */
  const canAll = useCallback(
    (perms: Permission[]) => perms.every((p) => permissionSet.has(p)),
    [permissionSet]
  );

  return {
    role: user?.role_name ?? null,
    permissions,
    can,
    canAny,
    canAll,
  };
}
