export interface LoginRequest {
  usuario: string;
  password: string;
}

export interface UserInfo {
  id: number;
  nombre: string;
  sistema_id: number;
  compagnia_id: number;
}

export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: UserInfo;
  error?: string;
}

export interface AuthState {
  user: UserInfo | null;
  token: string | null;
  isAuthenticated: boolean;
}
