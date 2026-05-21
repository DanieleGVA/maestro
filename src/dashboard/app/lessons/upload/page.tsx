"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useIngestLesson, useConfirmMapping, useTeacherCourses } from "@/hooks/useApi";
import LessonUpload from "@/components/lessons/LessonUpload";
import ConceptMappingReview from "@/components/lessons/ConceptMappingReview";
import Alert from "@/components/common/Alert";
import type { CandidateMapping, LessonIngestRequest } from "@/types";

/** Seed course ID used as default when no courseId is provided. */
const DEFAULT_COURSE_ID = "30000000-0000-0000-0000-000000000001";

/**
 * Lesson upload page content.
 * Flow: select course (or use default) -> upload text -> show concept mapping candidates -> confirm/reject.
 * POST to /api/v1/kg/courses/{courseId}/lessons/ingest.
 */
function LessonUploadContent() {
  const searchParams = useSearchParams();
  const courseIdParam = searchParams.get("courseId");

  // Fetch available courses so teacher can select one
  const { data: courses, isLoading: coursesLoading } = useTeacherCourses();

  const [selectedCourseId, setSelectedCourseId] = useState(
    courseIdParam ?? DEFAULT_COURSE_ID,
  );

  const ingestMutation = useIngestLesson(selectedCourseId);
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

      {/* Course selector */}
      {!uploadSuccess && (
        <div className="mt-4">
          <label htmlFor="course-select" className="mb-1 block text-sm font-medium text-page-fg">
            Corso
          </label>
          {coursesLoading ? (
            <p className="text-sm text-surface-fg" role="status" aria-live="polite">
              Caricamento corsi...
            </p>
          ) : courses && courses.length > 0 ? (
            <select
              id="course-select"
              value={selectedCourseId}
              onChange={(e) => setSelectedCourseId(e.target.value)}
              className="w-full max-w-md rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.class_name || c.name} - {c.subject}
                </option>
              ))}
            </select>
          ) : (
            <p className="text-sm text-surface-fg">
              Nessun corso disponibile. Viene utilizzato il corso predefinito.
            </p>
          )}
        </div>
      )}

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

export default function LessonUploadPage() {
  return (
    <Suspense
      fallback={
        <p className="text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento...
        </p>
      }
    >
      <LessonUploadContent />
    </Suspense>
  );
}
