"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { apiService, Project } from "@/lib/api";
import ExportButton from "@/components/ui/ExportButton";
import ModifyProjectModal from "@/components/features/ModifyProjectModal";
import ProjectDetailSkeleton from "@/components/ui/skeletons/ProjectDetailSkeleton";
import ErrorDisplay from "@/components/ui/ErrorDisplay";

// API call function
const fetchProject = async (id: string): Promise<Project> => {
  return await apiService.getProject(id);
};

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    data: project,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Project>({
    queryKey: ["project", id],
    queryFn: () => fetchProject(id),
    enabled: !!id && !!user, // Only run the query if the id and user are available
  });

  // Delete project mutation
  const deleteProjectMutation = useMutation({
    mutationFn: async () => {
      await apiService.deleteProject(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      router.push('/dashboard');
    },
    onError: (error: Error) => {
      alert(`Failed to delete project: ${error.message}`);
    },
  });

  const handleDeleteProject = async () => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteProjectMutation.mutateAsync();
    } catch (err) {
      // Error handled by mutation
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) return <ProjectDetailSkeleton />;
  if (isError) return <ErrorDisplay message={(error as Error).message} onRetry={() => refetch()} />;
  if (!project) return <div>Project not found.</div>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">{project.name}</h1>
          <p className="text-gray-600 mt-1">Project ID: {project.id}</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Modify Project
          </button>
          <ExportButton projectId={project.id} />
          <Link href={`/projects/${project.id}/settings`}>
            <button className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              Settings
            </button>
          </Link>
          <button
            onClick={handleDeleteProject}
            disabled={isDeleting}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      <ModifyProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        projectId={project.id}
      />

      {/* Project Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Project Overview</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="font-semibold text-gray-700 dark:text-gray-300">Created</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(project.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="font-semibold text-gray-700 dark:text-gray-300">Last Updated</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(project.updated_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">Project Status</h3>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                  Active
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Link
                href={`/projects/${project.id}/files`}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                📁 View Files
              </Link>
              <Link
                href={`/projects/${project.id}/agents`}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                🤖 AI Agents
              </Link>
              <Link
                href={`/projects/${project.id}/analytics`}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                📊 Analytics
              </Link>
              <Link
                href={`/projects/${project.id}/deploy`}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                🚀 Deploy
              </Link>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p>Project created</p>
                  <p className="text-xs text-gray-500">{new Date(project.created_at).toLocaleDateString()}</p>
                </div>
              </div>
              {project.updated_at !== project.created_at && (
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div>
                    <p>Project updated</p>
                    <p className="text-xs text-gray-500">{new Date(project.updated_at).toLocaleDateString()}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* File Management Section */}
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Project Files</h2>
        <div className="bg-gray-100 dark:bg-gray-900 p-8 rounded-lg text-center">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">File Management Coming Soon</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            File upload, editing, and version control features will be available here.
          </p>
          <button
            disabled
            className="bg-gray-300 text-gray-500 font-bold py-2 px-4 rounded cursor-not-allowed"
          >
            Upload Files (Coming Soon)
          </button>
        </div>
      </div>
    </div>
  );
}
