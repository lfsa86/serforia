import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { authService } from '../services/auth';
import type { UserInfo } from '../types/auth';

const TOKEN_CHECK_INTERVAL = 5 * 60 * 1000; // Verificar cada 5 minutos

interface AuthContextType {
  user: UserInfo | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (usuario: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleSessionExpired = useCallback(() => {
    authService.logout();
    setToken(null);
    setUser(null);
    window.location.href = '/login?expired=true';
  }, []);

  useEffect(() => {
    // Initialize auth state from localStorage
    const storedToken = authService.getToken();
    const storedUser = authService.getUser();

    if (storedToken && storedUser) {
      // Verificar si el token ya expiró al cargar
      if (authService.isTokenExpired()) {
        handleSessionExpired();
        setIsLoading(false);
        return;
      }
      setToken(storedToken);
      setUser(storedUser);
    }

    setIsLoading(false);
  }, [handleSessionExpired]);

  // Verificación periódica de expiración del token
  useEffect(() => {
    if (!token) return;

    const checkTokenExpiration = () => {
      if (authService.isTokenExpired()) {
        handleSessionExpired();
      }
    };

    const intervalId = setInterval(checkTokenExpiration, TOKEN_CHECK_INTERVAL);

    return () => clearInterval(intervalId);
  }, [token, handleSessionExpired]);

  const login = async (usuario: string, password: string): Promise<boolean> => {
    try {
      const response = await authService.login(usuario, password);

      if (response.success && response.token && response.user) {
        authService.saveAuth(response.token, response.user);
        setToken(response.token);
        setUser(response.user);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
