"use client";

import React, { useState, useEffect } from 'react';
import { useDebounce } from 'use-debounce';

interface SmartPromptInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

// Placeholder for the actual API call
const fetchSuggestions = async (text: string): Promise<string[]> => {
    if (!text || text.length < 10) { // Don't fetch for very short texts
        return [];
    }
    // const res = await fetch(`/api/suggest?q=${encodeURIComponent(text)}`);
    // if (!res.ok) {
    //   return [];
    // }
    // return res.json();

    // Mocking suggestions
    console.log(`Fetching suggestions for: "${text}"`);
    return [
        `${text} with user authentication`,
        `${text} and add a pricing page`,
        `Refactor ${text.substring(0, 20)}... to use a more modular approach`,
    ];
};

const SmartPromptInput: React.FC<SmartPromptInputProps> = ({ value, onChange, placeholder, disabled }) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [debouncedValue] = useDebounce(value, 500); // 500ms debounce delay

  useEffect(() => {
    const getSuggestions = async () => {
      if (debouncedValue) {
        const result = await fetchSuggestions(debouncedValue);
        setSuggestions(result);
      } else {
        setSuggestions([]);
      }
    };
    getSuggestions();
  }, [debouncedValue]);

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    setSuggestions([]);
  };

  return (
    <div className="relative w-full">
      <textarea
        className="w-full h-40 p-2 border rounded bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-200"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />
      {suggestions.length > 0 && !disabled && (
        <ul className="absolute z-10 w-full bg-white dark:bg-gray-900 border rounded-md shadow-lg mt-1">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer text-sm"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SmartPromptInput;
