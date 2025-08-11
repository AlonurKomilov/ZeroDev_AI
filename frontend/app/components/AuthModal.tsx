// components/AuthModal.tsx

import { X } from "lucide-react";

export default function AuthModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-zinc-900 rounded-2xl shadow-2xl p-8 w-[350px] relative">
        <button
          className="absolute top-3 right-3 text-zinc-400 hover:text-red-400 transition"
          onClick={onClose}
        >
          <X size={24} />
        </button>
        <h2 className="text-xl font-bold mb-4 text-white">Sign In</h2>
        {/* MOCK: User info or simple email input */}
        <form className="flex flex-col gap-3">
          <input
            type="email"
            className="rounded-lg px-4 py-2 bg-zinc-800 text-white placeholder-zinc-500 focus:ring-2 focus:ring-emerald-400"
            placeholder="Email address"
            required
          />
          <button
            type="submit"
            className="mt-2 bg-emerald-500 hover:bg-emerald-600 transition text-white rounded-lg py-2 font-semibold"
          >
            Sign In
          </button>
        </form>
        {/* Or demo account */}
        <div className="mt-4 text-center">
          <span className="text-xs text-zinc-400">Demo: No real auth needed</span>
        </div>
      </div>
    </div>
  );
}
