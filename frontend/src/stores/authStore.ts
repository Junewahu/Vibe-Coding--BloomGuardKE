import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  user: {
    id: string;
    email: string;
    role: string;
    name: string;
  } | null;
  setToken: (token: string) => void;
  setRefreshToken: (token: string) => void;
  setUser: (user: AuthState['user']) => void;
  login: (token: string, refreshToken: string, user: AuthState['user']) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      user: null,

      setToken: (token: string) => set({ token }),
      setRefreshToken: (token: string) => set({ refreshToken: token }),
      setUser: (user: AuthState['user']) => set({ user }),

      login: (token: string, refreshToken: string, user: AuthState['user']) =>
        set({
          token,
          refreshToken,
          user,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 