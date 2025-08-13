'use client';

import { usePromptStore } from '@/stores/promptStore';
import React from 'react';

const ModelSwitcher = () => {
  const { currentModel, setModel } = usePromptStore();

  const models = ['GPT-4o Mini', 'Claude 3 Sonnet'];

  return (
    <select
      value={currentModel}
      onChange={(e) => setModel(e.target.value)}
      className="p-2 bg-gray-200 dark:bg-gray-700 rounded-md"
    >
      {models.map((model) => (
        <option key={model} value={model}>
          {model}
        </option>
      ))}
    </select>
  );
};

export default ModelSwitcher;
