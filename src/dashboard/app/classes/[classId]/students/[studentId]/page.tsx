"use client";

import { Suspense, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useCourseNodes, useStudentMap, useTeacherOverride } from "@/hooks/useApi";
import StudentMap from "@/components/students/StudentMap";
import OverrideModal from "@/components/students/OverrideModal";
import HeatmapLegend from "@/components/heatmap/HeatmapLegend";
import Alert from "@/components/common/Alert";
import type { MasteryState } from "@/theme/tokens";

/**
 * Student detail page content: full mastery map with override capability.
 */
function StudentDetailContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const studentId = params.studentId as string;
  const classId = params.classId as string;
  // In MVP, classId = courseId. Fall back to query param for backwards compat.
  const courseId = searchParams.get("courseId") ?? classId;
  const highlightNodeId = searchParams.get("nodeId");

  const { data: studentMap, isLoading: mapLoading, isError: mapError, refetch: refetchMap } =
    useStudentMap(studentId, courseId);
  const { data: kgNodes, isLoading: nodesLoading, isError: nodesError, refetch: refetchNodes } =
    useCourseNodes(courseId);

  const [overrideNode, setOverrideNode] = useState<{
    nodeId: string;
    nodeLabel: string;
    currentState: MasteryState;
  } | null>(null);

  const overrideMutation = useTeacherOverride(
    studentId,
    overrideNode?.nodeId ?? "",
    courseId,
  );

  const isLoading = mapLoading || nodesLoading;
  const isError = mapError || nodesError;

  const handleRetry = () => {
    refetchMap();
    refetchNodes();
  };

  const handleNodeClick = (nodeId: string) => {
    if (!studentMap || !kgNodes) return;
    const kgNode = kgNodes.find((n) => n.id === nodeId);
    const nodeState = studentMap.nodes.find((n) => n.node_id === nodeId);
    if (kgNode) {
      setOverrideNode({
        nodeId,
        nodeLabel: kgNode.label_it,
        currentState: (nodeState?.current_state ?? "non_introdotto") as MasteryState,
      });
    }
  };

  const handleOverrideSubmit = (targetState: MasteryState, motivation: string) => {
    overrideMutation.mutate(
      { target_state: targetState, motivation },
      {
        onSuccess: () => setOverrideNode(null),
      },
    );
  };

  return (
    <>
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-surface-fg">
          <li>
            <a href="/classes" className="hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
              Classi
            </a>
          </li>
          <li aria-hidden="true">/</li>
          <li>
            <a
              href={`/classes/${classId}`}
              className="hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            >
              Heatmap classe
            </a>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page" className="font-medium text-page-fg">
            Studente
          </li>
        </ol>
      </nav>

      <h1 className="text-2xl font-bold text-page-fg">Dettaglio studente</h1>
      <p className="mt-1 text-sm text-surface-fg">ID: {studentId}</p>

      <div className="mt-4">
        <HeatmapLegend />
      </div>

      {isLoading && (
        <p className="mt-4 text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento mappa padronanza...
        </p>
      )}

      {isError && !isLoading && (
        <div className="mt-4">
          <Alert variant="error">
            Errore nel caricamento dei dati.
          </Alert>
          <button
            onClick={handleRetry}
            className="mt-3 rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
          >
            Riprova
          </button>
        </div>
      )}

      {!isLoading && !isError && studentMap && kgNodes ? (
        <div className="mt-4">
          <h2 className="mb-3 text-lg font-semibold text-page-fg">Mappa padronanza</h2>
          <p className="mb-4 text-sm text-surface-fg">
            Clicca su un nodo per effettuare un override dello stato.
          </p>
          <StudentMap
            nodes={studentMap.nodes}
            kgNodes={kgNodes}
            onNodeClick={handleNodeClick}
          />
        </div>
      ) : (
        !isLoading && !isError && (
          <p className="mt-4 text-sm text-surface-fg">Nessun dato disponibile.</p>
        )
      )}

      {overrideNode && (
        <OverrideModal
          isOpen={!!overrideNode}
          onClose={() => setOverrideNode(null)}
          studentName={studentId}
          nodeLabel={overrideNode.nodeLabel}
          currentState={overrideNode.currentState}
          onSubmit={handleOverrideSubmit}
          isPending={overrideMutation.isPending}
        />
      )}
    </>
  );
}

export default function StudentDetailPage() {
  return (
    <Suspense
      fallback={
        <p className="text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento...
        </p>
      }
    >
      <StudentDetailContent />
    </Suspense>
  );
}
