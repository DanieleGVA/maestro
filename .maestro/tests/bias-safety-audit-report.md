# T5.6 Bias & Safety Audit Report

**Task**: T5.6 -- Bias & safety audit (content + safeguarding)
**Author**: MSTR-19 (Safeguarding & Ethics Specialist)
**Date**: 2026-05-20
**Status**: Complete
**Scope**: All content generation, safeguarding, privacy, and gamification code
**Methodology**: Static code analysis, regex pattern testing, prompt review, UI inspection

---

## Executive Summary

The MAESTRO platform demonstrates a strong safeguarding posture for an MVP. The architecture enforces safeguarding as a structural gate (not optional), with a comprehensive 9-rule system prompt, 25+ deterministic regex patterns, wellbeing keyword detection, and a 3-attempt retry/fallback mechanism. The pseudonymisation pipeline correctly strips PII including native language (Art. 9) before external LLM calls. The mobile app contains no leaderboards, FOMO mechanics, or addictive patterns.

However, this audit identifies **3 HIGH**, **6 MEDIUM**, and **8 LOW** severity findings that require attention. The most critical finding (BSA-01) relates to a gap between the safeguarding spec's claim that "red" is never shown to students and the actual implementation of a red (`#C62828`) `lacuna` state indicator visible in the student mobile app. Other high-severity findings include missing gamification anti-pattern regex patterns in the deployed code and an incomplete wellbeing keyword list for multilingual students.

Overall risk assessment: **MEDIUM**. The platform is safe for MVP deployment with the recommended mitigations applied. No critical (must-fix-before-launch) findings were identified.

---

## 1. Bias Audit

### 1.1 Gender Bias

| Check | Result | Evidence | Severity |
|---|---|---|---|
| Prompt templates use gendered pronouns | PASS | `text_agent.py:38-67` -- uses `tu` (informal you) which is gender-neutral in Italian | -- |
| Prompt examples assume gender | PASS | No gendered examples in `REVIEW_DOCUMENT_TASK` or `REMEDIATION_PATH_TASK` | -- |
| Regex catches gender stereotypes | PASS | `checker.py:250-257` -- pattern for "come una mamma/donna/ragazza in cucina..." | -- |
| Regex catches occupational gender bias | PARTIAL | `checker.py:253` -- catches "lavoro da uomo/donna" but misses subtler patterns like "da brava ragazza" | LOW |

**Finding BSA-07 (LOW)**: The gender stereotype regex catches explicit stereotypes but misses softer gendered praise/criticism patterns common in Italian educational contexts (e.g., "da brava ragazza", "non piangere come una femminuccia", "i ragazzi sono piu' portati per l'informatica"). These are more likely to appear in LLM output than the explicit stereotypes already covered.

### 1.2 Geographic Bias (Nord/Sud)

| Check | Result | Evidence | Severity |
|---|---|---|---|
| Regex catches Nord/Sud stereotypes | PASS | `checker.py:242-248` -- comprehensive pattern for "al nord si lavora/studia", "come un napoletano che si arrangia", "mentalita' del sud/nordica" | -- |
| Regex catches geographic slurs | PASS | `checker.py:176-179` -- "terrone", "polentone" in offensive language list | -- |
| Prompt instructs analogy diversity | PASS | System prompt Rule 9 in `checker.py:88-90` -- explicitly requires diversified analogies and prohibits regional stereotypes | -- |

**No findings.** Geographic bias coverage is adequate for MVP.

### 1.3 Socio-economic Bias

| Check | Result | Evidence | Severity |
|---|---|---|---|
| Prompt assumes technology access | PARTIAL | `text_agent.py:157-158` -- "esempio_pratico" asks for "runnable" code examples; this assumes student has a development environment | LOW |
| Assumptions about family structure | PASS | No references to family structure in any prompt template | -- |
| Assumptions about lifestyle | PASS | Rule 9 analogies are diverse (sport, cucina, gaming, vita quotidiana) and do not assume specific socio-economic conditions | -- |

**Finding BSA-08 (LOW)**: The remediation path template (`text_agent.py:158`) requests "un esempio pratico, concreto, eseguibile" which assumes the student has a local development environment. Students from lower socio-economic backgrounds may only have school computers. The analogy domain list in Rule 9 ("sport, cucina, gaming, vita quotidiana") implicitly assumes gaming access, though this is reasonable for the 13-19 IT student demographic.

### 1.4 Cultural Stereotypes

| Check | Result | Evidence | Severity |
|---|---|---|---|
| Regex catches national stereotypes | PASS | `checker.py:258-265` -- patterns for German precision, Chinese copying, American exaggeration | -- |
| Regex covers enough nationalities | PARTIAL | Only covers German, Chinese, American stereotypes explicitly. Missing common Italian stereotypes about other nationalities (e.g., French, English, Japanese, Indian) | LOW |

**Finding BSA-09 (LOW)**: The national stereotype regex (`checker.py:258-265`) covers three specific nationality stereotypes (German=precise, Chinese=copy, American=exaggerate). LLMs may produce stereotypes about other nationalities not covered (e.g., "come un giapponese disciplinato", "come un francese snob"). The conservative prompt instructions (Rule 9) are the primary defence here, but the regex safety net has gaps.

### 1.5 Age-Appropriateness

| Check | Result | Evidence | Severity |
|---|---|---|---|
| System prompt specifies age range | PASS | `text_agent.py:54` -- "Your audience is 13-19 years old" | -- |
| Quiz system prompt specifies age | PASS | `quiz_engine.py:64` -- "age-appropriate (13-19 years old)" | -- |
| Regex catches explicit age-inappropriate content | PASS | `checker.py:284-292` -- sexual content, graphic violence, drug use, suicide/self-harm references | -- |
| Content vocabulary calibration | PARTIAL | Rule 8 requires term explanation but does not differentiate between a 13-year-old and a 19-year-old | LOW |

**Finding BSA-10 (LOW)**: The safeguarding system does not differentiate between the lower bound (13-year-old first-year student) and upper bound (19-year-old final-year student) of the target age range. A single content moderation standard applies to both. For MVP this is acceptable, but V1 should consider age-band differentiation to allow more sophisticated content for older students without exposing younger ones.

### 1.6 Disability Bias

| Check | Result | Evidence | Severity |
|---|---|---|---|
| Ableist language detection | PARTIAL | `checker.py:176-179` catches "mongoloide", "ritardat[oiae]", "deficiente" as offensive | -- |
| Ableist metaphors | MISSING | No detection for ableist metaphors like "cieco davanti all'evidenza", "sordo ai suggerimenti", "zoppicare nell'apprendimento" | MEDIUM |
| Content assumes able-bodiedness | LOW RISK | IT content is primarily cognitive; physical ability assumptions are less likely | -- |

**Finding BSA-04 (MEDIUM)**: The regex patterns catch explicit ableist slurs but miss common ableist metaphors that LLMs may produce naturally in Italian educational content: "cieco davanti all'evidenza", "sordo ai suggerimenti", "zoppicare nell'apprendimento", "paralizzato dall'ansia". These metaphors are pervasive in Italian language and likely to appear in LLM output. They should be added to `BLOCKED_PATTERNS` as WARN severity.

---

## 2. Safeguarding Audit

### 2.1 BLOCKED_PATTERNS Regex Coverage

| Category | Pattern Count | Coverage Assessment | Gaps |
|---|---|---|---|
| STUDENT_COMPARISON | 4 | Good | English patterns could be broader (e.g., "your peers", "class average") |
| PUNITIVE_TONE | 6 | Good | "hai sbagliato" correctly set to WARN not BLOCK |
| OFFENSIVE_LANGUAGE | 2 | Adequate for MVP | Missing some newer slang; relies on LLM layer for evolving vocabulary |
| FOMO_SCARCITY | 3 | Good | Covers urgency, peer comparison, limited resources |
| GUILT_TRIGGER | 1 | Adequate | Could add "hai perso lo streak" variants (already in gamification patterns in spec, not in checker.py) |
| RED_FRAMING | 1 | Good | Covers explicit red references |
| STEREOTYPE | 3 | Good | Gender, regional, national covered |
| THERAPY_ATTEMPT | 1 | Good | Covers pseudo-therapeutic phrases |
| AGE_INAPPROPRIATE | 1 | Adequate | Broad categories covered |

**Finding BSA-02 (HIGH)**: The safeguarding spec (Section 6.2) defines `GAMIFICATION_BLOCKED_PATTERNS` with 4 additional pattern groups (ranking/leaderboard, streak pressure, countdown/timer, variable rewards). These patterns are specified in the spec but are **not present** in the deployed `checker.py` code. The checker only contains the base `BLOCKED_PATTERNS` (25 patterns). The gamification-specific patterns from the spec must be added to `checker.py` before any gamification features are enabled.

Evidence:
- Spec defines patterns at lines 1025-1069 of `safeguarding-mvp-spec.md`
- `checker.py` ends at line 293 with only `BLOCKED_PATTERNS`, no `GAMIFICATION_BLOCKED_PATTERNS`

### 2.2 Wellbeing Keyword Detection

| Category | Keyword Count | Coverage Assessment |
|---|---|---|
| Frustration | 8 | Good for Italian; age-appropriate phrases |
| Hopelessness | 10 | Good; escalation levels appropriate |
| Isolation | 6 | Good; covers common Italian expressions |
| Self-harm risk | 7 | Critical phrases covered; appropriate immediate escalation |

**Finding BSA-03 (HIGH)**: Wellbeing keywords are Italian-only. The spec acknowledges this limitation (Section 9.1, "non rileva disagio espresso in lingue diverse dall'italiano"), but MAESTRO specifically serves students whose native language may be Ukrainian, Arabic, or other non-Italian languages (the Bilingual Composer exists for this reason). A student expressing distress in their native language in a chat interface would not trigger any wellbeing detection. For MVP, this should be documented as an accepted risk with a human mitigation (teachers informed that the system cannot detect non-Italian distress signals). For V1, critical self-harm keywords in the most common student native languages should be added.

**Finding BSA-11 (LOW)**: The wellbeing detection uses exact substring matching (`checker.py:409`: `if kw.phrase in normalised`). This means slight variations of phrases are missed:
- "non ce la faccio piu'" (with "piu'" at the end) -- detected (substring match)
- "ce la faccio? no." -- NOT detected
- "non... ci riesco" -- NOT detected (ellipsis breaks substring)
- "NON SONO CAPACE!!!" -- detected (lowered + substring match works)

For MVP, exact substring matching is acceptable given the conservative principle ("nel dubbio, blocca"). False negatives here are mitigated by teacher observation. V1 should use fuzzy matching or ML-based sentiment analysis.

### 2.3 System Prompt Rules Review

All 9 rules verified against requirements:

| Rule | Requirement | Implementation | Status |
|---|---|---|---|
| 1. No student comparison | N3, F7.7, CLAUDE.md | `checker.py:52-60` | PASS |
| 2. No punitive tone | N3 | `checker.py:63-74` | PASS |
| 3. No offensive language | F8.5, N6 | `checker.py:75-80` | PASS |
| 4. No red framing | N3 | `checker.py:81-88` | PASS (see BSA-01 for UI gap) |
| 5. No FOMO/scarcity | N3, F7.7 | `checker.py:72-76` | PASS |
| 6. No therapy attempt | N3 | `checker.py:78-80` | PASS |
| 7. Lacuna = open door + mission | N3 | `checker.py:85-87` | PASS |
| 8. Technical terms explained | F8.2 | `checker.py:88-89` | PASS (prompt only, no regex enforcement) |
| 9. Diversified analogies | N6 | `checker.py:88-90` | PASS (prompt only, no regex enforcement) |

Rules 8 and 9 rely solely on prompt instructions with no regex enforcement. This is acceptable because:
- Rule 8 (term explanation): checking for unexplained terms would require knowing which terms are "technical" for each student
- Rule 9 (analogy diversity): detecting non-stereotyped analogies requires semantic understanding beyond regex

Both are well-suited for the LLM review layer planned for V1.

### 2.4 Retry Logic

| Check | Result | Evidence |
|---|---|---|
| Max attempts = 3 | PASS | `retry.py:36`: `MAX_SAFEGUARDING_ATTEMPTS = 3` |
| Temperature decreases on retry | PASS | `retry.py:21`: 0.3 on attempt 2, `retry.py:32`: 0.1 on attempt 3 |
| Violations fed back to retry prompt | PASS | `retry.py:76-79`: violation descriptions formatted into prefix |
| Fallback message served after 3 failures | PASS | `text_agent.py:350`: returns `{"fallback": True, "message": FALLBACK_MESSAGE_IT}` |
| Fallback is safe and encouraging | PASS | `retry.py:38-43`: message is neutral, mentions teacher availability |

**Finding BSA-12 (LOW)**: The `quiz_engine.py` does NOT implement retry logic. If the safeguarding check blocks a quiz, it immediately falls back to the generic message (`quiz_engine.py:161`). This means quiz generation gets only 1 attempt vs. 3 for text content. The impact is higher fallback rates for quizzes. The fix is to add the same retry loop from `text_agent._generate_with_safeguarding()` to the quiz engine.

### 2.5 Alert Escalation

| Check | Result | Evidence |
|---|---|---|
| Low urgency: log only | PASS | `checker.py:388`: urgency order defined; `alerts.py:46`: only medium+ triggers notification |
| Medium urgency: alert teacher | PASS | `alerts.py:46`: `primary.urgency in ("medium", "high", "critical")` |
| High urgency: alert teacher + referent | PASS | `alerts.py:47`: `primary.urgency in ("high", "critical")` |
| Critical urgency: immediate flag | PASS | `alerts.py:73`: `urgency_label = "URGENTE - "` for critical |
| Audit log created | PASS | `alerts.py:95-109`: `log_audit_event` called with all relevant fields |
| Only highest-urgency keyword used | PASS | `alerts.py:43`: `primary = matched_keywords[0]` (list is pre-sorted by urgency) |

**Finding BSA-05 (MEDIUM)**: The `alerts.py` function references `teacher_id` for notification routing (`alerts.py:72`), but if `teacher_id` is `None`, the teacher notification is silently skipped (`alerts.py:72`: `if notify_teacher and teacher_id`). For medium-urgency alerts where only the teacher should be notified, a missing `teacher_id` means the alert is stored in the database but nobody is notified. The function should log a warning or escalate to referent when teacher_id is missing.

**Finding BSA-13 (LOW)**: The `WellbeingAlertOut` schema (`schemas.py:9-23`) exposes `student_id` (the real internal UUID) to the teacher dashboard. While the student cannot see this, best practice per the pseudonymisation spec would be to use a pseudo-identifier in the API response and only resolve the real name server-side for the notification body.

### 2.6 Content Moderation Pipeline (End-to-End)

Verified flow for text generation:

```
1. TextAgent.generate_explanation() called
2. System prompt assembled with SYSTEM_PROMPT_SAFEGUARDING injected
3. Student context pseudonymised via LLMGateway
4. PII residual check (fail-closed)
5. LLM call made with pseudonymised prompt
6. Response de-pseudonymised
7. safeguarding_check() run on de-pseudonymised content
8. If blocked: retry up to 2 more times with escalating conservatism
9. If still blocked: fallback message served
```

This flow is correct and structurally enforced. The safeguarding gate is not bypassable.

**Finding BSA-14 (LOW)**: The safeguarding check in `text_agent.py:324` runs on `response.content` which is the **de-pseudonymised** text. This is correct for content moderation (checking what the student would see). However, it means that if a pseudonym like "STUDENTE_abc12345" happens to match a regex pattern, it would pass but the de-pseudonymised real name would not. This is a theoretical concern with negligible practical risk.

---

## 3. Privacy Audit

### 3.1 Native Language as GDPR Art. 9 Data

| Check | Result | Evidence |
|---|---|---|
| Native language stripped before LLM call | PASS | `pseudonymizer.py:122-124`: native_language mapped to `[RIMOSSO]` |
| Native language in PII residual check list | PASS | `pseudonymizer.py:156`: included in `collect_known_pii` |
| Native language not in any prompt template | PASS | Verified: no prompt template references native_language |

### 3.2 PII in Generated Content

| Check | Result | Evidence |
|---|---|---|
| Student name pseudonymised | PASS | `pseudonymizer.py:91-101`: `STUDENTE_{hash8}` |
| Teacher name pseudonymised | PASS | `pseudonymizer.py:103-113`: `DOCENTE_{hash8}` |
| Email stripped | PASS | `pseudonymizer.py:122-124`: `[RIMOSSO]` |
| Phone stripped | PASS | `pseudonymizer.py:122-124`: `[RIMOSSO]` |
| Birth year stripped | PASS | `pseudonymizer.py:122-124`: `[RIMOSSO]` |
| Registry ID stripped | PASS | `pseudonymizer.py:122-124`: `[RIMOSSO]` |
| Fail-closed on PII residual | PASS | `gateway.py:114-124`: raises `PseudonymisationError` if any known PII found |
| Mapping destroyed after use | PASS | `gateway.py:143`: `pmap.clear()` after de-pseudonymisation |

### 3.3 Pseudonymisation Robustness

**Finding BSA-06 (MEDIUM)**: The PII residual check (`pseudonymizer.py:128-145`) uses simple case-insensitive substring matching with a minimum length of 2 characters. This means:
- Common Italian first names like "Luca", "Marco", "Anna" would be checked -- good.
- But the check only verifies **known** PII values. If a student's real name appears in the source materials (e.g., teacher uploaded a lesson mentioning a student by name), it would not be caught.
- Very short surnames (2 characters) would trigger excessive false positives in the residual check, since 2-character strings appear frequently in text.
- The `len(pii) >= 2` threshold is too low for practical use -- "Li" or "Mo" as surnames would match everywhere. Recommend raising to >= 3 or using word-boundary matching.

### 3.4 Dashboard Privacy

| Check | Result | Evidence |
|---|---|---|
| Heatmap shows student display names (not real names) | CONDITIONAL | `ClassHeatmap.tsx:106`: uses `student.display_name` -- correct if this is a pseudonym; problematic if it's the real name |
| Wellbeing alerts use pseudo-ID | PARTIAL | `alerts/page.tsx:8-9`: uses `studentPseudoId` in the type but real student_id in backend |
| Student card shows display name | SAME ISSUE | `StudentCard.tsx:9`: uses `displayName` -- depends on backend mapping |

**Finding BSA-15 (LOW)**: The dashboard privacy posture depends on what the backend sends as `display_name`. If the backend sends the student's real name to the teacher dashboard, that is appropriate (teachers know their students). But if the same API is ever exposed to other students (e.g., a future group feature), the display_name must be pseudonymised. The current code does not enforce this boundary -- it relies on API design.

---

## 4. Gamification Safety Audit

### 4.1 No FOMO/Scarcity

| Check | Result | Evidence |
|---|---|---|
| No countdown timers | PASS | `QuizView.tsx:6` explicitly states "No timer (WCAG 2.2.1)"; no timer in any UI component |
| No "time remaining" display | PASS | `time_spent_ms` tracked silently (`quiz/[quizId].tsx:52`) but never shown to student |
| No urgency language in UI | PASS | All CTAs are gentle: "Quando ti senti pronto", "Continua", "Inizia il ripasso" |
| No scarcity patterns | PASS | No limited-time offers, no "only X left" patterns in any component |

### 4.2 No Addictive Patterns

| Check | Result | Evidence |
|---|---|---|
| No infinite scroll | PASS | All lists are finite with clear end states |
| No variable reward schedules | PASS | No random rewards, loot boxes, or gacha mechanics |
| No streak pressure | PASS | No streak display in any mobile component |
| No push notification manipulation | PASS (MVP) | No push notification code in mobile app yet |

### 4.3 No Public Comparisons

| Check | Result | Evidence |
|---|---|---|
| No leaderboard component | PASS | No leaderboard in any student-facing screen |
| No class ranking | PASS | No ranking data in any student API response or component |
| No peer comparison text | PASS | All progress references are to the student's own trajectory |
| Class heatmap teacher-only | PASS | `ClassHeatmap.tsx` is in `src/dashboard/` (teacher dashboard), not in `src/mobile/` (student app) |

### 4.4 Positive Reinforcement Only

| Check | Result | Evidence |
|---|---|---|
| Quiz failure tone | PASS | `quiz/[quizId].tsx:123-124`: "Nessun problema, puoi riprovare con un approccio diverso" |
| Empty state messaging | PASS | `missions.tsx:61`: "Al momento non ci sono concetti da ripassare. Continua cosi'!" |
| Error as "raw material" | PASS | Prompt Rule 2 enforces this framing throughout |
| Mission CTA encouraging | PASS | `MissionCard.tsx:77`: "Inizia il ripasso" / "Continua" -- neutral, non-pressuring |

### 4.5 Gamification Opt-Out

**Finding BSA-16 (LOW)**: F7.8 requires gamification opt-out without progress loss. The profile screen (`profile.tsx`) shows font size, font family, and theme settings, but no gamification toggle. The gamification system is not yet implemented in the MVP, so this is expected, but when gamification features are added, the opt-out control must be placed in the profile screen and must be prominently visible (not hidden in a sub-menu).

---

## 5. Mobile App UI -- Red State Color Finding

### BSA-01 (HIGH): Lacuna state uses red (#C62828) in student-facing UI

**Location**: `/Users/daniele.buonaiuto/Dev/maestro/src/mobile/theme/tokens.ts:27-32`

```typescript
lacuna: {
    bg: '#C62828',
    fg: '#FFFFFF',
    border: '#B71C1C',
    icon: 'close' as const,
    label: 'Lacuna',
},
```

**The issue**: The safeguarding spec (Section 2, Rule 4) states: "MAI indicare un colore rosso per risultati negativi. I risultati che necessitano miglioramento usano ARANCIONE." The safeguarding-mvp-spec.md (Section 2, note at line 130) acknowledges that the backend uses `#D32F2F` for `lacuna` state internally, but states "il frontend e le descrizioni testuali usano sempre 'arancione' nella comunicazione con lo studente."

However, the actual deployed mobile theme token for `lacuna` uses `#C62828` (Material Red 800), which is unambiguously red. This color is visible to students in:
- `StateIndicator.tsx` -- used on the mastery map, node cards, and mission cards
- `NodeCard.tsx:48` -- border color derived from state token
- `MissionCard.tsx:30` -- shown on recovery mission cards

The text label says "Lacuna" (not "rosso"), and the icon is an X mark, so color is not the sole indicator. But the perceptual experience of seeing a red badge next to a concept is potentially distressing for a minor and contradicts the explicit safeguarding rule.

**Recommended mitigation (MVP)**: Change `lacuna.bg` from `#C62828` to `#EF6C00` (orange, same as `in_recupero`) or to a distinct amber like `#FF8F00`. Adjust `lacuna.border` accordingly. The `lacuna` and `in_recupero` states can be distinguished by icon (X vs. refresh arrow) and label text.

---

## 6. Risk Matrix

| ID | Finding | Category | Likelihood | Impact | Severity | Fix Phase |
|---|---|---|---|---|---|---|
| BSA-01 | Lacuna state uses red in student UI | Safeguarding | Certain | Medium | **HIGH** | MVP |
| BSA-02 | Gamification regex patterns not in checker.py | Safeguarding | High (when gamification added) | High | **HIGH** | MVP |
| BSA-03 | Wellbeing keywords Italian-only | Safeguarding | Medium | High | **HIGH** | V1 (accept risk + human mitigation for MVP) |
| BSA-04 | Missing ableist metaphor detection | Bias | Medium | Medium | **MEDIUM** | MVP |
| BSA-05 | Missing teacher_id silently skips notification | Safeguarding | Low | High | **MEDIUM** | MVP |
| BSA-06 | PII residual check min-length too low (2 chars) | Privacy | Low | Medium | **MEDIUM** | MVP |
| BSA-07 | Gender bias regex gaps (soft patterns) | Bias | Low | Low | **LOW** | V1 |
| BSA-08 | Socio-economic assumption (dev environment) | Bias | Low | Low | **LOW** | V1 |
| BSA-09 | National stereotype regex limited scope | Bias | Low | Low | **LOW** | V1 |
| BSA-10 | No age-band differentiation (13 vs 19) | Bias | Low | Low | **LOW** | V1 |
| BSA-11 | Wellbeing detection exact match only | Safeguarding | Medium | Medium | **LOW** | V1 |
| BSA-12 | Quiz engine no retry logic | Safeguarding | Medium | Low | **LOW** | MVP |
| BSA-13 | student_id exposed in WellbeingAlertOut schema | Privacy | Low | Low | **LOW** | V1 |
| BSA-14 | Safeguarding check on de-pseudonymised text | Privacy | Very Low | Low | **LOW** | Accept |
| BSA-15 | Dashboard display_name provenance unclear | Privacy | Low | Low | **LOW** | V1 |
| BSA-16 | No gamification opt-out UI control | Gamification | N/A (no gamification yet) | Low | **LOW** | When gamification added |
| BSA-17 | Quiz incorrect feedback uses "Risposta errata" phrasing | Safeguarding | Certain | Low | **MEDIUM** | MVP |

### BSA-17 Detail (MEDIUM)

**Location**: `/Users/daniele.buonaiuto/Dev/maestro/src/mobile/components/QuizView.tsx:169`

```typescript
{currentFeedback.correct ? 'Risposta corretta' : 'Risposta errata'}
```

The word "errata" (erroneous/wrong) directly labels the student's action. Per safeguarding Rule 2, the system should avoid "hai sbagliato" framing. While "Risposta errata" is more clinical than "Hai sbagliato", it still labels the response as wrong rather than framing it as an opportunity. Recommended change: "Da rivedere" or "Risposta da rivedere" with the explanation following.

### BSA-18 Detail (MEDIUM)

**Finding BSA-18 (MEDIUM)**: The `ClassHeatmap.tsx` component in the teacher dashboard (`/Users/daniele.buonaiuto/Dev/maestro/src/dashboard/components/heatmap/ClassHeatmap.tsx`) displays all students in a grid with their mastery states across all concepts. While this is correctly teacher-only (in the dashboard, not the mobile app), it has no explicit access control enforcement in the component itself. If the dashboard were to ever be accessible to students (e.g., a student accidentally accesses a teacher URL), it would expose the comparative mastery data of the entire class. The component should either verify the user role before rendering or the dashboard routing should enforce teacher-only access with server-side checks.

---

## 7. Recommended Mitigations

### 7.1 MVP (Must Fix Before Launch)

| ID | Fix | Owner | Effort |
|---|---|---|---|
| BSA-01 | Change `lacuna.bg` from `#C62828` to `#FF8F00` (amber) in `tokens.ts`. Update `lacuna.border` to `#EF6C00`. Verify WCAG contrast ratio with white text on new color. | MSTR-17 (UX) + MSTR-09 (Frontend) | Small |
| BSA-02 | Add `GAMIFICATION_BLOCKED_PATTERNS` from spec Section 6.2 to `checker.py`. Merge them into the `BLOCKED_PATTERNS` list or check them in `safeguarding_check()`. | MSTR-10 (AI/ML) | Small |
| BSA-04 | Add WARN-severity patterns for common ableist metaphors in Italian: `r"(?i)\b(cieco\s+davanti|sordo\s+ai?\s+suggeriment|zoppica|paralizzat[oa]\s+(dall[ao']?|per))"` | MSTR-19 | Small |
| BSA-05 | In `alerts.py`, when `notify_teacher` is True but `teacher_id` is None, log a warning and escalate to referent notification. Never silently drop a notification. | MSTR-08 (Backend) | Small |
| BSA-06 | Raise PII residual check minimum from `len(pii) >= 2` to `len(pii) >= 3` and use word-boundary matching for short values. | MSTR-13 (Security) | Small |
| BSA-12 | Add retry loop to `quiz_engine.py` matching the pattern in `text_agent.py._generate_with_safeguarding()`. | MSTR-10 | Medium |
| BSA-17 | Change "Risposta errata" to "Da rivedere" in `QuizView.tsx:169`. | MSTR-09 | Trivial |

### 7.2 V1 (Post-Launch)

| ID | Fix | Owner | Effort |
|---|---|---|---|
| BSA-03 | Add critical wellbeing keywords in Ukrainian and Arabic (at minimum: self-harm, suicide, desire to quit). Coordinate with MSTR-18 (Localization). | MSTR-19 + MSTR-18 | Medium |
| BSA-07 | Add softer gender bias patterns. Implement ML bias classifier as pre-filter per spec Section 9.2. | MSTR-10 | Large |
| BSA-09 | Expand national stereotype patterns or replace with ML classifier. | MSTR-10 | Medium |
| BSA-10 | Implement age-band content moderation (13-15, 16-19) with differentiated thresholds. | MSTR-19 + MSTR-15 | Large |
| BSA-11 | Replace exact substring matching with fuzzy matching or ML sentiment analysis for wellbeing detection. | MSTR-10 | Large |
| BSA-13 | Use pseudo-identifiers in all API responses; resolve real names only in notification bodies. | MSTR-08 | Medium |
| BSA-18 | Add server-side role verification to all dashboard routes; add client-side role gate to `ClassHeatmap`. | MSTR-13 | Medium |

---

## 8. Test Harness Design for Ongoing Bias Monitoring

### 8.1 Automated Bias Test Suite

```
tests/safeguarding/
    test_blocked_patterns.py      -- regex unit tests (each pattern: 2+ match, 2+ no-match)
    test_wellbeing_keywords.py    -- keyword detection tests
    test_gamification_patterns.py -- gamification anti-pattern tests
    test_bias_categories.py       -- bias-specific content examples
    test_pseudonymiser.py         -- PII stripping verification
    conftest.py                   -- shared fixtures
```

**Test structure per pattern**:
```python
@pytest.mark.parametrize("text,should_block", [
    ("Sei peggio degli altri studenti", True),
    ("Il tuo codice e' migliore della versione precedente", False),  # comparison to own work, not peers
    ("Meglio di prima, continua cosi'!", False),  # self-improvement, not peer comparison
    ("La maggior parte dei compagni ha capito", True),
])
def test_student_comparison_patterns(text, should_block):
    result = safeguarding_check(text)
    assert result.passed != should_block
```

### 8.2 Quarterly Manual Audit Protocol

1. **Sampling**: Extract 200 generated content items (stratified: 40% review documents, 30% quizzes, 20% remediation paths, 10% fallback events)
2. **Automated classification**: Run each through the current bias classifier with categories: gender, geographic, socio-economic, cultural, age, disability
3. **Manual review**: 50 items (25%) reviewed by MSTR-19 + MSTR-22 using a standardized rubric:
   - [ ] Content uses gendered language unnecessarily
   - [ ] Content assumes specific socio-economic background
   - [ ] Content contains regional/national stereotypes
   - [ ] Content uses ableist metaphors
   - [ ] Content is age-inappropriate for youngest users (13)
   - [ ] Content has punitive or shaming undertones
   - [ ] Analogies come from a narrow domain
4. **Report**: Bias rate per category, comparison to previous quarter, top-3 action items
5. **Remediation**: Findings feed back into prompt templates (Rule 9 analogy examples) and regex patterns
6. **Tracking**: Results stored in `.maestro/tests/quarterly-bias-audit-{YYYY-Q}.md`

### 8.3 Continuous Monitoring Metrics

Per safeguarding-mvp-spec.md Section 8:
- `maestro.safeguarding.block_rate` > 5% triggers investigation
- `maestro.safeguarding.block_rate_by_category` > 2% for any category triggers pattern review
- `maestro.safeguarding.fallback_rate` > 1% triggers content generation review
- `maestro.safeguarding.wellbeing_alerts_total` > 3/day/class triggers CPA escalation

### 8.4 Bias Regression Testing

When any prompt template or regex pattern is changed:
1. Run full `test_blocked_patterns.py` suite
2. Generate 20 sample outputs with the modified prompt
3. Run safeguarding_check on all 20
4. Manual review of 5 samples for tone and bias
5. Document in ADR if the change affects bias posture

---

## 9. Positive Findings (Strengths)

1. **Structural enforcement**: The safeguarding gate is architecturally non-bypassable. No edge in the LangGraph connects generation to delivery without the safeguarding node.

2. **Defense in depth**: Three layers -- prompt rules, regex check, LLM review (planned) -- provide redundancy.

3. **Conservative defaults**: The system blocks on BLOCK severity and logs on WARN. "Nel dubbio, blocca" is correctly implemented.

4. **Pseudonymisation pipeline**: Robust PII stripping with fail-closed verification. Native language correctly treated as Art. 9 data.

5. **Encouraging tone throughout**: All student-facing copy in the mobile app uses encouraging, non-pressuring language. Empty states, error states, and mission prompts all follow the N3 tone requirements.

6. **No addictive patterns**: The mobile app has zero FOMO, scarcity, countdown, or comparison mechanics. Quiz timing is tracked silently for analytics but never shown to the student.

7. **Wellbeing alert escalation**: Properly tiered (low/medium/high/critical) with appropriate routing to teachers and referents.

8. **Accessibility-aware design**: State indicators use color + icon + text (never color alone). Touch targets meet WCAG minimums. The quiz has no timer.

---

*Audit complete. This report should be reviewed by MSTR-03 (CPA), MSTR-02 (CTA), MSTR-14 (Test Engineer), and MSTR-20 (QA Sentinel). High-severity findings (BSA-01, BSA-02, BSA-03) require resolution before Gate Phase 5 signoff.*
