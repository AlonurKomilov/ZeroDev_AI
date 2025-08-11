// dashboard/app/components/FancyPromptInput.tsx

"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { useToast } from "./ToastContext";

export default function FancyPromptInput() {
  const [prompt, setPrompt] = useState("");
  const { showToast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      showToast("Prompt is empty!", "error");
      return;
    }
    showToast("Prompt submitted! (fake)", "success");
    setPrompt("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <textarea
        className="w-full rounded-xl bg-zinc-900 p-4 text-white text-lg border border-zinc-700 focus:ring-2 focus:ring-emerald-400 outline-none transition resize-none min-h-[72px]"
        placeholder="Enter your prompt here..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        maxLength={2000}
        autoFocus
      />
      <div className="flex justify-end">
        <button
          type="submit"
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 transition text-white font-semibold px-5 py-2 rounded-xl shadow disabled:opacity-60"
          disabled={!prompt.trim()}
        >
          <Send size={20} />
          Send
        </button>
      </div>
    </form>
  );
}
