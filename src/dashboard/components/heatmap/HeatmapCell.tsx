"use client";

import { MASTERY_TOKENS, type MasteryState } from "@/theme/tokens";
import StateIndicator from "@/components/common/StateIndicator";

interface HeatmapCellProps {
  state: MasteryState;
  studentName: string;
  conceptLabel: string;
  onClick?: () => void;
}

/**
 * Single cell in the heatmap grid.
 * Shows color + icon; tooltip via aria-label.
 * Keyboard: Enter/Space to open detail.
 */
export default function HeatmapCell({ state, studentName, conceptLabel, onClick }: HeatmapCellProps) {
  const token = MASTERY_TOKENS[state];
  const label = `${studentName}, ${conceptLabel}: ${token.label}`;

  return (
    <td
      aria-label={label}
      className="cursor-pointer p-1"
      onClick={onClick}
      onKeyDown={(e) => {
        if ((e.key === "Enter" || e.key === " ") && onClick) {
          e.preventDefault();
          onClick();
        }
      }}
      tabIndex={0}
      role="gridcell"
    >
      <StateIndicator state={state} size="sm" showLabel={false} />
      <span className="sr-only">{token.label}</span>
    </td>
  );
}
