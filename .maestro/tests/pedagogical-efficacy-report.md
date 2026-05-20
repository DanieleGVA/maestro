# Pedagogical Efficacy Report -- T5.5

**Reviewer**: MSTR-22 (Pedagogical Reviewer)
**Date**: 2026-05-20
**Verdict**: APPROVED WITH FINDINGS
**ADR Baseline**: ADR-002-pedagogical-model.md

---

## 1. Executive Summary

The MAESTRO codebase implements the pedagogical model defined in ADR-002 with high fidelity. The six-state mastery machine, worst-state rollup, retention scheduling, Bloom's taxonomy targeting, content-adaptation profile, and safeguarding framework are all present and structurally correct. Seven findings were identified -- two of medium severity and five of low severity. None are blocking; all are addressable before pilot deployment.

---

## 2. F11 Six-State Machine

### 2.1 States

| Criterion | Verdict | Evidence |
|---|---|---|
| All 6 states present | PASS | `src/backend/src/maestro/kmm/models.py:36-43` -- `MasteryState` enum declares all 6: `non_introdotto`, `introdotto`, `lacuna`, `in_recupero`, `da_consolidare`, `consolidato` |
| DB constraint enforces valid states | PASS | `models.py:81-84` -- `CheckConstraint` on `student_node_state.current_state` restricts to the 6 values |
| Canonical ordering correct | PASS | `state_machine.py:28-35` -- `STATE_ORDER` = lacuna(0) < in_recupero(1) < non_introdotto(2) < introdotto(3) < da_consolidare(4) < consolidato(5). Matches ADR-002 Section 2 and ADR-005 Conflict 3 |

### 2.2 Legal Transitions

| Criterion | Verdict | Evidence |
|---|---|---|
| Transition table matches spec | PASS | `state_machine.py:40-55` -- `LEGAL_TRANSITIONS` matches HLD-004 Section 3.3 and the canonical cycle in ADR-002 |
| non_introdotto -> introdotto | PASS | Line 41 |
| introdotto -> lacuna | PASS | Line 42 |
| lacuna -> in_recupero | PASS | Line 43 |
| in_recupero -> da_consolidare (quiz >=80%) | PASS | Lines 44-48, validated at line 118-124 |
| in_recupero -> in_recupero (retry 50-79%) | PASS | Line 45 (self-loop). Service layer at `service.py:139-141` |
| in_recupero -> lacuna (quiz <50%) | PASS | Line 46. Service layer at `service.py:136-138` |
| da_consolidare -> consolidato (retention OK) | PASS | Line 49 |
| da_consolidare -> lacuna (regression) | PASS | Line 51 |
| consolidato -> lacuna (regression) | PASS | Line 54 |
| Non-standard transitions require override | PASS | `state_machine.py:99-106` -- override_docente bypasses table, requires motivation >=20 chars |

### 2.3 Quiz Threshold >=80%

| Criterion | Verdict | Evidence |
|---|---|---|
| Quiz score >=80 validated for advancement | PASS | `state_machine.py:118-124` -- `quiz_superato` requires `quiz_score >= 80`. Raises `IllegalTransitionError` otherwise |
| Service layer respects threshold | PASS | `service.py:126-134` -- `process_quiz_result` branches on `score >= 80` |
| Score 50-79 keeps student in_recupero | PASS | `service.py:139-141` -- target = current state (self-loop) |
| Score <50 regresses to lacuna | PASS | `service.py:136-138` -- target = `lacuna` |

### 2.4 Teacher Override

| Criterion | Verdict | Evidence |
|---|---|---|
| Motivation >=20 chars required | PASS | `state_machine.py:100-105` (engine-level) and `service.py:199-204` (service-level double check). Both strip whitespace |
| Full audit logging | PASS | `state_machine.py:208-220` -- `StateTransitionLog` created with `trigger_type=override_docente`, `triggered_by=teacher_id`, `motivation` stored |
| Transition log is append-only | PASS | `models.py:140-175` -- `StateTransitionLog` comment states "PostgreSQL triggers deny UPDATE and DELETE" |
| Override modal in dashboard enforces 20 chars | PASS | `src/dashboard/components/students/OverrideModal.tsx:18` -- `MIN_MOTIVATION_LENGTH = 20`. Textarea with validation at line 36 |
| Override excluded from autonomous KPI | NOT VERIFIED | Code does not yet compute the "% consolidamenti autonomi vs override" KPI (F11.12, Section 8.7). This is a reporting gap, not a model gap. |

**FINDING F-01 (LOW)**: The KPI computation distinguishing autonomous consolidations from override-driven consolidations is not yet implemented. This is needed before pilot to measure model health. The data is present in `state_transition_log.trigger_type` so the KPI can be computed via a query.

### 2.5 Regression Mechanism

| Criterion | Verdict | Evidence |
|---|---|---|
| Regression resets retention | PASS | `state_machine.py:195-198` -- On regression to lacuna: `next_retention_check = None`, `retention_checks_passed = 0`, `attempt_count = 0` |
| Pending retention checks cancelled on regression | PARTIAL | `retention.py:117-139` -- `cancel_pending_checks` exists and correctly sets status to `cancelled`. However, this function is not called from `execute_transition`. The caller must invoke it separately |

**FINDING F-02 (MEDIUM)**: When a student regresses to `lacuna`, `execute_transition` resets the SNS retention fields but does not call `cancel_pending_checks` on the `retention_schedule` table. If the caller forgets to invoke this function, orphaned pending retention checks could fire for a concept the student has already regressed on. Recommendation: either call `cancel_pending_checks` inside `execute_transition` when target is `lacuna`, or add a documented contract requiring the caller to do so.

---

## 3. Content-Adaptation Profile (F3)

### 3.1 Framing as Content-Adaptation, Not Learning Styles

| Criterion | Verdict | Evidence |
|---|---|---|
| Class named ContentAdaptationProfile | PASS | `src/backend/src/maestro/content/schemas.py:20` -- `class ContentAdaptationProfile` |
| 5-dimension continuous vector | PASS | `schemas.py:21-25` -- `visuale`, `audio`, `pratico`, `lettura`, `dialogo`, all `float` 0.0-1.0 |
| Default = uniform (0.2 each) | PASS | `schemas.py:21-25` -- all defaults are `0.2` |
| Dimension names use content-format descriptors | PASS | Names are `visuale`, `audio`, `pratico`, `lettura`, `dialogo` -- these are content-delivery channels, not cognitive types. Matches ADR-002 Section 1 modification 3 |
| Term "learning style" absent from student-facing code | PASS | Searched all mobile and dashboard code; the term "learning style" does not appear in any student-facing label or text |
| Tone preference included | PASS | `schemas.py:26` -- `tone: Literal["confidenziale", "neutro", "formale"]` |
| Length preference included | PASS | `schemas.py:27` -- `length: Literal["sintesi", "approfondimento"]` |
| No inference from demographics | PASS | Default uniform profile is used; no code infers from age, gender, or school track |

### 3.2 Profile Used as Soft Weights

| Criterion | Verdict | Evidence |
|---|---|---|
| Profile passed to text agent | PASS | `text_agent.py:196-200` -- profile received in `generate_explanation` |
| Profile influences tone and length | PASS | `text_agent.py:217-224` -- tone and length from profile used in prompt construction |
| All modalities remain available | NOT YET TESTABLE | The mobile app does not yet implement full modality switching (F10.2 is V1). In MVP, text is the primary modality. No code forces a single modality |

---

## 4. Quiz Engine

### 4.1 Bloom's Taxonomy Progressive by State

| Criterion | Verdict | Evidence |
|---|---|---|
| Bloom's level mapped per state | PASS | `quiz_engine.py:31-36` -- `BLOOM_BY_STATE` maps states to Bloom's level pairs |
| introdotto -> remember_understand | PASS | Line 32 |
| in_recupero -> remember_understand | PASS | Line 33 |
| da_consolidare -> apply_analyze | PASS | Line 34 |
| consolidato -> evaluate_create | PASS | Line 35 |
| Bloom's instructions in prompt | PASS | `quiz_engine.py:38-54` -- `BLOOM_INSTRUCTIONS` provides clear generation directives per level |
| Bloom's level included in quiz metadata | PASS | `quiz_engine.py:169-174` -- metadata includes `bloom_level` |

**FINDING F-03 (LOW)**: ADR-002 Section 5 specifies differentiated Bloom's levels for retention checks by sequence: D+3 = Remember+Understand, D+7 = Understand+Apply, D+21 = Apply+Analyze. The current quiz engine uses a single `BLOOM_BY_STATE` mapping that always maps `da_consolidare` to `apply_analyze` regardless of which retention check number it is. This means D+3 and D+7 checks both target `apply_analyze` rather than the progressive escalation specified in the ADR. For MVP (D+7 only) this is acceptable since there is only one check, but this must be updated for V1 when D+3 and D+21 are added.

### 4.2 Teacher-Uploaded Questions Priority

| Criterion | Verdict | Evidence |
|---|---|---|
| Teacher bank priority documented | PASS | `quiz_engine.py:9` docstring states "Teacher-authored questions (question bank) have priority over AI-generated ones" |
| Implementation of teacher bank lookup | NOT YET IMPLEMENTED | The quiz engine only implements AI generation. There is no code that queries a teacher-uploaded question bank before generating. This is consistent with the MVP approach where teacher bank is the aspiration and AI generation is the practical backbone (ADR-002 OQ7 Section 5) |

**FINDING F-04 (LOW)**: The teacher question bank priority mechanism is documented in the docstring but not yet implemented as code. For MVP this is acceptable per ADR-002 OQ7, but the V1 milestone must add the bank lookup before falling through to AI generation.

### 4.3 Five-Layer Quality Control

| Layer | Verdict | Evidence |
|---|---|---|
| 1. Generation constraints (prompt-level) | PASS | `quiz_engine.py:56-72` -- system prompt includes: target specific node, clear correct answer, no trick questions, age-appropriate language, no student name, 4 options per MCQ |
| 2. Structural validation (automated) | PARTIAL | JSON parsing validates structure at `quiz_engine.py:163-167`, but no explicit validation of 4 options, no duplicate detection, no distractor plausibility check |
| 3. Human-in-the-loop (teacher review) | NOT YET IMPLEMENTED | No teacher review flow exists in code. Per ADR-002 this is required for MVP |
| 4. Bias/safety checks | PASS | `quiz_engine.py:156-161` -- `safeguarding_check()` called on quiz content before delivery |
| 5. Feedback on every question | PASS | `QuizView.tsx:157-173` -- feedback section with `feedbackCorrect` and `feedbackIncorrect` styles |

**FINDING F-05 (MEDIUM)**: Two of the five quality control layers are incomplete: (a) Layer 2 structural validation only checks JSON parsability, not the 4-option/no-duplicate/unambiguous-answer constraints specified in ADR-002. (b) Layer 3 teacher review on first use is not yet implemented. Since AI-generated quiz questions are directly served to minors, the teacher review flow should be prioritized for MVP. Recommendation: Add a `reviewed: bool` flag to AI-generated question sets and require teacher approval before first delivery.

### 4.4 Quiz UI Anti-Patterns

| Anti-pattern | Status | Evidence |
|---|---|---|
| No countdown timer | PASS | `QuizView.tsx` -- no timer component, no time-related state. Comment at line 6: "No timer (accessibility spec Section 2.1, WCAG 2.2.1)" |
| No negative scoring | PASS | `quiz_engine.py:210` -- `score = int((correct / total) * 100)`. Only correct answers count |
| No red screen on failure | PASS | `QuizView.tsx:332-336` -- `feedbackIncorrect` uses `backgroundColor: '#FFF3E0'` (light orange) and `borderLeftColor: '#EF6C00'` (orange). No red for failure |
| No public leaderboard | PASS | No leaderboard component exists anywhere in mobile or dashboard code |
| No trick questions | PASS | System prompt at `quiz_engine.py:61-62` explicitly prohibits trick questions |
| Feedback always visible | PASS | `QuizView.tsx:157-173` -- feedback rendered for every question after submission |

---

## 5. Rollup and Heatmap

### 5.1 Worst-State Rollup

| Criterion | Verdict | Evidence |
|---|---|---|
| worst_state function correct | PASS | `heatmap.py:57-61` -- `worst_state()` uses `min()` with `STATE_ORDER` as key. Returns `non_introdotto` for empty lists |
| Macro rollup computes worst of micros | PASS | `heatmap.py:153-176` -- `compute_macro_rollup_from_states` collects micro states and applies `worst_state()` |
| Missing micros default to non_introdotto | PASS | `heatmap.py:162-164` -- `node_states.get(nid, MasteryState.non_introdotto.value)` |

### 5.2 Two-Tier Display (ADR-002 Section 4 Enhancement)

| Criterion | Verdict | Evidence |
|---|---|---|
| Progress indicator present | PASS | `NodeCard.tsx:59-84` -- shows `microsConsolidato/totalMicros` with progress bar |
| MasteryMap shows summary count | PASS | `MasteryMap.tsx:41-42` and line 57-58 -- "X di Y macro-concetti consolidati" |
| MacroRollup stores per-state counts | PASS | `heatmap.py:20-26` -- `MacroRollup` dataclass includes `micros_per_state: dict[str, int]` and `total_micros: int` |
| Color follows worst-state rule | PASS | `NodeCard.tsx:48` -- `borderLeftColor: token.bg` where `token = MASTERY_TOKENS[state]` and `state` is the rollup state |

### 5.3 No Public Student Comparisons

| Criterion | Verdict | Evidence |
|---|---|---|
| Class heatmap is teacher-only | PASS | `ClassHeatmap.tsx` is in `src/dashboard/components/heatmap/` (teacher dashboard, not mobile) |
| Student sees only own map | PASS | `MasteryMap.tsx` renders only the student's own nodes. No class-level data is passed to or displayed in the mobile app |
| Safeguarding blocks comparisons | PASS | `checker.py:98-129` -- Multiple regex patterns block student comparison language |

---

## 6. Retention Scheduling

### 6.1 MVP D+7

| Criterion | Verdict | Evidence |
|---|---|---|
| D+7 constant defined | PASS | `state_machine.py:58` -- `MVP_RETENTION_DELAY_DAYS = 7` |
| Retention scheduled on da_consolidare transition | PASS | `state_machine.py:224-239` -- when target is `da_consolidare` and it is a fresh transition (not self-loop), creates `RetentionSchedule` with `scheduled_at = now + 7 days` |
| Self-loop increments counter | PASS | `state_machine.py:241-242` -- on self-loop (retention pass but not yet consolidato), `retention_checks_passed += 1` |
| Retention cleared on consolidato | PASS | `state_machine.py:245-246` -- `next_retention_check = None` |

### 6.2 FSRS Columns Present for V2

| Criterion | Verdict | Evidence |
|---|---|---|
| fsrs_stability column | PASS | `models.py:129` -- `fsrs_stability: Mapped[float | None]`, nullable |
| fsrs_difficulty column | PASS | `models.py:130` -- `fsrs_difficulty: Mapped[float | None]`, nullable |
| concept_difficulty_estimate | PASS | `models.py:222` -- `RetentionSchedule` includes `concept_difficulty_estimate: Mapped[float | None]` |
| Review data stored per event | PASS | `models.py:119-120` -- `last_quiz_score`, `last_quiz_at`. `RetentionSchedule` stores `quiz_score`, `response_time_ms`, `completed_at` |

### 6.3 Retention Check Processing

| Criterion | Verdict | Evidence |
|---|---|---|
| Pass -> consolidato | PASS | `service.py:167-169` -- `retention_check_ok` triggers transition to `consolidato` |
| Fail -> lacuna | PASS | `service.py:170-172` -- `retention_check_fail` triggers transition to `lacuna` |
| Due checks query | PASS | `retention.py:18-33` -- `get_due_retention_checks` filters by `status=pending` and `scheduled_at <= now` |

---

## 7. Safeguarding and Tone

### 7.1 Safeguarding System Prompt

| Criterion | Verdict | Evidence |
|---|---|---|
| Injected in all LLM calls | PASS | `text_agent.py:8` docstring: "Safeguarding system prompt is injected in EVERY call -- this is non-optional". `text_agent.py:212-216` injects `SYSTEM_PROMPT_SAFEGUARDING` into system prompt |
| Quiz engine injects safeguarding | PASS | `quiz_engine.py:125-128` -- safeguarding rules injected into quiz system prompt |
| Post-generation check on text | PASS | `text_agent.py:324` -- `safeguarding_check(response.content)` |
| Post-generation check on quiz | PASS | `quiz_engine.py:156-161` -- `safeguarding_check(response.content)` |

### 7.2 Safeguarding Pattern Coverage

| Pattern Category | Verdict | Evidence |
|---|---|---|
| Student comparison (N3, F7.7) | PASS | `checker.py:98-129` -- 4 patterns covering direct comparison, implicit comparison, class statistics, English-language comparisons |
| Punitive tone (N3) | PASS | `checker.py:132-171` -- 6 patterns covering personal judgments, negative projections, shame language, "hai sbagliato", incredulity, blame-despite-help |
| Offensive language (F8.5) | PASS | `checker.py:174-190` -- Italian and English profanity lists including discriminatory terms |
| FOMO/Scarcity (N3, F7.7) | PASS | `checker.py:193-215` -- urgency, peer-progress FOMO, scarcity patterns |
| Guilt triggers (N3) | PASS | `checker.py:219-226` -- inactivity guilt patterns |
| Red framing (N3) | PASS | `checker.py:229-238` -- blocks "rosso" in result context |
| Stereotypes (N6) | PASS | `checker.py:241-267` -- regional (Nord/Sud), gender, and national stereotypes |
| Therapy attempts (N3) | PASS | `checker.py:270-280` -- blocks improvised psychological support |
| Age-inappropriate content (F8.5) | PASS | `checker.py:283-292` -- blocks sexual, violent, drug, self-harm content |

### 7.3 Wellbeing Detection

| Criterion | Verdict | Evidence |
|---|---|---|
| Wellbeing keywords defined | PASS | `checker.py:336-386` -- 32 keywords across frustration, hopelessness, isolation, self_harm_risk |
| Urgency levels | PASS | low, medium, high, critical with escalation to log -> alert_teacher -> alert_referent |
| System does NOT provide therapy | PASS | `checker.py:397` -- docstring explicitly states "The system does NOT provide psychological support -- it facilitates contact with the school referent" |
| WellbeingPrompt UI component | PASS | `WellbeingPrompt.tsx` -- supportive tone, references teacher, does not attempt counseling. Text: "Se hai bisogno di parlare con qualcuno, il tuo docente e' sempre disponibile" |

### 7.4 Retry and Fallback

| Criterion | Verdict | Evidence |
|---|---|---|
| Max 3 attempts | PASS | `retry.py:36` -- `MAX_SAFEGUARDING_ATTEMPTS = 3` |
| Progressive conservatism | PASS | `retry.py:13-34` -- attempt 2 adds violation-specific context (temp 0.3), attempt 3 goes ultra-safe (temp 0.1, no analogies) |
| Fallback message appropriate | PASS | `retry.py:38-43` -- `FALLBACK_MESSAGE_IT` directs student to teacher materials, encouraging, no blame |

---

## 8. Gamification Anti-Patterns

| Anti-pattern | Status | Evidence |
|---|---|---|
| No public leaderboards | PASS | No leaderboard component in any frontend code |
| No public student comparisons | PASS | Mobile app contains no class-level comparison data. Safeguarding blocks comparative language |
| No FOMO patterns | PASS | No "your classmates are ahead" or scarcity messaging. Safeguarding regex blocks such patterns |
| No countdown pressure | PASS | No timer in quiz UI. Retention notifications are configurable (F16.2) |
| Mission cards use encouraging tone | PASS | `MissionCard.tsx:35-38` -- "Da ripassare" (not "Fallito"), "Recupero in corso" |
| No red for negative results | PASS | Quiz failure uses orange (#FFF3E0 bg, #EF6C00 border). Mobile `feedbackIncorrect` style confirmed |

---

## 9. UI Pedagogical Correctness

### 9.1 State Color/Icon/Label Triad

| State | Color | Icon | Label | WCAG OK |
|---|---|---|---|---|
| non_introdotto | #757575 grey | Empty circle | "Non introdotto" | fg #FFFFFF on #757575 = 4.6:1 PASS |
| introdotto | #FFFFFF white | Circle+dot | "Introdotto" | fg #1A1A1A on #FFFFFF = 17:1 PASS |
| lacuna | #C62828 red | X cross | "Lacuna" | fg #FFFFFF on #C62828 = 5.6:1 PASS |
| in_recupero | #EF6C00 orange | Refresh arrow | "In recupero" | fg #000000 on #EF6C00 = 4.6:1 PASS |
| da_consolidare | #FDD835 yellow | Check outline | "Da consolidare" | fg #000000 on #FDD835 = 14.7:1 PASS |
| consolidato | #2E7D32 green | Filled check circle | "Consolidato" | fg #FFFFFF on #2E7D32 = 5.2:1 PASS |

All states use color + distinct icon + text label. Never color alone (F9.3).

### 9.2 Text Agent Prompt Compliance

| Criterion | Verdict | Evidence |
|---|---|---|
| 4-block structure (F5.1) | PASS | `text_agent.py:96-136` -- REVIEW_DOCUMENT_TASK requires `il_tuo_errore`, `perche_succede`, `come_si_fa_giusto`, `ricordati` |
| Code ERRATO/CORRETTO labels | PASS | `text_agent.py:58-59` -- system prompt rule 7 requires [ERRATO] and [CORRETTO] labels |
| Source priority hierarchy | PASS | `text_agent.py:56-57` -- "Prioritise Teacher Lesson sources (TIER 1) over textbook (TIER 2) over external sources (TIER 3)" |
| Pseudonymized student ID | PASS | `text_agent.py:45-46` -- "You only know them as {student_pseudo_id}". No real name in prompts |
| Retry approach diversification | PASS | `text_agent.py:248-255` -- retry note explicitly requires "DIFFERENT explanatory approach: different analogy domain, more concrete examples, smaller sub-steps" |

---

## 10. Content-Adaptation Profile in Mobile UI

| Criterion | Verdict | Evidence |
|---|---|---|
| Term "learning style" absent | PASS | Searched all `src/mobile/` files. The phrase "learning style" does not appear in any student-facing text or label |
| Profile page exists | PASS | `src/mobile/app/(main)/profile.tsx` exists in the file list |
| Radar chart for profile | NOT VERIFIED IN CODE | The radar chart component was not found in the files read. This may be a V1 feature or may be implemented in a component not yet reviewed. ADR-002 requires it with the disclaimer text |

**FINDING F-06 (LOW)**: The radar chart with the mandatory explainability text ("Questo grafico mostra come preferisci ricevere i contenuti. Non e' un giudizio sulle tue capacita'. Puoi cambiarlo in qualsiasi momento.") was not found in the mobile code. If the radar chart is implemented in the profile page, it must include this text. If it is not yet implemented, it should be added before the profile page is exposed to students.

---

## 11. Bilingual Assessment Boundary (F13.19)

| Criterion | Verdict | Evidence |
|---|---|---|
| Quizzes in official language only | PASS | `quiz_engine.py:64` -- "Language: Italian" in system prompt. ADR-002 cross-cutting principle: "Mini-quizzes and retention checks are always in the official language of the course" |
| System prompt enforces language | PASS | `text_agent.py:62` -- "Content must be in {course_language} unless bilingual mode instructions say otherwise" |

---

## 12. Findings Summary

| ID | Severity | Component | Finding | Recommendation |
|---|---|---|---|---|
| F-01 | LOW | KMM/Reporting | Override-vs-autonomous KPI not computed | Add SQL query or service method computing the ratio from `state_transition_log.trigger_type` |
| F-02 | MEDIUM | KMM/State Machine | `execute_transition` does not cancel pending retention checks on regression | Either integrate `cancel_pending_checks` into `execute_transition` or document the caller contract explicitly |
| F-03 | LOW | Quiz Engine | Bloom's level not differentiated by retention check number (D+3 vs D+7 vs D+21) | Acceptable for MVP (D+7 only). Must be updated for V1 |
| F-04 | LOW | Quiz Engine | Teacher question bank priority not yet implemented | Acceptable for MVP per ADR-002 OQ7. Must be added for V1 |
| F-05 | MEDIUM | Quiz Engine | Structural validation (layer 2) and teacher review (layer 3) of the 5-layer quality framework are incomplete | Add JSON schema validation for quiz structure; implement teacher first-use review flow before serving AI-generated quizzes to students |
| F-06 | LOW | Mobile/Profile | Radar chart with explainability text not found in code | Ensure the radar chart includes the ADR-002 mandated disclaimer before student exposure |
| F-07 | LOW | KMM/State Machine | Orphaned retention checks possible if caller does not invoke cancel | See F-02. Either automate or document |

---

## 13. Overall Assessment

The pedagogical model implementation is sound and faithful to ADR-002. The critical elements -- the six-state machine, canonical ordering, quiz threshold, teacher override with audit, worst-state rollup, retention scheduling, safeguarding, and anti-pattern enforcement -- are all correctly implemented with evidence traceable to code.

The two medium-severity findings (F-02 and F-05) should be addressed before pilot deployment:

1. **F-02**: The retention check cancellation gap is a data integrity concern. A stale pending retention check firing for a regressed concept could confuse the student or trigger an invalid state transition. Fix by integrating the cancellation call into the transition engine.

2. **F-05**: Serving AI-generated quiz questions to minors without teacher review or structural validation contradicts the ADR-002 quality framework. For pilot, at minimum add a `teacher_approved` flag and a review queue.

The low-severity findings are tracking items for V1 and do not block MVP pilot.

**Verdict: APPROVED for MVP pilot with the condition that F-02 and F-05 are addressed before student-facing deployment.**

---

## 14. Code References Index

| File | Path | Key Content |
|---|---|---|
| KMM Models | `src/backend/src/maestro/kmm/models.py` | MasteryState enum, StudentNodeState, StateTransitionLog, RetentionSchedule |
| State Machine | `src/backend/src/maestro/kmm/state_machine.py` | STATE_ORDER, LEGAL_TRANSITIONS, validate_transition, execute_transition |
| KMM Service | `src/backend/src/maestro/kmm/service.py` | process_quiz_result, process_retention_check, teacher_override |
| Heatmap | `src/backend/src/maestro/kmm/heatmap.py` | worst_state, compute_macro_rollup_from_states, ClassHeatmap |
| Retention | `src/backend/src/maestro/kmm/retention.py` | schedule_retention, get_due_retention_checks, cancel_pending_checks |
| Quiz Engine | `src/backend/src/maestro/content/quiz_engine.py` | BLOOM_BY_STATE, QuizEngine.generate_quiz, evaluate_response |
| Text Agent | `src/backend/src/maestro/content/text_agent.py` | TextAgent, safeguarding integration, prompt templates |
| Content Schemas | `src/backend/src/maestro/content/schemas.py` | ContentAdaptationProfile, TargetNode |
| Content Cache | `src/backend/src/maestro/content/cache.py` | Three-level cache (L1 Redis, L2 DB, L3 batch) |
| Safeguarding | `src/backend/src/maestro/safeguarding/checker.py` | BLOCKED_PATTERNS, safeguarding_check, wellbeing_check |
| Safeguarding Retry | `src/backend/src/maestro/safeguarding/retry.py` | RetryContext, build_retry_prompt, FALLBACK_MESSAGE_IT |
| Mobile StateIndicator | `src/mobile/components/StateIndicator.tsx` | Color + icon + label rendering |
| Mobile QuizView | `src/mobile/components/QuizView.tsx` | No timer, orange for failure, feedback per question |
| Mobile MasteryMap | `src/mobile/components/MasteryMap.tsx` | Two-tier display, legend, summary count |
| Mobile NodeCard | `src/mobile/components/NodeCard.tsx` | Progress indicator, rollup state display |
| Mobile MissionCard | `src/mobile/components/MissionCard.tsx` | Encouraging copy, no punitive language |
| Mobile WellbeingPrompt | `src/mobile/components/WellbeingPrompt.tsx` | Supportive tone, teacher referral |
| Mobile Tokens | `src/mobile/theme/tokens.ts` | MASTERY_TOKENS with colors, icons, labels |
| Dashboard ClassHeatmap | `src/dashboard/components/heatmap/ClassHeatmap.tsx` | Teacher-only class view |
| Dashboard OverrideModal | `src/dashboard/components/students/OverrideModal.tsx` | 20-char motivation, transition preview |
| Dashboard Tokens | `src/dashboard/theme/tokens.ts` | Matching MASTERY_TOKENS |
