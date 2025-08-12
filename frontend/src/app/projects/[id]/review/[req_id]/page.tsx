"use client";

import { useQuery } from '@tanstack/react-query';
import ReactDiffViewer from 'react-diff-viewer-continued';
import AdvancedFeedback from '@/components/features/AdvancedFeedback';

// Mock data for the old and new code
const oldCode = `
function helloWorld() {
  console.log("Hello, World!");
}
`;

const newCode = `
function helloWorld() {
  console.log("Hello, World! I am an AI assistant.");
}
`;

type ReviewData = {
  id: string;
  old_code: string;
  new_code: string;
  // other fields...
};

// Placeholder for the actual API call
const fetchReviewData = async (req_id: string): Promise<ReviewData> => {
  // const res = await fetch(`/api/review/${req_id}`);
  // if (!res.ok) {
  //   throw new Error('Network response was not ok');
  // }
  // return res.json();

  // Mocking data for now
  return {
    id: req_id,
    old_code: oldCode,
    new_code: newCode,
  };
};

export default function ReviewPage({ params }: { params: { id: string, req_id: string } }) {
  const { req_id } = params;

  const { data: reviewData, isLoading, isError, error } = useQuery<ReviewData>({
    queryKey: ['review', req_id],
    queryFn: () => fetchReviewData(req_id),
    enabled: !!req_id,
  });

  if (isLoading) return <div>Loading review...</div>;
  if (isError) return <div>Error: {(error as Error).message}</div>;
  if (!reviewData) return <div>Review data not found.</div>;

  const handleFeedbackSubmit = (feedback: { line: number; comment: string }) => {
    console.log('Feedback submitted:', feedback);
    // Here you would call the backend API to save the feedback
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Review Proposed Changes</h1>

      <div className="mb-8">
        <ReactDiffViewer
          oldValue={reviewData.old_code}
          newValue={reviewData.new_code}
          splitView={true}
          useDarkTheme={true} // Assuming a dark theme is preferred for code
        />
      </div>

      <div className="flex justify-end space-x-4 mb-8">
        <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
          Reject
        </button>
        <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
          Approve
        </button>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Leave Feedback</h2>
        <AdvancedFeedback
          code={reviewData.new_code}
          onSubmitFeedback={handleFeedbackSubmit}
        />
      </div>
    </div>
  );
}
