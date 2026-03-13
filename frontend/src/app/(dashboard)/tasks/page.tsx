"use client";

import { useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { KanbanBoard } from "@/components/features/tasks/kanban-board";
import { TaskForm } from "@/components/features/tasks/task-form";
import { useTasks } from "@/hooks/queries/use-tasks";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Plus, List, LayoutGrid, CheckSquare } from "lucide-react";

export default function TasksPage() {
  const { data, isLoading } = useTasks({ page_size: 100 });
  const [createOpen, setCreateOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Tasks"
          description="Manage and track your tasks"
        />
        <LoadingSkeleton variant="card" />
      </div>
    );
  }

  const tasks = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tasks"
        description="Manage and track your tasks"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/tasks/list">
                <List className="mr-2 h-4 w-4" />
                List View
              </Link>
            </Button>
            <Button variant="outline" disabled>
              <LayoutGrid className="mr-2 h-4 w-4" />
              Board View
            </Button>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Task
            </Button>
          </div>
        }
      />

      {tasks.length === 0 ? (
        <EmptyState
          icon={CheckSquare}
          title="No tasks yet"
          description="Create your first task to start tracking work."
          actionLabel="Create Task"
          onAction={() => setCreateOpen(true)}
        />
      ) : (
        <KanbanBoard tasks={tasks} />
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>
          <TaskForm onSuccess={() => setCreateOpen(false)} />
        </DialogContent>
      </Dialog>
    </div>
  );
}
