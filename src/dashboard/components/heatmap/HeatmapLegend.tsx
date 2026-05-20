"use client";

import StateIndicator from "@/components/common/StateIndicator";
import { MASTERY_STATES } from "@/theme/tokens";

/**
 * Legend for the six mastery states, always visible near the heatmap.
 */
export default function HeatmapLegend() {
  return (
    <div role="complementary" aria-label="Legenda stati" className="flex flex-wrap gap-2">
      {MASTERY_STATES.map((state) => (
        <StateIndicator key={state} state={state} size="sm" showLabel />
      ))}
    </div>
  );
}
