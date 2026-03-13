"use client";

import { useState, useMemo } from "react";
import {
  DndContext,
  type DragEndEvent,
  type DragOverEvent,
  DragOverlay,
  type DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from "@dnd-kit/core";
import { type Task } from "@/types/task";
import { type TaskStatus } from "@/types/common";
import { KanbanColumn } from "./kanban-column";
import { KanbanCard } from "./kanban-card";
import { useUpdateTask } from "@/hooks/queries/use-tasks";

interface KanbanBoardProps {
  tasks: Task[];
}

const COLUMNS: {
  id: TaskStatus;
  title: string;
  color: string;
}[] = [
  { id: "todo", title: "To Do", color: "bg-gray-400" },
  { id: "in_progress", title: "In Progress", color: "bg-blue-400" },
  { id: "completed", title: "Completed", color: "bg-green-400" },
  { id: "cancelled", title: "Cancelled", color: "bg-red-400" },
];

export function KanbanBoard({ tasks }: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [localTasks, setLocalTasks] = useState<Task[]>(tasks);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    })
  );

  // Keep localTasks in sync when tasks prop changes
  useMemo(() => {
    setLocalTasks(tasks);
  }, [tasks]);

  const tasksByStatus = useMemo(() => {
    const grouped: Record<string, Task[]> = {};
    for (const col of COLUMNS) {
      grouped[col.id] = localTasks.filter((t) => t.status === col.id);
    }
    return grouped;
  }, [localTasks]);

  const updateTaskMutation = useUpdateTask(activeTask?.id ?? "");

  const handleDragStart = (event: DragStartEvent) => {
    const task = localTasks.find((t) => t.id === event.active.id);
    if (task) setActiveTask(task);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeTaskItem = localTasks.find((t) => t.id === activeId);
    if (!activeTaskItem) return;

    // Determine target column
    let targetStatus: string | undefined;

    // Check if dropped over a column directly
    const isColumn = COLUMNS.some((c) => c.id === overId);
    if (isColumn) {
      targetStatus = overId;
    } else {
      // Dropped over another task - find its column
      const overTask = localTasks.find((t) => t.id === overId);
      if (overTask) {
        targetStatus = overTask.status;
      }
    }

    if (targetStatus && targetStatus !== activeTaskItem.status) {
      setLocalTasks((prev) =>
        prev.map((t) =>
          t.id === activeId ? { ...t, status: targetStatus as TaskStatus } : t
        )
      );
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active } = event;
    const task = localTasks.find((t) => t.id === active.id);

    if (task && activeTask && task.status !== activeTask.status) {
      updateTaskMutation.mutate({ status: task.status });
    }

    setActiveTask(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-4 gap-4">
        {COLUMNS.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            tasks={tasksByStatus[column.id] || []}
            color={column.color}
          />
        ))}
      </div>

      <DragOverlay>
        {activeTask ? <KanbanCard task={activeTask} /> : null}
      </DragOverlay>
    </DndContext>
  );
}
