import apiClient from "@/lib/api-client";

export interface DashboardKPIs {
  active_clients: number;
  active_clients_change: number;
  active_cases: number;
  active_cases_change: number;
  pending_tasks: number;
  pending_tasks_change: number;
  monthly_revenue: number;
  monthly_revenue_change: number;
}

export interface ActivityItem {
  id: string;
  type: "client" | "case" | "document" | "task" | "payment" | "appointment";
  action: string;
  description: string;
  user_name: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export const dashboardService = {
  async getKPIs(): Promise<DashboardKPIs> {
    const { data } = await apiClient.get("/dashboard/kpis");
    return data;
  },

  async getRecentActivity(limit?: number): Promise<ActivityItem[]> {
    const { data } = await apiClient.get("/dashboard/activity", {
      params: { limit: limit || 10 },
    });
    return data;
  },
};
