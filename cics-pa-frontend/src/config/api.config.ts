/**
 * Configuración de la API
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
};

export const API_ENDPOINTS = {
  health: '/api/v1/health',
  abends: '/api/v1/query/abends',
  execute: '/api/v1/query/execute',
  summary: '/api/v1/query/abends/summary',
  tables: '/api/v1/tables',
};
