"use client";

import { useEffect, useState } from "react";

// Define PR data interface
interface PrData {
  title: string;
  author: string;
  filesChanged: number;
  commits: number;
  url: string;
}

// Mock data that would come from the GitHub API
const mockPrData: PrData = {
  title: "feat: Migrate to FastAPI",
  author: "zerodev-bot",
  filesChanged: 15,
  commits: 3,
  url: "https://github.com/your-username/your-repo/pull/1",
};

export default function UpgradeReviewPage({
  params,
}: {
  params: { id: string; pr_id: string };
}) {
  const [prData, setPrData] = useState<PrData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real app, you'd fetch this data from your backend,
    // which in turn would fetch it from the GitHub API.
    const fetchPrData = async () => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setPrData(mockPrData);
      setIsLoading(false);
    };

    fetchPrData();
  }, [params.pr_id]);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">Review Transformation</h1>
      <p className="mb-6">
        Project {params.id}, Pull Request #{params.pr_id}
      </p>

      {isLoading ? (
        <p>Loading pull request data...</p>
      ) : prData ? (
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">{prData.title}</h2>
            <p>
              Authored by: <strong>{prData.author}</strong>
            </p>
            <div className="stats stats-vertical lg:stats-horizontal shadow mt-4">
              <div className="stat">
                <div className="stat-title">Files Changed</div>
                <div className="stat-value">{prData.filesChanged}</div>
              </div>
              <div className="stat">
                <div className="stat-title">Commits</div>
                <div className="stat-value">{prData.commits}</div>
              </div>
            </div>
            <div className="card-actions justify-end mt-6">
              <a
                href={prData.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                View Pull Request on GitHub
              </a>
            </div>
          </div>
        </div>
      ) : (
        <p>Could not load pull request data.</p>
      )}
    </div>
  );
}
