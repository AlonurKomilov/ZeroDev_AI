// components/Topbar.tsx

import { UserCircle, Menu } from "lucide-react";
import ModelDropdown from "./ModelDropdown";
import WorkspaceDropdown from "./WorkspaceDropdown";
import AuthModal from "./AuthModal";
import { useState } from "react";

export default function Topbar() {
  const [selectedModel, setSelectedModel] = useState("gpt-4o");
  const [selectedWorkspace, setSelectedWorkspace] = useState("bolt");
  const [authOpen, setAuthOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState<{ name?: string } | null>(null);

  return (
    <>
      <header
        className="fixed top-0 left-0 z-40 w-full h-16 flex items-center justify-between
        bg-gradient-to-tr from-zinc-950/90 via-zinc-900/80 to-zinc-950/80
        border-b border-zinc-800 backdrop-blur-xl shadow-lg px-4"
      >
        {/* Chap: Logo + Hamburger (mobil uchun) */}
        <div className="flex items-center gap-2">
          {/* Hamburger faqat mobilda */}
          <button
            className="lg:hidden mr-2 p-2 rounded-md hover:bg-zinc-800"
            onClick={() => setMenuOpen((m) => !m)}
            aria-label="Open menu"
          >
            <Menu size={26} className="text-white" />
          </button>
          <span className="text-lg font-bold tracking-tight text-white select-none">ZeroDev</span>
        </div>
        {/* Orta: Workspace va ModelDropdown faqat md/lg+ */}
        <div className="hidden md:flex items-center gap-3">
          <WorkspaceDropdown
            selected={selectedWorkspace}
            onSelect={setSelectedWorkspace}
          />
          <ModelDropdown
            selected={selectedModel}
            onSelect={setSelectedModel}
          />
        </div>
        {/* O‘ng: User avatar/profil */}
        <div className="flex items-center gap-4">
          <button
            className="flex items-center gap-2 text-white hover:text-emerald-400 transition"
            title={user ? "Account" : "Sign in"}
            onClick={() => setAuthOpen(true)}
          >
            <UserCircle size={32} />
            <span className="hidden sm:inline font-medium text-sm">
              {user?.name || "Sign in"}
            </span>
          </button>
        </div>
      </header>
      {/* Mobile Dropmenu: Workspace va ModelDropdown */}
      {menuOpen && (
        <div className="fixed top-16 left-0 z-40 w-full bg-zinc-950 border-b border-zinc-800 md:hidden flex flex-col px-4 pb-4 gap-2 animate-fadeIn">
          <WorkspaceDropdown
            selected={selectedWorkspace}
            onSelect={(k) => { setSelectedWorkspace(k); setMenuOpen(false); }}
          />
          <ModelDropdown
            selected={selectedModel}
            onSelect={(k) => { setSelectedModel(k); setMenuOpen(false); }}
          />
        </div>
      )}
      {/* Auth Modal */}
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </>
  );
}
