import { TimestampMixin } from "./common";

export interface WorkflowStep {
  id: string;
  workflow_id: string;
  name: string;
  description?: string;
  step_type: "action" | "condition" | "delay" | "notification" | "approval";
  config: Record<string, unknown>;
  order: number;
  next_step_id?: string;
  condition_true_step_id?: string;
  condition_false_step_id?: string;
}

export interface Workflow extends TimestampMixin {
  id: string;
  name: string;
  description?: string;
  trigger_type: "manual" | "event" | "schedule";
  trigger_config: Record<string, unknown>;
  is_active: boolean;
  is_template: boolean;
  created_by: string;
  created_by_name?: string;
  steps: WorkflowStep[];
  execution_count?: number;
  last_executed_at?: string;
}

export interface WorkflowExecution extends TimestampMixin {
  id: string;
  workflow_id: string;
  workflow_name?: string;
  status: "running" | "completed" | "failed" | "cancelled";
  started_at: string;
  completed_at?: string;
  triggered_by: string;
  triggered_by_name?: string;
  context: Record<string, unknown>;
  current_step_id?: string;
  error_message?: string;
}
