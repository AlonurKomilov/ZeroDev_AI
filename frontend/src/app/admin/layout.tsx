import React from 'react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="absolute inset-0 bg-black/20" />
      <div className="relative z-10">
        {/* Admin Header */}
        <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">⚡</span>
                </div>
                <h1 className="text-xl font-bold text-white">Admin Dashboard</h1>
                <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                  SECURE
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-white/70 text-sm">Authorized Access Only</span>
              </div>
            </div>
          </div>
        </header>
        
        {/* Admin Content */}
        <main className="container mx-auto px-6 py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
