"use client";

import { useAuth } from "@/hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header role="banner" className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
      <span className="text-sm text-surface-fg">Dashboard Docente</span>
      <nav aria-label="Menu utente" className="flex items-center gap-4">
        {user && (
          <span className="text-sm font-medium text-page-fg">{user.username}</span>
        )}
        <button
          onClick={logout}
          className="rounded-md px-3 py-1.5 text-sm text-surface-fg hover:bg-surface-bg focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          Esci
        </button>
      </nav>
    </header>
  );
}
