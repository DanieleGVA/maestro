# ADR-002: Pedagogical Model Validation

## Status: Proposed

**Author**: MSTR-03 (Chief Pedagogical Architect)
**Reviewers required**: MSTR-15 (LSS), MSTR-02 (CTA), MSTR-20 (QA Sentinel)
**Date**: 2026-05-18
**Supersedes**: None
**Related requirements**: F3, F11, F11.10, F11.11, OQ7, OQ8

---

## Context

MAESTRO is a multi-agent learning companion for IT students aged 13-19 in Italian secondary schools. The pedagogical model underpins every student-facing interaction. Because the system serves **minors exclusively**, pedagogical decisions carry regulatory exposure (GDPR Art. 8/9, Age-Appropriate Design Codes) and ethical obligations beyond those of a typical EdTech product.

Five critical pedagogical decisions require evidence-based validation before architecture can proceed:

1. **F3**: The "learning style" profiling model
2. **F11**: The six-state mastery machine
3. **F11.10**: Retention-check intervals (spaced repetition schedule)
4. **F11.11**: Macro/micro rollup rule
5. **OQ7**: Mini-quiz question bank source and quality framework

The CLAUDE.md governance document mandates: *"Learning styles as fixed traits is contested (Pashler et al. 2009, Newton 2015). F3 must be framed as a content-adaptation profile, not a learner-typing claim, unless LSS validation explicitly justifies otherwise."*

This ADR validates each decision against the learning-sciences literature, resolves open questions OQ7 and OQ8, and establishes the pedagogical constraints that downstream architecture (HLDs for Agent, KG, Content, Data) must respect.

---

## Decisions

### 1. Content-Adaptation Profile (F3) -- Validation

#### Model proposed

A 5-dimension continuous vector (visivo, uditivo, cinestesico, riflessivo, sociale) representing content-presentation preferences. Values are percentages on a radar chart. The profile evolves over time based on observed behavior (F3.3, V1). The student can override any dimension (F3.4).

#### Literature review

| Source | Key finding | Relevance to F3 |
|---|---|---|
| Pashler et al. (2009), *Psychological Science in the Public Interest* | Reviewed the "meshing hypothesis" (match instruction modality to learner style). Found **no adequate evidence** that matching instructional format to diagnosed learning style improves outcomes. The few studies with adequate methodology mostly contradicted the hypothesis. | Directly invalidates any claim that MAESTRO should *type* students and *prescribe* a single modality. |
| Newton (2015), *Frontiers in Psychology* | 89% of recent papers in ERIC/PubMed implicitly endorse learning styles despite lacking evidence. The myth persists because supportive literature vastly outnumbers critical literature in search results. | Warns against citing surface-level EdTech literature to justify a learning-styles model. We must be explicit about what F3 is and is not. |
| Coffield et al. (2004), *Learning and Skills Research Centre* | Identified 71 distinct learning-style models, deeply analyzed 13. None was adequately validated. Classified models into 5 "families" from constitutionally fixed to flexibly stable preferences. | MAESTRO's model must sit in the "flexibly stable preference" family at most -- and we choose to go further by treating it as a *presentation preference* only. |
| Rogowsky et al. (2015), *Journal of Educational Psychology* | Experimental test: matching verbal/visual learners to text/audio formats produced no significant interaction effect on comprehension. | Confirms that even well-controlled matching studies fail to support the meshing hypothesis. |
| Kirschner (2017), *Teaching and Teacher Education* | Argues that while learners have preferences, preferences are not the same as effective learning conditions. Offering variety may help, but not because it matches a "style." | Supports MAESTRO's approach: offer variety, let the student choose, adapt based on engagement data -- but never claim this matches a cognitive type. |

#### Verdict: VALIDATED WITH MODIFICATIONS

The 5-dimension continuous vector is acceptable **if and only if** the following constraints are enforced:

**Modifications required:**

1. **Terminology**: The system must never use the term "learning style" in any student-facing, family-facing, or teacher-facing interface. Use "profilo di adattamento contenuti" (content-adaptation profile) or "preferenze di presentazione" (presentation preferences). This applies to UI labels, explanations, tooltips, reports, and the explainability panel (N7).

2. **No meshing claim**: The system must not claim that content presented in the student's preferred modality will produce better learning outcomes. The profile influences what is *offered first*, not what is *exclusively given*. All modalities remain available at all times (already in F10.3).

3. **Dimension naming**: The five dimensions are renamed from cognitive-type labels to **content-format descriptors**:
   - `visivo` -> `preferenza_contenuto_visuale` (visual content preference)
   - `uditivo` -> `preferenza_contenuto_audio` (audio content preference)
   - `cinestesico` -> `preferenza_esercizio_pratico` (hands-on exercise preference)
   - `riflessivo` -> `preferenza_lettura_approfondita` (in-depth reading preference)
   - `sociale` -> `preferenza_interazione_dialogica` (dialogic interaction preference)

   In user-facing contexts, shorter labels are acceptable (e.g., "Visuale", "Audio", "Pratico", "Lettura", "Dialogo") as long as they describe the *content format*, not the *learner type*.

4. **Default = uniform**: When consent (a) is denied OR before sufficient behavioral data, the vector defaults to uniform (20% each). The system must not infer a profile from demographics, age, gender, or school track.

5. **Decay and drift**: The profile is explicitly mutable. V1 behavioral adaptation (F3.3) must include a recency-weighted moving average so that the profile drifts toward current behavior, preventing stale classifications.

6. **Explainability**: The radar chart in SCR-ST-09 must include a plain-language explanation: "Questo grafico mostra come preferisci ricevere i contenuti. Non e' un giudizio sulle tue capacita'. Puoi cambiarlo in qualsiasi momento."

#### Justification

The continuous-vector approach avoids the primary failure mode identified by Pashler et al. (categorical typing followed by exclusive delivery in one modality). By treating dimensions as soft weights on content ranking rather than hard filters, MAESTRO sidesteps the meshing hypothesis entirely. The student's agency (F3.4 override) further prevents the system from imposing a profile.

The five dimensions are not derived from a validated psychometric instrument -- they are pragmatic content-delivery channels that MAESTRO actually supports (text, audio/podcast, visual/diagrammatic, interactive exercise, chatbot dialogue). This makes them engineering categories, not psychological constructs, which is the correct framing.

#### Risks

- **R-F3.1**: Teachers or families may still interpret the radar chart as a "learning style diagnosis." Mitigation: explicit labeling + onboarding guidance for teachers.
- **R-F3.2**: Behavioral adaptation in V1 may create a filter bubble (system only offers what student already consumes). Mitigation: enforce minimum diversity -- at least 2 modality types per recovery mission.
- **R-F3.3**: Regulatory risk if Italian DPA interprets F3 as automated profiling with legal effects on a minor (GDPR Art. 22). Mitigation: consent (a) is required; profile is always overridable; no decisions with "legal or similarly significant effects" are based solely on the profile. DPIA must address this explicitly.

---

### 2. Six-State Machine (F11) -- Validation

#### Model proposed

Six states with defined transitions:

```
non_introdotto --> introdotto --> [error mapping] --> lacuna --> [start recovery] --> in_recupero
--> [quiz >=80%] --> da_consolidare --> [all retention checks positive] --> consolidato
```

Regression: error on `da_consolidare` or `consolidato` -> `lacuna`.
Non-standard transitions (e.g., `lacuna` -> `consolidato` directly) require teacher override with documented motivation.

#### Literature review

| Source | Key finding | Relevance to F11 |
|---|---|---|
| Bloom (1968, 1984), *Learning for Mastery* | Students need sufficient time and corrective instruction to reach mastery. The "2-sigma problem": individual tutoring produces a 2-standard-deviation improvement over conventional instruction. Mastery-based assessment uses a criterion threshold (typically 80-90%). | MAESTRO's cycle (lacuna -> recovery -> quiz -> consolidation) directly implements the mastery-learning loop: diagnosis, corrective, formative assessment, and re-teaching. |
| Guskey (2010), *Educational Leadership* | Mastery learning requires: clear learning objectives, formative assessment, corrective activities, and second (or third) formative assessments. The cycle is repeatable until mastery is reached. | Validates the F11 loop structure. The "in_recupero -> quiz -> da_consolidare or back to lacuna" cycle is a faithful implementation of Guskey's corrective cycle. |
| Anderson et al. (2001), *Revised Bloom's Taxonomy* | Knowledge has different depth levels: Remember, Understand, Apply, Analyze, Evaluate, Create. Mastery at one level does not guarantee mastery at a deeper level. | Supports the distinction between `da_consolidare` (passed a quiz, may only test lower-order levels) and `consolidato` (demonstrated retention over time, implying deeper encoding). |
| Vygotsky (1978), *Zone of Proximal Development* | Learning occurs best in the ZPD -- tasks that are beyond current independent capability but achievable with scaffolding. | The `in_recupero` state is pedagogically analogous to the ZPD: the student has a diagnosed gap and is receiving scaffolded support. The state machine makes this zone explicit. |
| Block & Burns (1976), *Review of Educational Research* | Meta-analysis of mastery learning: students in mastery programs achieved higher, had more positive affect, and spent more time on task. Effect sizes ranged from 0.5 to 1.0 standard deviations. | Validates the overall approach of iterative recovery with threshold-based advancement. |
| Education Endowment Foundation (2024), *Teaching and Learning Toolkit* | Mastery learning shows +5 months of additional progress on average. Evidence strength rated "moderate." Cost rated "very low." | Contemporary meta-analytic evidence still supports mastery learning as effective and cost-efficient. |

#### State-by-state validation

| State | Pedagogical meaning | Validated? |
|---|---|---|
| `non_introdotto` | Concept not yet part of the student's curriculum. No assessment has occurred. | Yes. Necessary initial state for a curriculum-mapped system. |
| `introdotto` | Concept has been taught (lesson delivered) but not yet assessed. | Yes. Distinguishes "taught" from "mastered" -- a critical distinction in mastery learning. |
| `lacuna` | Assessment revealed a gap. The student has demonstrated a misconception or inability. | Yes. Direct operationalization of formative assessment diagnosis. |
| `in_recupero` | Corrective instruction is active. The student is engaged in a recovery mission. | Yes. Maps to Guskey's "corrective activities" phase. Analogous to Vygotsky's ZPD with scaffolding active. |
| `da_consolidare` | Passed the formative quiz but retention not yet confirmed through spaced checks. | Yes. Captures the distinction between short-term test performance and durable learning. Well supported by the spacing-effect literature (Cepeda et al. 2006). |
| `consolidato` | Demonstrated retention across multiple spaced checks. The concept is durably learned. | Yes. Represents successful long-term encoding, validated by retention checks. |

#### Verdict: VALIDATED

The six-state machine is pedagogically sound. It faithfully implements a mastery-learning cycle with spaced-repetition verification. The granularity is appropriate: fewer states (e.g., merging `in_recupero` with `lacuna`) would lose the pedagogically meaningful distinction between "diagnosed gap" and "actively receiving scaffolding." More states (e.g., splitting `consolidato` into "short-term consolidated" and "long-term consolidated") would add complexity without clear pedagogical benefit in an MVP.

**One refinement recommended:**

The `>=80%` quiz threshold for `in_recupero -> da_consolidare` (F11.9) is well-aligned with the mastery-learning literature. Bloom (1968) originally proposed 80-90% as the mastery criterion. The C-BEN field generally converges on 80% as the minimum acceptable threshold. Higher thresholds (90-100%) are used in safety-critical domains but are unnecessary for secondary-school IT concepts. The 50-79% "retry" band and <50% "alert teacher" band are also sound: they create a three-tier response (pass / retry / escalate) that avoids both false mastery and discouragement.

**Regression mechanism**: The regression from `da_consolidare` or `consolidato` to `lacuna` on a subsequent error is pedagogically conservative but justifiable. In mastery learning, an error on a previously "mastered" concept indicates that the original learning was fragile. Returning to `lacuna` rather than `in_recupero` ensures the full corrective cycle is re-engaged. This is consistent with the Leitner box system where a failed card returns to Box 1.

**Edge case -- teacher override**: F11.12 requires a minimum 20-character motivation and audit logging. This is pedagogically necessary because overrides bypass the evidence cycle. Overrides must not count toward autonomous consolidation KPIs (already specified in F11.12).

#### Risks

- **R-F11.1**: Students perceive the regression as punitive ("I was green and now I'm red again"). Mitigation: the UI must frame regression positively (N3 principle: "il rosso e' una porta aperta, non un marchio"). The notification should say something like "Questo argomento ha bisogno di un altro giro. E' normale, e ci sei quasi."
- **R-F11.2**: Overly aggressive regression could demoralize students with fragile confidence. Mitigation: consider a V1 enhancement where regression on a single isolated error after multiple successful retention checks triggers a "confirm" re-check before full regression. For MVP, the current model is acceptable.

---

### 3. Retention Intervals (F11.10) -- Validation

#### Schedule proposed

D+3, D+7, D+21 after a concept reaches `da_consolidare`. MVP: at least D+7. Three positive checks -> `consolidato`. One negative -> regression to `lacuna`.

#### Literature review

| Source | Key finding | Relevance |
|---|---|---|
| Ebbinghaus (1885), *Memory: A Contribution to Experimental Psychology* | Established the forgetting curve: rapid initial forgetting (50%+ within 1 hour for nonsense syllables) followed by a gradual plateau. Meaningful material is retained longer but the curve shape holds. | The foundational justification for spaced review. Without review, knowledge decays. The D+3/D+7/D+21 schedule places reviews at points where significant forgetting would otherwise occur. |
| Cepeda et al. (2006), *Psychological Bulletin* | Meta-analysis of 184 articles, 317 experiments. Optimal inter-study interval (ISI) depends on the retention interval (RI). For a 1-week RI, optimal ISI is 20-40% of RI. For a 1-year RI, optimal ISI is 5-10%. The ISI producing maximal retention increases as RI increases. | The D+3/D+7/D+21 schedule uses expanding intervals, which aligns with the finding that longer RIs need longer ISIs. However, the specific values are not derived from the Cepeda formula. |
| Cepeda et al. (2008), *Psychological Science* | Follow-up with experimental data. For a 350-day RI, optimal ISI was approximately 21 days. Expanding schedules outperformed uniform ones. | Supports D+21 as a reasonable point for a check aimed at month-scale retention. |
| Pimsleur (1967), *Modern Language Journal* | Proposed expanding intervals of 5s, 25s, 2min, 10min, 1h, 5h, 1d, 5d, 25d, 4mo, 2yr (graduated interval recall). | The general principle of expanding intervals is validated. The specific MAESTRO intervals (D+3, D+7, D+21) approximate a coarser version of this schedule for educational concepts (not vocabulary flashcards). |
| SM-2 algorithm (Wozniak 1990) | Used by SuperMemo and original Anki. Fixed intervals for initial reviews (1d, 6d), then multiplied by an "easiness factor" (default 2.5). Simple but not personalized. | SM-2 uses 1d and 6d as first intervals, then adapts. MAESTRO's D+3 and D+7 are in the same ballpark. SM-2's weakness: does not adapt to individual forgetting rates. |
| FSRS (Ye et al. 2023-2025) | Free Spaced Repetition Scheduler. Uses a forgetting-curve model with trainable parameters per user. FSRS-5 achieves 5.3% retention RMSE vs SM-2's 16.2% (benchmarked on 700M Anki reviews). Reduces daily reviews by ~25% for identical 90% retention. FSRS-6 (2025) added a per-user decay-rate parameter. | The gold standard for adaptive spaced repetition. MAESTRO's fixed intervals are a deliberate MVP simplification. Migration path to FSRS should be planned for V1. |

#### Analysis of D+3, D+7, D+21

The proposed intervals are a **reasonable heuristic** but are not directly derived from a single empirical source. They approximate the "J Method" (D+1, D+3, D+7, D+14, D+30) used in French education circles, simplified to three checkpoints.

**Strengths:**
- Expanding intervals: the 3->7->21 pattern follows the core principle that each successive interval should be longer than the previous one.
- Practical for a school setting: checks are aligned with weekly rhythms (D+3 mid-week, D+7 next week, D+21 roughly end of month). This matters when students use the system primarily during school hours.
- The omission of D+1 is defensible: for conceptual IT knowledge (not rote vocabulary), same-day or next-day review is less critical than for language flashcards.

**Weaknesses:**
- Fixed intervals ignore individual variation in forgetting rates. A student who consistently retains at D+7 does not need D+3.
- The jump from D+7 to D+21 is large (3x). If a student forgets between D+7 and D+21, the gap was too long. An intermediate check at D+14 would reduce this risk.
- No adjustment for concept difficulty. A complex concept (e.g., "SQL injection prevention") may need shorter intervals than a simple one (e.g., "variable declaration").

#### Verdict: VALIDATED FOR MVP, MODIFY FOR V1

**MVP (D+7 minimum)**: Acceptable. A single retention check at D+7 after quiz passage is a pragmatic starting point. It confirms short-term retention and is feasible within a school week.

**V1 (full schedule)**: The D+3, D+7, D+21 schedule is acceptable as a **default starting point**, with the following modifications:

1. **Add D+14** as an optional intermediate check. The schedule becomes D+3, D+7, D+14, D+21. The system presents D+14 only if the student's historical regression rate exceeds 20% (data available from MVP).

2. **Plan FSRS migration path**: The data model must store enough information (timestamps, outcomes, per-concept difficulty estimates) to enable a future transition from fixed intervals to FSRS. Specifically:
   - Store `review_timestamp`, `outcome` (pass/fail), `response_time`, `concept_difficulty_estimate` for every retention check.
   - This data will feed FSRS parameter estimation when the adaptive algorithm is implemented.

3. **Retention target**: Make the target retention rate explicit: **90% at D+21** (consistent with FSRS default and Anki standard). If cohort data shows actual retention below 85%, the fixed intervals should be shortened.

#### Recommended algorithm by phase

| Phase | Algorithm | Rationale |
|---|---|---|
| MVP | Fixed D+7 | Simplicity. One check. Sufficient evidence that week-scale spacing produces retention gains. |
| V1 | Fixed D+3, D+7, D+21 (with optional D+14) | Expanding fixed schedule. Collects the data needed for adaptive algorithms. |
| V2 | FSRS-based adaptive scheduling | Per-student, per-concept interval optimization. Requires accumulated review data from V1. |

#### Risks

- **R-F11.10.1**: Fixed intervals may over-test strong students and under-test weak ones. Mitigation: V1 optional D+14; V2 FSRS.
- **R-F11.10.2**: Students may perceive retention checks as additional "tests" rather than learning opportunities. Mitigation: frame as "Quick refresh" not "test." Never assign a grade to retention checks. Always show correct answers and explanations.
- **R-F11.10.3**: System-generated notifications for retention checks may contribute to notification fatigue. Mitigation: configurable cadence (F16.2), gentle tone, never more than 2 retention checks per day per student.

---

### 4. Worst-State Rollup Rule (F11.11 / OQ8) -- Resolution

#### Rule proposed

`macro_state = worst(micro_states)`. A macro-node is `consolidato` only when ALL its micro-node children are `consolidato`.

#### Alternatives analyzed

| Alternative | Description | Pros | Cons |
|---|---|---|---|
| **A. Worst-state** (proposed) | macro = min(micro) | Simple. Conservative. No false sense of mastery. | Harsh: 1 micro in `lacuna` out of 10 makes the entire macro red. May demoralize. |
| **B. Weighted average** | macro = weighted mean of micro states (with ordinal encoding) | Smoother. Reflects overall progress. | Requires assigning numeric values to qualitative states. A macro at "3.2 out of 6" is semantically unclear. Risks masking genuine gaps. |
| **C. Majority rule** | macro = most common micro state | Democratic. Avoids outlier influence. | Actively hides minority gaps. A student could have 6/10 micros consolidated and 4/10 in lacuna, and the macro shows "consolidated." This is pedagogically unacceptable. |
| **D. Threshold-based** | macro = consolidato if >=80% of micros are consolidato; otherwise = worst of non-consolidato micros | Balances conservatism with practical tolerance. | Introduces an arbitrary threshold. The 80% cutoff needs justification. |
| **E. Two-tier display** | Show macro state as worst-state but with a progress indicator (e.g., "7/10 consolidati") | Informative. Retains conservatism. Adds nuance. | Slightly more complex UI. |

#### Literature analysis

Mastery learning (Bloom 1968, Guskey 2010) requires that **all** subskills of a composite skill be mastered before the composite is considered mastered. This is because prerequisite relationships mean that an unmastered subskill can undermine the entire composite understanding. For example, if a student has mastered 9 out of 10 micro-concepts under "PHP Sessions" but has a lacuna on "session hijacking prevention," their macro understanding of sessions has a genuine security-critical gap.

Competency-based education (C-BEN) similarly defines mastery as meeting *all* specified competencies, not an average across them. The Aurora Institute (2024) standards reinforce that mastery is about demonstrating each competency, not a statistical aggregate.

#### Verdict: VALIDATED (Worst-State) WITH DISPLAY ENHANCEMENT (Alternative E hybrid)

**Decision**: Retain the worst-state rule as the **canonical rollup logic**. This is the pedagogically correct choice for a system that aims to close gaps rather than count them.

**Enhancement**: Adopt the two-tier display (Alternative E) for the student-facing and teacher-facing UI:

- The macro-node **color** follows the worst-state rule (the canonical state).
- A **progress indicator** is displayed alongside: "7/10 concetti consolidati" or a segmented progress bar showing the distribution of micro states.
- This gives the student truthful information about both the overall status AND the progress made, preventing the demoralizing effect of seeing a red macro when 9/10 micros are green.

**Example:**

```
[ROSSO] Sessioni PHP          7/10 consolidati  [===========---]
         ^ worst-state color    ^ progress indicator
```

The student sees: "I still have work to do on sessions, but I've already conquered 7 out of 10 concepts."

This approach satisfies the pedagogical requirement (no false mastery) while honoring the UX principle (N3: tono incoraggiante, mai punitivo).

#### Edge cases

| Scenario | Behavior |
|---|---|
| 1 micro in `lacuna` out of 10 | Macro = `lacuna`. Progress bar shows 9/10 ahead. Tone: "Ci sei quasi! Un ultimo concetto da rivedere." |
| All micros `non_introdotto` except 1 `introdotto` | Macro = `non_introdotto` (conservative). The progress indicator signals that teaching has begun. |
| Mixed `da_consolidare` and `consolidato` | Macro = `da_consolidare`. Progress bar shows how many are fully consolidated. |
| Teacher override on macro directly | Override sets the macro state explicitly. The micro states are NOT automatically changed. An audit note records the discrepancy. A "stato forzato" badge is shown. |

#### OQ8 Resolution

**OQ8 is resolved**: worst-state rollup validated with two-tier display enhancement. The canonical state for computation, reporting, and KPI purposes is always worst-state. The progress indicator is a UI-layer addition that does not change the underlying model.

#### Risks

- **R-OQ8.1**: Teachers may find the worst-state rule too conservative and override frequently. Mitigation: override audit log (F11.12), override-vs-autonomous KPI (section 8.7).
- **R-OQ8.2**: The progress indicator could undermine the worst-state message if poorly designed. Mitigation: the color/icon must remain the dominant visual signal; the progress bar is secondary.

---

### 5. Mini-Quiz Quality Framework (F11.8 / OQ7) -- Resolution

#### Source strategy proposed

Priority 1: teacher-provided question bank. Priority 2: AI-generated questions. 3-5 questions per quiz targeting a specific micro-node. Quiz always in the official language of the course (F13.19).

#### Bloom's Taxonomy targeting by state

The mini-quiz should assess different cognitive levels depending on the student's current state and the purpose of the quiz:

| Quiz purpose | Student comes from state | Bloom's level target | Rationale |
|---|---|---|---|
| Closure quiz (first attempt) | `in_recupero` | Remember + Understand | The student just completed a corrective activity. Verify basic comprehension before claiming progress. |
| Closure quiz (second+ attempt) | `in_recupero` (retry after 50-79%) | Understand + Apply | The student has seen the material multiple times. Test at a slightly higher level to confirm deeper encoding. |
| Retention check D+3 | `da_consolidare` | Remember + Understand | Early retention check. Verify that basic recall persists. |
| Retention check D+7 | `da_consolidare` | Understand + Apply | One week later. Test application, not just recall. |
| Retention check D+21 | `da_consolidare` | Apply + Analyze (where concept permits) | Three weeks out. If the student can apply and reason about the concept, retention is durable. |

This progressive Bloom's targeting ensures that later retention checks test *deeper* understanding, not just the ability to repeat memorized answers. It also prevents the system from asking the exact same questions repeatedly.

#### Quality controls for AI-generated questions

AI-generated questions carry significant risk when used with minors in a formal educational context. The following quality framework is mandatory:

**1. Generation constraints (prompt-level):**
- Questions must be anchored to specific source material (RAG over teacher-uploaded lessons and course materials). No "general knowledge" questions.
- Questions must target the specific micro-node being assessed, not adjacent concepts.
- Distractors in multiple-choice questions must be plausible but clearly wrong -- no trick questions, no ambiguous wording.
- Language level must match the student's year (biennio: simpler syntax; triennio: technical terminology acceptable).
- No cultural references, humor, or colloquialisms in assessment questions (assessment is formal even when the learning tone is playful).

**2. Structural validation (automated):**
- Each question must have exactly 4 options (MCQ) or a clear correct answer (fill-in/code completion).
- No duplicate or near-duplicate options.
- Correct answer must be unambiguous.
- Question stem must be self-contained (no external references the student cannot see).
- Code snippets in questions must be syntactically valid and complete enough to evaluate.

**3. Pedagogical review (human-in-the-loop):**
- For MVP: every AI-generated question set is reviewed by the teacher before first use. The teacher sees a preview with "Approva / Modifica / Scarta" per question.
- For V1: approved questions enter a vetted bank. The system can reuse vetted questions without per-use approval. New generations still require first-use review.
- For V2: statistical validation based on discrimination index and difficulty index from accumulated student responses. Questions with poor psychometric properties are flagged for review or retired.

**4. Bias and safety checks:**
- No questions that reference personal characteristics, family situation, or cultural background.
- No questions that could cause anxiety if answered incorrectly (e.g., "If you don't know this, you will fail").
- Code examples must not include offensive variable names, stereotyped scenarios, or inappropriate content.
- All questions pass through the Safeguarding Agent (MSTR-19) before delivery.

**5. Feedback on every question:**
- Regardless of correctness, the student sees: their answer, the correct answer, and a brief explanation.
- Incorrect answers receive encouraging tone: "Non e' la risposta giusta, ma ci sei vicino. Ecco cosa succede..."
- Correct answers are reinforced: "Esatto! Questo concetto e' ..."

#### Anti-patterns for quiz design with minors

| Anti-pattern | Why it is harmful | MAESTRO constraint |
|---|---|---|
| Timer pressure | Induces anxiety in adolescents, especially those with learning disabilities (BES/DSA). | No countdown timer on mini-quizzes. Optional "tempo impiegato" is recorded silently for analytics but never shown during the quiz. |
| Negative scoring | Punishes guessing, which discourages risk-taking in learning. | No negative scoring. Score = correct answers / total questions. |
| Red screen on failure | Creates shame association with the assessment experience. | Quiz results use arancione (orange) for incomplete mastery, never red. Green for success. (Already in F11.9.) |
| Public leaderboard | Violates N3 (no student comparisons) and can cause social anxiety. | Quiz results are private. No class-level quiz score aggregation visible to students. |
| Trick questions | Erode trust in the system and test test-taking skill rather than knowledge. | Prohibited. Distractors must be wrong for a clear, statable reason. |
| Repeated identical questions | Test memory of the specific question rather than the concept. | Question bank must contain at least 3x the quiz size per micro-node. Randomization with no-repeat-within-3-sessions constraint. |

#### OQ7 Resolution

**OQ7 is resolved**: Teacher-provided questions have priority. AI-generated questions are acceptable under the quality framework above (generation constraints + structural validation + human-in-the-loop review for first use + bias/safety checks + mandatory feedback). Bloom's taxonomy targeting is progressive by state and check number.

#### Risks

- **R-OQ7.1**: Insufficient teacher-provided question bank for many micro-nodes. Teachers have limited time to author questions. Mitigation: the AI-generation pipeline is the practical reality for most micro-nodes; the teacher review step ensures quality without requiring authorship.
- **R-OQ7.2**: AI-generated questions for advanced IT topics (SQL injection, session management) may contain technical inaccuracies. Mitigation: RAG anchoring to vetted materials; teacher first-use review; V2 psychometric validation.
- **R-OQ7.3**: Bloom's level targeting is difficult to enforce reliably with LLMs. Mitigation: include Bloom's level in the prompt template; validate with a classifier (research shows DistilBERT achieves ~91% accuracy on Bloom's level classification, per Akdeniz et al. 2025). Flag questions where classified level diverges from target.

---

## Cross-Cutting Pedagogical Principles

### Tone requirements for minors

All system-generated content -- whether recovery documents, quiz feedback, retention-check notifications, or state-change explanations -- must adhere to these tone rules:

1. **Never punitive.** Errors are opportunities. "Il rosso e' una porta aperta, non un marchio."
2. **Never comparative.** No references to class averages, other students' progress, or rankings.
3. **Always actionable.** Every negative state or result is accompanied by a clear next step.
4. **Age-appropriate.** Vocabulary and complexity adapted to the 13-19 range, with sensitivity to younger students (biennio). No sarcasm, no irony that could be misread, no condescension.
5. **Culturally neutral in assessment.** While learning content can use culturally diverse analogies, assessment questions must be culturally neutral.

### Safeguarding implications of pedagogical decisions

- The regression mechanism (consolidato -> lacuna) can be emotionally significant for adolescents. The Safeguarding Agent must monitor for patterns of repeated regression on the same concept (3+ regressions in 30 days) and trigger a support referral to the teacher.
- The content-adaptation profile must never be used to infer psychological characteristics, emotional states, or cognitive disabilities. It is a content-delivery preference, not a diagnostic instrument.
- Retention-check notifications must respect quiet hours (not before 7:00 or after 21:00) and never create urgency ("Hai un quiz in scadenza!").

### Bilingualism and assessment (F13.19)

- Mini-quizzes and retention checks are **always** in the official language of the course. No bilingual quiz mode.
- The rationale: assessment must measure IT knowledge, not language proficiency. A bilingual quiz would conflate the two.
- Study materials (recovery documents, explanations) **are** available bilingually. This asymmetry is intentional: learn in both languages, demonstrate in the official one.
- The explainability panel for quiz results can be bilingual if the student has bilingualism active.

---

## Open Items Resolved

### OQ7: Mini-quiz question bank source

**Resolution**: Teacher-provided questions take priority. AI-generated questions are the practical backbone, governed by a five-layer quality framework: (1) prompt-level generation constraints with RAG anchoring, (2) automated structural validation, (3) human-in-the-loop teacher review on first use, (4) Safeguarding Agent bias/safety check, (5) mandatory per-question feedback with encouraging tone. Bloom's taxonomy targeting is progressive by state and retention-check sequence. See Section 5 above.

### OQ8: Rollup macro/micro rule

**Resolution**: Worst-state rollup validated as the canonical rule. Enhanced with a two-tier display: macro color follows worst-state; a progress indicator (e.g., "7/10 consolidati") shows advancement. The progress indicator is UI-layer only and does not change the computational model. See Section 4 above.

---

## Consequences

### For architecture (downstream HLDs)

1. **Data model** (MSTR-07): Must store per-review-event data (`review_timestamp`, `outcome`, `response_time`, `concept_difficulty_estimate`) to enable future FSRS migration. The content-adaptation profile is a 5-float vector with timestamps and provenance (onboarding quiz vs. behavioral inference vs. manual override).

2. **Agent system** (MSTR-04): The Content Orchestrator must consume the content-adaptation profile as soft weights on content ranking, not hard filters. Minimum-diversity constraint: no recovery mission may use only a single modality.

3. **KG architecture** (MSTR-05): Macro-micro rollup is computed as worst-state. The KG query layer must support both "give me the macro state" and "give me the micro breakdown with counts per state."

4. **Content generation** (MSTR-06): Quiz generation pipeline must implement the five-layer quality framework. Prompt templates must include target Bloom's level. Generation must be RAG-anchored.

5. **Frontend** (MSTR-09): The radar chart must use content-format labels, not learner-type labels. The macro-node display must show both color (worst-state) and progress indicator. Quiz UI must not include timers, negative scoring, or red failure screens.

6. **DPIA** (MSTR-16): Must address the content-adaptation profile under GDPR Art. 22 (automated profiling of minors). Must confirm that the profile does not produce "legal or similarly significant effects."

### For the team

- MSTR-15 (LSS) should review this ADR and confirm the literature citations are accurately represented.
- MSTR-02 (CTA) should confirm the FSRS migration path is feasible within the data model.
- MSTR-22 (Pedagogical Reviewer) should use this ADR as the baseline for reviewing all generated content.
- MSTR-19 (Safeguarding) should incorporate the tone rules and anti-patterns into the Safeguarding Agent specification.

---

## References

1. Anderson, L.W., Krathwohl, D.R., et al. (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy of Educational Objectives*. Longman.

2. Akdeniz, H., Clark, T., & Roberts, J.L. (2025). "Can AI Generate Questions Aligned with Bloom's Taxonomy? A Framework for Gifted Education to Support Teachers." *Journal for the Education of the Gifted*.

3. Block, J.H. & Burns, R.B. (1976). "Mastery Learning." *Review of Research in Education*, 4, 3-49.

4. Bloom, B.S. (1968). "Learning for Mastery." *Evaluation Comment*, 1(2), 1-12.

5. Bloom, B.S. (1984). "The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring." *Educational Researcher*, 13(6), 4-16.

6. C-BEN (Competency-Based Education Network). (2024). "How is Mastery Defined in Postsecondary Competency-Based Education?"

7. Cepeda, N.J., Pashler, H., Vul, E., Wixted, J.T., & Rohrer, D. (2006). "Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis." *Psychological Bulletin*, 132(3), 354-380.

8. Cepeda, N.J., Vul, E., Rohrer, D., Wixted, J.T., & Pashler, H. (2008). "Spacing Effects in Learning: A Temporal Ridgeline of Optimal Retention." *Psychological Science*, 19(11), 1095-1102.

9. Coffield, F., Moseley, D., Hall, E., & Ecclestone, K. (2004). *Learning Styles and Pedagogy in Post-16 Learning: A Systematic and Critical Review*. London: Learning and Skills Research Centre.

10. Ebbinghaus, H. (1885/1913). *Memory: A Contribution to Experimental Psychology*. Teachers College, Columbia University (English translation).

11. Education Endowment Foundation. (2024). "Mastery Learning." *Teaching and Learning Toolkit*.

12. Guskey, T.R. (2010). "Lessons of Mastery Learning." *Educational Leadership*, 68(2), 52-57.

13. Kirschner, P.A. (2017). "Stop Propagating the Learning Styles Myth." *Computers & Education*, 106, 166-171.

14. Newton, P.M. (2015). "The Learning Styles Myth is Thriving in Higher Education." *Frontiers in Psychology*, 6, 1908.

15. Newton, P.M. & Miah, M. (2017). "Evidence-Based Higher Education -- Is the Learning Styles 'Myth' Important?" *Frontiers in Psychology*, 8, 444.

16. Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2009). "Learning Styles: Concepts and Evidence." *Psychological Science in the Public Interest*, 9(3), 105-119.

17. Pimsleur, P. (1967). "A Memory Schedule." *Modern Language Journal*, 51(2), 73-75.

18. Rogowsky, B.A., Calhoun, B.M., & Tallal, P. (2015). "Matching Learning Style to Instructional Method: Effects on Comprehension." *Journal of Educational Psychology*, 107(1), 64-78.

19. Vygotsky, L.S. (1978). *Mind in Society: The Development of Higher Psychological Processes*. Harvard University Press.

20. Wozniak, P.A. (1990). *Optimization of Learning: Application of the SuperMemo Method*. University of Technology in Poznan.

21. Ye, J. (2023). "FSRS: A Modern, Open-Source Spaced Repetition Algorithm." GitHub/open-spaced-repetition.

22. Aurora Institute. (2024). "National Standards for Quality Online, Blended, and Competency-Based Learning."
