"use client";

import Link from "next/link";
import { useWorkflows } from "@/hooks/queries/use-workflows";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import {
  Plus,
  Sparkles,
  GitBranch,
  Zap,
  Clock,
  MousePointerClick,
} from "lucide-react";

const triggerIcons: Record<string, typeof Zap> = {
  manual: MousePointerClick,
  event: Zap,
  schedule: Clock,
};

const triggerLabels: Record<string, string> = {
  manual: "Manual",
  event: "Event",
  schedule: "Scheduled",
};

const statusMap: Record<string, { label: string; color: string }> = {
  true: { label: "Active", color: "bg-green-100 text-green-800" },
  false: { label: "Inactive", color: "bg-gray-100 text-gray-800" },
};

export default function WorkflowsPage() {
  const { data, isLoading } = useWorkflows();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Workflows" description="Automate business processes" />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const workflows = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workflows"
        description="Automate business processes with visual workflows"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/workflows/builder">
                <Plus className="mr-2 h-4 w-4" />
                Create Workflow
              </Link>
            </Button>
            <Button asChild>
              <Link href="/workflows/builder?ai=true">
                <Sparkles className="mr-2 h-4 w-4" />
                AI Generate
              </Link>
            </Button>
          </div>
        }
      />

      {workflows.length === 0 ? (
        <EmptyState
          icon={GitBranch}
          title="No workflows yet"
          description="Create your first workflow to automate business processes, or use AI to generate one from a description."
          actionLabel="Create Workflow"
          onAction={() => {}}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {workflows.map((workflow) => {
            const TriggerIcon = triggerIcons[workflow.trigger_type] || Zap;
            return (
              <Link
                key={workflow.id}
                href={`/workflows/${workflow.id}`}
              >
                <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-base font-semibold line-clamp-1">
                        {workflow.name}
                      </CardTitle>
                      <StatusBadge
                        status={String(workflow.is_active)}
                        statusMap={statusMap}
                      />
                    </div>
                    {workflow.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {workflow.description}
                      </p>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2">
                      <TriggerIcon className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {triggerLabels[workflow.trigger_type]} trigger
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>
                        {workflow.steps.length} step
                        {workflow.steps.length !== 1 ? "s" : ""}
                      </span>
                      <span>
                        {workflow.execution_count ?? 0} execution
                        {(workflow.execution_count ?? 0) !== 1 ? "s" : ""}
                      </span>
                    </div>
                    {workflow.last_executed_at && (
                      <p className="text-xs text-muted-foreground">
                        Last run:{" "}
                        {format(
                          new Date(workflow.last_executed_at),
                          "MMM d, yyyy HH:mm"
                        )}
                      </p>
                    )}
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
