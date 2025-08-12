"use client";

import React, { useState } from 'react';

interface AdvancedFeedbackProps {
  code: string;
  onSubmitFeedback: (feedback: { line: number; comment: string }) => void;
}

const AdvancedFeedback: React.FC<AdvancedFeedbackProps> = ({ code, onSubmitFeedback }) => {
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [comment, setComment] = useState('');

  const lines = code.split('\n');

  const handleLineClick = (lineNumber: number) => {
    setSelectedLine(lineNumber);
    setComment(''); // Reset comment when a new line is selected
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedLine !== null && comment.trim() !== '') {
      onSubmitFeedback({ line: selectedLine, comment });
      setSelectedLine(null);
      setComment('');
    }
  };

  return (
    <div className="border rounded-lg">
      <div className="flex">
        {/* Code view */}
        <div className="w-2/3 p-4 bg-gray-50 dark:bg-gray-900 font-mono text-sm overflow-auto">
          {lines.map((line, index) => (
            <div
              key={index}
              className={`flex items-center cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 ${selectedLine === index + 1 ? 'bg-blue-100 dark:bg-blue-900' : ''}`}
              onClick={() => handleLineClick(index + 1)}
            >
              <span className="w-10 text-right pr-4 text-gray-500">{index + 1}</span>
              <pre className="whitespace-pre-wrap">{line}</pre>
            </div>
          ))}
        </div>
        {/* Feedback form */}
        <div className="w-1/3 p-4 border-l">
          <h3 className="text-lg font-semibold mb-4">Contextual Feedback</h3>
          {selectedLine === null ? (
            <p className="text-gray-500">Click on a line of code to leave a comment.</p>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="mb-2">
                <label className="font-semibold">Feedback for line {selectedLine}:</label>
              </div>
              <textarea
                className="w-full h-32 p-2 border rounded bg-white dark:bg-gray-800"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Leave your comment..."
              />
              <button
                type="submit"
                className="mt-2 w-full bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded"
              >
                Submit Feedback
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedFeedback;
