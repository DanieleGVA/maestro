/**
 * WellbeingPrompt -- student wellbeing prompt (safeguarding, phase3 T3.2).
 *
 * Shown when the system detects a wellbeing concern in the student's behavior.
 * This is NOT punitive. The tone is supportive and encouraging.
 * The prompt never replaces a professional (safeguarding rule #6).
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';

interface WellbeingPromptProps {
  onDismiss: () => void;
}

export default function WellbeingPrompt({ onDismiss }: WellbeingPromptProps) {
  return (
    <View
      accessible
      accessibilityRole="alert"
      accessibilityLiveRegion="polite"
      style={styles.container}
    >
      <Text style={styles.title}>Come stai?</Text>
      <Text style={styles.message}>
        Ricorda che puoi prenderti una pausa quando vuoi. Ogni passo conta, anche il
        piu' piccolo. Se hai bisogno di parlare con qualcuno, il tuo docente e' sempre
        disponibile.
      </Text>
      <TouchableOpacity
        accessible
        accessibilityRole="button"
        accessibilityLabel="Chiudi messaggio di benessere"
        style={styles.button}
        onPress={onDismiss}
        activeOpacity={0.7}
      >
        <Text style={styles.buttonText}>Ho capito, grazie</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#E8F5E9',
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginVertical: SPACING.md,
    borderLeftWidth: 4,
    borderLeftColor: '#2E7D32',
  },
  title: {
    fontSize: TEXT_SIZES.lg,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  message: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  button: {
    backgroundColor: '#2E7D32',
    borderRadius: BORDER_RADIUS.sm,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    alignSelf: 'flex-start',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  buttonText: {
    fontSize: TEXT_SIZES.sm,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
});
