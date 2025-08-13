'use client';

import { usePromptStore } from '@/stores/promptStore';

interface PromptHistoryProps {
  onSelectPrompt: (prompt: string) => void;
}

const PromptHistory = ({ onSelectPrompt }: PromptHistoryProps) => {
  const { history } = usePromptStore();

  return (
    <div className="absolute bottom-full mb-2 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg">
      <ul className="max-h-60 overflow-y-auto">
        {history.map((prompt, index) => (
          <li
            key={index}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
            onClick={() => onSelectPrompt(prompt)}
          >
            {prompt}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PromptHistory;
