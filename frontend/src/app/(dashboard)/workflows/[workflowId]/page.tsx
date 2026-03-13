"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useWorkflow, useExecuteWorkflow, useWorkflowExecutions } from "@/hooks/queries/use-workflows";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { WorkflowCanvas } from "@/components/features/workflows/workflow-canvas";
import { WorkflowMonitor } from "@/components/features/workflows/workflow-monitor";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WorkflowExecution } from "@/types/workflow";
import { format } from "date-fns";
import {
  Pencil,
  Play,
  Clock,
  Zap,
  MousePointerClick,
  GitBranch,
  Activity,
  Settings,
} from "lucide-react";

const statusMap: Record<string, { label: string; color: string }> = {
  true: { label: "Active", color: "bg-green-100 text-green-800" },
  false: { label: "Inactive", color: "bg-gray-100 text-gray-800" },
};

const triggerLabels: Record<string, string> = {
  manual: "Manual",
  event: "Event-based",
  schedule: "Scheduled",
};

const triggerIcons: Record<string, typeof Zap> = {
  manual: MousePointerClick,
  event: Zap,
  schedule: Clock,
};

export default function WorkflowDetailPage() {
  const params = useParams();
  const router = useRouter();
  const workflowId = params.workflowId as string;

  const { data: workflow, isLoading } = useWorkflow(workflowId);
  const executeWorkflow = useExecuteWorkflow(workflowId);
  const { data: executionsData } = useWorkflowExecutions(workflowId);

  const [selectedExecutionId, setSelectedExecutionId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Workflow" description="Loading workflow details..." />
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="space-y-6">
        <PageHeader title="Workflow Not Found" description="The requested workflow could not be found." />
      </div>
    );
  }

  const TriggerIcon = triggerIcons[workflow.trigger_type] || Zap;
  const executions = executionsData?.items ?? [];

  const handleRun = () => {
    executeWorkflow.mutate({});
  };

  const handleSelectExecution = (execution: WorkflowExecution) => {
    setSelectedExecutionId(execution.id);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={workflow.name}
        description={workflow.description}
        actions={
          <div className="flex items-center gap-2">
            <StatusBadge status={String(workflow.is_active)} statusMap={statusMap} />
            <Button variant="outline" asChild>
              <Link href={`/workflows/${workflowId}/edit`}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </Link>
            </Button>
            <Button onClick={handleRun} disabled={executeWorkflow.isPending}>
              <Play className="mr-2 h-4 w-4" />
              {executeWorkflow.isPending ? "Running..." : "Run"}
            </Button>
          </div>
        }
      />

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">
            <GitBranch className="mr-2 h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="executions">
            <Activity className="mr-2 h-4 w-4" />
            Executions
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Trigger Type
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center gap-2">
                <TriggerIcon className="h-4 w-4" />
                <span className="font-semibold">{triggerLabels[workflow.trigger_type]}</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Steps
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{workflow.steps.length}</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Executions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{workflow.execution_count ?? 0}</span>
                {workflow.last_executed_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Last: {format(new Date(workflow.last_executed_at), "MMM d, yyyy HH:mm")}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Workflow Flow</CardTitle>
            </CardHeader>
            <CardContent>
              <WorkflowCanvas workflow={workflow} readOnly />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="executions" className="space-y-4">
          <WorkflowMonitor
            executions={executions}
            onSelectExecution={handleSelectExecution}
            selectedExecutionId={selectedExecutionId}
          />
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Trigger Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Trigger Type</p>
                  <div className="flex items-center gap-2 mt-1">
                    <TriggerIcon className="h-4 w-4" />
                    <span className="text-sm">{triggerLabels[workflow.trigger_type]}</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Status</p>
                  <div className="mt-1">
                    <StatusBadge status={String(workflow.is_active)} statusMap={statusMap} />
                  </div>
                </div>
              </div>
              {Object.keys(workflow.trigger_config).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Configuration</p>
                  <pre className="rounded-md bg-muted p-4 text-sm overflow-auto">
                    {JSON.stringify(workflow.trigger_config, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Name</p>
                <p className="text-sm mt-0.5">{workflow.name}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Description</p>
                <p className="text-sm mt-0.5">{workflow.description || "No description"}</p>
              </div>
              {workflow.created_by_name && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Created By</p>
                  <p className="text-sm mt-0.5">{workflow.created_by_name}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-muted-foreground">Created</p>
                <p className="text-sm mt-0.5">
                  {format(new Date(workflow.created_at), "MMM d, yyyy HH:mm")}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                <p className="text-sm mt-0.5">
                  {format(new Date(workflow.updated_at), "MMM d, yyyy HH:mm")}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
