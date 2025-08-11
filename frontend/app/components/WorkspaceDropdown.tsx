// components/WorkspaceDropdown.tsx

import { ChevronDown, Check } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const workspaces = [
  { key: "bolt", label: "Project Bolt" },
  { key: "magma", label: "Magma Steel" },
  { key: "myapp", label: "My App" },
];

export default function WorkspaceDropdown({
  selected,
  onSelect,
}: {
  selected: string;
  onSelect: (key: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative select-none">
      <button
        className="flex items-center gap-2 text-white bg-zinc-800 rounded-lg px-3 py-1 font-semibold text-sm hover:bg-zinc-700 transition"
        onClick={() => setOpen((o) => !o)}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {workspaces.find((w) => w.key === selected)?.label || "Select Workspace"}
        <ChevronDown size={18} className="ml-1 text-emerald-300" />
      </button>
      {open && (
        <div
          className="absolute left-0 mt-2 w-48 rounded-xl bg-zinc-900 shadow-xl border border-zinc-700 z-40"
          role="listbox"
        >
          {workspaces.map((ws) => (
            <button
              key={ws.key}
              className={clsx(
                "flex items-center gap-2 px-4 py-2 w-full text-left rounded-lg text-sm transition",
                selected === ws.key
                  ? "bg-zinc-800 text-emerald-400 font-semibold"
                  : "hover:bg-zinc-800 text-zinc-200"
              )}
              onClick={() => {
                onSelect(ws.key);
                setOpen(false);
              }}
              role="option"
              aria-selected={selected === ws.key}
            >
              {ws.label}
              {selected === ws.key && (
                <Check size={16} className="ml-auto text-emerald-400" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
