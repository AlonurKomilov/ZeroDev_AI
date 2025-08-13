import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/layouts/Sidebar";
import Topbar from "@/components/layouts/Topbar";
import QueryProvider from "@/components/providers/QueryProvider";
import { ToastProvider } from "@/contexts/ToastContext";

export const metadata: Metadata = {
  title: "AI App Generator",
  description: "Generate applications using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <ToastProvider>
          <QueryProvider>
            <div className="flex h-screen bg-background text-foreground">
              <Sidebar />
              <main className="flex-1 flex flex-col h-screen">
                <Topbar />
                <div className="flex-1 overflow-y-auto p-8">{children}</div>
              </main>
            </div>
          </QueryProvider>
        </ToastProvider>
        <div id="modal-root" />
      </body>
    </html>
  );
}
