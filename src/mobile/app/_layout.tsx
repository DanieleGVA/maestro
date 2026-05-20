/**
 * Root layout -- auth guard + Expo Router Slot.
 *
 * Redirects unauthenticated users to /auth/login.
 * Wraps app in SafeAreaProvider.
 * Sets lang="it" equivalent metadata.
 */

import React, { useEffect } from 'react';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { Slot, useRouter, useSegments } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { useAuth } from '../hooks/useAuth';
import { PAGE_COLORS } from '../theme/spacing';

export default function RootLayout() {
  const { isLoggedIn, isLoading } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === 'auth';

    if (!isLoggedIn && !inAuthGroup) {
      router.replace('/auth/login');
    } else if (isLoggedIn && inAuthGroup) {
      router.replace('/');
    }
  }, [isLoggedIn, isLoading, segments]);

  if (isLoading) {
    return (
      <View style={styles.loading} accessible accessibilityLabel="Caricamento in corso">
        <ActivityIndicator size="large" color="#1565C0" />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Slot />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: PAGE_COLORS.bg,
  },
});
