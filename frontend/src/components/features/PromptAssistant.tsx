'use client';

import { useQuery } from '@tanstack/react-query';
import React from 'react';

interface PromptAssistantProps {
  onAppend: (text: string) => void;
  currentPrompt: string;
}

const fetchSuggestions = async (prompt: string): Promise<string[]> => {
  // In a real app, you'd fetch this from your backend
  // const res = await fetch(`/api/suggest?q=${encodeURIComponent(prompt)}`);
  // if (!res.ok) {
  //   throw new Error('Failed to fetch suggestions');
  // }
  // return res.json();

  // Mocked data for now
  if (prompt.toLowerCase().includes('database')) {
    return ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis'];
  }
  if (prompt.toLowerCase().includes('auth')) {
    return ['OAuth 2.0', 'JWT', 'Clerk', 'MagicLink'];
  }
  return ['user accounts', 'e-commerce features', 'a blog section', 'a dashboard'];
};

const PromptAssistant = ({ onAppend, currentPrompt }: PromptAssistantProps) => {
  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['prompt-suggestions', currentPrompt],
    queryFn: () => fetchSuggestions(currentPrompt),
    enabled: !!currentPrompt.trim(),
  });

  if (isLoading || !suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      <span className="text-sm font-medium text-muted-foreground">Suggestions:</span>
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onAppend(` ${suggestion}`)}
          className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-sm hover:bg-secondary/80"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
};

export default PromptAssistant;
