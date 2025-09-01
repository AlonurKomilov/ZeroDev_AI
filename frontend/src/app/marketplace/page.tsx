// frontend/src/app/marketplace/page.tsx
import React from 'react';

const plugins = [
  {
    title: 'Advanced Analytics',
    description: 'Unlock deep insights into your data with advanced analytics and visualizations.',
  },
  {
    title: 'Collaboration Tools',
    description: 'Work seamlessly with your team with real-time collaboration features.',
  },
  {
    title: 'Custom Exporters',
    description: 'Export your data in custom formats, including PDF, CSV, and Excel.',
  },
    {
    title: 'AI Assistant',
    description: 'Supercharge your workflow with an AI-powered assistant.',
  },
];

const MarketplacePage = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Plugin Marketplace</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plugins.map((plugin, index) => (
          <div key={index} className="border rounded-lg p-4 flex flex-col">
            <h2 className="text-xl font-semibold mb-2">{plugin.title}</h2>
            <p className="text-gray-600 mb-4 flex-grow">{plugin.description}</p>
            <button className="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 mt-auto">
              Install
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketplacePage;
