'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import { useAuthStore, useProvisioningStore } from '@/lib/store';
import { Button, Card } from '@/components/ui';

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { status, isLoading, setStatus, setLoading } = useProvisioningStore();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshStatus = useCallback(async () => {
    if (!user) return;
    setIsRefreshing(true);
    try {
      const result = await apiClient.getProvisioningStatus(user.id);
      setStatus(result);
    } catch (err) {
      console.error('Failed to refresh status', err);
    } finally {
      setIsRefreshing(false);
    }
  }, [user, setStatus]);

  useEffect(() => {
    if (!user) return;
    refreshStatus();
  }, [user, refreshStatus]);

  const handleStartEnvironment = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const result = await apiClient.startProvisioning(user.id);
      setStatus(result);
    } catch (err) {
      console.error('Failed to start environment', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStopEnvironment = async () => {
    if (!user) return;
    try {
      await apiClient.stopProvisioning(user.id);
      await refreshStatus();
    } catch (err) {
      console.error('Failed to stop environment', err);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Please log in first</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Welcome, {user.name}</h1>
          <Button variant="secondary" onClick={logout}>
            Logout
          </Button>
        </div>

        {/* Trial Status */}
        {user.trial_end && !user.has_active_subscription && (
          <Card className="mb-6 bg-blue-50 border-l-4 border-blue-500">
            <p className="text-blue-900">
              Your free trial expires on {new Date(user.trial_end).toLocaleDateString()}
            </p>
          </Card>
        )}

        {/* Environment Card */}
        <Card className="mb-6">
          <h2 className="text-xl font-bold mb-4">Your Environment</h2>
          
          {status?.status?.status === 'running' ? (
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-green-900 font-semibold">✓ Environment Running</p>
                <p className="text-green-800 text-sm mt-1">Subdomain: {status?.status?.subdomain}</p>
              </div>
              
              {status?.status?.url && (
                <a
                  href={status.status.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <Button variant="primary">
                    Open Environment
                  </Button>
                </a>
              )}

              <Button
                variant="danger"
                onClick={handleStopEnvironment}
              >
                Stop Environment
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">No active environment</p>
              <Button
                variant="primary"
                onClick={handleStartEnvironment}
                isLoading={isLoading}
              >
                Launch Environment
              </Button>
            </div>
          )}

          <Button
            variant="secondary"
            onClick={refreshStatus}
            isLoading={isRefreshing}
            className="mt-4"
          >
            Refresh Status
          </Button>
        </Card>

        {/* Billing Card */}
        <Card>
          <h2 className="text-xl font-bold mb-4">Billing</h2>
          {user.has_active_subscription ? (
            <p className="text-green-600 font-semibold">✓ Active Subscription</p>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">Upgrade to continue after your trial expires</p>
              <Button variant="primary">
                View Plans
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
