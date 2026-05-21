"use client";

import { useAlerts } from "@/hooks/useApi";
import Alert from "@/components/common/Alert";
import api from "@/lib/api";

/**
 * Wellbeing alerts page.
 * Fetches from GET /api/v1/safeguarding/alerts.
 * Per phase3-compliance-mvp.md Section T3.2 (wellbeing keyword alert).
 */

const SEVERITY_STYLES: Record<string, { border: string; bg: string; badge: string; badgeText: string; label: string }> = {
  high: {
    border: "border-maestro-lacuna-border",
    bg: "bg-red-50",
    badge: "bg-red-100 text-red-800",
    badgeText: "text-red-800",
    label: "Alta",
  },
  medium: {
    border: "border-maestro-in-recupero-border",
    bg: "bg-orange-50",
    badge: "bg-orange-100 text-orange-800",
    badgeText: "text-orange-800",
    label: "Media",
  },
  low: {
    border: "border-focus",
    bg: "bg-blue-50",
    badge: "bg-blue-100 text-blue-800",
    badgeText: "text-blue-800",
    label: "Bassa",
  },
};

export default function AlertsPage() {
  const { data: alerts, isLoading, isError, refetch } = useAlerts();

  const markAsRead = async (id: string) => {
    try {
      await api.post(`/api/v1/safeguarding/alerts/${id}/acknowledge`);
      refetch();
    } catch {
      // Optimistic: refetch regardless
      refetch();
    }
  };

  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">Alert benessere</h1>
      <p className="mt-1 text-sm text-surface-fg">
        Segnalazioni di possibile disagio rilevate dal sistema tramite analisi delle parole chiave.
      </p>

      {isLoading && (
        <p className="mt-6 text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento...
        </p>
      )}

      {isError && !isLoading && (
        <div className="mt-6">
          <Alert variant="error">
            Errore nel caricamento dei dati.
          </Alert>
          <button
            onClick={() => refetch()}
            className="mt-3 rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
          >
            Riprova
          </button>
        </div>
      )}

      {!isLoading && !isError && (
        <div className="mt-6 space-y-4">
          {(!alerts || alerts.length === 0) ? (
            <p className="text-sm text-surface-fg" role="status">
              Nessun alert attivo.
            </p>
          ) : (
            alerts.map((alert) => {
              const severity = SEVERITY_STYLES[alert.severity] ?? SEVERITY_STYLES.low;
              return (
                <div
                  key={alert.id}
                  role="alert"
                  aria-live="assertive"
                  className={`rounded-lg border p-4 ${
                    alert.read
                      ? "border-gray-200 bg-gray-50"
                      : `${severity.border} ${severity.bg}`
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-page-fg">
                          Segnalazione benessere
                        </p>
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${severity.badge}`}
                        >
                          {severity.label}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-surface-fg">
                        Studente: {alert.student_pseudo_id}
                      </p>
                      <p className="mt-1 text-sm text-surface-fg">
                        Frase rilevata: &ldquo;{alert.phrase}&rdquo;
                      </p>
                      {alert.context && (
                        <p className="mt-1 text-sm text-surface-fg">
                          Contesto: {alert.context}
                        </p>
                      )}
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
              );
            })
          )}
        </div>
      )}
    </>
  );
}
