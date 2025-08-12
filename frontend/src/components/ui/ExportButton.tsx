"use client";

import { useMutation } from "@tanstack/react-query";

const exportProject = async (projectId: string) => {
  console.log(`Exporting project ${projectId}`);
  const res = await fetch(`/api/projects/${projectId}/export`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("Failed to start export process.");
  }
  // The backend will handle the zip generation and download trigger.
  // The response might be a confirmation message.
  return res.json();
};

export default function ExportButton({ projectId }: { projectId: string }) {
  const mutation = useMutation({
    mutationFn: exportProject,
    onSuccess: () => {
      alert("Export started! You will be notified when the download is ready.");
    },
    onError: (error) => {
      alert(`Export failed: ${error.message}`);
    },
  });

  return (
    <button
      onClick={() => mutation.mutate(projectId)}
      disabled={mutation.isPending}
      className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-400"
    >
      {mutation.isPending ? "Exporting..." : "Export as .zip"}
    </button>
  );
}
