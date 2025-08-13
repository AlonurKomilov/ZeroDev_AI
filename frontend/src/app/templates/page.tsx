"use client";

import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import { useRouter } from "next/navigation";
import TemplateSkeleton from "@/components/ui/skeletons/TemplateSkeleton";
import ErrorDisplay from "@/components/ui/ErrorDisplay";

// Define the type for a template
type Template = {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
  tags: string[];
};

// Placeholder for the actual API call
const fetchTemplates = async (): Promise<Template[]> => {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const res = await fetch(`${baseUrl}/api/templates`);
  if (!res.ok) {
    throw new Error("Network response was not ok");
  }
  // Mocking data for now
  return [
    { id: "t1", name: "E-commerce Starter", description: "A full-featured e-commerce site.", thumbnail_url: "/placeholder.svg", tags: ["Next.js", "Stripe", "Tailwind"] },
    { id: "t2", name: "Blog Platform", description: "A simple and clean blog.", thumbnail_url: "/placeholder.svg", tags: ["React", "Markdown"] },
    { id: "t3", name: "SaaS Boilerplate", description: "Start your SaaS with user auth and billing.", thumbnail_url: "/placeholder.svg", tags: ["Next.js", "Auth.js", "PostgreSQL"] },
    { id: "t4", name: "Portfolio Website", description: "A beautiful portfolio to showcase your work.", thumbnail_url: "/placeholder.svg", tags: ["React", "Framer Motion"] },
  ];
};

export default function TemplatesPage() {
  const router = useRouter();
  const {
    data: templates,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Template[]>({
    queryKey: ["templates"],
    queryFn: fetchTemplates,
  });

  const handleSelectTemplate = (templateId: string) => {
    router.push(`/generate/new?template=${templateId}`);
  };

  if (isLoading) return <TemplateSkeleton />;
  if (isError) return <ErrorDisplay message={error.message} onRetry={() => refetch()} />;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Template Marketplace</h1>

      {templates && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {templates.map((template) => (
            <div key={template.id} className="border rounded-lg shadow-lg overflow-hidden dark:bg-gray-800 dark:border-gray-700 flex flex-col">
              <Image
                src={`https://via.placeholder.com/400x250.png?text=${template.name.replace(' ', '+')}`}
                alt={`${template.name} thumbnail`}
                width={400}
                height={250}
                className="w-full h-48 object-cover"
              />
              <div className="p-4 flex flex-col flex-grow">
                <h2 className="text-xl font-semibold mb-2">{template.name}</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4 flex-grow">{template.description}</p>
                <div className="mb-4">
                  {template.tags.map(tag => (
                    <span key={tag} className="inline-block bg-gray-200 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-300 mr-2 mb-2">
                      {tag}
                    </span>
                  ))}
                </div>
                <button
                  onClick={() => handleSelectTemplate(template.id)}
                  className="mt-auto w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                  Select Template
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
