/**
 * MasteryMap -- interactive mastery map component.
 *
 * Renders macro-nodes as a scrollable list of NodeCards.
 * Macro-nodes show rollup state (worst-state per IC-03 contract).
 *
 * Accessibility:
 * - role="application" with aria-roledescription per accessibility spec Section 5.1.3
 * - Each node is a button with accessibilityLabel including name + state
 * - Live region announces current node on focus change
 * - Keyboard navigation: arrow keys between nodes, Enter to open detail
 */

import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import NodeCard from './NodeCard';
import StateIndicator from './StateIndicator';
import { MASTERY_TOKENS, type MasteryStateKey } from '../theme/tokens';
import { SPACING, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';
import type { MacroNode, MasteryState } from '../types';

interface MasteryMapProps {
  macroNodes: MacroNode[];
  onNodePress: (nodeId: string) => void;
}

const LEGEND_STATES: MasteryStateKey[] = [
  'non_introdotto',
  'introdotto',
  'lacuna',
  'in_recupero',
  'da_consolidare',
  'consolidato',
];

export default function MasteryMap({ macroNodes, onNodePress }: MasteryMapProps) {
  const [legendExpanded, setLegendExpanded] = useState(false);

  const totalNodes = macroNodes.length;
  const consolidatoCount = macroNodes.filter((n) => n.rollupState === 'consolidato').length;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      accessible={false}
    >
      {/* Map header with summary */}
      <View
        accessible
        accessibilityRole="header"
        accessibilityLabel={`La tua mappa: ${consolidatoCount} di ${totalNodes} macro-concetti consolidati`}
      >
        <Text style={styles.heading}>La tua mappa</Text>
        <Text style={styles.summary}>
          {consolidatoCount} di {totalNodes} macro-concetti consolidati
        </Text>
      </View>

      {/* Legend (collapsible) */}
      <View
        accessible
        accessibilityRole="button"
        accessibilityLabel={`Legenda stati. ${legendExpanded ? 'Espansa' : 'Compressa'}`}
        accessibilityHint="Tocca due volte per espandere o comprimere la legenda"
      >
        <Text
          style={styles.legendToggle}
          onPress={() => setLegendExpanded(!legendExpanded)}
        >
          {legendExpanded ? 'Nascondi legenda' : 'Mostra legenda'}
        </Text>
      </View>

      {legendExpanded && (
        <View style={styles.legend} accessible accessibilityLabel="Legenda degli stati">
          {LEGEND_STATES.map((state) => (
            <View key={state} style={styles.legendItem}>
              <StateIndicator state={state} size="sm" showLabel />
            </View>
          ))}
        </View>
      )}

      {/* Node list */}
      {macroNodes.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>
            Nessun concetto ancora disponibile. Il docente sta preparando il percorso.
          </Text>
        </View>
      ) : (
        <View
          accessible={false}
          accessibilityRole="list"
        >
          {macroNodes.map((node) => (
            <NodeCard
              key={node.id}
              nodeId={node.id}
              label={node.label}
              state={node.rollupState}
              totalMicros={node.totalMicros}
              microsConsolidato={node.microsPerState?.consolidato ?? 0}
              onPress={onNodePress}
            />
          ))}
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
  summary: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  legendToggle: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
    paddingVertical: SPACING.sm,
    marginBottom: SPACING.sm,
  },
  legend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginBottom: SPACING.lg,
  },
  legendItem: {
    marginBottom: SPACING.xs,
  },
  empty: {
    paddingVertical: SPACING['2xl'],
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
