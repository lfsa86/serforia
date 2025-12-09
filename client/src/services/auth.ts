import axios from 'axios';
import type { LoginRequest, LoginResponse, UserInfo } from '../types/auth';

const API_URL = '/api';

const TOKEN_KEY = 'serfor_token';
const USER_KEY = 'serfor_user';

export const authService = {
  login: async (usuario: string, password: string): Promise<LoginResponse> => {
    const request: LoginRequest = { usuario, password };
    const response = await axios.post<LoginResponse>(`${API_URL}/auth/login`, request);
    return response.data;
  },

  logout: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
  },

  getUser: (): UserInfo | null => {
    const userJson = localStorage.getItem(USER_KEY);
    if (!userJson) return null;
    try {
      return JSON.parse(userJson) as UserInfo;
    } catch {
      return null;
    }
  },

  isAuthenticated: (): boolean => {
    return !!authService.getToken();
  },

  saveAuth: (token: string, user: UserInfo): void => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
};
