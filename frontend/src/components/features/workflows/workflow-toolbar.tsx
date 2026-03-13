"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Save, Play, Trash2, Pencil } from "lucide-react";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";

interface WorkflowToolbarProps {
  workflowName: string;
  workflowDescription: string;
  onNameChange: (name: string) => void;
  onDescriptionChange: (description: string) => void;
  onSave: () => void;
  onExecute: () => void;
  onDelete: () => void;
  isSaving?: boolean;
  isExecuting?: boolean;
  isDeleting?: boolean;
}

export function WorkflowToolbar({
  workflowName,
  workflowDescription,
  onNameChange,
  onDescriptionChange,
  onSave,
  onExecute,
  onDelete,
  isSaving = false,
  isExecuting = false,
  isDeleting = false,
}: WorkflowToolbarProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <div className="flex items-center justify-between border-b bg-card px-4 py-3">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-2 flex-1 max-w-lg">
            <Input
              value={workflowName}
              onChange={(e) => onNameChange(e.target.value)}
              className="h-8 text-sm font-semibold"
              placeholder="Workflow name"
              onKeyDown={(e) => e.key === "Enter" && setIsEditing(false)}
              autoFocus
            />
            <Input
              value={workflowDescription}
              onChange={(e) => onDescriptionChange(e.target.value)}
              className="h-8 text-sm"
              placeholder="Description"
              onBlur={() => setIsEditing(false)}
            />
          </div>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="flex items-center gap-2 hover:bg-accent rounded-md px-2 py-1 transition-colors"
          >
            <h2 className="text-sm font-semibold truncate">
              {workflowName || "Untitled Workflow"}
            </h2>
            <Pencil className="h-3 w-3 text-muted-foreground shrink-0" />
          </button>
        )}
        {workflowDescription && !isEditing && (
          <span className="text-xs text-muted-foreground truncate hidden md:block">
            {workflowDescription}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          disabled={isSaving}
        >
          <Save className="mr-2 h-4 w-4" />
          {isSaving ? "Saving..." : "Save"}
        </Button>
        <Button
          variant="default"
          size="sm"
          onClick={onExecute}
          disabled={isExecuting}
        >
          <Play className="mr-2 h-4 w-4" />
          {isExecuting ? "Running..." : "Run"}
        </Button>
        <Button
          variant="destructive"
          size="sm"
          onClick={() => setDeleteOpen(true)}
          disabled={isDeleting}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete Workflow"
        description="Are you sure you want to delete this workflow? This action cannot be undone."
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => {
          setDeleteOpen(false);
          onDelete();
        }}
        loading={isDeleting}
      />
    </div>
  );
}
