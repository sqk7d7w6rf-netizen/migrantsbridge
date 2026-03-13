"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { reportsService, DateRange } from "@/services/reports.service";

export function useDashboardData(params?: DateRange) {
  return useQuery({
    queryKey: [...queryKeys.dashboard.all, "data", params],
    queryFn: () => reportsService.getDashboardData(params),
  });
}

export function useKPIs(params?: DateRange) {
  return useQuery({
    queryKey: queryKeys.dashboard.kpis(),
    queryFn: () => reportsService.getKPIs(params),
  });
}

export function useClientGrowth(params?: DateRange) {
  return useQuery({
    queryKey: [...queryKeys.reports.clients(), "growth", params],
    queryFn: () => reportsService.getClientGrowth(params),
  });
}

export function useClientDemographics() {
  return useQuery({
    queryKey: [...queryKeys.reports.clients(), "demographics"],
    queryFn: () => reportsService.getClientDemographics(),
  });
}

export function useLanguageDistribution() {
  return useQuery({
    queryKey: [...queryKeys.reports.clients(), "languages"],
    queryFn: () => reportsService.getLanguageDistribution(),
  });
}

export function useRevenueTrend(params?: DateRange) {
  return useQuery({
    queryKey: [...queryKeys.reports.financial(), "revenue", params],
    queryFn: () => reportsService.getRevenueTrend(params),
  });
}

export function useBillingStatusBreakdown() {
  return useQuery({
    queryKey: [...queryKeys.reports.financial(), "billing-status"],
    queryFn: () => reportsService.getBillingStatusBreakdown(),
  });
}

export function useTopServices() {
  return useQuery({
    queryKey: [...queryKeys.reports.financial(), "top-services"],
    queryFn: () => reportsService.getTopServices(),
  });
}

export function useCaseOutcomes(params?: DateRange) {
  return useQuery({
    queryKey: [...queryKeys.reports.cases(), "outcomes", params],
    queryFn: () => reportsService.getCaseOutcomes(params),
  });
}

export function useCaseResolutionTimes() {
  return useQuery({
    queryKey: [...queryKeys.reports.cases(), "resolution-times"],
    queryFn: () => reportsService.getCaseResolutionTimes(),
  });
}

export function useCaseStatusDistribution() {
  return useQuery({
    queryKey: [...queryKeys.reports.cases(), "status-distribution"],
    queryFn: () => reportsService.getCaseStatusDistribution(),
  });
}

export function useReports(reportType: string, params?: DateRange) {
  return useQuery({
    queryKey: [...queryKeys.reports.all, reportType, params],
    queryFn: () => {
      switch (reportType) {
        case "clients":
          return reportsService.getClientGrowth(params);
        case "financial":
          return reportsService.getRevenueTrend(params);
        case "cases":
          return reportsService.getCaseOutcomes(params);
        default:
          return reportsService.getDashboardData(params);
      }
    },
  });
}
