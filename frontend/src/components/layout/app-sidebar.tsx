"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { navigation } from "@/config/navigation";
import { useSidebarStore } from "@/stores/use-sidebar-store";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export function AppSidebar() {
  const pathname = usePathname();
  const { isCollapsed, toggle } = useSidebarStore();

  return (
    <aside
      className={cn(
        "relative flex h-full flex-col border-r bg-card transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-14 items-center border-b px-4">
        {!isCollapsed && (
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
              MB
            </div>
            <span className="font-semibold text-lg">MigrantsBridge</span>
          </Link>
        )}
        {isCollapsed && (
          <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            MB
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        {navigation.map((section, idx) => (
          <div key={section.title} className="mb-2">
            {!isCollapsed && (
              <p className="mb-1 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {section.title}
              </p>
            )}
            {idx > 0 && isCollapsed && <Separator className="my-2 mx-2" />}
            <ul className="space-y-0.5 px-2">
              {section.items.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/" && pathname.startsWith(item.href));
                return (
                  <li key={item.title}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                        isCollapsed && "justify-center px-2"
                      )}
                      title={isCollapsed ? item.title : undefined}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      {!isCollapsed && <span>{item.title}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <Button
        variant="ghost"
        size="icon"
        className="absolute -right-3 top-16 z-10 h-6 w-6 rounded-full border bg-background shadow-sm"
        onClick={toggle}
      >
        {isCollapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </Button>
    </aside>
  );
}
