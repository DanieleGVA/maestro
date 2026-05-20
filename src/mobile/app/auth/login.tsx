/**
 * Login screen (SCR-ST-01 / SCR-ST-02).
 *
 * Username + password via Keycloak (MVP, no SSO).
 * Accessibility: labels on all inputs, error messages in aria-live,
 * autocomplete hints (WCAG 1.3.5).
 *
 * No PII stored outside secure storage.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useAuth } from '../../hooks/useAuth';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';

export default function LoginScreen() {
  const { login, isLoading, loginError } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) return;
    await login({ username: username.trim(), password });
  };

  const canSubmit = username.trim().length > 0 && password.length > 0 && !isLoading;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <View accessible accessibilityRole="header">
          <Text style={styles.title}>MAESTRO</Text>
          <Text style={styles.subtitle}>Accedi al tuo percorso di apprendimento</Text>
        </View>

        {/* Error message (aria-live) */}
        {loginError && (
          <View
            accessible
            accessibilityRole="alert"
            accessibilityLiveRegion="assertive"
            style={styles.error}
          >
            <Text style={styles.errorText}>{loginError}</Text>
          </View>
        )}

        {/* Username field */}
        <View style={styles.field}>
          <Text
            style={styles.label}
            nativeID="username-label"
          >
            Nome utente
          </Text>
          <TextInput
            style={styles.input}
            accessible
            accessibilityLabel="Nome utente"
            accessibilityLabelledBy="username-label"
            autoCapitalize="none"
            autoCorrect={false}
            autoComplete="username"
            textContentType="username"
            value={username}
            onChangeText={setUsername}
            placeholder="Inserisci il tuo nome utente"
            placeholderTextColor="#9E9E9E"
            returnKeyType="next"
          />
        </View>

        {/* Password field */}
        <View style={styles.field}>
          <Text
            style={styles.label}
            nativeID="password-label"
          >
            Password
          </Text>
          <View style={styles.passwordRow}>
            <TextInput
              style={[styles.input, styles.passwordInput]}
              accessible
              accessibilityLabel="Password"
              accessibilityLabelledBy="password-label"
              autoCapitalize="none"
              autoCorrect={false}
              autoComplete="password"
              textContentType="password"
              secureTextEntry={!showPassword}
              value={password}
              onChangeText={setPassword}
              placeholder="Inserisci la tua password"
              placeholderTextColor="#9E9E9E"
              returnKeyType="done"
              onSubmitEditing={handleLogin}
            />
            <TouchableOpacity
              accessible
              accessibilityRole="button"
              accessibilityLabel={showPassword ? 'Nascondi password' : 'Mostra password'}
              style={styles.showPasswordButton}
              onPress={() => setShowPassword(!showPassword)}
            >
              <Text style={styles.showPasswordText}>
                {showPassword ? 'Nascondi' : 'Mostra'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Submit button */}
        <TouchableOpacity
          accessible
          accessibilityRole="button"
          accessibilityLabel="Accedi"
          accessibilityState={{ disabled: !canSubmit, busy: isLoading }}
          style={[styles.button, !canSubmit && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={!canSubmit}
          activeOpacity={0.7}
        >
          <Text style={styles.buttonText}>
            {isLoading ? 'Accesso in corso...' : 'Accedi'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: PAGE_COLORS.bg,
  },
  content: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: SPACING.xl,
    maxWidth: 400,
    alignSelf: 'center',
    width: '100%',
  },
  title: {
    fontSize: TEXT_SIZES['3xl'],
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    textAlign: 'center',
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    textAlign: 'center',
    marginBottom: SPACING['2xl'],
  },
  error: {
    backgroundColor: '#FFF3E0',
    borderRadius: BORDER_RADIUS.sm,
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
  field: {
    marginBottom: SPACING.lg,
  },
  label: {
    fontSize: TEXT_SIZES.sm,
    fontWeight: '500',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xs,
  },
  input: {
    borderWidth: 1.5,
    borderColor: PAGE_COLORS.borderInput,
    borderRadius: BORDER_RADIUS.md,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    minHeight: TOUCH_TARGET.min,
    backgroundColor: PAGE_COLORS.bg,
  },
  passwordRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  passwordInput: {
    flex: 1,
  },
  showPasswordButton: {
    minWidth: TOUCH_TARGET.min,
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.sm,
  },
  showPasswordText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
  },
  button: {
    backgroundColor: '#1565C0',
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    minHeight: TOUCH_TARGET.min + 4,
    justifyContent: 'center',
    marginTop: SPACING.md,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
});
