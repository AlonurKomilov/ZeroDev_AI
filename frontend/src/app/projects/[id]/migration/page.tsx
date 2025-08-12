"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import StatusIndicator from '@/components/ui/StatusIndicator';

type Step = 'start' | 'in_progress' | 'complete' | 'error';

interface TaskStatus {
  task_id: string;
  status: string;
  result: any;
}

const MigrationPage = () => {
  const [currentStep, setCurrentStep] = useState<Step>('start');
  const [migrationStatus, setMigrationStatus] = useState('Not Started');
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const params = useParams();
  const projectId = params.id as string;
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const pollTaskStatus = async (taskId: string) => {
    try {
      const res = await fetch(`/tasks/${taskId}`);
      if (!res.ok) {
        throw new Error('Failed to fetch task status');
      }
      const data: TaskStatus = await res.json();

      setMigrationStatus(data.status);

      if (data.status === 'SUCCESS') {
        setDownloadUrl(data.result.download_url);
        setCurrentStep('complete');
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
      } else if (data.status === 'FAILURE' || data.status === 'REVOKED') {
        setErrorMessage(data.result?.error || 'An unknown error occurred during migration.');
        setCurrentStep('error');
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
      }
    } catch (error) {
      console.error('Polling error:', error);
      setErrorMessage('Could not connect to the server to get migration status.');
      setCurrentStep('error');
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }
  };

  const handleStartMigration = async () => {
    setMigrationStatus('Initiating...');
    setCurrentStep('in_progress');

    try {
      const res = await fetch('/api/migration/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // The backend endpoint uses the authenticated user, so no body is needed.
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to start migration');
      }

      const data = await res.json();
      const taskId = data.task_id;

      setMigrationStatus('Migration process started. Waiting for progress...');

      // Start polling for the task status
      pollingIntervalRef.current = setInterval(() => {
        pollTaskStatus(taskId);
      }, 3000); // Poll every 3 seconds

    } catch (error) {
      console.error('Migration start error:', error);
      setErrorMessage(error instanceof Error ? error.message : 'An unknown error occurred.');
      setCurrentStep('error');
    }
  };

  useEffect(() => {
    // Cleanup interval on component unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Project Migration Wizard</h1>

      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 min-h-[300px]">
        {currentStep === 'start' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Step 1: Start Migration</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">
              Click the button below to begin the process of packaging your application.
              This will prepare your project for deployment on your own infrastructure.
            </p>
            <button
              onClick={handleStartMigration}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Start One-Click Migration
            </button>
          </div>
        )}

        {currentStep === 'in_progress' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Step 2: Migration in Progress</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">Your project is being packaged. You can monitor the status below.</p>
            <StatusIndicator status={migrationStatus} />
          </div>
        )}

        {currentStep === 'complete' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Step 3: Migration Complete</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">
              Congratulations! Your project has been successfully packaged.
            </p>
            <div className="bg-green-100 dark:bg-green-800 border border-green-400 text-green-700 dark:text-green-200 px-4 py-3 rounded relative" role="alert">
              <strong className="font-bold">Download Your Assets:</strong>
              <span className="block sm:inline ml-2">
                {downloadUrl ? (
                  <a href={downloadUrl} className="font-medium underline" download>
                    Your-Project-Archive.zip
                  </a>
                ) : (
                  <span>Generating link...</span>
                )}
              </span>
            </div>
            <h3 className="text-xl font-semibold mt-6 mb-2">Next Steps</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Follow the instructions in the downloaded README file to deploy your application.
            </p>
          </div>
        )}

        {currentStep === 'error' && (
          <div>
            <h2 className="text-2xl font-semibold mb-4 text-red-600 dark:text-red-400">Migration Failed</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">
              An error occurred during the migration process.
            </p>
            <div className="bg-red-100 dark:bg-red-800 border border-red-400 text-red-700 dark:text-red-200 px-4 py-3 rounded relative" role="alert">
              <strong className="font-bold">Error Details:</strong>
              <span className="block sm:inline ml-2">{errorMessage || 'Unknown error'}</span>
            </div>
            <button
              onClick={() => setCurrentStep('start')}
              className="mt-6 px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MigrationPage;
