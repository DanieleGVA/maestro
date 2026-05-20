/**
 * NodeCard -- card for a single knowledge graph node in the mastery map.
 *
 * Shows: node label, state indicator (color + icon + text), micro-node summary.
 * Touch target >= 44x44px (WCAG 2.5.5).
 * accessibilityLabel includes node name and state text (never color alone).
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import StateIndicator from './StateIndicator';
import { MASTERY_TOKENS } from '../theme/tokens';
import { TOUCH_TARGET, SPACING, BORDER_RADIUS, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';
import type { MasteryState } from '../types';

interface NodeCardProps {
  nodeId: string;
  label: string;
  state: MasteryState;
  totalMicros?: number;
  microsConsolidato?: number;
  onPress: (nodeId: string) => void;
}

export default function NodeCard({
  nodeId,
  label,
  state,
  totalMicros,
  microsConsolidato,
  onPress,
}: NodeCardProps) {
  const token = MASTERY_TOKENS[state];
  const hasMicros = totalMicros !== undefined && totalMicros > 0;

  return (
    <TouchableOpacity
      accessible
      accessibilityRole="button"
      accessibilityLabel={`${label}: ${token.label}${hasMicros ? `. ${microsConsolidato} di ${totalMicros} concetti consolidati` : ''}`}
      accessibilityHint="Tocca due volte per aprire il dettaglio"
      style={[styles.card, { borderLeftColor: token.bg, borderLeftWidth: 4 }]}
      activeOpacity={0.7}
      onPress={() => onPress(nodeId)}
    >
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={2}>
          {label}
        </Text>
        <StateIndicator state={state} size="sm" />
      </View>

      {hasMicros && (
        <View style={styles.micros}>
          <View
            accessible
            accessibilityRole="progressbar"
            accessibilityLabel={`Progresso: ${microsConsolidato} di ${totalMicros} concetti consolidati`}
            accessibilityValue={{
              min: 0,
              max: totalMicros,
              now: microsConsolidato,
            }}
            style={styles.progressTrack}
          >
            <View
              style={[
                styles.progressFill,
                {
                  width: `${((microsConsolidato ?? 0) / totalMicros) * 100}%`,
                },
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {microsConsolidato}/{totalMicros}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: PAGE_COLORS.surfaceBg,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
    minHeight: TOUCH_TARGET.min,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: SPACING.md,
  },
  title: {
    flex: 1,
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  micros: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.sm,
    gap: SPACING.sm,
  },
  progressTrack: {
    flex: 1,
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2E7D32',
    borderRadius: 4,
  },
  progressText: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
  },
});
