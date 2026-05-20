/**
 * Missions screen -- list of active recovery missions (SCR-ST-06).
 *
 * Shows all nodes in lacuna or in_recupero state with recovery progress.
 * Tone: encouraging. Lacuna = "una porta aperta" (safeguarding).
 *
 * Heading: h1 = "Le tue missioni" (accessibility spec Section 7.3).
 */

import React, { useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import MissionCard from '../../components/MissionCard';
import { useMissions } from '../../hooks/useApi';
import { SPACING, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';
import type { Mission } from '../../types';

const STUDENT_ID = 'me';

export default function MissionsScreen() {
  const router = useRouter();
  const { data: missions, loading, error, fetch } = useMissions(STUDENT_ID);

  useEffect(() => {
    fetch();
  }, []);

  const handleMissionPress = (mission: Mission) => {
    router.push(`/quiz/${mission.quizId ?? mission.id}`);
  };

  if (loading) {
    return (
      <View style={styles.center} accessible accessibilityLabel="Caricamento missioni in corso">
        <ActivityIndicator size="large" color="#1565C0" />
      </View>
    );
  }

  const activeMissions = (missions ?? []).filter(
    (m) => m.state === 'lacuna' || m.state === 'in_recupero',
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading} accessible accessibilityRole="header">
        Le tue missioni
      </Text>

      {error && (
        <View accessible accessibilityRole="alert" accessibilityLiveRegion="polite" style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {activeMissions.length === 0 && !error && (
        <View style={styles.empty}>
          <Text style={styles.emptyTitle}>Nessuna missione attiva</Text>
          <Text style={styles.emptyText}>
            Al momento non ci sono concetti da ripassare. Continua cosi'!
          </Text>
        </View>
      )}

      {activeMissions.map((mission) => (
        <MissionCard
          key={mission.id}
          mission={mission}
          onPress={handleMissionPress}
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: PAGE_COLORS.bg,
  },
  content: {
    padding: SPACING.lg,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: PAGE_COLORS.bg,
  },
  heading: {
    fontSize: TEXT_SIZES['2xl'],
    lineHeight: TEXT_SIZES['2xl'] * LINE_HEIGHTS.tight,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  errorBox: {
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
    padding: SPACING.md,
    marginBottom: SPACING.lg,
    borderLeftWidth: 4,
    borderLeftColor: '#EF6C00',
  },
  errorText: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  empty: {
    paddingVertical: SPACING['2xl'],
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: TEXT_SIZES.lg,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  emptyText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    textAlign: 'center',
  },
});
