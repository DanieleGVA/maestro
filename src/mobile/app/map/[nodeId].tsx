/**
 * Node detail screen (SCR-ST-05).
 *
 * Shows:
 * - Current state with visual indicator (color + icon + text)
 * - Concept explanation (from content generation API)
 * - If lacuna: link to recovery mission (encouraging tone)
 * - If da_consolidare: next retention check date (no urgency/FOMO)
 * - Prerequisites and dependents
 *
 * Heading: h1 = "{Nome concetto}" (accessibility spec Section 7.3).
 */

import React, { useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import StateIndicator from '../../components/StateIndicator';
import { useNodeDetail } from '../../hooks/useApi';
import { MASTERY_TOKENS } from '../../theme/tokens';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';

const STUDENT_ID = 'me';

export default function NodeDetailScreen() {
  const { nodeId } = useLocalSearchParams<{ nodeId: string }>();
  const router = useRouter();
  const { data: node, loading, error, fetch } = useNodeDetail(STUDENT_ID, nodeId ?? '');

  useEffect(() => {
    if (nodeId) fetch();
  }, [nodeId]);

  if (loading) {
    return (
      <View style={styles.center} accessible accessibilityLabel="Caricamento dettaglio concetto">
        <ActivityIndicator size="large" color="#1565C0" />
      </View>
    );
  }

  if (error || !node) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText} accessible accessibilityRole="alert">
          {error ?? 'Concetto non trovato.'}
        </Text>
        <TouchableOpacity
          accessible
          accessibilityRole="button"
          accessibilityLabel="Torna alla mappa"
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Text style={styles.backButtonText}>Torna alla mappa</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const token = MASTERY_TOKENS[node.state];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Back button */}
      <TouchableOpacity
        accessible
        accessibilityRole="button"
        accessibilityLabel="Torna alla mappa"
        style={styles.back}
        onPress={() => router.back()}
      >
        <Text style={styles.backText}>Torna alla mappa</Text>
      </TouchableOpacity>

      {/* Title (h1) */}
      <Text style={styles.title} accessible accessibilityRole="header">
        {node.label}
      </Text>

      {/* State indicator */}
      <View style={styles.stateRow}>
        <Text style={styles.sectionTitle} accessible accessibilityRole="header">
          Stato attuale
        </Text>
        <StateIndicator state={node.state} size="md" />
      </View>

      {/* Lacuna: encouraging recovery CTA */}
      {node.state === 'lacuna' && (
        <View style={styles.actionCard}>
          <Text style={styles.actionText}>
            C'e' qualcosa da ripassare su questo argomento. Nessun problema, e' un'opportunita'
            per rafforzare le tue conoscenze!
          </Text>
          {node.missionId && (
            <TouchableOpacity
              accessible
              accessibilityRole="button"
              accessibilityLabel={`Inizia il ripasso per ${node.label}`}
              style={styles.actionButton}
              onPress={() => router.push(`/quiz/${node.missionId}`)}
              activeOpacity={0.7}
            >
              <Text style={styles.actionButtonText}>Inizia il ripasso</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* In recupero: progress */}
      {node.state === 'in_recupero' && (
        <View style={styles.actionCard}>
          <Text style={styles.actionText}>
            Stai gia' lavorando su questo argomento. Continua cosi'!
          </Text>
          {node.missionId && (
            <TouchableOpacity
              accessible
              accessibilityRole="button"
              accessibilityLabel={`Continua il recupero per ${node.label}`}
              style={styles.actionButton}
              onPress={() => router.push(`/quiz/${node.missionId}`)}
              activeOpacity={0.7}
            >
              <Text style={styles.actionButtonText}>Continua il recupero</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Da consolidare: retention check info (no FOMO) */}
      {node.state === 'da_consolidare' && node.retentionCheckDue && (
        <View style={styles.infoCard}>
          <Text style={styles.infoText}>
            Prossimo ripasso previsto: {new Date(node.retentionCheckDue).toLocaleDateString('it-IT')}.
            Non preoccuparti, te lo ricorderemo al momento giusto.
          </Text>
        </View>
      )}

      {/* Consolidato: positive feedback */}
      {node.state === 'consolidato' && (
        <View style={styles.successCard}>
          <Text style={styles.successText}>
            Ottimo! Hai consolidato questo concetto.
          </Text>
        </View>
      )}

      {/* Description */}
      {node.description && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle} accessible accessibilityRole="header">
            Descrizione
          </Text>
          <Text style={styles.bodyText}>{node.description}</Text>
        </View>
      )}

      {/* Prerequisites */}
      {node.prerequisiteIds.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle} accessible accessibilityRole="header">
            Prerequisiti
          </Text>
          <Text style={styles.bodyText}>
            Questo concetto dipende da {node.prerequisiteIds.length} concetti
            precedenti.
          </Text>
        </View>
      )}

      {/* Dependents */}
      {node.dependentIds.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle} accessible accessibilityRole="header">
            Sblocca
          </Text>
          <Text style={styles.bodyText}>
            Completando questo concetto potrai accedere a {node.dependentIds.length} nuovi
            argomenti.
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
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: PAGE_COLORS.bg,
    padding: SPACING.xl,
  },
  back: {
    paddingVertical: SPACING.sm,
    marginBottom: SPACING.md,
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  backText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
  },
  title: {
    fontSize: TEXT_SIZES['2xl'],
    lineHeight: TEXT_SIZES['2xl'] * LINE_HEIGHTS.tight,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  stateRow: {
    marginBottom: SPACING.lg,
  },
  sectionTitle: {
    fontSize: TEXT_SIZES.lg,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  actionCard: {
    backgroundColor: '#FFF3E0',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderLeftWidth: 4,
    borderLeftColor: '#EF6C00',
  },
  actionText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.md,
  },
  actionButton: {
    backgroundColor: '#1565C0',
    borderRadius: BORDER_RADIUS.sm,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    alignSelf: 'flex-start',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  actionButtonText: {
    fontSize: TEXT_SIZES.sm,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
  infoCard: {
    backgroundColor: '#FFF8E1',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderLeftWidth: 4,
    borderLeftColor: '#FDD835',
  },
  infoText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  successCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderLeftWidth: 4,
    borderLeftColor: '#2E7D32',
  },
  successText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  section: {
    marginBottom: SPACING.lg,
  },
  bodyText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
  },
  errorText: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    textAlign: 'center',
    marginBottom: SPACING.lg,
  },
  backButton: {
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  backButtonText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
  },
});
