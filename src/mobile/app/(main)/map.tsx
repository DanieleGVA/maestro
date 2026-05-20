/**
 * Mastery Map screen (SCR-ST-04).
 *
 * Renders the full knowledge map with macro-nodes.
 * Each node shows rollup state (worst-state among micro-nodes).
 * Tap on a node navigates to detail screen.
 *
 * Heading: h1 = "La tua mappa" (accessibility spec Section 7.3).
 */

import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import MasteryMap from '../../components/MasteryMap';
import { useKnowledgeMap } from '../../hooks/useApi';
import { SPACING, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';

const STUDENT_ID = 'me';

export default function MapScreen() {
  const router = useRouter();
  const { data: map, loading, error, fetch } = useKnowledgeMap(STUDENT_ID);

  useEffect(() => {
    fetch();
  }, []);

  const handleNodePress = (nodeId: string) => {
    router.push(`/map/${nodeId}`);
  };

  if (loading) {
    return (
      <View style={styles.center} accessible accessibilityLabel="Caricamento mappa in corso">
        <ActivityIndicator size="large" color="#1565C0" />
        <Text style={styles.loadingText}>Caricamento mappa...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text
          style={styles.errorText}
          accessible
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
        >
          {error}
        </Text>
      </View>
    );
  }

  return (
    <MasteryMap
      macroNodes={map?.macroNodes ?? []}
      onNodePress={handleNodePress}
    />
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: PAGE_COLORS.bg,
    padding: SPACING.xl,
  },
  loadingText: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginTop: SPACING.md,
  },
  errorText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    textAlign: 'center',
  },
});
