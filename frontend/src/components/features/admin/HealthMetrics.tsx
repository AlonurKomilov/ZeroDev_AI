import React from 'react';

interface HealthMetricsProps {
  data?: {
    active_users: number;
    total_projects: number;
    api_requests_per_minute: number;
    error_rate: number;
  };
  isLoading: boolean;
  isError: boolean;
}

const HealthMetrics: React.FC<HealthMetricsProps> = ({ data, isLoading, isError }) => {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Platform Health</h2>
        <p>Loading...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Platform Health</h2>
        <p className="text-red-500">Error loading health metrics.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">Platform Health</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-green-100 dark:bg-green-900 rounded-lg">
          <h3 className="font-semibold">Active Users</h3>
          <p className="text-2xl font-bold">{data?.active_users}</p>
        </div>
        <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded-lg">
          <h3 className="font-semibold">Total Projects</h3>
          <p className="text-2xl font-bold">{data?.total_projects}</p>
        </div>
        <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
          <h3 className="font-semibold">API RPM</h3>
          <p className="text-2xl font-bold">{data?.api_requests_per_minute}</p>
        </div>
        <div className="p-4 bg-red-100 dark:bg-red-900 rounded-lg">
          <h3 className="font-semibold">Error Rate</h3>
          <p className="text-2xl font-bold">{(data?.error_rate || 0) * 100}%</p>
        </div>
      </div>
    </div>
  );
};

export default HealthMetrics;
