/**
 * Shared type definitions for E2E test fixtures.
 * Mirrors the canonical 6-state machine from CLAUDE.md.
 */

export type MasteryState =
  | "non_introdotto"
  | "introdotto"
  | "lacuna"
  | "in_recupero"
  | "da_consolidare"
  | "consolidato";
