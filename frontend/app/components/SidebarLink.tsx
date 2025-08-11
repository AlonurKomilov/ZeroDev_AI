// components/SidebarLink.tsx
import Link from "next/link";
import clsx from "clsx";

type SidebarLinkProps = {
  href: string;
  icon: React.ReactNode;
  label: string;
  active?: boolean;
};

export default function SidebarLink({ href, icon, label, active }: SidebarLinkProps) {
  return (
    <Link
      href={href}
      className={clsx(
        "flex items-center gap-3 px-4 py-2 rounded-xl transition-colors",
        "hover:bg-zinc-800/70 hover:text-emerald-300",
        active
          ? "bg-zinc-800 text-emerald-400 font-semibold shadow"
          : "text-zinc-300"
      )}
      aria-current={active ? "page" : undefined}
    >
      <span className="shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
    </Link>
  );
}
