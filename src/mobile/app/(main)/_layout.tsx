/**
 * Main tab layout -- bottom tab navigator for the student app.
 *
 * Tabs: Home, Mappa, Missioni, Profilo.
 * Tab bar uses role="tablist" semantics (accessibility spec Section 5.1.2).
 * Consistent navigation across all pages (WCAG 3.2.3).
 */

import React from 'react';
import { Tabs } from 'expo-router';
import { TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES } from '../../theme/typography';

export default function MainLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#1565C0',
        tabBarInactiveTintColor: PAGE_COLORS.surfaceFg,
        tabBarStyle: {
          backgroundColor: PAGE_COLORS.bg,
          borderTopColor: '#E0E0E0',
          minHeight: TOUCH_TARGET.min + 16,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: TEXT_SIZES.xs,
          fontFamily: 'Inter',
        },
        headerStyle: {
          backgroundColor: PAGE_COLORS.bg,
        },
        headerTitleStyle: {
          fontFamily: 'Inter',
          fontSize: TEXT_SIZES.lg,
          fontWeight: '600',
          color: PAGE_COLORS.fg,
        },
        tabBarAccessibilityLabel: 'Menu principale',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          headerTitle: 'MAESTRO',
          tabBarAccessibilityLabel: 'Home',
        }}
      />
      <Tabs.Screen
        name="map"
        options={{
          title: 'Mappa',
          headerTitle: 'La tua mappa',
          tabBarAccessibilityLabel: 'Mappa della conoscenza',
        }}
      />
      <Tabs.Screen
        name="missions"
        options={{
          title: 'Missioni',
          headerTitle: 'Le tue missioni',
          tabBarAccessibilityLabel: 'Missioni di recupero',
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profilo',
          headerTitle: 'Il mio profilo',
          tabBarAccessibilityLabel: 'Il mio profilo',
        }}
      />
    </Tabs>
  );
}
