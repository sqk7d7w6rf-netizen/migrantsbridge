import apiClient from "@/lib/api-client";
import { Workflow, WorkflowStep, WorkflowExecution } from "@/types/workflow";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface WorkflowCreate {
  name: string;
  description?: string;
  trigger_type: Workflow["trigger_type"];
  trigger_config: Record<string, unknown>;
  is_active?: boolean;
  is_template?: boolean;
  steps: Omit<WorkflowStep, "id" | "workflow_id">[];
}

export interface WorkflowUpdate {
  name?: string;
  description?: string;
  trigger_type?: Workflow["trigger_type"];
  trigger_config?: Record<string, unknown>;
  is_active?: boolean;
  steps?: Omit<WorkflowStep, "id" | "workflow_id">[];
}

export interface WorkflowGenerateRequest {
  description: string;
  context?: Record<string, unknown>;
}

export interface WorkflowExecuteRequest {
  context?: Record<string, unknown>;
  triggered_by?: string;
}

export interface RoutingRule {
  id: string;
  workflow_id: string;
  name: string;
  condition: Record<string, unknown>;
  target_step_id: string;
  priority: number;
  is_active: boolean;
}

export interface RoutingRuleCreate {
  workflow_id: string;
  name: string;
  condition: Record<string, unknown>;
  target_step_id: string;
  priority: number;
}

export interface AiSuggestion {
  id: string;
  workflow_name: string;
  description: string;
  trigger_type: Workflow["trigger_type"];
  steps: Omit<WorkflowStep, "id" | "workflow_id">[];
  confidence: number;
}

export const workflowsService = {
  async getWorkflows(
    params?: PaginationParams & { is_template?: boolean }
  ): Promise<PaginatedResponse<Workflow>> {
    const { data } = await apiClient.get("/workflows", { params });
    return data;
  },

  async getWorkflow(id: string): Promise<Workflow> {
    const { data } = await apiClient.get(`/workflows/${id}`);
    return data;
  },

  async createWorkflow(payload: WorkflowCreate): Promise<Workflow> {
    const { data } = await apiClient.post("/workflows", payload);
    return data;
  },

  async updateWorkflow(
    id: string,
    payload: WorkflowUpdate
  ): Promise<Workflow> {
    const { data } = await apiClient.patch(`/workflows/${id}`, payload);
    return data;
  },

  async deleteWorkflow(id: string): Promise<void> {
    await apiClient.delete(`/workflows/${id}`);
  },

  async generateWorkflow(
    payload: WorkflowGenerateRequest
  ): Promise<AiSuggestion> {
    const { data } = await apiClient.post("/workflows/generate", payload);
    return data;
  },

  async executeWorkflow(
    id: string,
    payload?: WorkflowExecuteRequest
  ): Promise<WorkflowExecution> {
    const { data } = await apiClient.post(
      `/workflows/${id}/execute`,
      payload
    );
    return data;
  },

  async getExecutions(
    workflowId: string,
    params?: PaginationParams
  ): Promise<PaginatedResponse<WorkflowExecution>> {
    const { data } = await apiClient.get(
      `/workflows/${workflowId}/executions`,
      { params }
    );
    return data;
  },

  async getExecution(
    workflowId: string,
    executionId: string
  ): Promise<WorkflowExecution> {
    const { data } = await apiClient.get(
      `/workflows/${workflowId}/executions/${executionId}`
    );
    return data;
  },

  async getTemplates(): Promise<Workflow[]> {
    const { data } = await apiClient.get("/workflows/templates");
    return data;
  },

  async cloneTemplate(templateId: string): Promise<Workflow> {
    const { data } = await apiClient.post(
      `/workflows/templates/${templateId}/clone`
    );
    return data;
  },

  async getRoutingRules(workflowId: string): Promise<RoutingRule[]> {
    const { data } = await apiClient.get(
      `/workflows/${workflowId}/routing-rules`
    );
    return data;
  },

  async createRoutingRule(payload: RoutingRuleCreate): Promise<RoutingRule> {
    const { data } = await apiClient.post(
      `/workflows/${payload.workflow_id}/routing-rules`,
      payload
    );
    return data;
  },

  async deleteRoutingRule(
    workflowId: string,
    ruleId: string
  ): Promise<void> {
    await apiClient.delete(
      `/workflows/${workflowId}/routing-rules/${ruleId}`
    );
  },
};
