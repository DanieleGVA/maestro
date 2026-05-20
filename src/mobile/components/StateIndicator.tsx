/**
 * StateIndicator -- renders mastery state with color + icon + text label.
 *
 * WCAG 1.4.1: Color is NEVER the only means to convey information.
 * Every state is indicated by color background + distinct SVG icon + text label.
 *
 * Colors from accessibility-mvp-spec.md Section 3.1 (corrected contrast).
 */

import React from 'react';
import { View, Text, StyleSheet, AccessibilityRole } from 'react-native';
import Svg, { Circle, Path } from 'react-native-svg';
import { MASTERY_TOKENS, type MasteryStateKey } from '../theme/tokens';
import { TOUCH_TARGET, SPACING, BORDER_RADIUS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';

interface StateIndicatorProps {
  state: MasteryStateKey;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const ICON_SIZES = { sm: 16, md: 20, lg: 24 } as const;
const BADGE_PADDINGS = {
  sm: { v: 2, h: 6 },
  md: { v: 4, h: 8 },
  lg: { v: 6, h: 12 },
} as const;

/**
 * Renders the SVG icon for each mastery state.
 * Each icon is visually distinct (accessibility spec Section 3.2 daltonismo).
 */
function StateIcon({ state, size, color }: { state: MasteryStateKey; size: number; color: string }) {
  const s = size;
  const half = s / 2;

  switch (state) {
    case 'non_introdotto':
      // Empty circle
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Circle cx="12" cy="12" r="10" fill="none" stroke={color} strokeWidth="2" />
        </Svg>
      );
    case 'introdotto':
      // Circle with center dot
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Circle cx="12" cy="12" r="10" fill="none" stroke={color} strokeWidth="2" />
          <Circle cx="12" cy="12" r="5" fill={color} />
        </Svg>
      );
    case 'lacuna':
      // X cross
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Path
            d="M6 6l12 12M18 6L6 18"
            stroke={color}
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </Svg>
      );
    case 'in_recupero':
      // Circular arrow (refresh)
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Path
            d="M12 4v8l4 4"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
          <Path
            d="M4 12a8 8 0 1 1 3 6"
            stroke={color}
            strokeWidth="2"
            fill="none"
          />
        </Svg>
      );
    case 'da_consolidare':
      // Check outline
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Path
            d="M6 12l4 4 8-8"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
        </Svg>
      );
    case 'consolidato':
      // Filled circle with check
      return (
        <Svg width={s} height={s} viewBox="0 0 24 24" accessibilityElementsHidden>
          <Circle cx="12" cy="12" r="10" fill={color} />
          <Path
            d="M7 12l3 3 6-6"
            stroke={state === 'consolidato' ? '#FFFFFF' : color}
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
        </Svg>
      );
  }
}

export default function StateIndicator({
  state,
  size = 'md',
  showLabel = true,
}: StateIndicatorProps) {
  const token = MASTERY_TOKENS[state];
  const iconSize = ICON_SIZES[size];
  const padding = BADGE_PADDINGS[size];
  const fontSize = size === 'sm' ? TEXT_SIZES.xs : size === 'md' ? TEXT_SIZES.sm : TEXT_SIZES.base;

  return (
    <View
      accessible
      accessibilityRole={'image' as AccessibilityRole}
      accessibilityLabel={token.label}
      style={[
        styles.badge,
        {
          backgroundColor: token.bg,
          borderColor: token.border,
          paddingVertical: padding.v,
          paddingHorizontal: padding.h,
          minHeight: size === 'sm' ? undefined : TOUCH_TARGET.min,
        },
      ]}
    >
      <StateIcon state={state} size={iconSize} color={token.fg} />
      {showLabel && (
        <Text
          style={[
            styles.label,
            { color: token.fg, fontSize, lineHeight: fontSize * LINE_HEIGHTS.normal },
          ]}
        >
          {token.label}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
    borderWidth: 1.5,
    borderRadius: BORDER_RADIUS.sm,
    alignSelf: 'flex-start',
  },
  label: {
    fontFamily: 'Inter',
    fontWeight: '500',
  },
});
