'use client';

import { create, SetState } from 'zustand';
import { User, ProvisioningResponse } from '@/lib/api';

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set: SetState<AuthStore>) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
  isLoading: false,
  isAuthenticated: false,
  setUser: (user: User | null) => set({ user, isAuthenticated: !!user }),
  setToken: (token: string | null) => {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
    set({ token });
  },
  setLoading: (isLoading: boolean) => set({ isLoading }),
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));

interface ProvisioningStore {
  status: ProvisioningResponse | null;
  isLoading: boolean;
  error: string | null;
  setStatus: (status: ProvisioningResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useProvisioningStore = create<ProvisioningStore>((set: SetState<ProvisioningStore>) => ({
  status: null,
  isLoading: false,
  error: null,
  setStatus: (status: ProvisioningResponse | null) => set({ status }),
  setLoading: (isLoading: boolean) => set({ isLoading }),
  setError: (error: string | null) => set({ error }),
}));
