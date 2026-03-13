"use client";

import { Workflow, WorkflowStep } from "@/types/workflow";
import { TriggerNode } from "./nodes/trigger-node";
import { ActionNode } from "./nodes/action-node";
import { ConditionNode } from "./nodes/condition-node";
import { ArrowDown } from "lucide-react";

interface WorkflowCanvasProps {
  workflow: Workflow;
  selectedStepId?: string | null;
  onSelectStep?: (stepId: string | null) => void;
  onSelectTrigger?: () => void;
  readOnly?: boolean;
}

function ConnectorArrow() {
  return (
    <div className="flex justify-center py-2">
      <div className="flex flex-col items-center">
        <div className="w-px h-4 bg-border" />
        <ArrowDown className="h-4 w-4 text-muted-foreground" />
      </div>
    </div>
  );
}

function buildStepOrder(steps: WorkflowStep[]): WorkflowStep[] {
  if (steps.length === 0) return [];

  const sorted = [...steps].sort((a, b) => a.order - b.order);
  return sorted;
}

export function WorkflowCanvas({
  workflow,
  selectedStepId,
  onSelectStep,
  onSelectTrigger,
  readOnly = false,
}: WorkflowCanvasProps) {
  const orderedSteps = buildStepOrder(workflow.steps);

  return (
    <div className="flex flex-col items-center py-8 px-4 min-h-[400px]">
      <TriggerNode
        triggerType={workflow.trigger_type}
        config={workflow.trigger_config}
        isSelected={selectedStepId === "trigger"}
        onClick={() => {
          if (!readOnly) {
            onSelectStep?.(null);
            onSelectTrigger?.();
          }
        }}
      />

      {orderedSteps.map((step) => (
        <div key={step.id} className="flex flex-col items-center">
          <ConnectorArrow />
          {step.step_type === "condition" ? (
            <ConditionNode
              step={step}
              isSelected={selectedStepId === step.id}
              onClick={() => !readOnly && onSelectStep?.(step.id)}
            />
          ) : (
            <ActionNode
              step={step}
              isSelected={selectedStepId === step.id}
              onClick={() => !readOnly && onSelectStep?.(step.id)}
            />
          )}
        </div>
      ))}

      {orderedSteps.length === 0 && !readOnly && (
        <div className="mt-8 flex flex-col items-center gap-2">
          <ConnectorArrow />
          <div className="rounded-lg border-2 border-dashed border-muted-foreground/30 p-6 text-center">
            <p className="text-sm text-muted-foreground">
              Add steps from the sidebar to build your workflow
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
