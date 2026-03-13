"use client";

import { useState, useCallback, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useWorkflow, useUpdateWorkflow } from "@/hooks/queries/use-workflows";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { WorkflowToolbar } from "@/components/features/workflows/workflow-toolbar";
import { WorkflowCanvas } from "@/components/features/workflows/workflow-canvas";
import { WorkflowSidebar } from "@/components/features/workflows/workflow-sidebar";
import { AiSuggestionsPanel } from "@/components/features/workflows/ai-suggestions-panel";
import { Button } from "@/components/ui/button";
import { Workflow, WorkflowStep } from "@/types/workflow";
import { AiSuggestion } from "@/services/workflows.service";
import { useGenerateWorkflow, useDeleteWorkflow } from "@/hooks/queries/use-workflows";
import { Sparkles, PanelRightClose, PanelRightOpen } from "lucide-react";

function generateId() {
  return `step-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export default function WorkflowEditPage() {
  const params = useParams();
  const router = useRouter();
  const workflowId = params.workflowId as string;

  const { data: existingWorkflow, isLoading } = useWorkflow(workflowId);
  const updateWorkflow = useUpdateWorkflow(workflowId);
  const deleteWorkflow = useDeleteWorkflow();
  const generateWorkflow = useGenerateWorkflow();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [triggerType, setTriggerType] = useState<Workflow["trigger_type"]>("manual");
  const [triggerConfig, setTriggerConfig] = useState<Record<string, unknown>>({});
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [aiPanelOpen, setAiPanelOpen] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<AiSuggestion | null>(null);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (existingWorkflow && !initialized) {
      setName(existingWorkflow.name);
      setDescription(existingWorkflow.description ?? "");
      setTriggerType(existingWorkflow.trigger_type);
      setTriggerConfig(existingWorkflow.trigger_config);
      setSteps(existingWorkflow.steps);
      setInitialized(true);
    }
  }, [existingWorkflow, initialized]);

  const workflow: Workflow = {
    id: workflowId,
    name,
    description,
    trigger_type: triggerType,
    trigger_config: triggerConfig,
    is_active: existingWorkflow?.is_active ?? false,
    is_template: existingWorkflow?.is_template ?? false,
    created_by: existingWorkflow?.created_by ?? "",
    steps,
    created_at: existingWorkflow?.created_at ?? new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const selectedStep = steps.find((s) => s.id === selectedStepId) ?? null;

  const handleAddStep = useCallback(
    (stepType: WorkflowStep["step_type"]) => {
      const newStep: WorkflowStep = {
        id: generateId(),
        workflow_id: workflowId,
        name: `New ${stepType.charAt(0).toUpperCase() + stepType.slice(1)}`,
        description: "",
        step_type: stepType,
        config: {},
        order: steps.length,
      };
      setSteps((prev) => [...prev, newStep]);
      setSelectedStepId(newStep.id);
    },
    [steps.length, workflowId]
  );

  const handleUpdateStep = useCallback(
    (stepId: string, updates: Partial<WorkflowStep>) => {
      setSteps((prev) =>
        prev.map((s) => (s.id === stepId ? { ...s, ...updates } : s))
      );
    },
    []
  );

  const handleSave = async () => {
    await updateWorkflow.mutateAsync({
      name,
      description,
      trigger_type: triggerType,
      trigger_config: triggerConfig,
      steps: steps.map(({ id, workflow_id, ...rest }) => rest),
    });
    router.push(`/workflows/${workflowId}`);
  };

  const handleExecute = () => {
    handleSave();
  };

  const handleDelete = async () => {
    await deleteWorkflow.mutateAsync(workflowId);
    router.push("/workflows");
  };

  const handleGenerate = (desc: string) => {
    generateWorkflow.mutate(
      { description: desc },
      {
        onSuccess: (data) => {
          setAiSuggestion(data);
        },
      }
    );
  };

  const handleApplySuggestion = (suggestion: AiSuggestion) => {
    setName(suggestion.workflow_name);
    setDescription(suggestion.description);
    setTriggerType(suggestion.trigger_type);
    const newSteps: WorkflowStep[] = suggestion.steps.map((step, index) => ({
      ...step,
      id: generateId(),
      workflow_id: workflowId,
      order: index,
    }));
    setSteps(newSteps);
    setSelectedStepId(null);
    setAiSuggestion(null);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Edit Workflow" description="Loading workflow..." />
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (!existingWorkflow) {
    return (
      <div className="space-y-6">
        <PageHeader title="Workflow Not Found" description="The requested workflow could not be found." />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <WorkflowToolbar
        workflowName={name}
        workflowDescription={description}
        onNameChange={setName}
        onDescriptionChange={setDescription}
        onSave={handleSave}
        onExecute={handleExecute}
        onDelete={handleDelete}
        isSaving={updateWorkflow.isPending}
        isDeleting={deleteWorkflow.isPending}
      />

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-auto relative">
          <WorkflowCanvas
            workflow={workflow}
            selectedStepId={selectedStepId}
            onSelectStep={setSelectedStepId}
          />

          <div className="absolute top-4 right-4 z-10">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAiPanelOpen(!aiPanelOpen)}
            >
              {aiPanelOpen ? (
                <PanelRightClose className="mr-2 h-4 w-4" />
              ) : (
                <PanelRightOpen className="mr-2 h-4 w-4" />
              )}
              <Sparkles className="mr-1 h-4 w-4" />
              AI
            </Button>
          </div>

          {aiPanelOpen && (
            <div className="absolute top-14 right-4 w-96 z-10">
              <AiSuggestionsPanel
                onGenerate={handleGenerate}
                onApply={handleApplySuggestion}
                suggestion={aiSuggestion}
                isGenerating={generateWorkflow.isPending}
              />
            </div>
          )}
        </div>

        <WorkflowSidebar
          selectedStep={selectedStep}
          onAddStep={handleAddStep}
          onUpdateStep={handleUpdateStep}
        />
      </div>
    </div>
  );
}
