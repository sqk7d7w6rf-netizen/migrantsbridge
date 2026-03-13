"use client";

import { type Task } from "@/types/task";
import { StatusBadge } from "@/components/shared/status-badge";
import { PRIORITIES, TASK_STATUSES } from "@/lib/constants";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Calendar, CheckCircle2, Circle } from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";
import { useUpdateTask } from "@/hooks/queries/use-tasks";

interface TaskListItemProps {
  task: Task;
}

export function TaskListItem({ task }: TaskListItemProps) {
  const updateTask = useUpdateTask(task.id);

  const toggleComplete = () => {
    const newStatus = task.status === "completed" ? "todo" : "completed";
    updateTask.mutate({ status: newStatus });
  };

  const initials = task.assigned_to_name
    ? task.assigned_to_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : null;

  const isCompleted = task.status === "completed";

  return (
    <div className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 transition-colors">
      <button
        onClick={toggleComplete}
        className="flex-shrink-0 text-muted-foreground hover:text-foreground"
      >
        {isCompleted ? (
          <CheckCircle2 className="h-5 w-5 text-green-500" />
        ) : (
          <Circle className="h-5 w-5" />
        )}
      </button>

      <div className="flex-1 min-w-0">
        <Link
          href={`/tasks/${task.id}`}
          className={`text-sm font-medium hover:underline ${
            isCompleted ? "line-through text-muted-foreground" : ""
          }`}
        >
          {task.title}
        </Link>
        {task.description && (
          <p className="text-xs text-muted-foreground truncate mt-0.5">
            {task.description}
          </p>
        )}
      </div>

      <StatusBadge status={task.priority} statusMap={PRIORITIES} />
      <StatusBadge status={task.status} statusMap={TASK_STATUSES} />

      {task.due_date && (
        <span className="flex items-center gap-1 text-xs text-muted-foreground whitespace-nowrap">
          <Calendar className="h-3 w-3" />
          {format(new Date(task.due_date), "MMM d")}
        </span>
      )}

      {initials && (
        <Avatar className="h-7 w-7">
          <AvatarFallback className="text-[10px]">{initials}</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
