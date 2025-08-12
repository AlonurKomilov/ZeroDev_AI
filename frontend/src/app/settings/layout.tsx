"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const settingsNav = [
  { name: "Profile", href: "/settings/profile" },
  { name: "Billing", href: "/settings/billing" },
  { name: "API Keys", href: "/settings/api-keys" },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <div className="flex">
        <aside className="w-1/4 pr-8">
          <nav className="flex flex-col space-y-2">
            {settingsNav.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  pathname === item.href
                    ? "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </aside>
        <div className="w-3/4">
          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
