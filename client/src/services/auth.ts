import axios from 'axios';
import type { LoginRequest, LoginResponse, UserInfo } from '../types/auth';

const API_URL = import.meta.env.VITE_API_URL;

const TOKEN_KEY = 'serfor_token';
const USER_KEY = 'serfor_user';
const TOKEN_EXP_KEY = 'serfor_token_exp';

// Decodifica el payload del JWT (sin validar firma)
const decodeJwtPayload = (token: string): { exp?: number } | null => {
  try {
    const base64Payload = token.split('.')[1];
    const payload = atob(base64Payload);
    return JSON.parse(payload);
  } catch {
    return null;
  }
};

export const authService = {
  login: async (usuario: string, password: string): Promise<LoginResponse> => {
    try {
      const request: LoginRequest = { usuario, password };
      const response = await axios.post<LoginResponse>(`${API_URL}/auth/login`, request);
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;

        // 429 - Rate limit exceeded
        if (status === 429) {
          return {
            success: false,
            error: 'Ha alcanzado el límite de intentos. Por favor, espere un momento antes de volver a intentar.',
          };
        }

        // 401 - Unauthorized
        if (status === 401) {
          return {
            success: false,
            error: 'Usuario o contraseña incorrectos',
          };
        }

        // Other HTTP errors
        return {
          success: false,
          error: 'Error al conectar con el servidor',
        };
      }

      // Non-axios error
      return {
        success: false,
        error: 'Error al conectar con el servidor',
      };
    }
  },

  logout: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_EXP_KEY);
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

    // Extraer y guardar expiración del token
    const payload = decodeJwtPayload(token);
    if (payload?.exp) {
      localStorage.setItem(TOKEN_EXP_KEY, payload.exp.toString());
    }
  },

  getTokenExpiration: (): number | null => {
    const exp = localStorage.getItem(TOKEN_EXP_KEY);
    return exp ? parseInt(exp, 10) : null;
  },

  isTokenExpired: (): boolean => {
    const exp = authService.getTokenExpiration();
    if (!exp) return true;
    // exp está en segundos, Date.now() en milisegundos
    return Date.now() >= exp * 1000;
  },
};
