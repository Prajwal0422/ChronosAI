import { create } from "zustand";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  college_id: string | null;
  department_id: string | null;
  is_active?: boolean;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  setUser: (user) => set({ user, isLoading: false, isAuthenticated: !!user }),
  setLoading: (isLoading) => set({ isLoading }),
  clear: () => set({ user: null, isLoading: false, isAuthenticated: false }),
}));
