# Pedagogical Efficacy Test Specifications -- T5.5

**Author**: MSTR-22 (Pedagogical Reviewer) jointly with MSTR-14 (Test Engineer)
**Date**: 2026-05-20
**Status**: Draft -- requires CPA (MSTR-03) and LSS (MSTR-15) review before pilot

---

## 1. Purpose

This document defines the pilot efficacy test protocol for MAESTRO. The test measures whether the system produces measurable improvements in:

1. Knowledge retention (primary outcome)
2. State progression rates (operational outcome)
3. Student engagement and affect (secondary outcome)

The design accounts for the fact that all participants are minors (13-19) in a formal school setting, requiring specific ethical safeguards.

---

## 2. Study Design

### 2.1 Design Type

**Within-subject crossover design** (preferred over between-group RCT for ethical reasons -- see Section 9).

Each student serves as their own control across different curriculum units:

- **Phase A (Control)**: Traditional teaching + teacher-generated review materials for Unit X
- **Phase B (Treatment)**: Traditional teaching + MAESTRO-generated personalized materials for Unit Y

Units X and Y are of comparable difficulty (validated by the teacher). The order is counterbalanced: half the class does A-then-B, the other half does B-then-A, to control for sequence effects.

### 2.2 Justification for Within-Subject Design

A between-group RCT (one class gets MAESTRO, another does not) raises ethical concerns:

1. **Equipoise violation**: If MAESTRO works, the control group is denied a beneficial intervention. In a school with minors, this is problematic.
2. **Contamination risk**: Students in the same school talk to each other. A pure between-group design in a single school is unrealistic.
3. **Sample size**: A single pilot school does not provide enough classes for a powered between-group comparison.

The within-subject crossover avoids these issues: every student receives both conditions, and the comparison is within the individual's own trajectory.

### 2.3 Limitations

- The within-subject design cannot measure long-term effects (only unit-level effects).
- Sequence effects (learning-to-learn improvement over time) are mitigated by counterbalancing but not eliminated.
- The pilot is underpowered for definitive causal claims. It is designed to estimate effect sizes for a future multi-school trial.

---

## 3. Participants

### 3.1 Pilot School

I.T.E.T. Pantanelli-Monnet, class 5AI (or equivalent IT class, pending confirmation via OQ12).

### 3.2 Inclusion Criteria

- Enrolled in the pilot class
- Family consent for MAESTRO use (all 5 granular consents for full participation; consent (a) and (d) specifically required for efficacy measurement)
- Student assent (verbal or written, age-appropriate)

### 3.3 Exclusion Criteria

- Students whose family denies consent (a) (profiling) cannot participate in the treatment condition. They receive standard teaching in both phases. Their data is excluded from the efficacy analysis but they are not disadvantaged educationally.
- Students who join the class mid-study are excluded from the analysis but receive MAESTRO access in the treatment phase.

### 3.4 Expected Sample Size

Based on the reference case (5AI, 9 students): N = 8-12 students.

This is a **pilot study**. The goal is effect size estimation, not statistical significance. With N=10 and a within-subject design, we can detect a large effect (d >= 0.8) with ~80% power at alpha=0.05 (paired t-test). For medium effects (d ~0.5), power is ~50%. This is acceptable for a pilot.

---

## 4. Measures

### 4.1 Primary Outcome: Knowledge Retention

**Measure**: Pre-post quiz score delta per curriculum unit.

**Protocol**:
1. **Pre-test**: Teacher-authored quiz (5-10 questions) covering Unit X/Y concepts, administered before any instruction begins. This establishes baseline knowledge.
2. **Post-test (immediate)**: Same-format quiz (different questions, same concepts, same Bloom's levels) administered 1 day after the review/recovery phase completes.
3. **Post-test (delayed)**: Same-format quiz administered at D+21 after the recovery phase completes. Measures durable retention.

**Scoring**: Score = correct / total * 100. The quiz must be teacher-authored (not AI-generated) to ensure validity and prevent teaching-to-the-test contamination.

**Analysis**:
- Primary metric: `delta_immediate = post_immediate - pre` for treatment vs control
- Secondary metric: `delta_delayed = post_delayed - pre` for treatment vs control
- Within-subject comparison: paired t-test or Wilcoxon signed-rank (if normality assumption fails)
- Effect size: Cohen's d (paired)

### 4.2 Operational Outcome: State Progression Rates

**Measures** (extracted directly from the MAESTRO database):

| Metric | Source | Formula |
|---|---|---|
| Time lacuna -> consolidato | `state_transition_log` | `timestamp(consolidato) - timestamp(lacuna)` for each node |
| Quiz pass rate at first attempt | `state_transition_log` | Count of `quiz_superato` on first attempt / total quiz attempts |
| Retention check pass rate | `retention_schedule` | Count of `completed_pass` / total completed |
| Regression rate | `state_transition_log` | Count of regressions / total transitions to `da_consolidare` or `consolidato` |
| Recovery mission completion rate | `state_transition_log` | Count of nodes reaching `da_consolidare` / count of nodes entering `in_recupero` |

These are measured only in the treatment condition (MAESTRO phase).

### 4.3 Secondary Outcome: Engagement and Affect

**Measures**:

1. **System usage metrics** (from application logs):
   - Sessions per week
   - Time-on-task per session (mean, median)
   - Content modality distribution (which channels does the student use)
   - Recovery mission initiation rate (% of lacune where student starts the mission within 48h)

2. **Student self-report** (administered post-study):
   - 5-item questionnaire adapted from the Student Computer Anxiety Scale (SCAS) and the Intrinsic Motivation Inventory (IMI) short form
   - Items rated on a 5-point Likert scale (1=Per niente d'accordo, 5=Molto d'accordo)
   - Administered in Italian, age-appropriate language

**Proposed questionnaire items**:

| # | Item | Construct |
|---|---|---|
| Q1 | "Mi e' piaciuto usare MAESTRO per ripassare" | Enjoyment/engagement |
| Q2 | "Le spiegazioni di MAESTRO mi hanno aiutato a capire meglio gli argomenti" | Perceived learning benefit |
| Q3 | "Mi sono sentito/a incoraggiato/a anche quando avevo delle lacune" | Tone/affect (N3 compliance) |
| Q4 | "Ho sentito che il sistema capiva come preferisco studiare" | Content adaptation effectiveness |
| Q5 | "Preferirei usare MAESTRO anche per i prossimi argomenti" | Continued use intention |

3. **Teacher interview** (semi-structured, 30 minutes):
   - Perceived impact on student engagement
   - Workload impact (time saved or added)
   - Quality of generated materials (accuracy, appropriateness)
   - Override frequency and reasons
   - Suggestions for improvement

---

## 5. Protocol Timeline

### Phase A (Control Unit)

| Week | Activity |
|---|---|
| W1 | Pre-test (Unit X). Teacher delivers instruction as normal |
| W2 | Teacher provides traditional review materials. Students study independently |
| W3 | Post-test immediate (Unit X) |
| W3+21d | Post-test delayed (Unit X). Retention check |

### Phase B (Treatment Unit)

| Week | Activity |
|---|---|
| W4 | Pre-test (Unit Y). Teacher delivers instruction. MAESTRO onboarding (content-adaptation profile quiz) |
| W5 | Teacher uploads verification. MAESTRO generates personalized review documents. Students use MAESTRO for recovery missions. Mini-quizzes administered via MAESTRO |
| W6 | Post-test immediate (Unit Y). Student questionnaire |
| W6+21d | Post-test delayed (Unit Y). MAESTRO retention check fires at D+7 (within MVP) |
| W7 | Teacher interview |

### Counterbalancing

- Group Alpha (random half of class): Phase A first, then Phase B
- Group Beta (other half): Phase B first, then Phase A

The counterbalancing is at the unit level, not the student level, to simplify logistics in a single classroom. The teacher teaches Unit X first to the whole class, then Unit Y. The difference is whether MAESTRO materials are available for Unit X or Unit Y.

---

## 6. Data Collection and Privacy

### 6.1 Data Collected

| Data Category | Source | Consent Required | Retention |
|---|---|---|---|
| Pre/post quiz scores | Paper or digital quizzes | Consent (a) | Pseudonymized after analysis, max 2 years |
| MAESTRO state transitions | `kmm.state_transition_log` | Consent (a) + (d) | Per DPIA retention policy |
| Usage logs (sessions, time) | Application logs | Consent (a) | Pseudonymized after analysis, max 1 year |
| Content adaptation profile | `core.student_profile` | Consent (a) | Per DPIA retention policy |
| Student questionnaire | Digital form | Consent (a) + separate study consent | Anonymized immediately after collection |
| Teacher interview | Audio recording + transcript | Teacher consent | Audio deleted after transcription; transcript retained anonymized |

### 6.2 Pseudonymization

All analysis uses pseudonymized IDs (MAESTRO's `student_pseudo_id`). The mapping from pseudo-ID to real identity is held only by the school and is never available to the analysis team (MSTR-22, MSTR-15).

### 6.3 Data Minimization

- Only the metrics listed in Section 4 are extracted. No raw content (generated documents, quiz text) is included in the analysis dataset.
- The analysis dataset is aggregated (per-student summary statistics, not per-event raw data) except where event-level data is needed for state progression analysis.

---

## 7. Analysis Plan

### 7.1 Primary Analysis

**Hypothesis**: Students show greater pre-to-post improvement on the MAESTRO-supported unit than on the traditionally-supported unit.

**Test**: Paired t-test on `delta_immediate` (treatment minus control) across students. If normality is violated (Shapiro-Wilk p < 0.05), use Wilcoxon signed-rank test.

**Effect size**: Cohen's d (paired). Report with 95% confidence interval.

**Significance threshold**: alpha = 0.05 (two-tailed). Given the pilot nature, we also report and interpret the effect size regardless of statistical significance.

### 7.2 Secondary Analyses

1. **Delayed retention**: Same as primary but on `delta_delayed`. This is the more important pedagogical measure.
2. **State progression rates**: Descriptive statistics (median, IQR) for time-to-consolidation, quiz pass rates, regression rates. No inferential test (no control comparison for these system-internal metrics).
3. **Engagement**: Descriptive statistics on questionnaire items. Mean, SD, distribution per item.
4. **Subgroup exploration** (if N permits): Compare outcomes for students with different content-adaptation profiles (e.g., high-visual vs high-reading preference). This is exploratory only -- not powered for subgroup comparisons.

### 7.3 Sequence Effect Check

Compare `delta_treatment` for Group Alpha (control-first) vs Group Beta (treatment-first) using an independent-samples t-test. If significant, report the sequence effect and interpret results conditional on order.

---

## 8. Success Criteria

### 8.1 Minimum Viable Evidence (for pilot go/no-go)

| Criterion | Threshold | Rationale |
|---|---|---|
| Pre-post immediate delta (treatment) > delta (control) | d >= 0.3 (small-to-medium effect) | Meaningful educational effect. Bloom's mastery learning literature reports d = 0.5-1.0, but the MAESTRO intervention is supplementary, not full tutoring |
| Retention check pass rate | >= 70% of D+7 checks passed | Indicates the system's content produces durable learning |
| Student questionnaire mean | >= 3.5/5.0 on all items | Indicates positive affect and perceived benefit |
| No safeguarding incidents | 0 unblocked harmful content deliveries | Mandatory. Any failure here blocks pilot |
| Teacher satisfaction | Net positive assessment | Qualitative. Teacher recommends continued use |

### 8.2 Stretch Goals (for full deployment recommendation)

| Criterion | Threshold |
|---|---|
| Pre-post delayed delta (treatment) > delta (control) | d >= 0.5 |
| Time lacuna -> consolidato | Median <= 14 days |
| Quiz first-attempt pass rate | >= 60% |
| Regression rate | < 15% |
| Student questionnaire Q5 (continued use) | Mean >= 4.0/5.0 |

---

## 9. Ethical Considerations

### 9.1 Research Ethics for Minors

This pilot constitutes educational evaluation, not clinical research. However, because it involves minors and data collection, the following safeguards apply:

1. **Informed consent**: Family consent specifically for the efficacy study (separate from MAESTRO usage consent). The consent form must explain: what data is collected, how it is used, that participation is voluntary, that withdrawal has no academic consequences.

2. **Student assent**: Students aged 14+ provide their own written assent alongside family consent. Students aged 13 provide verbal assent witnessed by the teacher.

3. **No academic harm**: No student receives worse instruction because of the study. Both conditions (traditional and MAESTRO) are supplementary to normal teaching. The control condition is the status quo, not a degraded condition.

4. **Right to withdraw**: Any student (or family) can withdraw from the study at any time without consequence. Withdrawal means their data is excluded from analysis. They continue to have access to MAESTRO if they choose.

5. **Data access**: Students and families can request their individual data at any time (GDPR Art. 15). The analysis report uses only aggregate data.

6. **DPO involvement**: If the school has a DPO, they must review and approve the study protocol. If not, the study protocol is reviewed by the school principal as the data controller's representative (pending OQ11 resolution).

### 9.2 Why Not a Standard RCT

A randomized controlled trial with a "no MAESTRO" control group in the same class would:

- Create inequity: some students get personalized help, others do not
- Be logistically impractical: students in the same room would see each other's materials
- Violate the principle of educational benefit: withholding a potentially beneficial tool from minors for research purposes is ethically questionable without strong justification

The within-subject crossover design avoids these issues. Every student eventually receives both conditions.

### 9.3 Safeguarding During the Study

- The Safeguarding Agent operates normally during the treatment phase. All content is checked before delivery.
- The wellbeing keyword detection system is active. If a student shows signs of distress, the protocol is the same as in production: alert the teacher, facilitate referral.
- The study does not increase the student's interaction with AI-generated content beyond what MAESTRO would normally provide.
- The student questionnaire does not ask about personal difficulties, family, or emotional state. It focuses on the learning experience.

---

## 10. Reporting

### 10.1 Internal Report

Produced within 2 weeks of study completion. Audience: MSTR-03 (CPA), MSTR-15 (LSS), MSTR-01 (Director), Daniele.

Structure:
1. Study design and execution summary
2. Sample characteristics (N, demographics -- aggregated only)
3. Primary outcome results with effect size and CI
4. State progression descriptive statistics
5. Engagement and affect results
6. Teacher interview synthesis
7. Findings with limitations
8. Go/no-go recommendation for expanded pilot

### 10.2 School Report

A non-technical summary for the school principal and participating teacher. In Italian. No individual student data. Focus on:
- Overall class improvement
- System usage patterns
- Teacher feedback summary
- Recommendations for continued use

### 10.3 OQ6 Resolution

OQ6 ("Studio di efficacia randomizzato") will be partially resolved by this pilot. The pilot provides preliminary effect size estimates. A fully powered multi-school RCT (or stepped-wedge design) can be planned based on these estimates if the pilot shows d >= 0.3 on the primary outcome.

---

## 11. Dependencies and Blockers

| Dependency | Status | Notes |
|---|---|---|
| T4.3 (KMM state machine implemented) | Complete | Code reviewed in efficacy report |
| T4.4 (Content generation pipeline) | Complete | Text agent and quiz engine reviewed |
| T4.8 (Dashboard + heatmap) | Complete | Dashboard components reviewed |
| F-02 finding (retention check cancellation) | Must fix | From efficacy report. Required before pilot |
| F-05 finding (quiz quality framework gaps) | Must fix | From efficacy report. Required before pilot |
| OQ12 (pilot school confirmation) | Open | Blocks participant recruitment |
| DPIA draft (T3.1) | Required | Must be complete before collecting student data |
| Teacher training | Required | Teacher must understand MAESTRO, override mechanism, and study protocol |

---

## 12. Appendices

### A. Sample Pre/Post Quiz Template

```
Unit: Sessioni PHP e Autenticazione
Level: Triennio (3rd year)
Bloom's levels: Remember + Understand + Apply

Q1 (Remember): Cosa contiene una variabile di sessione in PHP?
  A) Il codice sorgente della pagina
  B) Dati associati a un singolo utente tra diverse pagine
  C) L'indirizzo IP del server
  D) Le query SQL eseguite

Q2 (Understand): Perche' e' necessario chiamare session_start() prima di
   qualsiasi output HTML?
  A) Perche' PHP genera un errore di sintassi
  B) Perche' i cookie di sessione vengono inviati negli header HTTP,
     che precedono il body
  C) Perche' il browser non supporta sessioni dopo il body
  D) Perche' le variabili di sessione non esistono prima di session_start()

Q3 (Apply): [Code snippet] Identifica l'errore nel seguente codice di
   autenticazione e scegli la correzione appropriata.
  ...
```

### B. Student Questionnaire (Italian)

```
Questionario sull'esperienza con MAESTRO

Per ogni affermazione, indica quanto sei d'accordo:
1 = Per niente d'accordo
2 = Poco d'accordo
3 = Indifferente
4 = D'accordo
5 = Molto d'accordo

1. Mi e' piaciuto usare MAESTRO per ripassare.
   [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]

2. Le spiegazioni di MAESTRO mi hanno aiutato a capire meglio gli argomenti.
   [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]

3. Mi sono sentito/a incoraggiato/a anche quando avevo delle lacune.
   [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]

4. Ho sentito che il sistema capiva come preferisco studiare.
   [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]

5. Preferirei usare MAESTRO anche per i prossimi argomenti.
   [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]

Commento libero (facoltativo):
_____________________________________________
```

### C. Semi-Structured Teacher Interview Guide

1. Come ha trovato la qualita' dei documenti di ripasso generati? Ci sono stati casi di contenuto errato o inappropriato?
2. Ha dovuto usare l'override? Se si', per quali motivi e con che frequenza?
3. La heatmap di classe le e' stata utile? Come l'ha usata?
4. Ha notato cambiamenti nel comportamento degli studenti (motivazione, autonomia, ansia)?
5. Quanto tempo ha risparmiato (o investito in piu') rispetto al metodo tradizionale?
6. Cosa cambierebbe del sistema per il prossimo anno?
7. Consiglierebbe MAESTRO a un collega? Perche' si/no?

### D. Statistical Power Notes

For a within-subject paired t-test with N=10, alpha=0.05 (two-tailed):
- d = 0.3: power ~ 15% (underpowered -- pilot limitation)
- d = 0.5: power ~ 46%
- d = 0.8: power ~ 81%
- d = 1.0: power ~ 95%

The pilot is designed to estimate effect size, not to achieve statistical significance for small effects. If the estimated effect is d >= 0.3, a multi-school trial with N=30+ per condition can be planned with adequate power.

For the multi-school trial (V1+): N = 64 per condition provides 80% power for d = 0.5 in a between-group design.
