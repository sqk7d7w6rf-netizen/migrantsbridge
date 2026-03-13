"use client";

import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import {
  User,
  Users,
  Plug,
  CreditCard,
  ChevronRight,
} from "lucide-react";

const settingsCards = [
  {
    title: "Profile",
    description: "Manage your personal information, password, and preferences",
    icon: User,
    href: "/settings/profile",
  },
  {
    title: "Team",
    description: "Manage team members, roles, and invite new collaborators",
    icon: Users,
    href: "/settings/team",
  },
  {
    title: "Integrations",
    description: "Connect external services like email, SMS, storage, and AI",
    icon: Plug,
    href: "/settings/integrations",
  },
  {
    title: "Billing",
    description: "View your plan, usage, and manage payment methods",
    icon: CreditCard,
    href: "/settings/billing",
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your account, team, and application preferences"
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {settingsCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link key={card.href} href={card.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                <CardContent className="flex items-center gap-4 p-6">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold">{card.title}</h3>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      {card.description}
                    </p>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
