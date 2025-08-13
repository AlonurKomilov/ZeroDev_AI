import React from 'react';

const ProjectDetailSkeleton = () => {
  return (
    <div className="container mx-auto p-4 animate-pulse">
      <div className="flex justify-between items-center mb-6">
        <div className="h-9 bg-gray-300 rounded w-1/3"></div>
        <div className="flex items-center space-x-2">
          <div className="h-10 bg-gray-300 rounded w-24"></div>
          <div className="h-10 bg-gray-300 rounded w-24"></div>
          <div className="h-10 bg-gray-300 rounded w-24"></div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <div className="h-8 bg-gray-300 rounded w-1/4 mb-4"></div>
        <div className="h-6 bg-gray-300 rounded w-full mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <div className="h-5 bg-gray-300 rounded w-1/2"></div>
          </div>
          <div>
            <div className="h-5 bg-gray-300 rounded w-1/2"></div>
          </div>
          <div>
            <div className="h-5 bg-gray-300 rounded w-1/2"></div>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <div className="h-8 bg-gray-300 rounded w-1/4 mb-4"></div>
        <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg">
          <div className="h-6 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailSkeleton;
