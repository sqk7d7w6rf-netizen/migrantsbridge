import apiClient from "@/lib/api-client";
import { Case, CaseNote, CaseHistory } from "@/types/case";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export const casesService = {
  async getCases(
    params?: PaginationParams & { client_id?: string }
  ): Promise<PaginatedResponse<Case>> {
    const { data } = await apiClient.get("/cases", { params });
    return data;
  },

  async getCase(id: string): Promise<Case> {
    const { data } = await apiClient.get(`/cases/${id}`);
    return data;
  },

  async createCase(
    payload: Omit<Case, "id" | "created_at" | "updated_at" | "case_number">
  ): Promise<Case> {
    const { data } = await apiClient.post("/cases", payload);
    return data;
  },

  async updateCase(id: string, payload: Partial<Case>): Promise<Case> {
    const { data } = await apiClient.patch(`/cases/${id}`, payload);
    return data;
  },

  async deleteCase(id: string): Promise<void> {
    await apiClient.delete(`/cases/${id}`);
  },

  async getCaseNotes(caseId: string): Promise<CaseNote[]> {
    const { data } = await apiClient.get(`/cases/${caseId}/notes`);
    return data;
  },

  async addCaseNote(
    caseId: string,
    payload: { content: string; is_internal: boolean }
  ): Promise<CaseNote> {
    const { data } = await apiClient.post(
      `/cases/${caseId}/notes`,
      payload
    );
    return data;
  },

  async getCaseHistory(caseId: string): Promise<CaseHistory[]> {
    const { data } = await apiClient.get(`/cases/${caseId}/history`);
    return data;
  },
};
