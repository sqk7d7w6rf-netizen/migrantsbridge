import apiClient from "@/lib/api-client";
import { Task, TaskComment } from "@/types/task";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface TaskCreate {
  title: string;
  description?: string;
  status?: string;
  priority: string;
  assigned_to?: string;
  client_id?: string;
  case_id?: string;
  due_date?: string;
  estimated_hours?: number;
  tags?: string[];
}

export interface TaskUpdate extends Partial<TaskCreate> {
  completed_at?: string;
}

export interface TaskFilters extends PaginationParams {
  status?: string;
  priority?: string;
  assigned_to?: string;
  case_id?: string;
  due_before?: string;
  due_after?: string;
}

export interface TeamWorkload {
  user_id: string;
  user_name: string;
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  overdue_tasks: number;
}

export const tasksService = {
  async getTasks(params?: TaskFilters): Promise<PaginatedResponse<Task>> {
    const { data } = await apiClient.get("/tasks", { params });
    return data;
  },

  async getTask(id: string): Promise<Task> {
    const { data } = await apiClient.get(`/tasks/${id}`);
    return data;
  },

  async createTask(payload: TaskCreate): Promise<Task> {
    const { data } = await apiClient.post("/tasks", payload);
    return data;
  },

  async updateTask(id: string, payload: TaskUpdate): Promise<Task> {
    const { data } = await apiClient.patch(`/tasks/${id}`, payload);
    return data;
  },

  async deleteTask(id: string): Promise<void> {
    await apiClient.delete(`/tasks/${id}`);
  },

  async assignTask(id: string, userId: string): Promise<Task> {
    const { data } = await apiClient.post(`/tasks/${id}/assign`, {
      assigned_to: userId,
    });
    return data;
  },

  async getMyTasks(params?: TaskFilters): Promise<PaginatedResponse<Task>> {
    const { data } = await apiClient.get("/tasks/my-tasks", { params });
    return data;
  },

  async addComment(
    taskId: string,
    content: string
  ): Promise<TaskComment> {
    const { data } = await apiClient.post(`/tasks/${taskId}/comments`, {
      content,
    });
    return data;
  },

  async getWorkload(): Promise<TeamWorkload[]> {
    const { data } = await apiClient.get("/tasks/workload");
    return data;
  },
};
