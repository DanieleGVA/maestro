"use client";

import { useCallback, useRef, useState } from "react";
import { MASTERY_TOKENS, type MasteryState } from "@/theme/tokens";
import type { KGNode, StudentHeatmapRow } from "@/types";
import HeatmapCell from "./HeatmapCell";
import HeatmapLegend from "./HeatmapLegend";
import StateIndicator from "@/components/common/StateIndicator";

interface ClassHeatmapProps {
  macroNodes: KGNode[];
  students: StudentHeatmapRow[];
  onCellClick: (studentId: string, nodeId: string) => void;
}

/**
 * Class heatmap: rows = students, columns = macro-nodes.
 * Accessible as an HTML table with proper th/scope.
 * Keyboard navigable: arrow keys within the grid.
 * Per accessibility-mvp-spec.md Section 5.1.6, 6.5.
 */
export default function ClassHeatmap({ macroNodes, students, onCellClick }: ClassHeatmapProps) {
  const [focusRow, setFocusRow] = useState(0);
  const [focusCol, setFocusCol] = useState(0);
  const gridRef = useRef<HTMLTableElement>(null);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      let newRow = focusRow;
      let newCol = focusCol;
      switch (e.key) {
        case "ArrowDown":
          newRow = Math.min(focusRow + 1, students.length - 1);
          break;
        case "ArrowUp":
          newRow = Math.max(focusRow - 1, 0);
          break;
        case "ArrowRight":
          newCol = Math.min(focusCol + 1, macroNodes.length - 1);
          break;
        case "ArrowLeft":
          newCol = Math.max(focusCol - 1, 0);
          break;
        case "Enter":
        case " ":
          e.preventDefault();
          if (students[focusRow] && macroNodes[focusCol]) {
            onCellClick(students[focusRow].student_id, macroNodes[focusCol].id);
          }
          return;
        default:
          return;
      }
      e.preventDefault();
      setFocusRow(newRow);
      setFocusCol(newCol);
      const cell = gridRef.current?.querySelector(
        `[data-row="${newRow}"][data-col="${newCol}"]`,
      ) as HTMLElement | null;
      cell?.focus();
    },
    [focusRow, focusCol, students, macroNodes, onCellClick],
  );

  return (
    <section aria-labelledby="heatmap-heading">
      <div className="mb-3 flex items-center justify-between">
        <h2 id="heatmap-heading" className="text-lg font-semibold text-page-fg">
          Padronanza della classe
        </h2>
        <HeatmapLegend />
      </div>

      <div className="overflow-x-auto" role="region" aria-label="Tabella heatmap con scorrimento orizzontale">
        <table
          ref={gridRef}
          role="grid"
          aria-label="Mappa padronanza della classe"
          className="w-full border-collapse text-sm"
          onKeyDown={handleKeyDown}
        >
          <caption className="sr-only">
            Stato di padronanza per ogni studente su ogni macro-concetto.
            Usa le frecce per navigare tra le celle, Invio per aprire il dettaglio.
          </caption>
          <thead>
            <tr className="border-b-2 border-surface-bg">
              <th scope="col" className="sticky left-0 bg-white px-3 py-2 text-left font-semibold">
                Studente
              </th>
              {macroNodes.map((node) => (
                <th key={node.id} scope="col" className="px-3 py-2 text-center font-semibold">
                  {node.label_it}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {students.map((student, rowIdx) => (
              <tr key={student.student_id} className="border-b border-surface-bg">
                <th
                  scope="row"
                  className="sticky left-0 bg-white px-3 py-2 text-left font-medium"
                >
                  {student.display_name}
                </th>
                {macroNodes.map((node, colIdx) => {
                  const state = student.states[node.id] ?? "non_introdotto";
                  const token = MASTERY_TOKENS[state];
                  const isFocused = rowIdx === focusRow && colIdx === focusCol;
                  return (
                    <td
                      key={node.id}
                      data-row={rowIdx}
                      data-col={colIdx}
                      tabIndex={isFocused ? 0 : -1}
                      role="gridcell"
                      aria-label={`${student.display_name}, ${node.label_it}: ${token.label}`}
                      className={`cursor-pointer p-1 text-center ${isFocused ? "ring-2 ring-focus ring-offset-1" : ""}`}
                      onClick={() => onCellClick(student.student_id, node.id)}
                      onFocus={() => {
                        setFocusRow(rowIdx);
                        setFocusCol(colIdx);
                      }}
                    >
                      <StateIndicator state={state} size="sm" showLabel={false} />
                      <span className="sr-only">{token.label}</span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
