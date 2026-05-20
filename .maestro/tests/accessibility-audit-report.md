# MAESTRO -- Accessibility Audit Report (T5.3)

**Auditor**: MSTR-17 (Accessibility & UX Specialist)
**Date**: 2026-05-20
**Scope**: Student mobile app (`src/mobile/`), Teacher dashboard (`src/dashboard/`)
**Standard**: WCAG 2.1 Level AA
**Reference**: `.maestro/accessibility/accessibility-mvp-spec.md`

---

## 1. Executive Summary

The MAESTRO codebase demonstrates **strong accessibility awareness** throughout both the student mobile app (React Native / Expo Router, 25 files) and the teacher dashboard (Next.js 15, 33 files). The design token system correctly implements the spec's corrected contrast values, the six-state mastery indicator consistently uses color + icon + text label (WCAG 1.4.1), and semantic structure is well-applied.

**4 critical/high issues** were found and **fixed in this audit**. **10 medium issues** and **6 low issues** remain as recommendations. No conformance-blocking issues remain after the fixes applied.

### Summary Table

| Severity | Found | Fixed | Remaining |
|---|---|---|---|
| Critical | 1 | 1 | 0 |
| High | 3 | 3 | 0 |
| Medium | 10 | 0 | 10 |
| Low | 6 | 0 | 6 |
| **Total** | **20** | **4** | **16** |

### Overall Conformance Assessment

**Conditional pass for WCAG 2.1 AA** -- the codebase meets the structural requirements for AA conformance with the fixes applied. Full conformance requires:

1. Manual screen reader testing (VoiceOver iOS, TalkBack Android, VoiceOver macOS, NVDA Windows)
2. axe-core automated scan on rendered pages
3. Keyboard-only navigation walkthrough on actual running app
4. DSA/BES user testing (V1, per spec Section 10.3)

---

## 2. Findings -- Critical (Fixed)

### C-01: Modal overlay hides dialog from assistive technology

- **Component**: `src/dashboard/components/common/Modal.tsx:53-57`
- **WCAG Criterion**: 4.1.2 Name, Role, Value
- **Description**: The modal overlay `<div>` had `aria-hidden="true"`, which is inherited by all descendants including the `<div role="dialog">` inside it. This means the entire modal content would be invisible to screen readers.
- **Evidence**: Line 55 had `aria-hidden="true"` on the backdrop wrapper that contains the dialog.
- **Remediation**: **FIXED** -- Removed `aria-hidden="true"` from the overlay div. The dialog now uses `role="dialog"` and `aria-modal="true"` on the inner container, which is the correct pattern for informing assistive tech that content outside the dialog is inert.

---

## 3. Findings -- High (Fixed)

### H-01: MasteryMap legend toggle uses Text with onPress instead of TouchableOpacity

- **Component**: `src/mobile/components/MasteryMap.tsx:62-74`
- **WCAG Criterion**: 2.1.1 Keyboard, 4.1.2 Name, Role, Value
- **Description**: The legend expand/collapse control was a `<View>` wrapping a `<Text onPress={...}>`. While the `<View>` had `accessibilityRole="button"`, the `onPress` handler was on the `<Text>` element, not the `<View>`. This meant tapping the accessible element (the View) would not trigger the action, and the Text element is not natively focusable for assistive technology.
- **Evidence**: Line 68-73 had `<Text style={styles.legendToggle} onPress={() => setLegendExpanded(!legendExpanded)}>`.
- **Remediation**: **FIXED** -- Replaced the `<View>` + `<Text onPress>` pattern with a `<TouchableOpacity onPress>` wrapper that has the accessibility attributes. The text is now a non-interactive child.

### H-02: StudentMap micro-node buttons rely on title instead of aria-label

- **Component**: `src/dashboard/components/students/StudentMap.tsx:77-84`
- **WCAG Criterion**: 4.1.2 Name, Role, Value
- **Description**: Micro-node buttons in the StudentMap component used only `title` attribute for their accessible name. The `title` attribute is not reliably announced by screen readers (NVDA ignores it in many contexts, VoiceOver may not announce it). Since the `StateIndicator` inside has `showLabel={false}`, the button had no programmatically determinable name for many screen reader + browser combinations.
- **Evidence**: Line 81 had `title={...}` without a corresponding `aria-label`.
- **Remediation**: **FIXED** -- Added `aria-label` matching the `title` value so screen readers consistently announce the node name and state.

### H-03: QuizView radiogroup role lost due to accessible={false}

- **Component**: `src/mobile/components/QuizView.tsx:117-121`
- **WCAG Criterion**: 4.1.2 Name, Role, Value
- **Description**: The radio group container had `accessible={false}` combined with `accessibilityRole="radiogroup"`. In React Native, `accessible={false}` means the element is not an accessibility element, so `accessibilityRole` and `accessibilityLabel` are ignored. Screen readers would not announce the group role or label. Also applied the same fix to the MasteryMap node list container which had `accessible={false}` with `accessibilityRole="list"`.
- **Evidence**: Line 118 had `accessible={false}` and line 119 had `accessibilityRole="radiogroup"`.
- **Remediation**: **FIXED** -- Removed `accessible={false}` from the radiogroup container (and from the MasteryMap list container). The role and label are now properly exposed.

---

## 4. Findings -- Medium (Recommendations)

### M-01: No skip link on mobile app

- **Component**: `src/mobile/app/_layout.tsx`, `src/mobile/app/(main)/_layout.tsx`
- **WCAG Criterion**: 2.4.1 Bypass Blocks
- **Description**: The mobile app does not implement a skip link mechanism. The accessibility spec (Section 5.3) describes skip links for web; for React Native, the equivalent would be an `accessibilityElementsHidden` on repeated navigation or using `AccessibilityInfo.setAccessibilityFocus` to jump to main content. The tab bar (Expo Router Tabs) is at the bottom, which partly mitigates this, but screen reader users navigating linearly would still traverse the header on every page.
- **Recommendation**: Implement a mechanism to allow screen reader users to skip directly to the main content area on each page. Consider using `accessibilityViewIsModal` or programmatic focus management.

### M-02: No aria-live announcements for loading states on mobile

- **Component**: Various mobile screens (map.tsx, missions.tsx, quiz/[quizId].tsx)
- **WCAG Criterion**: 4.1.3 Status Messages
- **Description**: Loading states display `<ActivityIndicator>` with `accessibilityLabel` but do not use `accessibilityLiveRegion` to announce when loading completes and content appears. A screen reader user would not be notified that data has loaded.
- **Recommendation**: Add a live region or use `AccessibilityInfo.announceForAccessibility()` when data finishes loading to inform screen reader users.

### M-03: Dashboard home page breadcrumb missing

- **Component**: `src/dashboard/app/page.tsx`
- **WCAG Criterion**: 2.4.5 Multiple Ways
- **Description**: The dashboard home page has no breadcrumb navigation, while other pages do. This is minor since the home page is the root, but adding a consistent "Dashboard" breadcrumb would improve the pattern.
- **Recommendation**: Add a breadcrumb showing "Dashboard" (current page) for consistency.

### M-04: HeatmapCell component is unused and inconsistent with ClassHeatmap

- **Component**: `src/dashboard/components/heatmap/HeatmapCell.tsx`
- **WCAG Criterion**: N/A (code quality)
- **Description**: `HeatmapCell.tsx` is a standalone component that renders a `<td>` with its own keyboard handler, but `ClassHeatmap.tsx` renders cells inline with its own grid keyboard navigation. Having two implementations creates maintenance risk -- if one gets accessibility fixes, the other may not.
- **Recommendation**: Either use `HeatmapCell` inside `ClassHeatmap` or remove the unused component.

### M-05: Dashboard login page has no skip link

- **Component**: `src/dashboard/app/login/page.tsx`
- **WCAG Criterion**: 2.4.1 Bypass Blocks
- **Description**: The login page is excluded from the `ClientLayout` skip link (`isLoginPage` check). Since it's a standalone page with minimal content, this is low impact, but the spec requires a skip link on every page.
- **Recommendation**: Add a skip link targeting the form on the login page.

### M-06: Missing reduced-motion support on mobile

- **Component**: `src/mobile/` (app-wide)
- **WCAG Criterion**: 2.3.1 Three Flashes, 2.2.2 Pause Stop Hide
- **Description**: The dashboard has `@media (prefers-reduced-motion: reduce)` in globals.css, but the mobile app has no equivalent. The accessibility spec (Section 10.1) acknowledges this as a V1 item for full animation audit, but the toggle in the profile screen does not actually apply to any animations.
- **Recommendation**: Wire up the reduced-motion toggle in the profile screen to a global context that disables React Native `Animated` transitions.

### M-07: Profile screen accessibility settings do not persist

- **Component**: `src/mobile/app/(main)/profile.tsx`
- **WCAG Criterion**: F9.8 (MAESTRO-specific)
- **Description**: The font size slider state is local (`useState`). The spec requires persistence to AsyncStorage/DB (Section F9.8). Changing the font size has no effect beyond the preview.
- **Recommendation**: Store the user's font size preference in AsyncStorage and apply it app-wide via a ThemeProvider context.

### M-08: Dashboard tables lack row count announcement

- **Component**: `src/dashboard/components/common/DataTable.tsx`, `src/dashboard/components/heatmap/ClassHeatmap.tsx`
- **WCAG Criterion**: 1.3.1 Info and Relationships
- **Description**: Tables have proper `<caption>`, `<th scope>`, and `aria-label`, but do not announce the number of rows/columns. Screen reader users navigating large tables benefit from knowing the dimensions.
- **Recommendation**: Include row/column counts in the `<caption>` or `aria-label` text.

### M-09: Home screen missing live region for error announcements

- **Component**: `src/mobile/app/(main)/index.tsx:63-80`
- **WCAG Criterion**: 4.1.3 Status Messages
- **Description**: The error box uses `accessibilityLiveRegion="polite"` which is correct, but errors are important and may warrant `"assertive"` to ensure they are announced immediately.
- **Recommendation**: Consider using `accessibilityLiveRegion="assertive"` for error messages.

### M-10: Dashboard select dropdowns show raw state keys instead of Italian labels

- **Component**: `src/dashboard/components/students/OverrideModal.tsx:71-76`
- **WCAG Criterion**: 3.3.2 Labels or Instructions
- **Description**: The "Nuovo stato" select dropdown displays raw state keys like `non_introdotto`, `in_recupero` instead of the human-readable Italian labels from `MASTERY_TOKENS[state].label`. This is a usability issue for all users including those with cognitive disabilities.
- **Recommendation**: Use `MASTERY_TOKENS[s].label` as the option text instead of the raw key.

---

## 5. Findings -- Low (Recommendations)

### L-01: font-family "Inter" may not be loaded on all devices

- **Component**: `src/mobile/theme/typography.ts`, various mobile components
- **WCAG Criterion**: N/A (best practice)
- **Description**: Components hardcode `fontFamily: 'Inter'` but the Expo app does not include `expo-font` loading for Inter. If the font is not bundled, React Native falls back to the system default silently.
- **Recommendation**: Ensure Inter is bundled via `expo-font` or use `system` as the font family.

### L-02: Mobile app root layout does not set language metadata

- **Component**: `src/mobile/app/_layout.tsx`
- **WCAG Criterion**: 3.1.1 Language of Page
- **Description**: The dashboard correctly sets `<html lang="it">` in `layout.tsx`. The mobile app (Expo/React Native) has no equivalent. React Native does not have an `<html>` element, but the `expo-localization` module can be used with `accessibilityLanguage` prop.
- **Recommendation**: Set `accessibilityLanguage="it"` on root containers for VoiceOver Italian pronunciation.

### L-03: Dashboard breadcrumb separators use regular `<li>` instead of CSS

- **Component**: `src/dashboard/app/classes/[classId]/page.tsx:49`, `src/dashboard/app/classes/[classId]/students/[studentId]/page.tsx:71,79`
- **WCAG Criterion**: 1.3.1 Info and Relationships
- **Description**: Breadcrumb separators (`/`) are rendered as `<li aria-hidden="true">` elements. While `aria-hidden` correctly hides them from screen readers, using CSS `::before` or `::after` pseudo-elements would be cleaner semantically.
- **Recommendation**: Use CSS separators instead of DOM elements.

### L-04: ConseptMappingReview has no live region for feedback

- **Component**: `src/dashboard/components/lessons/ConceptMappingReview.tsx`
- **WCAG Criterion**: 4.1.3 Status Messages
- **Description**: When a mapping is confirmed or rejected and removed from the list, no screen reader announcement is made. The list just silently shrinks.
- **Recommendation**: Add an `aria-live="polite"` region that announces "Mapping confermato" or "Mapping rifiutato".

### L-05: Alerts page items use aria-live on static elements

- **Component**: `src/dashboard/app/alerts/page.tsx:47`
- **WCAG Criterion**: 4.1.3 Status Messages
- **Description**: Each wellbeing alert div has `aria-live="assertive"`. Since these are rendered on page load (not dynamically injected), `aria-live` has no effect. If alerts are added dynamically via API, this would work correctly. Currently it's benign but misleading.
- **Recommendation**: Move `aria-live` to a container that receives new children dynamically, not on static elements.

### L-06: NodeCard progress bar track has low contrast background

- **Component**: `src/mobile/components/NodeCard.tsx:122`
- **WCAG Criterion**: 1.4.11 Non-text Contrast
- **Description**: The progress bar track uses `#E0E0E0` on a `#F5F5F5` surface background. The contrast ratio is approximately 1.1:1, which is below the 3:1 threshold for UI components. However, progress bars are supplementary indicators (the exact count is shown as text), so this is informational rather than the sole means of conveying data.
- **Recommendation**: Darken the track to `#BDBDBD` (contrast ~1.7:1 on surface) or `#9E9E9E` (contrast ~2.8:1) for better visual distinction.

---

## 6. WCAG 2.1 AA Criterion-by-Criterion Assessment

### 6.1 Level A Criteria

| # | Criterion | Status | Notes |
|---|---|---|---|
| 1.1.1 | Non-text Content | Pass | All icons use `aria-hidden` + text labels; StateIndicator has `accessibilityLabel`/`aria-label` |
| 1.3.1 | Info and Relationships | Pass | Semantic HTML in dashboard (headings, nav, main, table with th/scope); React Native uses accessibilityRole |
| 1.3.2 | Meaningful Sequence | Pass | DOM/render order matches visual order throughout |
| 1.3.3 | Sensory Characteristics | Pass | No instructions rely on shape/color/position alone |
| 1.4.1 | Use of Color | Pass | All 6 mastery states use color + distinct icon + text label consistently |
| 1.4.2 | Audio Control | N/A | No auto-playing audio in MVP |
| 2.1.1 | Keyboard | Pass (with notes) | Dashboard fully keyboard navigable; heatmap has arrow-key grid nav; mobile uses TouchableOpacity for all interactive elements. M-01 notes skip link gap |
| 2.1.2 | No Keyboard Trap | Pass | Modal focus trap correctly implements Esc to close; Tab cycles within modal |
| 2.1.4 | Character Key Shortcuts | Pass | No single-character shortcuts |
| 2.2.1 | Timing Adjustable | Pass | No timers in quiz or anywhere |
| 2.2.2 | Pause Stop Hide | Pass (partial) | No auto-playing animations. M-06 notes reduced-motion gap on mobile |
| 2.3.1 | Three Flashes | Pass | No flashing content |
| 2.4.1 | Bypass Blocks | Pass (partial) | Dashboard has skip link in client-layout.tsx. Mobile lacks equivalent (M-01). Login page excluded (M-05) |
| 2.4.2 | Page Titled | Pass | Dashboard uses Next.js Metadata with descriptive titles. Mobile uses Expo Router headerTitle |
| 2.4.3 | Focus Order | Pass | Tab order follows visual layout |
| 2.4.4 | Link Purpose | Pass | Links have descriptive text ("Dettaglio studente", "Vedi mappa completa") |
| 2.5.1 | Pointer Gestures | N/A | No multi-point gestures in MVP |
| 2.5.2 | Pointer Cancellation | Pass | Default React Native/browser behavior (up-event activation) |
| 2.5.3 | Label in Name | Pass | Button text matches accessible name |
| 3.1.1 | Language of Page | Pass (partial) | Dashboard has `<html lang="it">`. Mobile lacks equivalent (L-02) |
| 3.2.1 | On Focus | Pass | No context change on focus |
| 3.2.2 | On Input | Pass | Form submissions are explicit (button press) |
| 3.3.1 | Error Identification | Pass | Login errors shown as text with role="alert"; OverrideModal has inline validation |
| 3.3.2 | Labels or Instructions | Pass | All form inputs have associated labels via `<label htmlFor>` or `accessibilityLabel` |
| 4.1.1 | Parsing | Pass | React/JSX produces valid HTML |
| 4.1.2 | Name, Role, Value | Pass (after fixes) | C-01, H-01, H-02, H-03 resolved. All custom components now expose proper ARIA |

### 6.2 Level AA Criteria

| # | Criterion | Status | Notes |
|---|---|---|---|
| 1.3.4 | Orientation | Pass | No orientation lock |
| 1.3.5 | Identify Input Purpose | Pass | Login inputs have `autoComplete="username"` / `autoComplete="password"` |
| 1.4.3 | Contrast (Minimum) | Pass | Token colors verified per spec Section 3.1; all text >= 4.5:1 |
| 1.4.4 | Resize Text | Pass (partial) | Font size slider 12-24pt available; layout responsive. M-07 notes persistence gap |
| 1.4.5 | Images of Text | Pass | No images of text |
| 1.4.10 | Reflow | Pass | Dashboard is responsive; heatmap has horizontal scroll with aria region |
| 1.4.11 | Non-text Contrast | Pass (partial) | Focus ring #1565C0 on white = 4.9:1; borders #616161 on white = 5.3:1. L-06 notes progress bar track |
| 1.4.12 | Text Spacing | Not verified | Requires runtime testing with WCAG text spacing bookmarklet |
| 1.4.13 | Content on Hover/Focus | N/A | No hover/focus content in MVP |
| 2.4.5 | Multiple Ways | Pass | Dashboard: sidebar + breadcrumbs; Mobile: tab bar + navigation links |
| 2.4.6 | Headings and Labels | Pass | Proper heading hierarchy (h1-h2-h3), no skipped levels, descriptive labels |
| 2.4.7 | Focus Visible | Pass | Global focus-visible styles in globals.css; all interactive elements use focus-visible |
| 3.1.2 | Language of Parts | Not applicable | MVP is Italian only; V1 bilingual content will need lang attributes |
| 3.2.3 | Consistent Navigation | Pass | Dashboard sidebar is fixed; mobile tab bar is consistent |
| 3.2.4 | Consistent Identification | Pass | Same labels for same functions throughout |
| 3.3.3 | Error Suggestion | Pass | Login error gives "Credenziali non valide. Riprova."; override has character count hint |
| 3.3.4 | Error Prevention | Pass | Override requires motivation text; confirmation step via modal |
| 4.1.3 | Status Messages | Pass (partial) | Dashboard has live regions (client-layout.tsx). Mobile has accessibilityLiveRegion on alerts/feedback. M-02 notes loading state gap |

---

## 7. MAESTRO-Specific Checks

| Check | Status | Evidence |
|---|---|---|
| 6 state colors meet contrast requirements | Pass | `tokens.ts` uses corrected values from spec Section 3.1 |
| Touch targets >= 44x44px on mobile | Pass | `TOUCH_TARGET.min = 44` used consistently; buttons have `minHeight: TOUCH_TARGET.min` |
| StateIndicator has text label alongside color | Pass | `showLabel` defaults to `true`; icon + text always rendered |
| Typography: Inter/system font, >= 16px base | Pass | `TEXT_SIZES.base = 16`; `fontFamily: 'Inter'` throughout |
| Keyboard navigation for heatmap grid | Pass | `ClassHeatmap.tsx` implements arrow-key navigation with roving tabindex |
| Focus trap in modals | Pass | `Modal.tsx` traps Tab/Shift+Tab, Esc closes |
| Screen reader announcements for state changes | Pass (partial) | Quiz feedback uses `accessibilityLiveRegion="assertive"`; M-02 notes gaps for loading |
| No auto-playing content | Pass | No auto-play audio/video/animation |
| Reduced motion support | Pass (dashboard) / Partial (mobile) | Dashboard: `@media (prefers-reduced-motion)` in globals.css; Mobile: M-06 |
| "Lacuna as open door" tone | Pass | NodeDetail and MissionCard use encouraging language ("C'e' qualcosa da ripassare", "Da ripassare") |

---

## 8. Component-Level Audit Summary

### 8.1 Mobile App

| Component | File | Findings | Status |
|---|---|---|---|
| StateIndicator | `src/mobile/components/StateIndicator.tsx` | None | Clean |
| NodeCard | `src/mobile/components/NodeCard.tsx` | None | Clean |
| MasteryMap | `src/mobile/components/MasteryMap.tsx` | H-01 (legend toggle), accessible={false} on list | Fixed |
| QuizView | `src/mobile/components/QuizView.tsx` | H-03 (radiogroup role lost) | Fixed |
| MissionCard | `src/mobile/components/MissionCard.tsx` | None | Clean |
| ProgressBar | `src/mobile/components/ProgressBar.tsx` | None | Clean |
| WellbeingPrompt | `src/mobile/components/WellbeingPrompt.tsx` | None | Clean |
| RootLayout | `src/mobile/app/_layout.tsx` | L-02 (no lang) | Recommendation |
| LoginScreen | `src/mobile/app/auth/login.tsx` | None | Clean |
| MainLayout (tabs) | `src/mobile/app/(main)/_layout.tsx` | None | Clean |
| HomeScreen | `src/mobile/app/(main)/index.tsx` | M-09 (error live region severity) | Recommendation |
| MapScreen | `src/mobile/app/(main)/map.tsx` | M-02 (loading announcement) | Recommendation |
| MissionsScreen | `src/mobile/app/(main)/missions.tsx` | M-02 (loading announcement) | Recommendation |
| ProfileScreen | `src/mobile/app/(main)/profile.tsx` | M-07 (persistence) | Recommendation |
| NodeDetailScreen | `src/mobile/app/map/[nodeId].tsx` | None | Clean |
| QuizScreen | `src/mobile/app/quiz/[quizId].tsx` | None | Clean |

### 8.2 Dashboard

| Component | File | Findings | Status |
|---|---|---|---|
| StateIndicator | `src/dashboard/components/common/StateIndicator.tsx` | None | Clean |
| Modal | `src/dashboard/components/common/Modal.tsx` | C-01 (aria-hidden on overlay) | Fixed |
| DataTable | `src/dashboard/components/common/DataTable.tsx` | M-08 (row count) | Recommendation |
| Alert | `src/dashboard/components/common/Alert.tsx` | None | Clean |
| ProgressBar | `src/dashboard/components/common/ProgressBar.tsx` | None | Clean |
| Sidebar | `src/dashboard/components/layout/Sidebar.tsx` | None | Clean |
| Header | `src/dashboard/components/layout/Header.tsx` | None | Clean |
| HeatmapLegend | `src/dashboard/components/heatmap/HeatmapLegend.tsx` | None | Clean |
| HeatmapCell | `src/dashboard/components/heatmap/HeatmapCell.tsx` | M-04 (unused) | Recommendation |
| ClassHeatmap | `src/dashboard/components/heatmap/ClassHeatmap.tsx` | None | Clean |
| StudentCard | `src/dashboard/components/students/StudentCard.tsx` | None | Clean |
| StudentMap | `src/dashboard/components/students/StudentMap.tsx` | H-02 (missing aria-label) | Fixed |
| OverrideModal | `src/dashboard/components/students/OverrideModal.tsx` | M-10 (raw state keys) | Recommendation |
| LessonUpload | `src/dashboard/components/lessons/LessonUpload.tsx` | None | Clean |
| ConceptMappingReview | `src/dashboard/components/lessons/ConceptMappingReview.tsx` | L-04 (no live region) | Recommendation |
| RootLayout | `src/dashboard/app/layout.tsx` | None | Clean |
| ClientLayout | `src/dashboard/app/client-layout.tsx` | None | Clean |
| DashboardHome | `src/dashboard/app/page.tsx` | M-03 (no breadcrumb) | Recommendation |
| LoginPage | `src/dashboard/app/login/page.tsx` | M-05 (no skip link) | Recommendation (aria-label added) |
| ClassesPage | `src/dashboard/app/classes/page.tsx` | None | Clean |
| ClassDetailPage | `src/dashboard/app/classes/[classId]/page.tsx` | L-03 (breadcrumb separators) | Recommendation |
| StudentDetailPage | `src/dashboard/app/classes/[classId]/students/[studentId]/page.tsx` | L-03 (breadcrumb separators) | Recommendation |
| LessonsPage | `src/dashboard/app/lessons/page.tsx` | None | Clean |
| LessonUploadPage | `src/dashboard/app/lessons/upload/page.tsx` | None | Clean |
| AlertsPage | `src/dashboard/app/alerts/page.tsx` | L-05 (aria-live on static) | Recommendation |

---

## 9. Token and Theme Verification

### 9.1 Color Contrast Verification

All mastery state token colors were verified against the accessibility spec Section 3.1 corrected values:

| State | Background | Foreground | Ratio | Threshold | Status |
|---|---|---|---|---|---|
| non_introdotto | #757575 | #FFFFFF | 4.6:1 | >= 4.5:1 | Pass |
| introdotto | #FFFFFF | #1A1A1A | 18.4:1 | >= 4.5:1 | Pass |
| lacuna | #C62828 | #FFFFFF | 5.6:1 | >= 4.5:1 | Pass |
| in_recupero | #EF6C00 | #000000 | 4.7:1 | >= 4.5:1 | Pass |
| da_consolidare | #FDD835 | #000000 | 12.1:1 | >= 4.5:1 | Pass |
| consolidato | #2E7D32 | #FFFFFF | 5.9:1 | >= 4.5:1 | Pass |

Both `src/mobile/theme/tokens.ts` and `src/dashboard/theme/tokens.ts` use identical corrected values matching the spec.

### 9.2 Focus Ring

- Color: `#1565C0` on white background = 4.9:1 contrast ratio (passes 3:1 non-text threshold)
- Width: 2px (spec: 2px)
- Offset: 2px (spec: 2px)
- Dashboard: Applied via `globals.css :focus-visible` selector
- Mobile: `FOCUS_RING` token defined; used in quiz option selection borders

### 9.3 Typography

- Base font: Inter (both mobile and dashboard)
- Base size: 16px (both)
- Line height: 1.5 (both -- meeting WCAG 1.4.12 recommendation)
- Font scale: 12-24pt range defined in mobile `typography.ts`

---

## 10. Automated Testing Recommendations (V1)

The following automated tests should be integrated into CI:

1. **axe-core**: Run on all dashboard pages via `@axe-core/playwright` or `jest-axe`
2. **Lighthouse CI**: Accessibility score >= 90 required per build
3. **eslint-plugin-jsx-a11y**: Enable for both mobile and dashboard TSX files
4. **Color contrast checker**: Automated verification of token values against spec thresholds

### Suggested axe-core test template

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('Dashboard home has no a11y violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test('Class heatmap has no a11y violations', async ({ page }) => {
    await page.goto('/classes/class-1?courseId=course-1');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test('Login page has no a11y violations', async ({ page }) => {
    await page.goto('/login');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
});
```

---

## 11. Manual Testing Checklist (Pre-deployment)

These tests must be performed manually before any production deployment:

- [ ] VoiceOver (iOS): Full student journey -- login, home, map, node detail, quiz, profile
- [ ] TalkBack (Android): Same student journey
- [ ] VoiceOver (macOS): Full teacher journey -- login, dashboard, class heatmap, student detail, override, lesson upload
- [ ] NVDA (Windows): Same teacher journey
- [ ] Keyboard only (dashboard): Tab through all pages, operate heatmap grid, complete override flow
- [ ] WCAG text spacing bookmarklet: Verify no content clipping at modified spacing
- [ ] Font size slider (mobile): Verify layout at 12pt and 24pt extremes

---

## 12. DSA/BES Testing Protocol Status

Per spec Section 10.3, the DSA/BES testing protocol is planned for V1 and not executed in this MVP audit. The protocol design is documented in the spec and covers:

- 3-5 students with certified DSA (L. 170/2010)
- 2-3 students with BES (Dir. MIUR 27/12/2012)
- 5 task flows with completion rate, error count, and SUS scoring
- Ethical approval and parental consent required

---

## 13. Files Modified in This Audit

| File | Change | Finding |
|---|---|---|
| `src/dashboard/components/common/Modal.tsx` | Removed `aria-hidden="true"` from overlay div | C-01 |
| `src/dashboard/components/students/StudentMap.tsx` | Added `aria-label` to micro-node buttons | H-02 |
| `src/dashboard/app/login/page.tsx` | Added `aria-label` to "show password" button | Best practice |
| `src/mobile/components/MasteryMap.tsx` | Replaced `<View>+<Text onPress>` with `<TouchableOpacity>`; removed `accessible={false}` from list container | H-01 |
| `src/mobile/components/QuizView.tsx` | Removed `accessible={false}` from radiogroup container | H-03 |

---

*Report produced by MSTR-17 (Accessibility & UX Specialist). Archived in `.maestro/tests/` per governance rules (CLAUDE.md).*
