"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from 'next/link';

// --- Types and Mock API ---

type ProjectConfig = {
  projectName: string;
  framework: 'Next.js' | 'React' | 'Vue';
  deployment: 'Vercel' | 'Netlify' | 'AWS';
  database?: 'PostgreSQL' | 'MySQL' | 'MongoDB';
};

const fetchConfig = async (id: string): Promise<ProjectConfig> => {
  console.log(`Fetching config for project ${id}`);
  // const res = await fetch(`/api/projects/${id}/config`);
  // if (!res.ok) throw new Error("Failed to fetch config");
  // return res.json();
  return Promise.resolve({
    projectName: `Project ${id}`,
    framework: "Next.js",
    deployment: "Vercel",
    database: "PostgreSQL",
  });
};

const updateConfig = async ({ id, config }: { id: string; config: ProjectConfig }): Promise<ProjectConfig> => {
  console.log(`Updating config for project ${id}`, config);
  // const res = await fetch(`/api/projects/${id}/config`, {
  //   method: "PUT",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify(config),
  // });
  // if (!res.ok) throw new Error("Failed to update config");
  // return res.json();
  return Promise.resolve(config);
};

// --- Component ---

export default function ProjectSettingsPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const queryClient = useQueryClient();
  const router = useRouter();
  const [config, setConfig] = useState<ProjectConfig | null>(null);

  const { data: initialConfig, isLoading, isError } = useQuery<ProjectConfig>({
    queryKey: ["projectConfig", id],
    queryFn: () => fetchConfig(id),
    enabled: !!id,
  });

  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig);
    }
  }, [initialConfig]);

  const mutation = useMutation({
    mutationFn: updateConfig,
    onSuccess: (data) => {
      queryClient.setQueryData(["projectConfig", id], data);
      queryClient.invalidateQueries({ queryKey: ["projectConfig", id] });
      alert("Settings saved successfully!");
      router.push(`/projects/${id}`);
    },
    onError: (error) => {
      alert(`Failed to save settings: ${error.message}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (config) {
      mutation.mutate({ id, config });
    }
  };

  if (isLoading) return <div>Loading project settings...</div>;
  if (isError) return <div>Error loading settings.</div>;
  if (!config) return <div>Could not load settings form.</div>;

  return (
    <div className="container mx-auto p-4">
        <div className="flex items-center mb-6">
            <Link href={`/projects/${id}`} className="text-blue-500 hover:underline">
                &larr; Back to Project
            </Link>
            <h1 className="text-3xl font-bold ml-4">Project Settings</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 space-y-6">
            <div>
                <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Project Name</label>
                <input
                    type="text"
                    id="projectName"
                    value={config.projectName}
                    onChange={(e) => setConfig({ ...config, projectName: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm"
                />
            </div>

            <div>
                <label htmlFor="framework" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Framework</label>
                <select id="framework" value={config.framework} onChange={(e) => setConfig({ ...config, framework: e.target.value as ProjectConfig['framework'] })} className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm">
                    <option>Next.js</option>
                    <option>React</option>
                    <option>Vue</option>
                </select>
            </div>

            {/* Add more form fields for other settings here */}

            <div className="flex justify-end space-x-4">
                <button type="button" onClick={() => router.back()} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium">Cancel</button>
                <button type="submit" disabled={mutation.isPending} className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400">
                    {mutation.isPending ? "Saving..." : "Save Changes"}
                </button>
            </div>
        </form>
    </div>
  );
}
