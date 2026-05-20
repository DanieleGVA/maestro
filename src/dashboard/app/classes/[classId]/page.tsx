"use client";

import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useState } from "react";
import { useClassHeatmap, useCourseNodes } from "@/hooks/useApi";
import ClassHeatmap from "@/components/heatmap/ClassHeatmap";
import HeatmapLegend from "@/components/heatmap/HeatmapLegend";
import type { StudentHeatmapRow } from "@/types";
import type { MasteryState } from "@/theme/tokens";

/**
 * Class detail page: heatmap view.
 * Per SCR-DOC-08, accessibility-mvp-spec.md Section 5.1.6.
 */
export default function ClassDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const classId = params.classId as string;
  const courseId = searchParams.get("courseId") ?? "";

  const { data: heatmapData, isLoading: heatmapLoading } = useClassHeatmap(classId, courseId);
  const { data: kgNodes, isLoading: nodesLoading } = useCourseNodes(courseId);

  const isLoading = heatmapLoading || nodesLoading;

  // Transform heatmap data into rows for the grid view
  // MVP: generate student rows from heatmap node summaries
  // In production, a dedicated endpoint would return per-student-per-node states
  const macroNodes = (kgNodes ?? []).filter((n) => n.node_type === "macro");

  // MVP placeholder: derive student list from API data or use placeholder
  const students: StudentHeatmapRow[] = [];
  // When real data is available, populate from a per-student endpoint

  const handleCellClick = (studentId: string, nodeId: string) => {
    router.push(`/classes/${classId}/students/${studentId}?courseId=${courseId}&nodeId=${nodeId}`);
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
          <li aria-current="page" className="font-medium text-page-fg">
            Heatmap classe
          </li>
        </ol>
      </nav>

      <h1 className="text-2xl font-bold text-page-fg">Padronanza della classe</h1>

      {isLoading ? (
        <p className="mt-4 text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento in corso...
        </p>
      ) : (
        <>
          <div className="mt-4">
            <HeatmapLegend />
          </div>

          {students.length > 0 ? (
            <div className="mt-4">
              <ClassHeatmap
                macroNodes={macroNodes}
                students={students}
                onCellClick={handleCellClick}
              />
            </div>
          ) : (
            <div className="mt-6">
              {/* Fallback: aggregate view from the existing heatmap API */}
              <h2 className="mb-3 text-lg font-semibold text-page-fg">Riepilogo per concetto</h2>
              {heatmapData && (
                <div className="overflow-x-auto">
                  <table aria-label="Riepilogo padronanza per concetto" className="w-full border-collapse text-sm">
                    <caption className="sr-only">
                      Numero di studenti in ogni stato per ciascun macro-concetto.
                    </caption>
                    <thead>
                      <tr className="border-b-2 border-surface-bg">
                        <th scope="col" className="px-3 py-2 text-left font-semibold">Concetto</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Non introdotto</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Introdotto</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Lacuna</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">In recupero</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Da consolidare</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Consolidato</th>
                        <th scope="col" className="px-3 py-2 text-center font-semibold">Totale</th>
                      </tr>
                    </thead>
                    <tbody>
                      {heatmapData.node_summaries.map((ns) => {
                        const node = macroNodes.find((n) => n.id === ns.node_id);
                        return (
                          <tr key={ns.node_id} className="border-b border-surface-bg">
                            <th scope="row" className="px-3 py-2 text-left font-medium">
                              {node?.label_it ?? ns.node_id}
                            </th>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.non_introdotto ?? 0}</td>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.introdotto ?? 0}</td>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.lacuna ?? 0}</td>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.in_recupero ?? 0}</td>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.da_consolidare ?? 0}</td>
                            <td className="px-3 py-2 text-center">{ns.counts_per_state.consolidato ?? 0}</td>
                            <td className="px-3 py-2 text-center font-medium">{ns.total_students}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </>
  );
}
