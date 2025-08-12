"use client";

import React, { useState, useEffect } from 'react';
import StatusIndicator from '../ui/StatusIndicator';
import SmartPromptInput from '../ui/SmartPromptInput';
import Portal from '../ui/Portal';

interface ModifyProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
}

const ModifyProjectModal: React.FC<ModifyProjectModalProps> = ({ isOpen, onClose, projectId }) => {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('Idle');
  const [isModifying, setIsModifying] = useState(false);

  // Mock WebSocket updates
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isModifying) {
      const statuses = [
        "Analyzing your code...",
        "Generating changes...",
        "Running automated tests...",
        "Finalizing...",
        "Modification complete. Redirecting to review..."
      ];
      let statusIndex = 0;
      interval = setInterval(() => {
        setStatus(statuses[statusIndex]);
        statusIndex++;
        if (statusIndex === statuses.length) {
          clearInterval(interval);
          setIsModifying(false);
          // Here you would typically redirect to the review page
          // For now, just closing the modal
          onClose();
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isModifying, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsModifying(true);
    setStatus('Connecting to modification service...');
    // In a real implementation, you would make the API call to /api/modify here
    // and set up the WebSocket listener.
    console.log(`Modifying project ${projectId} with prompt: ${prompt}`);
  };

  if (!isOpen) return null;

  return (
    <Portal>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center" data-testid="modify-project-modal">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-2xl">
          <h2 className="text-2xl font-bold mb-4">Modify Project</h2>
          <form onSubmit={handleSubmit}>
            <SmartPromptInput
              value={prompt}
              onChange={setPrompt}
              placeholder="Describe the changes you want to make..."
              disabled={isModifying}
            />
            <div className="mb-4">
              <StatusIndicator status={status} />
            </div>
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={onClose}
                className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                disabled={isModifying}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                disabled={isModifying}
              >
                {isModifying ? 'Modifying...' : 'Start Modification'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Portal>
  );
};

export default ModifyProjectModal;
