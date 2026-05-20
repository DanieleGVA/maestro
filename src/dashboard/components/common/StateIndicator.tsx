"use client";

import { MASTERY_TOKENS, type MasteryState } from "@/theme/tokens";

interface StateIndicatorProps {
  state: MasteryState;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

/**
 * SVG icons for each mastery state per accessibility-mvp-spec.md Section 3.1.
 * Each icon is visually distinct without relying on color (WCAG 1.4.1, F9.3).
 */
function MasteryIcon({ state, size }: { state: MasteryState; size: number }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", "aria-hidden": true as const };
  switch (state) {
    case "non_introdotto":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
        </svg>
      );
    case "introdotto":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
          <circle cx="12" cy="12" r="5" fill="currentColor" />
        </svg>
      );
    case "lacuna":
      return (
        <svg {...common}>
          <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      );
    case "in_recupero":
      return (
        <svg {...common}>
          <path d="M12 4v8l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          <path d="M4 12a8 8 0 1 1 3 6" stroke="currentColor" strokeWidth="2" fill="none" />
        </svg>
      );
    case "da_consolidare":
      return (
        <svg {...common}>
          <path d="M6 12l4 4 8-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
        </svg>
      );
    case "consolidato":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="10" fill="currentColor" />
          <path d="M7 12l3 3 6-6" stroke="white" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        </svg>
      );
  }
}

const SIZES = { sm: 16, md: 20, lg: 24 } as const;

/**
 * Badge displaying mastery state with color + icon + text.
 * Never color alone (WCAG 1.4.1, F9.3).
 */
export default function StateIndicator({ state, size = "md", showLabel = true }: StateIndicatorProps) {
  const token = MASTERY_TOKENS[state];
  const px = SIZES[size];

  return (
    <span
      role="img"
      aria-label={token.label}
      className="inline-flex items-center gap-1.5 rounded px-2 py-1 text-sm font-medium"
      style={{
        backgroundColor: token.bg,
        color: token.fg,
        border: `1.5px solid ${token.border}`,
      }}
    >
      <MasteryIcon state={state} size={px} />
      {showLabel && <span>{token.label}</span>}
    </span>
  );
}
