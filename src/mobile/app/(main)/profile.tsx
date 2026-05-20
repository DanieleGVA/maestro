/**
 * Profile screen (SCR-ST-09, SCR-ST-14).
 *
 * Shows basic student info and accessibility settings.
 * MVP: font size slider only (12-24pt, F9.4).
 * Other settings (font family, theme, high contrast) are V1.
 *
 * Heading: h1 = "Il mio profilo" (accessibility spec Section 7.3).
 * No PII displayed beyond what the student already knows.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import Slider from '@react-native-community/slider';
import { useAuth } from '../../hooks/useAuth';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS, FONT_SCALE } from '../../theme/typography';

export default function ProfileScreen() {
  const { logout } = useAuth();
  const [fontSize, setFontSize] = useState(FONT_SCALE.default);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading} accessible accessibilityRole="header">
        Il mio profilo
      </Text>

      {/* Accessibility section (h2) */}
      <Text style={styles.sectionTitle} accessible accessibilityRole="header">
        Accessibilita'
      </Text>

      {/* Font size slider (F9.4) */}
      <View style={styles.setting}>
        <Text style={styles.settingLabel} nativeID="fontsize-label">
          Dimensione testo: {fontSize}pt
        </Text>
        <View
          accessible
          accessibilityRole="adjustable"
          accessibilityLabel={`Dimensione testo: ${fontSize} punti`}
          accessibilityValue={{
            min: FONT_SCALE.min,
            max: FONT_SCALE.max,
            now: fontSize,
          }}
        >
          <Slider
            style={styles.slider}
            minimumValue={FONT_SCALE.min}
            maximumValue={FONT_SCALE.max}
            step={1}
            value={fontSize}
            onValueChange={setFontSize}
            minimumTrackTintColor="#1565C0"
            maximumTrackTintColor="#E0E0E0"
            thumbTintColor="#1565C0"
          />
        </View>
        <View style={styles.sliderLabels}>
          <Text style={styles.sliderLabel}>{FONT_SCALE.min}pt</Text>
          <Text style={styles.sliderLabel}>{FONT_SCALE.max}pt</Text>
        </View>

        {/* Preview */}
        <View style={styles.preview} accessible accessibilityLabel="Anteprima dimensione testo">
          <Text style={[styles.previewText, { fontSize }]}>
            Questo e' un testo di esempio per verificare la dimensione scelta.
          </Text>
        </View>
      </View>

      {/* Font selection (V1 -- disabled) */}
      <View style={styles.setting}>
        <Text style={styles.settingLabel}>Font</Text>
        <Text style={styles.disabledValue}>Inter (predefinito)</Text>
        <Text style={styles.v1Note}>
          OpenDyslexic e Atkinson Hyperlegible saranno disponibili nella prossima versione.
        </Text>
      </View>

      {/* Theme selection (V1 -- disabled) */}
      <View style={styles.setting}>
        <Text style={styles.settingLabel}>Tema</Text>
        <Text style={styles.disabledValue}>Chiaro</Text>
        <Text style={styles.v1Note}>
          I temi Scuro e Seppia saranno disponibili nella prossima versione.
        </Text>
      </View>

      {/* Info section */}
      <Text style={styles.sectionTitle} accessible accessibilityRole="header">
        I miei dati
      </Text>
      <Text style={styles.infoText}>
        I tuoi dati personali sono protetti e crittografati. Per qualsiasi richiesta,
        contatta il tuo docente o l'amministratore della scuola.
      </Text>

      {/* Logout */}
      <TouchableOpacity
        accessible
        accessibilityRole="button"
        accessibilityLabel="Esci dal tuo account"
        style={styles.logoutButton}
        onPress={logout}
        activeOpacity={0.7}
      >
        <Text style={styles.logoutText}>Esci</Text>
      </TouchableOpacity>
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
    paddingBottom: SPACING['3xl'],
  },
  heading: {
    fontSize: TEXT_SIZES['2xl'],
    lineHeight: TEXT_SIZES['2xl'] * LINE_HEIGHTS.tight,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    fontSize: TEXT_SIZES.xl,
    lineHeight: TEXT_SIZES.xl * LINE_HEIGHTS.tight,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.md,
    marginTop: SPACING.lg,
  },
  setting: {
    backgroundColor: PAGE_COLORS.surfaceBg,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
  },
  settingLabel: {
    fontSize: TEXT_SIZES.sm,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  slider: {
    width: '100%',
    height: TOUCH_TARGET.min,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sliderLabel: {
    fontSize: TEXT_SIZES.xs,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
  },
  preview: {
    marginTop: SPACING.md,
    padding: SPACING.md,
    backgroundColor: PAGE_COLORS.bg,
    borderRadius: BORDER_RADIUS.sm,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  previewText: {
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    lineHeight: 1.5 * 16,
  },
  disabledValue: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
  },
  v1Note: {
    fontSize: TEXT_SIZES.xs,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    fontStyle: 'italic',
    marginTop: SPACING.xs,
  },
  infoText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  logoutButton: {
    borderWidth: 1.5,
    borderColor: '#C62828',
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    marginTop: SPACING.xl,
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  logoutText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: '#C62828',
    fontFamily: 'Inter',
  },
});
