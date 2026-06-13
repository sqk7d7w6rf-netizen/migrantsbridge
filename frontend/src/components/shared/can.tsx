"use client";

import { ReactNode } from "react";
import { usePermission } from "@/hooks/use-permission";
import { Permission } from "@/types/user";

interface CanProps {
  /** A single permission, or a list of permissions to check. */
  permission: Permission | Permission[];
  /**
   * When `permission` is a list: "any" (default) requires at least one,
   * "all" requires every permission.
   */
  mode?: "any" | "all";
  /** Rendered when the user lacks the required permission(s). */
  fallback?: ReactNode;
  children: ReactNode;
}

/**
 * Conditionally renders children based on the current user's permissions.
 *
 * Usage:
 *   <Can permission="clients:write"><Button>New client</Button></Can>
 *   <Can permission={["invoices:read", "reports:read"]} mode="any">...</Can>
 *
 * This gates the UI only — the backend independently enforces access.
 */
export function Can({ permission, mode = "any", fallback = null, children }: CanProps) {
  const { can, canAny, canAll } = usePermission();

  const allowed = Array.isArray(permission)
    ? mode === "all"
      ? canAll(permission)
      : canAny(permission)
    : can(permission);

  return <>{allowed ? children : fallback}</>;
}
