import React from 'react';

const SkeletonTemplateCard = () => (
  <div className="border rounded-lg shadow-lg overflow-hidden dark:bg-gray-800 dark:border-gray-700 flex flex-col animate-pulse">
    <div className="w-full h-48 bg-gray-300"></div>
    <div className="p-4 flex flex-col flex-grow">
      <div className="h-6 bg-gray-300 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-300 rounded w-full mb-4"></div>
      <div className="h-4 bg-gray-300 rounded w-5/6 mb-4"></div>
      <div className="mb-4">
        <div className="h-6 w-20 bg-gray-300 rounded-full inline-block mr-2"></div>
        <div className="h-6 w-20 bg-gray-300 rounded-full inline-block mr-2"></div>
        <div className="h-6 w-20 bg-gray-300 rounded-full inline-block"></div>
      </div>
      <div className="mt-auto w-full h-10 bg-gray-300 rounded"></div>
    </div>
  </div>
);

const TemplateSkeleton = () => {
  return (
    <div className="container mx-auto p-4">
      <div className="h-9 bg-gray-300 rounded w-1/4 mb-6"></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
        <SkeletonTemplateCard />
      </div>
    </div>
  );
};

export default TemplateSkeleton;
