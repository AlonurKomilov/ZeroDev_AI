// components/Sidebar.tsx

import { Home, MessageSquare, Settings, Rocket } from "lucide-react";
import SidebarLink from "./SidebarLink";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const navLinks = [
  {
    label: "Prompt",
    href: "/prompt",
    icon: <Home size={22} />,
  },
  {
    label: "Feedback",
    href: "/feedback",
    icon: <MessageSquare size={22} />,
  },
  {
    label: "Settings",
    href: "/settings",
    icon: <Settings size={22} />,
  },
  {
    label: "Deploy",
    href: "/deploy",
    icon: <Rocket size={22} />,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className={clsx(
        "fixed left-0 top-0 z-30 h-screen w-64 flex flex-col",
        "bg-gradient-to-b from-zinc-900/95 to-zinc-900/60 backdrop-blur-2xl",
        "border-r border-zinc-800 shadow-xl"
      )}
    >
      {/* ✅ Branded Project Header */}
      <div className="flex flex-col px-6 py-6">
        <span className="text-xl font-bold tracking-tight text-white">
          ZeroDev <span className="text-emerald-400">V2</span>
        </span>
        <span className="text-xs text-zinc-400">
          powered by <strong>ABC LEGACY LLC</strong>
        </span>
      </div>

      <nav className="flex-1 flex flex-col gap-2 px-3 mt-2">
        {navLinks.map((link) => (
          <SidebarLink
            key={link.href}
            href={link.href}
            icon={link.icon}
            label={link.label}
            active={pathname === link.href}
          />
        ))}
      </nav>

      <div className="mt-auto px-6 pb-6 flex flex-col gap-2">
        <span className="text-xs text-zinc-500">
          v2.0.0 &mdash; ABC LEGACY LLC
        </span>
      </div>
    </aside>
  );
}
