"use client";

import React, { useState } from "react";

type Suggestion = {
  suggested_prompt: string;
  confidence: number;
  explanation?: string;
};

interface SuggestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  suggestions: Suggestion[];
  onApply: (value: string) => void;
  originalPrompt: string;
}

export default function SuggestionModal({
  isOpen,
  onClose,
  suggestions,
  onApply,
  originalPrompt
}: SuggestionModalProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<Record<number, string>>({});

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 1500);
  };

  const sendFeedback = async (idx: number, type: "up" | "down", s: Suggestion) => {
    if (feedback[idx]) return;

    try {
      const res = await fetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_user",
          feedback: type,
          suggested_prompt: s.suggested_prompt,
          original_prompt: originalPrompt,
          index: idx
        }),
      });

      if (res.ok) {
        setFeedback((prev) => ({ ...prev, [idx]: type }));
        console.log("✅ Feedback sent:", type, idx);
      } else {
        console.error("❌ Feedback failed");
      }
    } catch (err) {
      console.error("⚠️ Feedback error:", err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6 relative">
        <h3 className="text-lg font-semibold mb-4">✍️ AI Suggestions</h3>

        <ul className="space-y-3">
          {suggestions.map((s, idx) => (
            <li
              key={idx}
              className="border rounded p-3 hover:bg-gray-100 transition relative"
            >
              <p
                className="text-sm text-gray-800 mb-1 cursor-pointer"
                onClick={() => {
                  onApply(s.suggested_prompt);
                  onClose();
                }}
              >
                {s.suggested_prompt}
              </p>

              {s.explanation && (
                <p className="text-xs text-gray-600 italic mb-1">
                  💡 {s.explanation}
                </p>
              )}

              <div className="w-full bg-gray-200 h-2 rounded">
                <div
                  className="h-2 bg-green-500 rounded"
                  style={{ width: `${s.confidence * 100}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Confidence: {(s.confidence * 100).toFixed(0)}%
              </p>

              <div className="mt-2 flex gap-3 items-center">
                <button
                  onClick={() => handleCopy(s.suggested_prompt, idx)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  📋 {copiedIndex === idx ? "Copied!" : "Copy"}
                </button>

                <div className="flex items-center gap-1 ml-auto text-sm">
                  <button
                    onClick={() => sendFeedback(idx, "up", s)}
                    disabled={feedback[idx] === "up"}
                    className={`hover:text-green-600 ${
                      feedback[idx] === "up" ? "text-green-600 font-bold" : "text-gray-500"
                    }`}
                  >
                    👍
                  </button>
                  <button
                    onClick={() => sendFeedback(idx, "down", s)}
                    disabled={feedback[idx] === "down"}
                    className={`hover:text-red-600 ${
                      feedback[idx] === "down" ? "text-red-600 font-bold" : "text-gray-500"
                    }`}
                  >
                    👎
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        <button
          onClick={onClose}
          className="absolute top-2 right-3 text-gray-500 hover:text-gray-700 text-xl"
        >
          &times;
        </button>
      </div>
    </div>
  );
}
