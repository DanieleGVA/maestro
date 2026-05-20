"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

/**
 * Dashboard home: class summary, active alerts, recent activity.
 */
export default function DashboardHome() {
  const { user } = useAuth();

  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">
        Dashboard
      </h1>
      {user && (
        <p className="mt-1 text-sm text-surface-fg">
          Bentornato, {user.username}
        </p>
      )}

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Class summary card */}
        <Link
          href="/classes"
          className="rounded-lg border border-gray-200 p-6 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          <h2 className="text-lg font-semibold text-page-fg">Le tue classi</h2>
          <p className="mt-2 text-sm text-surface-fg">
            Visualizza la heatmap di padronanza e il dettaglio di ogni studente.
          </p>
        </Link>

        {/* Lessons card */}
        <Link
          href="/lessons"
          className="rounded-lg border border-gray-200 p-6 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          <h2 className="text-lg font-semibold text-page-fg">Lezioni</h2>
          <p className="mt-2 text-sm text-surface-fg">
            Carica nuove lezioni e revisiona i concept mapping suggeriti.
          </p>
        </Link>

        {/* Alerts card */}
        <Link
          href="/alerts"
          className="rounded-lg border border-gray-200 p-6 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          <h2 className="text-lg font-semibold text-page-fg">Alert benessere</h2>
          <p className="mt-2 text-sm text-surface-fg">
            Segnalazioni di benessere rilevate dal sistema.
          </p>
        </Link>
      </div>
    </>
  );
}
