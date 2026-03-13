"use client";

import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  CreditCard,
  Zap,
  HardDrive,
  Users,
  Check,
  ArrowUpRight,
} from "lucide-react";

const planFeatures = [
  "Unlimited clients and cases",
  "AI-powered workflow generation",
  "Document management with OCR",
  "Email and SMS notifications",
  "Team collaboration (up to 10 members)",
  "Custom workflow builder",
  "Advanced reporting and analytics",
  "Priority email support",
];

const usageStats = [
  {
    title: "API Calls",
    used: 12_450,
    limit: 50_000,
    icon: Zap,
    unit: "calls",
  },
  {
    title: "Storage",
    used: 2.4,
    limit: 10,
    icon: HardDrive,
    unit: "GB",
  },
  {
    title: "Team Members",
    used: 5,
    limit: 10,
    icon: Users,
    unit: "members",
  },
];

export default function BillingSettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Billing & Plan"
        description="Manage your subscription, usage, and payment methods"
      />

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CardTitle className="text-base">Current Plan</CardTitle>
              <Badge className="bg-primary text-primary-foreground">Professional</Badge>
            </div>
            <Button variant="outline">
              <ArrowUpRight className="mr-2 h-4 w-4" />
              Upgrade Plan
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold">$99</span>
            <span className="text-sm text-muted-foreground">/ month</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Billed monthly. Next billing date: April 1, 2026
          </p>
          <Separator />
          <div>
            <p className="text-sm font-medium mb-3">Plan Features</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {planFeatures.map((feature) => (
                <div key={feature} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600 shrink-0" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <div>
        <h2 className="text-base font-semibold mb-4">Usage This Month</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {usageStats.map((stat) => {
            const Icon = stat.icon;
            const percentage = Math.round((stat.used / stat.limit) * 100);
            return (
              <Card key={stat.title}>
                <CardContent className="p-6 space-y-3">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{stat.title}</span>
                  </div>
                  <div>
                    <span className="text-2xl font-bold">
                      {typeof stat.used === "number" && stat.used % 1 !== 0
                        ? stat.used.toFixed(1)
                        : stat.used.toLocaleString()}
                    </span>
                    <span className="text-sm text-muted-foreground ml-1">
                      / {typeof stat.limit === "number" && stat.limit % 1 !== 0
                        ? stat.limit.toFixed(1)
                        : stat.limit.toLocaleString()}{" "}
                      {stat.unit}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        percentage > 80
                          ? "bg-red-500"
                          : percentage > 60
                          ? "bg-yellow-500"
                          : "bg-primary"
                      }`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">{percentage}% used</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <CreditCard className="h-4 w-4" />
            Payment Method
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
                <CreditCard className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p className="text-sm font-medium">Visa ending in 4242</p>
                <p className="text-xs text-muted-foreground">Expires 12/2027</p>
              </div>
            </div>
            <Badge variant="outline">Default</Badge>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              Update Payment Method
            </Button>
            <Button variant="outline" size="sm">
              View Billing History
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
