"use client";

import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

const clientTabs = [
  { label: "Overview", href: "" },
  { label: "Cases", href: "/cases" },
  { label: "Documents", href: "/documents" },
  { label: "Billing", href: "/billing" },
  { label: "Communications", href: "/communications" },
];

export default function ClientDetailLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const clientId = params.clientId as string;
  const basePath = `/clients/${clientId}`;

  const activeTab =
    clientTabs.find(
      (tab) =>
        tab.href !== "" && pathname.startsWith(basePath + tab.href)
    )?.href ?? "";

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} className="w-full">
        <TabsList>
          {clientTabs.map((tab) => (
            <TabsTrigger key={tab.href} value={tab.href} asChild>
              <Link href={basePath + tab.href}>{tab.label}</Link>
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
      {children}
    </div>
  );
}
