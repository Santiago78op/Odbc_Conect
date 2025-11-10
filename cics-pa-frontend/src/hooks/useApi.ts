import { useQuery, useMutation, UseQueryOptions } from '@tanstack/react-query';
import { apiService } from '../services/api.service';
import { API_ENDPOINTS } from '../config/api.config';
import type {
  HealthResponse,
  AbendsResponse,
  AbendsFilterRequest,
  QueryRequest,
  QueryResponse,
  TableInfoResponse,
  AbendsSummaryResponse,
} from '../types/api.types';

// ========== Health Check ==========

export function useHealth() {
  return useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: () => apiService.get<HealthResponse>(API_ENDPOINTS.health),
    refetchInterval: 30000, // Refetch cada 30 segundos
  });
}

// ========== Abends ==========

export function useAbends(
  filters?: AbendsFilterRequest,
  options?: Omit<UseQueryOptions<AbendsResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery<AbendsResponse>({
    queryKey: ['abends', filters],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters?.region) params.append('region', filters.region);
      if (filters?.program) params.append('program', filters.program);
      if (filters?.limit) params.append('limit', filters.limit.toString());

      const url = `${API_ENDPOINTS.abends}${params.toString() ? `?${params.toString()}` : ''}`;
      return apiService.get<AbendsResponse>(url);
    },
    ...options,
  });
}

export function useAbendsSummary(
  region?: string,
  options?: Omit<UseQueryOptions<AbendsSummaryResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery<AbendsSummaryResponse>({
    queryKey: ['abends', 'summary', region],
    queryFn: () => {
      const params = region ? `?region=${region}` : '';
      const url = `${API_ENDPOINTS.summary}${params}`;
      return apiService.get<AbendsSummaryResponse>(url);
    },
    ...options,
  });
}

// ========== Custom Query ==========

export function useExecuteQuery() {
  return useMutation<QueryResponse, Error, QueryRequest>({
    mutationFn: (queryRequest: QueryRequest) =>
      apiService.post<QueryResponse>(API_ENDPOINTS.execute, queryRequest),
  });
}

// ========== Tables ==========

export function useTableInfo(
  tableName: string,
  options?: Omit<UseQueryOptions<TableInfoResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery<TableInfoResponse>({
    queryKey: ['tables', 'info', tableName],
    queryFn: () => apiService.get<TableInfoResponse>(`${API_ENDPOINTS.tables}/info/${tableName}`),
    enabled: !!tableName, // Solo ejecutar si hay un nombre de tabla
    ...options,
  });
}

export function useListTables(
  options?: Omit<UseQueryOptions<{ tables: string[] }>, 'queryKey' | 'queryFn'>
) {
  return useQuery<{ tables: string[] }>({
    queryKey: ['tables', 'list'],
    queryFn: () => apiService.get<{ tables: string[] }>(`${API_ENDPOINTS.tables}/list`),
    ...options,
  });
}
