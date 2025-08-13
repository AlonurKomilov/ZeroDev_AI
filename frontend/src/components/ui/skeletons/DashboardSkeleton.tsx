import React from 'react';

const SkeletonCard = () => (
  <div className="border p-4 rounded-lg shadow animate-pulse">
    <div className="h-6 bg-gray-300 rounded w-3/4 mb-4"></div>
    <div className="h-4 bg-gray-300 rounded w-full mb-2"></div>
    <div className="h-4 bg-gray-300 rounded w-5/6"></div>
    <div className="h-8 bg-gray-300 rounded w-1/4 mt-4"></div>
  </div>
);

const DashboardSkeleton = () => {
  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div className="h-8 bg-gray-300 rounded w-1/4"></div>
        <div className="h-10 bg-gray-300 rounded w-1/6"></div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
};

export default DashboardSkeleton;
