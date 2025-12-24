import axios from 'axios';
import type { QueryRequest, QueryResponse, HealthResponse, ViewCountsResponse } from '../types';
import { authService } from './auth';

const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle error responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    // 401 Unauthorized - Session expired
    if (status === 401) {
      authService.logout();
      window.location.href = '/login?expired=true';
    }

    // 429 Too Many Requests - Rate limit exceeded
    if (status === 429) {
      error.message = 'Demasiadas solicitudes. Por favor, espere un momento antes de intentar nuevamente.';
    }

    return Promise.reject(error);
  }
);

export const queryApi = {
  processQuery: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  },

  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  getViewCounts: async (): Promise<ViewCountsResponse> => {
    const response = await api.get<ViewCountsResponse>('/views/counts');
    return response.data;
  },
};

export default api;
