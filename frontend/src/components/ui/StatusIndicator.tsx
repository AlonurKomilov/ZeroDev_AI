"use client";

import React from 'react';

interface StatusIndicatorProps {
  status: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  return (
    <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
      <p className="text-sm text-gray-700 dark:text-gray-300">
        <span className="font-semibold">Status:</span> {status}
      </p>
    </div>
  );
};

export default StatusIndicator;
