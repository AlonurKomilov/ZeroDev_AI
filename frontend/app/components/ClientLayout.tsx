// dashboard/app/components/ClientLayout.tsx

"use client";

import ThemeToggle from './ThemeToggle';
import { ToastProvider } from './ToastContext';
import Sidebar from './Sidebar';
import MobileSidebar from './MobileSidebar';
import HamburgerButton from './HamburgerButton';
import { useState } from "react";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <ToastProvider>
      {/* Topbar (mobile only) */}
      <div className="flex items-center justify-between lg:hidden px-4 py-4">
        <div className="flex items-center gap-2">
          <HamburgerButton onClick={() => setMobileOpen(true)} />
          <span className="font-bold text-white text-xl">ZeroDev</span>
        </div>
        <ThemeToggle />
      </div>
      {/* Sidebar (desktop only) */}
      <div className="hidden lg:flex min-h-screen">
        <Sidebar />
        <main className="flex-1 ml-64 px-8 py-8">{children}</main>
      </div>
      {/* Mobile Drawer */}
      <MobileSidebar open={mobileOpen} onClose={() => setMobileOpen(false)} />
      {/* Main content (mobile, sidebar closed) */}
      <div className="lg:hidden px-4 py-2">{children}</div>
    </ToastProvider>
  );
}
