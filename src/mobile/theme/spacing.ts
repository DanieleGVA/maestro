/**
 * MAESTRO spacing and layout tokens.
 *
 * Touch target minimum: 44x44px (WCAG 2.5.5, accessibility spec Section 8.1).
 * Map node touch area: 48x48px.
 */

export const TOUCH_TARGET = {
  min: 44,
  mapNode: 48,
} as const;

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  '2xl': 32,
  '3xl': 48,
} as const;

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  full: 9999,
} as const;

/**
 * Page-level colors (MVP: light theme only).
 * Prepared for V1 theme switching.
 */
export const PAGE_COLORS = {
  bg: '#FFFFFF',
  fg: '#1A1A1A',
  surfaceBg: '#F5F5F5',
  surfaceFg: '#212121',
  borderInput: '#616161',
  iconDefault: '#424242',
} as const;
