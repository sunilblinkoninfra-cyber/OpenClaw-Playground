// Shared type definitions used across backend and frontend

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  created_at: string;
  trial_start: string | null;
  trial_end: string | null;
  has_active_subscription: boolean;
}

export interface EnvironmentStatus {
  status: 'provisioning' | 'running' | 'stopped' | 'error';
  container_id: string | null;
  subdomain: string | null;
  url: string | null;
  created_at: string | null;
  error?: string;
}

export interface BillingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
  stripe_price_id: string;
}

export interface APIResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export const API_ENDPOINTS = {
  AUTH: {
    SIGNUP: '/api/auth/signup',
    LOGIN: '/api/auth/login',
    ME: '/api/auth/me',
  },
  PROVISIONING: {
    START: '/api/provision/start',
    STATUS: (userId: string) => `/api/provision/status/${userId}`,
    STOP: '/api/provision/stop',
  },
  BILLING: {
    PLANS: '/api/billing/plans',
    SUBSCRIBE: '/api/billing/subscribe',
    WEBHOOK: '/api/billing/webhook',
  },
} as const;
