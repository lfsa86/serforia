import axios from 'axios';
import type { QueryRequest, QueryResponse, HealthResponse } from '../types';
import { authService } from './auth';

const API_URL = '/api';

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

// Response interceptor - Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.href = '/login?expired=true';
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
};

export default api;
