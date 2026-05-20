"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function ClientLayout({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
      },
    },
  }));
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  return (
    <QueryClientProvider client={queryClient}>
      {isLoginPage ? (
        children
      ) : (
        <>
          <a href="#main-content" className="skip-link">
            Vai al contenuto principale
          </a>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
              <Header />
              <main id="main-content" role="main" className="flex-1 overflow-y-auto p-6">
                {children}
              </main>
            </div>
          </div>
          {/* Live regions for dynamic status updates */}
          <div aria-live="polite" aria-atomic="true" className="sr-only" id="status-live-region" />
          <div aria-live="assertive" aria-atomic="true" className="sr-only" id="alert-live-region" />
        </>
      )}
    </QueryClientProvider>
  );
}
