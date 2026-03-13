"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { WorkflowExecution } from "@/types/workflow";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  AlertCircle,
  ChevronRight,
} from "lucide-react";

interface ExecutionStepLog {
  step_id: string;
  step_name: string;
  status: "completed" | "failed" | "running" | "pending";
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

interface WorkflowMonitorProps {
  executions: WorkflowExecution[];
  onSelectExecution?: (execution: WorkflowExecution) => void;
  selectedExecutionId?: string | null;
  stepLogs?: ExecutionStepLog[];
}

const statusConfig: Record<
  string,
  { icon: typeof CheckCircle2; color: string; label: string }
> = {
  completed: {
    icon: CheckCircle2,
    color: "text-green-600",
    label: "Completed",
  },
  failed: { icon: XCircle, color: "text-red-600", label: "Failed" },
  running: { icon: Loader2, color: "text-blue-600", label: "Running" },
  cancelled: {
    icon: AlertCircle,
    color: "text-yellow-600",
    label: "Cancelled",
  },
  pending: { icon: Clock, color: "text-muted-foreground", label: "Pending" },
};

export function WorkflowMonitor({
  executions,
  onSelectExecution,
  selectedExecutionId,
  stepLogs,
}: WorkflowMonitorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Execution Monitor</CardTitle>
      </CardHeader>
      <CardContent>
        {executions.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No executions yet. Run the workflow to see execution history.
          </p>
        ) : (
          <div className="flex gap-4">
            <div className="w-1/2 space-y-2 max-h-[400px] overflow-y-auto">
              {executions.map((execution) => {
                const config = statusConfig[execution.status];
                const Icon = config?.icon || Clock;
                return (
                  <button
                    key={execution.id}
                    onClick={() => onSelectExecution?.(execution)}
                    className={cn(
                      "flex items-center gap-3 w-full rounded-md border p-3 text-left transition-colors hover:bg-accent",
                      selectedExecutionId === execution.id && "bg-accent border-primary"
                    )}
                  >
                    <Icon
                      className={cn(
                        "h-4 w-4 shrink-0",
                        config?.color,
                        execution.status === "running" && "animate-spin"
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">
                        {format(
                          new Date(execution.started_at),
                          "MMM d, HH:mm:ss"
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {config?.label}
                        {execution.triggered_by_name &&
                          ` by ${execution.triggered_by_name}`}
                      </p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
                  </button>
                );
              })}
            </div>

            <div className="w-1/2 border-l pl-4">
              {selectedExecutionId && stepLogs ? (
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold">Step Progress</h4>
                  <div className="space-y-2">
                    {stepLogs.map((log) => {
                      const config = statusConfig[log.status];
                      const Icon = config?.icon || Clock;
                      return (
                        <div
                          key={log.step_id}
                          className="flex items-start gap-3 rounded-md border p-2"
                        >
                          <Icon
                            className={cn(
                              "h-4 w-4 shrink-0 mt-0.5",
                              config?.color,
                              log.status === "running" && "animate-spin"
                            )}
                          />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium">
                              {log.step_name}
                            </p>
                            {log.started_at && (
                              <p className="text-xs text-muted-foreground">
                                {format(
                                  new Date(log.started_at),
                                  "HH:mm:ss"
                                )}
                                {log.completed_at &&
                                  ` - ${format(new Date(log.completed_at), "HH:mm:ss")}`}
                              </p>
                            )}
                            {log.error_message && (
                              <p className="text-xs text-red-600 mt-0.5">
                                {log.error_message}
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                  Select an execution to view step details
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
