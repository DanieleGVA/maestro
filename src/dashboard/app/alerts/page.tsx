"use client";

import { useState } from "react";
import Alert from "@/components/common/Alert";

interface WellbeingAlert {
  id: string;
  studentPseudoId: string;
  phrase: string;
  timestamp: string;
  read: boolean;
}

/**
 * Wellbeing alerts page.
 * MVP: displays hardcoded placeholder. Production: fetched from safeguarding API.
 * Per phase3-compliance-mvp.md Section T3.2 (wellbeing keyword alert).
 */
export default function AlertsPage() {
  const [alerts, setAlerts] = useState<WellbeingAlert[]>([
    // MVP placeholder data
  ]);

  const markAsRead = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a)),
    );
  };

  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">Alert benessere</h1>
      <p className="mt-1 text-sm text-surface-fg">
        Segnalazioni di possibile disagio rilevate dal sistema tramite analisi delle parole chiave.
      </p>

      <div className="mt-6 space-y-4">
        {alerts.length === 0 ? (
          <p className="text-sm text-surface-fg" role="status">
            Nessun alert attivo.
          </p>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              role="alert"
              aria-live="assertive"
              className={`rounded-lg border p-4 ${
                alert.read
                  ? "border-gray-200 bg-gray-50"
                  : "border-maestro-in-recupero-border bg-orange-50"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-page-fg">
                    Segnalazione benessere
                  </p>
                  <p className="mt-1 text-sm text-surface-fg">
                    Studente: {alert.studentPseudoId}
                  </p>
                  <p className="mt-1 text-sm text-surface-fg">
                    Frase rilevata: &ldquo;{alert.phrase}&rdquo;
                  </p>
                  <p className="mt-1 text-xs text-surface-fg">
                    {new Date(alert.timestamp).toLocaleString("it-IT")}
                  </p>
                </div>
                {!alert.read && (
                  <button
                    onClick={() => markAsRead(alert.id)}
                    className="rounded-md bg-focus px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
                  >
                    Ho preso visione
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </>
  );
}
