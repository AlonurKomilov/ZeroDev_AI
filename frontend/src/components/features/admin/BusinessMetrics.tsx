import React from 'react';

interface BusinessMetricsProps {
  data?: {
    mrr: number;
    new_customers_last_30_days: number;
    churn_rate: number;
  };
  isLoading: boolean;
  isError: boolean;
}

const BusinessMetrics: React.FC<BusinessMetricsProps> = ({ data, isLoading, isError }) => {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Business Metrics</h2>
        <p>Loading...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Business Metrics</h2>
        <p className="text-red-500">Error loading business metrics.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">Business Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-purple-100 dark:bg-purple-900 rounded-lg">
          <h3 className="font-semibold">MRR</h3>
          <p className="text-2xl font-bold">${data?.mrr.toLocaleString()}</p>
        </div>
        <div className="p-4 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
          <h3 className="font-semibold">New Customers (30d)</h3>
          <p className="text-2xl font-bold">{data?.new_customers_last_30_days}</p>
        </div>
        <div className="p-4 bg-pink-100 dark:bg-pink-900 rounded-lg">
          <h3 className="font-semibold">Churn Rate</h3>
          <p className="text-2xl font-bold">{(data?.churn_rate || 0) * 100}%</p>
        </div>
      </div>
    </div>
  );
};

export default BusinessMetrics;
