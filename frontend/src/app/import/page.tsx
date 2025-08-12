"use client";

import { useState } from "react";

export default function ImportPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const handleImport = async () => {
    if (!repoUrl) return;
    setIsLoading(true);
    // In a real app, you'd call the backend API here.
    // For now, we'll simulate an API call with a delay.
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setAnalysis({
      techStack: ["Next.js", "Tailwind CSS", "TypeScript"],
      architecture: {
        models: 10,
        endpoints: 25,
      },
    });
    setIsLoading(false);
  };

  const handleConfirm = () => {
    // Navigate to the transformation page
    // In a real app, you would navigate to the next step, e.g.,
    // router.push(`/projects/${projectId}/transform`);
    alert("Confirmed! Navigating to the next step.");
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">Import Repository</h1>
      <div className="flex gap-4">
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/your-username/your-repo"
          className="input input-bordered w-full max-w-lg"
        />
        <button
          onClick={handleImport}
          className={`btn btn-primary ${isLoading ? "loading" : ""}`}
          disabled={isLoading || !!analysis}
        >
          {isLoading ? "Analyzing..." : "Import & Analyze"}
        </button>
      </div>

      {analysis && (
        <div className="card bg-base-100 shadow-xl mt-8">
          <div className="card-body">
            <h2 className="card-title">Repository Analysis</h2>
            <p>
              <strong>Technology Stack:</strong>{" "}
              {analysis.techStack.join(", ")}
            </p>
            <div className="mt-4">
              <h3 className="font-bold">Architecture Summary</h3>
              <p>Models: {analysis.architecture.models}</p>
              <p>API Endpoints: {analysis.architecture.endpoints}</p>
            </div>
            <div className="card-actions justify-end mt-4">
              <button onClick={handleConfirm} className="btn btn-success">
                Confirm & Proceed
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
