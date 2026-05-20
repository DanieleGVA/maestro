/**
 * ProgressBar -- accessible progress bar component.
 *
 * Uses role="progressbar" with aria-valuenow, aria-valuemin, aria-valuemax.
 * Visual + text display of progress (accessibility spec Section 6.3).
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SPACING, BORDER_RADIUS, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';

interface ProgressBarProps {
  current: number;
  total: number;
  label: string;
  color?: string;
  showText?: boolean;
}

export default function ProgressBar({
  current,
  total,
  label,
  color = '#2E7D32',
  showText = true,
}: ProgressBarProps) {
  const pct = total > 0 ? (current / total) * 100 : 0;

  return (
    <View style={styles.wrapper}>
      <View
        accessible
        accessibilityRole="progressbar"
        accessibilityLabel={`${label}: ${current} di ${total}`}
        accessibilityValue={{ min: 0, max: total, now: current }}
        style={styles.track}
      >
        <View style={[styles.fill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
      {showText && (
        <Text style={styles.text} accessible={false}>
          {current}/{total}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  track: {
    flex: 1,
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 4,
  },
  text: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    minWidth: 40,
    textAlign: 'right',
  },
});
