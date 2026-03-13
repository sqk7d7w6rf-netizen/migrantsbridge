import { TimestampMixin } from "./common";

export type Role =
  | "admin"
  | "manager"
  | "caseworker"
  | "intake_specialist"
  | "accountant"
  | "viewer";

export type Permission =
  | "clients:read"
  | "clients:write"
  | "clients:delete"
  | "cases:read"
  | "cases:write"
  | "cases:delete"
  | "documents:read"
  | "documents:write"
  | "documents:delete"
  | "appointments:read"
  | "appointments:write"
  | "appointments:delete"
  | "communications:read"
  | "communications:write"
  | "invoices:read"
  | "invoices:write"
  | "invoices:delete"
  | "tasks:read"
  | "tasks:write"
  | "tasks:delete"
  | "wealth:read"
  | "wealth:write"
  | "workflows:read"
  | "workflows:write"
  | "workflows:delete"
  | "reports:read"
  | "settings:read"
  | "settings:write"
  | "team:manage";

export interface User extends TimestampMixin {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  permissions: Permission[];
  is_active: boolean;
  avatar_url?: string;
  phone?: string;
}
