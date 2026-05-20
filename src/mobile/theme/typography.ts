/**
 * MAESTRO typography tokens.
 *
 * Font: Inter (MVP). Line-height 1.5 per accessibility spec Section 4.
 * Font scale slider range: 12-24pt (F9.4).
 */

export const FONT_FAMILY = 'Inter';

export const FONT_SCALE = {
  min: 12,
  max: 24,
  default: 16,
} as const;

/**
 * Compute a scaled font size based on user preference (12-24pt).
 */
export function scaledFontSize(basePx: number, userPt: number): number {
  const clamped = Math.max(FONT_SCALE.min, Math.min(FONT_SCALE.max, userPt));
  return basePx * (clamped / FONT_SCALE.default);
}

/**
 * Typography scale (accessibility-mvp-spec.md Section 4.2).
 * Values are base pixel sizes before user scaling.
 */
export const TEXT_SIZES = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
} as const;

export const LINE_HEIGHTS = {
  tight: 1.25,
  normal: 1.5,
  relaxed: 1.75,
} as const;
