"use client";

import { useState } from "react";

export default function AnalyzePrompt() {
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState<"safe" | "risky" | "blocked" | null>(null);
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const checkPrompt = async () => {
    setLoading(true);
    setStatus(null);
    setViolations([]);

    try {
      const res = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          role: "guest", // yoki dynamic
          user_id: "demo_user"
        }),
      });

      const data = await res.json();

      setStatus(data.status);
      setViolations(data.violations || []);
    } catch (err) {
      alert("Server error. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const highlightedPromptInteractive = () => {
    let parts: (string | JSX.Element)[] = [prompt];

    violations.forEach((v) => {
      if (!v.word || !v.suggestions?.length) return;

      const newParts: (string | JSX.Element)[] = [];
      parts.forEach((part) => {
        if (typeof part === "string") {
          const pieces = part.split(new RegExp(`(${v.word})`, "gi"));
          pieces.forEach((p) => {
            if (p.toLowerCase() === v.word.toLowerCase()) {
              newParts.push(
                <button
                  key={Math.random()}
                  onClick={() => {
                    const suggestion = v.suggestions[0];
                    setPrompt((prev) =>
                      prev.replace(new RegExp(v.word, "gi"), suggestion)
                    );
                  }}
                  className="bg-red-100 text-red-800 px-1 rounded hover:underline cursor-pointer"
                  title={`Click to replace with "${v.suggestions[0]}"`}
                >
                  {p}
                </button>
              );
            } else {
              newParts.push(p);
            }
          });
        } else {
          newParts.push(part);
        }
      });

      parts = newParts;
    });

    return <>{parts}</>;
  };

  return (
    <div className="space-y-4 max-w-xl mx-auto">
      <h2 className="text-xl font-bold">ZeroDev Prompt Safety Check</h2>

      <textarea
        rows={4}
        className="w-full p-3 border rounded bg-gray-100"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your project idea..."
      />

      <button
        onClick={checkPrompt}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        {loading ? "Checking..." : "Analyze Prompt"}
      </button>

      {status && (
        <div className={`p-3 rounded ${status === "safe" ? "bg-green-100" : "bg-yellow-100"}`}>
          <p className="font-semibold">
            Status: <span className="capitalize">{status}</span>
          </p>
          {violations.length > 0 && (
            <ul className="mt-2 list-disc list-inside text-sm text-red-700">
              {violations.map((v, i) => (
                <li key={i}>
                  ⚠️ <strong>{v.word || v.pattern}</strong> – {v.message}
                  {v.suggestions?.length > 0 && (
                    <div className="text-xs mt-1 text-gray-600">
                      Try:{" "}
                      {v.suggestions.map((s, idx) => (
                        <span key={idx} className="inline-block px-2 py-0.5 bg-gray-200 rounded mr-1">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {status === "safe" && (
        <div className="bg-green-50 border-l-4 border-green-400 p-3 mt-2 text-green-700 text-sm rounded">
          ✅ Prompt is safe to proceed!
        </div>
      )}

      {violations.length > 0 && (
        <div className="mt-3 p-3 bg-white border rounded text-sm">
          <p className="font-medium mb-1">Interactive Preview (click to fix):</p>
          <div className="prose prose-sm">{highlightedPromptInteractive()}</div>
        </div>
      )}
    </div>
  );
}
