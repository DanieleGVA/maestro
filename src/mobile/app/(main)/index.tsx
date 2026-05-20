/**
 * Home / Dashboard screen (SCR-ST-03).
 *
 * Shows:
 * - Welcome message with student name (encouraging tone)
 * - Summary: consolidated/total nodes, active missions, next quiz
 * - Quick links to map and missions
 *
 * Heading hierarchy: h1 = "Bentornato, {nome}"
 * (accessibility spec Section 7.3).
 */

import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useStudentState } from '../../hooks/useStudentState';
import MissionCard from '../../components/MissionCard';
import ProgressBar from '../../components/ProgressBar';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';
import type { Mission } from '../../types';

// TODO: get real student ID from auth token
const STUDENT_ID = 'me';

export default function HomeScreen() {
  const router = useRouter();
  const { knowledgeMap, missions, profile, loading, error, refresh } =
    useStudentState(STUDENT_ID);

  const totalNodes = knowledgeMap?.totalNodes ?? 0;
  const consolidato = knowledgeMap?.nodesConsolidato ?? 0;
  const activeMissions = missions.filter(
    (m) => m.state === 'lacuna' || m.state === 'in_recupero',
  );

  const handleMissionPress = (mission: Mission) => {
    router.push(`/quiz/${mission.quizId ?? mission.id}`);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      {/* Welcome (h1) */}
      <View accessible accessibilityRole="header">
        <Text style={styles.heading}>
          Bentornato{profile ? '' : ''}!
        </Text>
        <Text style={styles.subheading}>
          Ecco un riepilogo del tuo percorso.
        </Text>
      </View>

      {/* Loading / Error */}
      {loading && (
        <Text style={styles.status} accessible accessibilityRole="text">
          Caricamento in corso...
        </Text>
      )}
      {error && (
        <View
          accessible
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
          style={styles.errorBox}
        >
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            accessible
            accessibilityRole="button"
            accessibilityLabel="Riprova"
            onPress={refresh}
            style={styles.retryButton}
          >
            <Text style={styles.retryText}>Riprova</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Progress summary card */}
      {!loading && (
        <View
          style={styles.summaryCard}
          accessible
          accessibilityLabel={`Progresso: ${consolidato} di ${totalNodes} concetti consolidati`}
        >
          <Text style={styles.sectionTitle}>Il tuo progresso</Text>
          <ProgressBar
            current={consolidato}
            total={totalNodes}
            label="Concetti consolidati"
          />
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{consolidato}</Text>
              <Text style={styles.statLabel}>Consolidati</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{activeMissions.length}</Text>
              <Text style={styles.statLabel}>Missioni attive</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{totalNodes - consolidato}</Text>
              <Text style={styles.statLabel}>Da completare</Text>
            </View>
          </View>
        </View>
      )}

      {/* Quick link to map */}
      <TouchableOpacity
        accessible
        accessibilityRole="button"
        accessibilityLabel="Vedi mappa completa della conoscenza"
        style={styles.quickLink}
        onPress={() => router.push('/map')}
        activeOpacity={0.7}
      >
        <Text style={styles.quickLinkText}>Vedi mappa completa</Text>
      </TouchableOpacity>

      {/* Active missions (h2) */}
      {activeMissions.length > 0 && (
        <View>
          <Text style={styles.sectionTitle} accessible accessibilityRole="header">
            Le tue missioni
          </Text>
          {activeMissions.slice(0, 3).map((mission) => (
            <MissionCard
              key={mission.id}
              mission={mission}
              onPress={handleMissionPress}
            />
          ))}
          {activeMissions.length > 3 && (
            <TouchableOpacity
              accessible
              accessibilityRole="button"
              accessibilityLabel={`Vedi tutte le ${activeMissions.length} missioni`}
              onPress={() => router.push('/missions')}
              style={styles.seeAll}
            >
              <Text style={styles.seeAllText}>
                Vedi tutte ({activeMissions.length})
              </Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Empty state: encouraging */}
      {!loading && activeMissions.length === 0 && totalNodes > 0 && (
        <View style={styles.emptyMissions}>
          <Text style={styles.emptyText}>
            Nessuna missione attiva al momento. Continua cosi'!
          </Text>
        </View>
      )}
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
  heading: {
    fontSize: TEXT_SIZES['2xl'],
    lineHeight: TEXT_SIZES['2xl'] * LINE_HEIGHTS.tight,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xs,
  },
  subheading: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xl,
  },
  status: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    textAlign: 'center',
    paddingVertical: SPACING.xl,
  },
  errorBox: {
    backgroundColor: '#FFF3E0',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderLeftWidth: 4,
    borderLeftColor: '#EF6C00',
  },
  errorText: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  retryButton: {
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  retryText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '600',
  },
  summaryCard: {
    backgroundColor: PAGE_COLORS.surfaceBg,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  sectionTitle: {
    fontSize: TEXT_SIZES.xl,
    lineHeight: TEXT_SIZES.xl * LINE_HEIGHTS.tight,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.md,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: SPACING.lg,
  },
  stat: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: TEXT_SIZES['2xl'],
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  statLabel: {
    fontSize: TEXT_SIZES.xs,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginTop: SPACING.xs,
  },
  quickLink: {
    backgroundColor: '#1565C0',
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    marginBottom: SPACING.xl,
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  quickLinkText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
  seeAll: {
    paddingVertical: SPACING.md,
    alignItems: 'center',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  seeAllText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
  },
  emptyMissions: {
    paddingVertical: SPACING.xl,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    textAlign: 'center',
  },
});
