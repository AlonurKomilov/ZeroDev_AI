"use client";

import { useState } from "react";

export default function TransformPage({ params }: { params: { id: string } }) {
  const [prompt, setPrompt] = useState("");
  const [isTransforming, setIsTransforming] = useState(false);

  const handleTransform = async () => {
    if (!prompt) return;
    setIsTransforming(true);
    // In a real app, you'd call the backend API here.
    // For now, we'll simulate an API call with a delay.
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setIsTransforming(false);
    // In a real app, you would navigate to the review page, e.g.,
    // router.push(`/projects/${params.id}/upgrade/1`);
    alert("Transformation complete! Navigating to the review page.");
  };

  const examplePrompts = [
    "Migrate this from Flask to FastAPI.",
    "Rebrand this open-source project with my new design system.",
    "Refactor the authentication logic to use JWT.",
  ];

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">
        Transform Project {params.id}
      </h1>
      <p className="mb-4">
        Define your high-level transformation goal. Here are some examples:
      </p>
      <div className="flex flex-col gap-2 mb-4">
        {examplePrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => setPrompt(p)}
            className="btn btn-outline btn-sm self-start"
          >
            {p}
          </button>
        ))}
      </div>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your transformation prompt..."
        className="textarea textarea-bordered w-full h-48"
      ></textarea>
      <div className="mt-4">
        <button
          onClick={handleTransform}
          className={`btn btn-primary ${isTransforming ? "loading" : ""}`}
          disabled={isTransforming || !prompt}
        >
          {isTransforming ? "Transforming..." : "Start Transformation"}
        </button>
      </div>
    </div>
  );
}
