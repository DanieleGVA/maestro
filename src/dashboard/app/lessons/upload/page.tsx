"use client";

import { useState } from "react";
import { useIngestLesson, useConfirmMapping } from "@/hooks/useApi";
import LessonUpload from "@/components/lessons/LessonUpload";
import ConceptMappingReview from "@/components/lessons/ConceptMappingReview";
import Alert from "@/components/common/Alert";
import type { CandidateMapping, LessonIngestRequest } from "@/types";

/**
 * Lesson upload page.
 * Flow: upload text -> show concept mapping candidates -> confirm/reject.
 * POST to /api/v1/kg/courses/{courseId}/lessons/ingest.
 */
export default function LessonUploadPage() {
  // MVP: single course
  const courseId = "course-1";
  const ingestMutation = useIngestLesson(courseId);
  const confirmMutation = useConfirmMapping();

  const [candidates, setCandidates] = useState<CandidateMapping[]>([]);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleUpload = (data: LessonIngestRequest) => {
    ingestMutation.mutate(data, {
      onSuccess: (result) => {
        setCandidates(result.candidates_for_review);
        setUploadSuccess(true);
      },
    });
  };

  const handleConfirm = (nodeId: string) => {
    confirmMutation.mutate(
      { mappingId: nodeId, action: "confirm" },
      {
        onSuccess: () => {
          setCandidates((prev) => prev.filter((c) => c.node_id !== nodeId));
        },
      },
    );
  };

  const handleReject = (nodeId: string) => {
    confirmMutation.mutate(
      { mappingId: nodeId, action: "reject" },
      {
        onSuccess: () => {
          setCandidates((prev) => prev.filter((c) => c.node_id !== nodeId));
        },
      },
    );
  };

  return (
    <>
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-surface-fg">
          <li>
            <a href="/lessons" className="hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
              Lezioni
            </a>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page" className="font-medium text-page-fg">
            Carica nuova lezione
          </li>
        </ol>
      </nav>

      <h1 className="text-2xl font-bold text-page-fg">Carica nuova lezione</h1>

      {ingestMutation.isError && (
        <div className="mt-4">
          <Alert variant="error">
            Errore durante il caricamento della lezione. Riprova.
          </Alert>
        </div>
      )}

      {uploadSuccess && (
        <div className="mt-4">
          <Alert variant="info">
            Lezione caricata con successo. Revisiona i concetti estratti di seguito.
          </Alert>
        </div>
      )}

      <div className="mt-6">
        {!uploadSuccess ? (
          <LessonUpload onSubmit={handleUpload} isPending={ingestMutation.isPending} />
        ) : (
          <ConceptMappingReview
            candidates={candidates}
            onConfirm={handleConfirm}
            onReject={handleReject}
          />
        )}
      </div>
    </>
  );
}
