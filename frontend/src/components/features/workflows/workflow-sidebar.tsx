"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { WorkflowStep } from "@/types/workflow";
import {
  CheckSquare,
  Bell,
  Clock,
  FileText,
  GitBranch,
} from "lucide-react";

interface WorkflowSidebarProps {
  selectedStep: WorkflowStep | null;
  onAddStep: (stepType: WorkflowStep["step_type"]) => void;
  onUpdateStep: (stepId: string, updates: Partial<WorkflowStep>) => void;
}

const stepTypes: {
  type: WorkflowStep["step_type"];
  label: string;
  description: string;
  icon: typeof CheckSquare;
}[] = [
  {
    type: "action",
    label: "Action",
    description: "Perform an automated task",
    icon: CheckSquare,
  },
  {
    type: "condition",
    label: "Condition",
    description: "Branch based on a condition",
    icon: GitBranch,
  },
  {
    type: "notification",
    label: "Notification",
    description: "Send a notification",
    icon: Bell,
  },
  {
    type: "delay",
    label: "Delay",
    description: "Wait before continuing",
    icon: Clock,
  },
  {
    type: "approval",
    label: "Approval",
    description: "Require human approval",
    icon: FileText,
  },
];

export function WorkflowSidebar({
  selectedStep,
  onAddStep,
  onUpdateStep,
}: WorkflowSidebarProps) {
  const [stepName, setStepName] = useState(selectedStep?.name || "");
  const [stepDescription, setStepDescription] = useState(
    selectedStep?.description || ""
  );

  const handleSave = () => {
    if (!selectedStep) return;
    onUpdateStep(selectedStep.id, {
      name: stepName,
      description: stepDescription,
    });
  };

  return (
    <div className="w-72 border-l bg-card overflow-y-auto">
      <div className="p-4 space-y-6">
        <div>
          <h3 className="text-sm font-semibold mb-3">Add Step</h3>
          <div className="grid grid-cols-1 gap-2">
            {stepTypes.map((stepType) => {
              const Icon = stepType.icon;
              return (
                <button
                  key={stepType.type}
                  onClick={() => onAddStep(stepType.type)}
                  className="flex items-center gap-3 rounded-md border p-3 text-left hover:bg-accent transition-colors"
                >
                  <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{stepType.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {stepType.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {selectedStep && (
          <>
            <Separator />
            <div>
              <h3 className="text-sm font-semibold mb-3">
                Configure Step
              </h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="step-name">Name</Label>
                  <Input
                    id="step-name"
                    value={stepName}
                    onChange={(e) => setStepName(e.target.value)}
                    placeholder="Step name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="step-type">Type</Label>
                  <Select
                    value={selectedStep.step_type}
                    onValueChange={(value) =>
                      onUpdateStep(selectedStep.id, {
                        step_type: value as WorkflowStep["step_type"],
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {stepTypes.map((st) => (
                        <SelectItem key={st.type} value={st.type}>
                          {st.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="step-description">Description</Label>
                  <Textarea
                    id="step-description"
                    value={stepDescription}
                    onChange={(e) => setStepDescription(e.target.value)}
                    placeholder="Describe what this step does"
                    rows={3}
                  />
                </div>
                <Button onClick={handleSave} className="w-full" size="sm">
                  Save Changes
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
