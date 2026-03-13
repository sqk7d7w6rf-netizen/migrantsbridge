import apiClient from "@/lib/api-client";
import { FinancialGoal, SavingsProgram, Investment, Asset } from "@/types/goal";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface WealthDashboard {
  total_savings: number;
  total_investments: number;
  net_worth: number;
  active_goals_count: number;
  savings_change: number;
  investments_change: number;
  net_worth_change: number;
  savings_history: { date: string; balance: number }[];
  investment_allocation: { type: string; value: number; percentage: number }[];
  recent_transactions: {
    id: string;
    date: string;
    description: string;
    amount: number;
    type: "credit" | "debit";
    category: string;
  }[];
}

export interface GoalCreate {
  name: string;
  description?: string;
  target_amount: number;
  target_date: string;
  category: FinancialGoal["category"];
  client_id?: string;
}

export interface GoalUpdate {
  name?: string;
  description?: string;
  target_amount?: number;
  current_amount?: number;
  target_date?: string;
  status?: FinancialGoal["status"];
  category?: FinancialGoal["category"];
}

export interface GoalMilestone {
  id: string;
  goal_id: string;
  title: string;
  target_amount: number;
  reached_at?: string;
  is_reached: boolean;
}

export interface GoalTransaction {
  id: string;
  goal_id: string;
  amount: number;
  type: "deposit" | "withdrawal";
  date: string;
  notes?: string;
}

export interface SavingsProgramCreate {
  client_id: string;
  goal_id?: string;
  name: string;
  contribution_amount: number;
  frequency: SavingsProgram["frequency"];
  start_date: string;
  end_date?: string;
}

export interface InvestmentCreate {
  client_id: string;
  name: string;
  type: Investment["type"];
  amount_invested: number;
  start_date: string;
  notes?: string;
}

export interface AssetCreate {
  client_id: string;
  name: string;
  type: Asset["type"];
  estimated_value: number;
  purchase_date?: string;
  notes?: string;
}

export interface EntrepreneurProfile {
  id: string;
  client_id: string;
  business_name: string;
  business_type: string;
  annual_revenue: number;
  employee_count: number;
  started_date: string;
  description?: string;
}

export const wealthService = {
  async getDashboard(): Promise<WealthDashboard> {
    const { data } = await apiClient.get("/wealth/dashboard");
    return data;
  },

  async getGoals(
    params?: PaginationParams & { status?: string }
  ): Promise<PaginatedResponse<FinancialGoal>> {
    const { data } = await apiClient.get("/wealth/goals", { params });
    return data;
  },

  async getGoal(id: string): Promise<FinancialGoal> {
    const { data } = await apiClient.get(`/wealth/goals/${id}`);
    return data;
  },

  async createGoal(payload: GoalCreate): Promise<FinancialGoal> {
    const { data } = await apiClient.post("/wealth/goals", payload);
    return data;
  },

  async updateGoal(id: string, payload: GoalUpdate): Promise<FinancialGoal> {
    const { data } = await apiClient.patch(`/wealth/goals/${id}`, payload);
    return data;
  },

  async deleteGoal(id: string): Promise<void> {
    await apiClient.delete(`/wealth/goals/${id}`);
  },

  async getGoalMilestones(goalId: string): Promise<GoalMilestone[]> {
    const { data } = await apiClient.get(`/wealth/goals/${goalId}/milestones`);
    return data;
  },

  async getGoalTransactions(goalId: string): Promise<GoalTransaction[]> {
    const { data } = await apiClient.get(
      `/wealth/goals/${goalId}/transactions`
    );
    return data;
  },

  async getSavingsPrograms(
    params?: PaginationParams
  ): Promise<PaginatedResponse<SavingsProgram>> {
    const { data } = await apiClient.get("/wealth/savings", { params });
    return data;
  },

  async createSavingsProgram(
    payload: SavingsProgramCreate
  ): Promise<SavingsProgram> {
    const { data } = await apiClient.post("/wealth/savings", payload);
    return data;
  },

  async updateSavingsProgram(
    id: string,
    payload: Partial<SavingsProgramCreate>
  ): Promise<SavingsProgram> {
    const { data } = await apiClient.patch(`/wealth/savings/${id}`, payload);
    return data;
  },

  async getInvestments(
    params?: PaginationParams
  ): Promise<PaginatedResponse<Investment>> {
    const { data } = await apiClient.get("/wealth/investments", { params });
    return data;
  },

  async createInvestment(payload: InvestmentCreate): Promise<Investment> {
    const { data } = await apiClient.post("/wealth/investments", payload);
    return data;
  },

  async getAssets(
    params?: PaginationParams
  ): Promise<PaginatedResponse<Asset>> {
    const { data } = await apiClient.get("/wealth/assets", { params });
    return data;
  },

  async createAsset(payload: AssetCreate): Promise<Asset> {
    const { data } = await apiClient.post("/wealth/assets", payload);
    return data;
  },

  async getEntrepreneurProfile(
    clientId: string
  ): Promise<EntrepreneurProfile | null> {
    const { data } = await apiClient.get(
      `/wealth/entrepreneur/${clientId}`
    );
    return data;
  },
};
