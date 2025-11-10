/**
 * Tipos TypeScript que coinciden con los modelos Pydantic del backend
 */

// ========== Request Types ==========

export interface QueryRequest {
  query: string;
  params?: unknown[];
  fetch_all?: boolean;
}

export interface AbendsFilterRequest {
  region?: string;
  program?: string;
  limit?: number;
}

export interface TableInfoRequest {
  table_name: string;
}

// ========== Response Types ==========

export interface ColumnInfo {
  name: string;
  type: string;
  size?: number | null;
  nullable: boolean;
}

export interface TableInfoResponse {
  table_name: string;
  columns: ColumnInfo[];
  total_columns: number;
}

export interface QueryResponse<T = Record<string, unknown>> {
  success: boolean;
  data: T[];
  row_count: number;
  execution_time_ms?: number;
}

export interface AbendRecord {
  timestamp?: string;
  cics_region?: string;
  program_name?: string;
  abend_code?: string;
  transaction_id?: string;
  user_id?: string;
  terminal_id?: string;
  [key: string]: unknown; // Permite campos adicionales
}

export interface AbendsResponse {
  success: boolean;
  abends: AbendRecord[];
  total: number;
  filters_applied: {
    region?: string;
    program?: string;
    limit: number;
  };
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database_connected: boolean;
  details?: Record<string, unknown>;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  error_type: string;
  timestamp: string;
  path?: string;
}

// ========== Summary Types ==========

export interface TopItem {
  name: string;
  count: number;
}

export interface AbendsSummaryResponse {
  success: boolean;
  summary: {
    total_abends: number;
    top_regions: TopItem[];
    top_programs: TopItem[];
    top_abend_codes: TopItem[];
  };
  filters_applied: {
    region?: string;
  };
}
