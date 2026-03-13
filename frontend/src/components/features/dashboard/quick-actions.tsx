"use client";

import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  UserPlus,
  FolderPlus,
  Calendar,
  FileUp,
  Receipt,
  CheckSquare,
} from "lucide-react";

const actions = [
  {
    label: "New Client",
    icon: UserPlus,
    href: "/clients/new",
  },
  {
    label: "New Case",
    icon: FolderPlus,
    href: "/clients",
  },
  {
    label: "Schedule",
    icon: Calendar,
    href: "/scheduling",
  },
  {
    label: "Upload Doc",
    icon: FileUp,
    href: "/documents",
  },
  {
    label: "New Invoice",
    icon: Receipt,
    href: "/billing/invoices/new",
  },
  {
    label: "Add Task",
    icon: CheckSquare,
    href: "/tasks/list",
  },
];

export function QuickActions() {
  const router = useRouter();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {actions.map((action) => (
            <Button
              key={action.label}
              variant="outline"
              className="h-auto flex-col gap-2 py-4"
              onClick={() => router.push(action.href)}
            >
              <action.icon className="h-5 w-5" />
              <span className="text-xs">{action.label}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
