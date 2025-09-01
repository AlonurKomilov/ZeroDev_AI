"use client";

import { useMutation } from "@tanstack/react-query";
import { useSubscription } from '@/hooks/useSubscription';

const exportProject = async (projectId: string) => {
  console.log(`Exporting project ${projectId}`);
  const res = await fetch(`/api/projects/${projectId}/export`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("Failed to start export process.");
  }
  return res.json();
};

export default function ExportButton({ projectId }: { projectId: string }) {
  const { isPro, isLoading } = useSubscription();

  const mutation = useMutation({
    mutationFn: exportProject,
    onSuccess: () => {
      alert("Export started! You will be notified when the download is ready.");
    },
    onError: (error) => {
      alert(`Export failed: ${error.message}`);
    },
  });

  const isDisabled = mutation.isPending || !isPro || isLoading;

  const button = (
    <button
      onClick={() => mutation.mutate(projectId)}
      disabled={isDisabled}
      className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-400"
    >
      {mutation.isPending ? "Exporting..." : "Export as .zip"}
    </button>
  );

  if (!isPro && !isLoading) {
    return (
      <div className="relative group">
        {button}
        <div className="absolute bottom-full mb-2 w-max bg-black text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100">
          Upgrade to Pro to use this feature.
        </div>
      </div>
    );
  }

  return button;
}
