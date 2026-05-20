"use client";

import type { CandidateMapping } from "@/types";

interface ConceptMappingReviewProps {
  candidates: CandidateMapping[];
  onConfirm: (mappingNodeId: string) => void;
  onReject: (mappingNodeId: string) => void;
}

/**
 * Review and confirm/reject auto-suggested concept mappings after lesson ingestion.
 */
export default function ConceptMappingReview({ candidates, onConfirm, onReject }: ConceptMappingReviewProps) {
  if (candidates.length === 0) {
    return (
      <p className="text-sm text-surface-fg" role="status">
        Nessun mapping da revisionare.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="font-medium text-page-fg">Concetti estratti dalla lezione</h3>
      <ul className="space-y-2">
        {candidates.map((c) => (
          <li
            key={c.node_id}
            className="flex items-center justify-between rounded-md border border-gray-200 p-3"
          >
            <div>
              <p className="font-medium text-page-fg">{c.label_it}</p>
              {c.description && (
                <p className="text-xs text-surface-fg">{c.description}</p>
              )}
              <p className="mt-1 text-xs text-surface-fg">
                Tipo: {c.node_type} | Confidence: {Math.round(c.composite_score * 100)}%
                {c.llm_explanation && ` | ${c.llm_explanation}`}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onConfirm(c.node_id)}
                aria-label={`Conferma mapping per ${c.label_it}`}
                className="rounded-md bg-maestro-consolidato-bg px-3 py-1.5 text-sm font-medium text-white hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
              >
                Conferma
              </button>
              <button
                onClick={() => onReject(c.node_id)}
                aria-label={`Rifiuta mapping per ${c.label_it}`}
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-surface-fg hover:bg-surface-bg focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
              >
                Rifiuta
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
