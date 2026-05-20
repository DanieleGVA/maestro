"use client";

import StateIndicator from "@/components/common/StateIndicator";
import ProgressBar from "@/components/common/ProgressBar";
import type { NodeState } from "@/types";
import type { KGNode } from "@/types";
import { MASTERY_TOKENS, type MasteryState } from "@/theme/tokens";

interface StudentMapProps {
  nodes: NodeState[];
  kgNodes: KGNode[];
  onNodeClick: (nodeId: string) => void;
}

/**
 * Student mastery map: list of macro nodes with rollup state and micro breakdown.
 */
export default function StudentMap({ nodes, kgNodes, onNodeClick }: StudentMapProps) {
  const macroNodes = kgNodes.filter((n) => n.node_type === "macro");
  const microByMacro = new Map<string, KGNode[]>();
  for (const n of kgNodes) {
    if (n.node_type === "micro" && n.macro_id) {
      const list = microByMacro.get(n.macro_id) ?? [];
      list.push(n);
      microByMacro.set(n.macro_id, list);
    }
  }

  const stateByNodeId = new Map<string, MasteryState>();
  for (const ns of nodes) {
    stateByNodeId.set(ns.node_id, ns.current_state);
  }

  return (
    <div className="space-y-4">
      {macroNodes.map((macro) => {
        const micros = microByMacro.get(macro.id) ?? [];
        const microStates = micros.map((m) => stateByNodeId.get(m.id) ?? "non_introdotto");
        const consolidatedCount = microStates.filter((s) => s === "consolidato").length;

        // Worst-state rollup per ADR-005 ordering
        const STATE_ORDER: Record<string, number> = {
          lacuna: 0,
          in_recupero: 1,
          non_introdotto: 2,
          introdotto: 3,
          da_consolidare: 4,
          consolidato: 5,
        };
        const worstState = (microStates.length > 0
          ? microStates.reduce((a, b) => ((STATE_ORDER[a] ?? 5) < (STATE_ORDER[b] ?? 5) ? a : b))
          : "non_introdotto") as MasteryState;

        return (
          <div
            key={macro.id}
            className="rounded-lg border border-gray-200 p-4"
          >
            <div className="flex items-center justify-between">
              <button
                onClick={() => onNodeClick(macro.id)}
                className="text-left font-medium text-page-fg hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
              >
                {macro.label_it}
              </button>
              <StateIndicator state={worstState} size="sm" />
            </div>
            <ProgressBar
              current={consolidatedCount}
              total={micros.length}
              label={`${macro.label_it}: ${consolidatedCount} di ${micros.length} consolidati`}
            />
            <div className="mt-2 flex flex-wrap gap-1">
              {micros.map((m) => {
                const s = stateByNodeId.get(m.id) ?? "non_introdotto";
                return (
                  <button
                    key={m.id}
                    onClick={() => onNodeClick(m.id)}
                    className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
                    aria-label={`${m.label_it}: ${MASTERY_TOKENS[s].label}`}
                    title={`${m.label_it}: ${MASTERY_TOKENS[s].label}`}
                  >
                    <StateIndicator state={s} size="sm" showLabel={false} />
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
