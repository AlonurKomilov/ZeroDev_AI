"use client";

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import HealthMetrics from '@/components/features/admin/HealthMetrics';
import BusinessMetrics from '@/components/features/admin/BusinessMetrics';
import UserAnalytics from '@/components/features/admin/UserAnalytics';
import FeedbackManagement from '@/components/features/admin/FeedbackManagement';

const fetchHealthMetrics = async () => {
  const res = await fetch('/api/dashboard/health', {
    headers: {
      'X-CEO-Token': 'ceo_super_secret_token',
      'X-2FA-Code': '123456',
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch health metrics');
  }
  return res.json();
};

const fetchBusinessMetrics = async () => {
  const res = await fetch('/api/dashboard/business', {
    headers: {
      'X-CEO-Token': 'ceo_super_secret_token',
      'X-2FA-Code': '123456',
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch business metrics');
  }
  return res.json();
};

const AdminDashboardPage = () => {
  const { data: healthData, isLoading: isHealthLoading, isError: isHealthError } = useQuery({
    queryKey: ['adminHealthMetrics'],
    queryFn: fetchHealthMetrics,
  });

  const { data: businessData, isLoading: isBusinessLoading, isError: isBusinessError } = useQuery({
    queryKey: ['adminBusinessMetrics'],
    queryFn: fetchBusinessMetrics,
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">CEO Admin Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <HealthMetrics data={healthData} isLoading={isHealthLoading} isError={isHealthError} />
        </div>
        <div className="col-span-1 lg:col-span-2">
          <BusinessMetrics data={businessData} isLoading={isBusinessLoading} isError={isBusinessError} />
        </div>
        <div className="col-span-1">
          <UserAnalytics />
        </div>
        <div className="col-span-1">
          <FeedbackManagement />
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
