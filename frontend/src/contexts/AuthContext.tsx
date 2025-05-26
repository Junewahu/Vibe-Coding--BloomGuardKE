import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => Promise<void>;
  refreshToken: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

interface TokenPayload {
  sub: string;
  email: string;
  name: string;
  role: string;
  exp: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_REFRESH_INTERVAL = 4 * 60 * 1000; // 4 minutes

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (storedToken) {
        try {
          const decodedToken = jwtDecode<TokenPayload>(storedToken);
          if (decodedToken.exp * 1000 > Date.now()) {
            setToken(storedToken);
            setUser({
              id: decodedToken.sub,
              email: decodedToken.email,
              name: decodedToken.name,
              role: decodedToken.role,
            });
          } else {
            // Token expired, try to refresh
            await refreshToken();
          }
        } catch (error) {
          console.error('Error decoding token:', error);
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  // Set up token refresh interval
  useEffect(() => {
    if (token) {
      const interval = setInterval(() => {
        refreshToken();
      }, TOKEN_REFRESH_INTERVAL);

      return () => clearInterval(interval);
    }
  }, [token]);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      const { accessToken, refreshToken: newRefreshToken } = data;

      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);

      const decodedToken = jwtDecode<TokenPayload>(accessToken);
      setToken(accessToken);
      setUser({
        id: decodedToken.sub,
        email: decodedToken.email,
        name: decodedToken.name,
        role: decodedToken.role,
      });

      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      setIsLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      // After successful registration, log the user in
      await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setToken(null);
    setUser(null);
    navigate('/login');
  };

  const updateUser = async (userData: Partial<User>) => {
    try {
      setIsLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/users/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      const updatedUser = await response.json();
      setUser((prev) => prev ? { ...prev, ...updatedUser } : null);
    } catch (error) {
      console.error('Update user error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      const { accessToken, refreshToken: newRefreshToken } = data;

      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);

      const decodedToken = jwtDecode<TokenPayload>(accessToken);
      setToken(accessToken);
      setUser({
        id: decodedToken.sub,
        email: decodedToken.email,
        name: decodedToken.name,
        role: decodedToken.role,
      });
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  };

  const resetPassword = async (email: string) => {
    try {
      setIsLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Failed to send reset password email');
      }
    } catch (error) {
      console.error('Reset password error:', error);
      setError(error instanceof Error ? error.message : 'Failed to reset password');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    token,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    updateUser,
    refreshToken,
    resetPassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 