"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { dashboardService } from "@/services/dashboard.service";

export function useDashboardKPIs() {
  return useQuery({
    queryKey: queryKeys.dashboard.kpis(),
    queryFn: () => dashboardService.getKPIs(),
  });
}

export function useRecentActivity(limit?: number) {
  return useQuery({
    queryKey: queryKeys.dashboard.recentActivity(),
    queryFn: () => dashboardService.getRecentActivity(limit),
  });
}
