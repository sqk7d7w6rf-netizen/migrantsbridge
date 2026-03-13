import {
  LayoutDashboard,
  Users,
  FolderOpen,
  FileText,
  Calendar,
  MessageSquare,
  Receipt,
  BarChart3,
  CheckSquare,
  Landmark,
  GitBranch,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { Permission } from "@/types/user";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  permission?: Permission;
  badge?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const navigation: NavSection[] = [
  {
    title: "Main",
    items: [
      {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
      },
      {
        title: "Clients",
        href: "/clients",
        icon: Users,
        permission: "clients:read",
      },
      {
        title: "Cases",
        href: "/clients",
        icon: FolderOpen,
        permission: "cases:read",
      },
      {
        title: "Documents",
        href: "/documents",
        icon: FileText,
        permission: "documents:read",
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        title: "Scheduling",
        href: "/scheduling",
        icon: Calendar,
        permission: "appointments:read",
      },
      {
        title: "Communications",
        href: "/communications",
        icon: MessageSquare,
        permission: "communications:read",
      },
      {
        title: "Tasks",
        href: "/tasks/list",
        icon: CheckSquare,
        permission: "tasks:read",
      },
    ],
  },
  {
    title: "Finance",
    items: [
      {
        title: "Billing",
        href: "/billing/invoices",
        icon: Receipt,
        permission: "invoices:read",
      },
      {
        title: "Wealth",
        href: "/wealth/goals",
        icon: Landmark,
        permission: "wealth:read",
      },
    ],
  },
  {
    title: "Intelligence",
    items: [
      {
        title: "Reports",
        href: "/reports/clients",
        icon: BarChart3,
        permission: "reports:read",
      },
      {
        title: "Workflows",
        href: "/workflows",
        icon: GitBranch,
        permission: "workflows:read",
      },
      {
        title: "Settings",
        href: "/settings/profile",
        icon: Settings,
        permission: "settings:read",
      },
    ],
  },
];
