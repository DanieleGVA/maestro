/**
 * MissionCard -- card for an active recovery mission.
 *
 * Missions pair a lacuna/in_recupero state with recovery content.
 * Tone: encouraging. "Lacuna" is presented as an open door, not a failure
 * (safeguarding rules, CLAUDE.md).
 *
 * Progress bar uses role="progressbar" with aria-valuenow/min/max.
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
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';
import type { Mission } from '../types';

interface MissionCardProps {
  mission: Mission;
  onPress: (mission: Mission) => void;
}

export default function MissionCard({ mission, onPress }: MissionCardProps) {
  const token = MASTERY_TOKENS[mission.state];
  const { current, total } = mission.progress;
  const progressPct = total > 0 ? (current / total) * 100 : 0;

  // Encouraging copy: lacuna = "da ripassare", in_recupero = "in corso"
  const statusCopy =
    mission.state === 'lacuna'
      ? 'Da ripassare'
      : 'Recupero in corso';

  return (
    <TouchableOpacity
      accessible
      accessibilityRole="button"
      accessibilityLabel={`Missione: ${mission.nodeLabel}. ${statusCopy}. Progresso: ${current} di ${total} step completati`}
      accessibilityHint="Tocca due volte per continuare la missione"
      style={styles.card}
      activeOpacity={0.7}
      onPress={() => onPress(mission)}
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.title} numberOfLines={2}>
            {mission.nodeLabel}
          </Text>
          <StateIndicator state={mission.state} size="sm" />
        </View>
        <Text style={styles.subtitle}>{statusCopy}</Text>
      </View>

      {/* Progress bar */}
      <View
        accessible
        accessibilityRole="progressbar"
        accessibilityLabel={`Progresso missione ${mission.nodeLabel}: ${current} di ${total} step completati`}
        accessibilityValue={{ min: 0, max: total, now: current }}
        style={styles.progressTrack}
      >
        <View style={[styles.progressFill, { width: `${progressPct}%` }]} />
      </View>
      <Text style={styles.progressText} accessible={false}>
        {current}/{total} step
      </Text>

      {/* CTA */}
      <View style={styles.cta}>
        <Text style={styles.ctaText}>
          {current === 0 ? 'Inizia il ripasso' : 'Continua'}
        </Text>
      </View>
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
    marginBottom: SPACING.md,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: SPACING.sm,
  },
  title: {
    flex: 1,
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  subtitle: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginTop: SPACING.xs,
  },
  progressTrack: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: SPACING.xs,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#EF6C00',
    borderRadius: 4,
  },
  progressText: {
    fontSize: TEXT_SIZES.xs,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginBottom: SPACING.md,
  },
  cta: {
    backgroundColor: '#1565C0',
    borderRadius: BORDER_RADIUS.sm,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    alignSelf: 'flex-start',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  ctaText: {
    fontSize: TEXT_SIZES.sm,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
});
