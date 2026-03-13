export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  message: string;
  detail?: string;
  status_code: number;
  errors?: Record<string, string[]>;
}

export type SortDirection = "asc" | "desc";

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_direction?: SortDirection;
  search?: string;
}
