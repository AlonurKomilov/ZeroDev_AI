"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import ExportButton from "@/components/ui/ExportButton";
import ModifyProjectModal from "@/components/features/ModifyProjectModal";

// Using the same Project type definition as in the dashboard.
type Project = {
  id: string;
  name:string;
  description: string;
  // Add other fields that might come from the detailed view
  source_code_hash?: string;
  created_at?: string;
};

// Placeholder for the actual API call
const fetchProject = async (id: string): Promise<Project> => {
  // The fetch call is commented out as it's not needed for mock data
  // and causes issues in the test environment without a running backend API.
  // const res = await fetch(`/api/projects/${id}`);
  // if (!res.ok) {
  //   throw new Error("Network response was not ok");
  // }

  // Simulate a brief network delay
  await new Promise(resolve => setTimeout(resolve, 300));

  // Mocking data for now, assuming the API returns a project object.
  // The name and description will be based on the ID for mock purposes.
  return {
    id: id,
    name: `Project ${id}`,
    description: `This is the detailed description for project ${id}.`,
    source_code_hash: "a1b2c3d4e5f6",
    created_at: new Date().toISOString(),
  };
};

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    data: project,
    isLoading,
    isError,
    error,
  } = useQuery<Project>({
    queryKey: ["project", id],
    queryFn: () => fetchProject(id),
    enabled: !!id, // Only run the query if the id is available
  });

  if (isLoading) return <div>Loading project details...</div>;
  if (isError) return <div>Error: {error.message}</div>;
  if (!project) return <div>Project not found.</div>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{project.name}</h1>
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
        </div>
      </div>

      <ModifyProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        projectId={project.id}
      />

      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Project Details</h2>
        <p className="text-lg mb-4">{project.description}</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div>
            <span className="font-semibold">Project ID:</span> {project.id}
          </div>
          <div>
            <span className="font-semibold">Created At:</span>{" "}
            {project.created_at ? new Date(project.created_at).toLocaleString() : 'N/A'}
          </div>
          <div>
            <span className="font-semibold">Source Hash:</span> {project.source_code_hash || 'N/A'}
          </div>
        </div>
      </div>

      {/* Placeholder for future components like a file viewer */}
      <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">Code Viewer</h2>
          <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg">
            <p className="text-gray-500">File and code viewer will be implemented here.</p>
          </div>
      </div>
    </div>
  );
}
