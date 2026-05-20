/**
 * MAESTRO design tokens -- mastery state colors.
 *
 * Source: accessibility-mvp-spec.md Section 3.1 (corrected contrast values).
 * All ratios verified for WCAG 2.1 AA (>= 4.5:1 for normal text).
 *
 * Each state has: bg, fg, border, icon name, label.
 * Color alone is NEVER used to convey state (F9.3, WCAG 1.4.1).
 */

export const MASTERY_TOKENS = {
  non_introdotto: {
    bg: '#757575',
    fg: '#FFFFFF',
    border: '#616161',
    icon: 'circle-outline' as const,
    label: 'Non introdotto',
  },
  introdotto: {
    bg: '#FFFFFF',
    fg: '#1A1A1A',
    border: '#616161',
    icon: 'circle-half-full' as const,
    label: 'Introdotto',
  },
  lacuna: {
    bg: '#FF8F00',
    fg: '#000000',
    border: '#EF6C00',
    icon: 'alert-circle-outline' as const,
    label: 'Lacuna',
  },
  in_recupero: {
    bg: '#EF6C00',
    fg: '#000000',
    border: '#E65100',
    icon: 'refresh' as const,
    label: 'In recupero',
  },
  da_consolidare: {
    bg: '#FDD835',
    fg: '#000000',
    border: '#F9A825',
    icon: 'check-outline' as const,
    label: 'Da consolidare',
  },
  consolidato: {
    bg: '#2E7D32',
    fg: '#FFFFFF',
    border: '#1B5E20',
    icon: 'check-circle' as const,
    label: 'Consolidato',
  },
} as const;

export type MasteryStateKey = keyof typeof MASTERY_TOKENS;

/**
 * Focus ring token (accessibility-mvp-spec.md Section 5.2).
 */
export const FOCUS_RING = {
  color: '#1565C0',
  width: 2,
  offset: 2,
} as const;
