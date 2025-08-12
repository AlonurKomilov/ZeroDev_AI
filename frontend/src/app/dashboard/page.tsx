"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

// Define the type for a project. I'll guess the structure for now.
// In a real scenario, this would be shared with the backend.
type Project = {
  id: string;
  name: string;
  description: string;
};

// This is a placeholder for the actual API call.
// In a real app, this would be in a dedicated API service file.
const fetchProjects = async (): Promise<Project[]> => {
  // The prompt says the API is at /projects, and since this is a Next.js app
  // making a request from the client, it will be relative to the domain.
  // We assume the backend is served on the same domain or proxied.
  // The prompt mentions B22: /projects, which I'll interpret as /api/projects
  // as per common practice in Next.js projects with a backend.
  const res = await fetch("/api/projects");
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  // For now, returning mock data as the API is not yet available.
  // In a real scenario, the next line would be: return res.json();
  return [
    { id: "1", name: "Project Alpha", description: "This is the first project." },
    { id: "2", name: "Project Beta", description: "This is the second project." },
    { id: "3", name: "Project Gamma", description: "This is the third project." },
  ];
};

export default function DashboardPage() {
  const {
    data: projects,
    isLoading,
    isError,
    error,
  } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Projects Dashboard</h1>
        {/* This button should trigger the creation of a new project
            and then redirect to the ideation canvas for that new project.
            For now, it links to a placeholder route. A POST to /api/projects
            would likely be needed. */}
        <Link href="/generate/new" passHref>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Create New Project
          </button>
        </Link>
      </div>

      {isLoading && <div>Loading projects...</div>}
      {isError && <div>Error fetching projects: {error.message}</div>}

      {projects && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div key={project.id} className="border p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold">{project.name}</h2>
              <p className="text-gray-600">{project.description}</p>
              {/* Link to the project detail page */}
              <Link href={`/projects/${project.id}`} className="text-blue-500 hover:underline mt-4 inline-block">
                View Project
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
