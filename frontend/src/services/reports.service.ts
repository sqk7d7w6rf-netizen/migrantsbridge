import apiClient from "@/lib/api-client";

export interface DateRange {
  date_from?: string;
  date_to?: string;
}

export interface KPIData {
  total_clients: number;
  active_cases: number;
  total_revenue: number;
  cases_resolved: number;
  client_growth_pct: number;
  revenue_growth_pct: number;
  avg_resolution_days: number;
  satisfaction_rate: number;
}

export interface DashboardData {
  kpis: KPIData;
  case_outcomes: CaseOutcomeData[];
  client_growth: ClientGrowthData[];
  revenue_trend: RevenueTrendData[];
}

export interface CaseOutcomeData {
  case_type: string;
  approved: number;
  denied: number;
  pending: number;
}

export interface ClientGrowthData {
  month: string;
  new_clients: number;
  total_clients: number;
}

export interface RevenueTrendData {
  month: string;
  revenue: number;
  collected: number;
  outstanding: number;
}

export interface ClientDemographics {
  status: string;
  count: number;
}

export interface LanguageDistribution {
  language: string;
  count: number;
}

export interface BillingStatusBreakdown {
  status: string;
  count: number;
  total_amount: number;
}

export interface TopService {
  service_name: string;
  count: number;
  revenue: number;
}

export interface CaseResolutionTime {
  case_type: string;
  avg_days: number;
  median_days: number;
}

export interface CaseStatusDistribution {
  status: string;
  count: number;
}

export const reportsService = {
  async getDashboardData(params?: DateRange): Promise<DashboardData> {
    const { data } = await apiClient.get("/reports/dashboard", { params });
    return data;
  },

  async getKPIs(params?: DateRange): Promise<KPIData> {
    const { data } = await apiClient.get("/reports/kpis", { params });
    return data;
  },

  async getClientGrowth(params?: DateRange): Promise<ClientGrowthData[]> {
    const { data } = await apiClient.get("/reports/clients/growth", {
      params,
    });
    return data;
  },

  async getClientDemographics(): Promise<ClientDemographics[]> {
    const { data } = await apiClient.get("/reports/clients/demographics");
    return data;
  },

  async getLanguageDistribution(): Promise<LanguageDistribution[]> {
    const { data } = await apiClient.get(
      "/reports/clients/languages"
    );
    return data;
  },

  async getRevenueTrend(params?: DateRange): Promise<RevenueTrendData[]> {
    const { data } = await apiClient.get("/reports/financial/revenue", {
      params,
    });
    return data;
  },

  async getBillingStatusBreakdown(): Promise<BillingStatusBreakdown[]> {
    const { data } = await apiClient.get(
      "/reports/financial/billing-status"
    );
    return data;
  },

  async getTopServices(): Promise<TopService[]> {
    const { data } = await apiClient.get("/reports/financial/top-services");
    return data;
  },

  async getCaseOutcomes(params?: DateRange): Promise<CaseOutcomeData[]> {
    const { data } = await apiClient.get("/reports/cases/outcomes", {
      params,
    });
    return data;
  },

  async getCaseResolutionTimes(): Promise<CaseResolutionTime[]> {
    const { data } = await apiClient.get("/reports/cases/resolution-times");
    return data;
  },

  async getCaseStatusDistribution(): Promise<CaseStatusDistribution[]> {
    const { data } = await apiClient.get("/reports/cases/status-distribution");
    return data;
  },

  async exportReport(
    reportType: string,
    params?: DateRange & { format?: "csv" | "pdf" }
  ): Promise<Blob> {
    const { data } = await apiClient.get(
      `/reports/export/${reportType}`,
      {
        params,
        responseType: "blob",
      }
    );
    return data;
  },
};
