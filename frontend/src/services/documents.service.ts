import apiClient from "@/lib/api-client";
import { Document } from "@/types/document";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface DocumentClassification {
  document_type: string;
  confidence: number;
  suggested_name?: string;
}

export interface DocumentVerification {
  is_verified: boolean;
  verified_by?: string;
  verified_at?: string;
  notes?: string;
}

export const documentsService = {
  async getDocuments(
    params?: PaginationParams & { client_id?: string; case_id?: string; document_type?: string; status?: string }
  ): Promise<PaginatedResponse<Document>> {
    const { data } = await apiClient.get("/documents", { params });
    return data;
  },

  async getDocument(id: string): Promise<Document> {
    const { data } = await apiClient.get(`/documents/${id}`);
    return data;
  },

  async uploadDocument(payload: FormData): Promise<Document> {
    const { data } = await apiClient.post("/documents", payload, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async updateDocument(id: string, payload: Partial<Document>): Promise<Document> {
    const { data } = await apiClient.patch(`/documents/${id}`, payload);
    return data;
  },

  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/documents/${id}`);
  },

  async classifyDocument(id: string): Promise<DocumentClassification> {
    const { data } = await apiClient.post(`/documents/${id}/classify`);
    return data;
  },

  async verifyDocument(
    id: string,
    payload: { is_verified: boolean; notes?: string }
  ): Promise<DocumentVerification> {
    const { data } = await apiClient.post(`/documents/${id}/verify`, payload);
    return data;
  },
};
