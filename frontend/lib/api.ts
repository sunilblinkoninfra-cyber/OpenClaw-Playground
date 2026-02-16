'use client';

import axios, { AxiosInstance } from 'axios';

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  trial_start: string | null;
  trial_end: string | null;
  has_active_subscription: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ContainerStatus {
  status: 'provisioning' | 'running' | 'stopped' | 'error';
  container_id: string | null;
  subdomain: string | null;
  url: string | null;
  created_at: string | null;
  error_message: string | null;
}

export interface ProvisioningResponse {
  user_id: string;
  status: ContainerStatus;
  trial_end: string | null;
}

export interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
  stripe_price_id: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan_id: string;
  status: 'active' | 'past_due' | 'canceled';
  current_period_end: string;
  stripe_subscription_id: string;
}

export class APIClient {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Restore token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
      if (this.token) {
        this.api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    }
  }

  setToken(token: string) {
    this.token = token;
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    delete this.api.defaults.headers.common['Authorization'];
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // Auth endpoints
  async signup(email: string, password: string, name: string): Promise<TokenResponse> {
    const response = await this.api.post('/api/auth/signup', {
      email,
      password,
      name,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await this.api.post('/api/auth/login', {
      email,
      password,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/api/auth/me');
    return response.data;
  }

  // Provisioning endpoints
  async startProvisioning(userId: string): Promise<ProvisioningResponse> {
    const response = await this.api.post('/api/provision/start', {
      user_id: userId,
      environment_type: 'openclaw',
    });
    return response.data;
  }

  async getProvisioningStatus(userId: string): Promise<ProvisioningResponse> {
    const response = await this.api.get(`/api/provision/status/${userId}`);
    return response.data;
  }

  async stopProvisioning(userId: string): Promise<{ success: boolean }> {
    const response = await this.api.post('/api/provision/stop', {
      user_id: userId,
    });
    return response.data;
  }

  // Billing endpoints
  async getPlans(): Promise<Plan[]> {
    const response = await this.api.get('/api/billing/plans');
    return response.data;
  }

  async subscribe(planId: string, paymentMethodId: string): Promise<Subscription> {
    const response = await this.api.post('/api/billing/subscribe', {
      plan_id: planId,
      payment_method_id: paymentMethodId,
    });
    return response.data;
  }

  // Health check
  async health() {
    const response = await this.api.get('/health');
    return response.data;
  }
}

export const apiClient = new APIClient();
