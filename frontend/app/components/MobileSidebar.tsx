// components/MobileSidebar.tsx
import { X } from "lucide-react";
import Sidebar from "./Sidebar";

export default function MobileSidebar({ open, onClose }: { open: boolean, onClose: () => void }) {
  return (
    <div
      className={`fixed inset-0 z-50 bg-black/40 transition-opacity duration-200 ${
        open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
      }`}
      aria-hidden={!open}
      onClick={onClose}
    >
      <div
        className={`fixed left-0 top-0 h-full w-64 z-60 bg-gradient-to-b from-zinc-900/95 to-zinc-900/60 backdrop-blur-2xl border-r border-zinc-800 shadow-xl transform transition-transform duration-300
        ${open ? "translate-x-0" : "-translate-x-full"}`}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-end p-4">
          <button onClick={onClose}>
            <X size={28} className="text-zinc-400 hover:text-emerald-400 transition-colors" />
          </button>
        </div>
        <Sidebar />
      </div>
    </div>
  );
}
