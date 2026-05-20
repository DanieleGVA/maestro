/**
 * MAESTRO design tokens -- mastery state colors.
 * Contrast ratios verified per accessibility-mvp-spec.md Section 3.
 * All colors meet WCAG 2.1 AA contrast requirements (>= 4.5:1 for normal text).
 */

export const MASTERY_TOKENS = {
  non_introdotto: {
    bg: "#757575",
    fg: "#FFFFFF",
    border: "#616161",
    icon: "circle-outline",
    label: "Non introdotto",
  },
  introdotto: {
    bg: "#FFFFFF",
    fg: "#1A1A1A",
    border: "#616161",
    icon: "circle-half-full",
    label: "Introdotto",
  },
  lacuna: {
    bg: "#C62828",
    fg: "#FFFFFF",
    border: "#B71C1C",
    icon: "close",
    label: "Lacuna",
  },
  in_recupero: {
    bg: "#EF6C00",
    fg: "#000000",
    border: "#E65100",
    icon: "refresh",
    label: "In recupero",
  },
  da_consolidare: {
    bg: "#FDD835",
    fg: "#000000",
    border: "#F9A825",
    icon: "check-outline",
    label: "Da consolidare",
  },
  consolidato: {
    bg: "#2E7D32",
    fg: "#FFFFFF",
    border: "#1B5E20",
    icon: "check-circle",
    label: "Consolidato",
  },
} as const;

export type MasteryState = keyof typeof MASTERY_TOKENS;

export const MASTERY_STATES: MasteryState[] = [
  "non_introdotto",
  "introdotto",
  "lacuna",
  "in_recupero",
  "da_consolidare",
  "consolidato",
];
