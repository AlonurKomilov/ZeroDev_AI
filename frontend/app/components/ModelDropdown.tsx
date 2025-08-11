// components/ModelDropdown.tsx

import { ChevronDown, Check } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const models = [
  { key: "gpt-4o", label: "GPT-4o" },
  { key: "claude-3", label: "Claude 3" },
  { key: "mistral", label: "Mistral" },
];

export default function ModelDropdown({
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
        className="flex items-center gap-1 text-emerald-400 bg-zinc-800 rounded-lg px-3 py-1 font-semibold text-sm hover:bg-zinc-700 transition"
        onClick={() => setOpen((o) => !o)}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {models.find((m) => m.key === selected)?.label || "Select AI"}
        <ChevronDown size={18} className="ml-1 text-emerald-300" />
      </button>
      {open && (
        <div
          className="absolute left-0 mt-2 w-36 rounded-xl bg-zinc-900 shadow-xl border border-zinc-700 z-40"
          role="listbox"
        >
          {models.map((model) => (
            <button
              key={model.key}
              className={clsx(
                "flex items-center gap-2 px-4 py-2 w-full text-left rounded-lg text-sm transition",
                selected === model.key
                  ? "bg-zinc-800 text-emerald-400 font-semibold"
                  : "hover:bg-zinc-800 text-zinc-200"
              )}
              onClick={() => {
                onSelect(model.key);
                setOpen(false);
              }}
              role="option"
              aria-selected={selected === model.key}
            >
              {model.label}
              {selected === model.key && (
                <Check size={16} className="ml-auto text-emerald-400" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
