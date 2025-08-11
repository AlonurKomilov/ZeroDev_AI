"use client";

import { useState } from "react";
import { useToast } from "./ToastContext";

export default function FeedbackModal() {
  const [open, setOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const { showToast } = useToast();

  const submitFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    showToast("Thanks for your feedback!", "success");
    setFeedback("");
    setOpen(false);
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="px-4 py-2 bg-zinc-700 rounded-lg text-white hover:bg-emerald-600"
      >
        Feedback
      </button>
      {open && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center">
          <div className="bg-zinc-900 rounded-2xl shadow-2xl p-8 w-[350px] relative">
            <button
              className="absolute top-3 right-3 text-zinc-400 hover:text-red-400 transition"
              onClick={() => setOpen(false)}
            >
              ×
            </button>
            <h2 className="text-xl font-bold mb-4 text-white">Feedback</h2>
            <form className="flex flex-col gap-3" onSubmit={submitFeedback}>
              <textarea
                className="rounded-lg px-4 py-2 bg-zinc-800 text-white placeholder-zinc-500 focus:ring-2 focus:ring-emerald-400"
                placeholder="Share your thoughts…"
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                rows={3}
                required
              />
              <button
                type="submit"
                className="mt-2 bg-emerald-500 hover:bg-emerald-600 transition text-white rounded-lg py-2 font-semibold"
              >
                Submit
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
