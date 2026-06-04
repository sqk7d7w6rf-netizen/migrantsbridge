"use client";

import { format, parseISO, isPast, isToday } from "date-fns";
import { AlertCircle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTasks } from "@/hooks/queries/use-tasks";
import { cn } from "@/lib/utils";
import { type Task } from "@/types/task";

const priorityBorderMap: Record<string, string> = {
  urgent: "border-l-red-400",
  high: "border-l-orange-400",
};

const priorityIconColorMap: Record<string, string> = {
  urgent: "text-red-500",
  high: "text-orange-500",
};

function DueDateLabel({ due_date }: { due_date?: string }) {
  if (!due_date) return null;

  const parsed = parseISO(due_date);

  if (isToday(parsed)) {
    return (
      <span className="flex items-center gap-1 text-orange-600">
        <Clock className="h-3 w-3" />
        Due today
      </span>
    );
  }

  if (isPast(parsed)) {
    return (
      <span className="flex items-center gap-1 text-red-600">
        <Clock className="h-3 w-3" />
        Overdue &middot; {format(parsed, "MMM d")}
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1 text-muted-foreground">
      <Clock className="h-3 w-3" />
      Due {format(parsed, "MMM d")}
    </span>
  );
}

export function UrgentTasks() {
  const { data: urgentData, isLoading: urgentLoading } = useTasks({
    priority: "urgent",
    status: "todo",
    page_size: 5,
  });

  const { data: highData, isLoading: highLoading } = useTasks({
    priority: "high",
    status: "todo",
    page_size: 5,
  });

  const isLoading = urgentLoading || highLoading;

  const tasks: Task[] = [
    ...(urgentData?.items ?? []),
    ...(highData?.items ?? []),
  ].slice(0, 5);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-base">Urgent Tasks</CardTitle>
        {!isLoading && (
          <Badge
            variant={tasks.length > 0 ? "destructive" : "outline"}
            className="text-xs"
          >
            {tasks.length}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-4 w-4 shrink-0 rounded" />
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : tasks.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-6">
            No urgent tasks
          </p>
        ) : (
          <div className="space-y-2">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={cn(
                  "rounded-md border border-l-4 p-3",
                  priorityBorderMap[task.priority] ?? "border-l-gray-300"
                )}
              >
                <div className="flex items-start gap-2">
                  <AlertCircle
                    className={cn(
                      "h-4 w-4 mt-0.5 shrink-0",
                      priorityIconColorMap[task.priority] ??
                        "text-muted-foreground"
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{task.title}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs">
                      {task.client_name && (
                        <span className="text-muted-foreground truncate">
                          {task.client_name}
                        </span>
                      )}
                      {task.client_name && task.due_date && (
                        <span className="text-muted-foreground">&middot;</span>
                      )}
                      <DueDateLabel due_date={task.due_date} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
