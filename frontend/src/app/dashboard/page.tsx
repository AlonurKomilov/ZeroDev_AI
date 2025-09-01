"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { apiService, Project } from "@/lib/api";
import DashboardSkeleton from "@/components/ui/skeletons/DashboardSkeleton";
import ErrorDisplay from "@/components/ui/ErrorDisplay";

// API call function
const fetchProjects = async (): Promise<Project[]> => {
  return await apiService.getProjects();
};

export default function DashboardPage() {
  const { user } = useAuth();
  
  const {
    data: projects,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    enabled: !!user, // Only fetch when user is available
  });

  if (isLoading) return <DashboardSkeleton />;
  if (isError) return <ErrorDisplay message={(error as Error).message} onRetry={() => refetch()} />;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Projects Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.email}!</p>
        </div>
        <Link href="/generate/new" passHref>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Create New Project
          </button>
        </Link>
      </div>

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500">Total Projects</h3>
          <p className="text-2xl font-bold text-gray-900">{projects?.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500">Active Projects</h3>
          <p className="text-2xl font-bold text-green-600">{projects?.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500">Recent Activity</h3>
          <p className="text-2xl font-bold text-blue-600">
            {projects && projects.length > 0 ? 'Active' : 'None'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500">Account Status</h3>
          <p className="text-2xl font-bold text-purple-600">Active</p>
        </div>
      </div>

      {/* Projects Grid */}
      {projects && projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div key={project.id} className="border p-4 rounded-lg shadow bg-white hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-xl font-semibold text-gray-900">{project.name}</h2>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Active</span>
              </div>
              <div className="text-sm text-gray-500 mb-4">
                <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
                <p>Updated: {new Date(project.updated_at).toLocaleDateString()}</p>
              </div>
              <div className="flex space-x-2">
                <Link 
                  href={`/projects/${project.id}`} 
                  className="text-blue-500 hover:text-blue-700 text-sm font-medium"
                >
                  View Details
                </Link>
                <Link 
                  href={`/projects/${project.id}/edit`} 
                  className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                >
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-500 mb-4">Get started by creating your first project</p>
          <Link href="/generate/new" passHref>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Create Your First Project
            </button>
          </Link>
        </div>
      )}
    </div>
  );
}
