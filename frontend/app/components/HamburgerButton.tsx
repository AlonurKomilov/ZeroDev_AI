// components/HamburgerButton.tsx
import { Menu } from "lucide-react";

export default function HamburgerButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      className="lg:hidden p-2 rounded-md hover:bg-zinc-800 transition-colors"
      onClick={onClick}
      aria-label="Open sidebar"
    >
      <Menu size={28} className="text-white" />
    </button>
  );
}
