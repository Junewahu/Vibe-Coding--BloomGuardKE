import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export type UserRole = 'doctor' | 'nurse' | 'receptionist' | 'admin' | 'chw' | 'caregiver';

interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  clinicId?: string;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: Partial<User>) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    // Check for stored session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error(t('auth.invalidCredentials'));
      }

      const userData = await response.json();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.loginError'));
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      await fetch('/api/auth/logout', { method: 'POST' });
      setUser(null);
      localStorage.removeItem('user');
      navigate('/login');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.logoutError'));
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: Partial<User>) => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error(t('auth.registrationError'));
      }

      const newUser = await response.json();
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.registrationError'));
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual API call
      const response = await fetch('/api/auth/profile', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(t('auth.profileUpdateError'));
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.profileUpdateError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        logout,
        register,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider; 