"use client";

import { useEffect, useState } from "react";

type FeedbackEntry = {
  user_id: string;
  feedback: string; // "up" or "down"
  suggested_prompt: string;
  original_prompt: string;
  index: number;
  timestamp: string;
};

export default function AdminFeedbackTable() {
  const [logs, setLogs] = useState<FeedbackEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch("/admin/feedback_logs");
        const data = await res.json();
        setLogs(data);
      } catch (err) {
        console.error("Failed to load feedback logs", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">📊 AI Feedback History</h2>

      {loading ? (
        <p>Loading logs...</p>
      ) : logs.length === 0 ? (
        <p className="text-gray-500">No feedback entries yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border text-sm">
            <thead className="bg-gray-100 border-b text-left">
              <tr>
                <th className="px-4 py-2">#</th>
                <th className="px-4 py-2">User</th>
                <th className="px-4 py-2">Original Prompt</th>
                <th className="px-4 py-2">Suggested Prompt</th>
                <th className="px-4 py-2">Feedback</th>
                <th className="px-4 py-2">Variant</th>
                <th className="px-4 py-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{idx + 1}</td>
                  <td className="px-4 py-2 text-blue-800">{log.user_id}</td>
                  <td className="px-4 py-2">{log.original_prompt}</td>
                  <td className="px-4 py-2 text-gray-700">{log.suggested_prompt}</td>
                  <td className="px-4 py-2">
                    {log.feedback === "up" ? "👍" : "👎"}
                  </td>
                  <td className="px-4 py-2">#{log.index}</td>
                  <td className="px-4 py-2 text-gray-500">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
