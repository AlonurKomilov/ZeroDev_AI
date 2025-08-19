'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/lib/api';

const CreateProjectPage = () => {
  const [projectName, setProjectName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Mutation for creating a project
  const createProjectMutation = useMutation({
    mutationFn: async (name: string) => {
      return await apiService.createProject({ name });
    },
    onSuccess: (newProject) => {
      // Invalidate and refetch projects
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      
      // Redirect to the new project
      router.push(`/projects/${newProject.id}`);
    },
    onError: (error: Error) => {
      setError(error.message);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }

    if (!user) {
      setError('You must be logged in to create a project');
      return;
    }

    setError(null);
    setIsSubmitting(true);
    
    try {
      await createProjectMutation.mutateAsync(projectName.trim());
    } catch (err) {
      // Error is handled by the mutation
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Create New Project</h1>
          <p className="text-gray-600 mt-1">
            Start a new project and let AI help you build it
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label 
              htmlFor="projectName" 
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Project Name
            </label>
            <input
              id="projectName"
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter your project name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isSubmitting}
              maxLength={100}
            />
            <p className="mt-1 text-xs text-gray-500">
              Choose a descriptive name for your project (max 100 characters)
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">What happens next?</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Your project will be created with the specified name</li>
              <li>• You'll be redirected to the project dashboard</li>
              <li>• You can then add files, configure settings, and start coding</li>
              <li>• AI agents will be available to help with development</li>
            </ul>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !projectName.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
                  Creating...
                </>
              ) : (
                'Create Project'
              )}
            </button>
          </div>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Quick Start Templates (Coming Soon)</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="border border-gray-200 rounded-md p-3 bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">Web App</h4>
              <p className="text-xs text-gray-400 mt-1">React + TypeScript + Tailwind</p>
            </div>
            <div className="border border-gray-200 rounded-md p-3 bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">API Backend</h4>
              <p className="text-xs text-gray-400 mt-1">FastAPI + PostgreSQL</p>
            </div>
            <div className="border border-gray-200 rounded-md p-3 bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">Full Stack</h4>
              <p className="text-xs text-gray-400 mt-1">Next.js + FastAPI + DB</p>
            </div>
            <div className="border border-gray-200 rounded-md p-3 bg-gray-50">
              <h4 className="text-sm font-medium text-gray-500">CLI Tool</h4>
              <p className="text-xs text-gray-400 mt-1">Python + Click</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectPage;
