# MAESTRO -- Pilot Deployment Plan

**Document**: PILOT-PLAN-001
**Status**: Draft
**Version**: 1.0
**Date**: 2026-05-20
**Author**: MSTR-01 (Programme Director)
**Approved by**: Pending -- Director (MSTR-01) + CTA (MSTR-02) + CPA (MSTR-03) + Privacy (MSTR-16) + QA Sentinel (MSTR-20) + Human (Daniele)
**Task**: T6.5
**References**: CLAUDE.md Phase 6 Gate, DPIA (`dpia-mvp-slim.md`), DR Plan (`dr-plan.md`), EU Residency (`eu-residency-architecture.md`), Cost Model (`cost-model.md`), Security Pen-Test (`security-pentest-report.md`), Accessibility Audit (`accessibility-audit-report.md`), Pedagogical Efficacy (`pedagogical-efficacy-report.md`), Bias/Safety Audit (`bias-safety-audit-report.md`), Audit Trail Validation (`audit-trail-validation-report.md`), Safeguarding Spec (`safeguarding-mvp-spec.md`), Requirements (`MAESTRO_requisiti_v0.3.md`), Production HLD (`production-HLD.md`)

---

## 1. Executive Summary

### 1.1 Pilot Scope

MAESTRO is a personalised learning companion for Italian IT students (minors, ages 13-19). This pilot deploys the MVP to a single school, a single class, and a single subject to validate the system under real-world conditions before broader rollout.

| Parameter | Value |
|---|---|
| School | I.T.E.T. Pantanelli-Monnet, Brindisi (or confirmed alternative) |
| Class | 5AI (~25 students, ages 17-19) |
| Subject | Informatica (Computer Science) |
| Teacher | Referent teacher for 5AI Informatica |
| Duration | 8 weeks (Week 0 pre-pilot + Weeks 1-8 active) |
| Infrastructure | Hetzner Cloud (DE) + Scaleway (FR) -- EU-only |
| Budget | EUR 285-465/month (within EUR 300-520 budget allocation) |

### 1.2 Success Criteria (Measurable)

| ID | Criterion | Threshold | Measurement Method |
|---|---|---|---|
| SC-01 | Knowledge retention improvement | Effect size d >= 0.3 (pre/post within-subject crossover) | Teacher-authored pre/post quizzes (T5.5 protocol) |
| SC-02 | D+7 retention check pass rate | >= 70% | System data: `kmm.retention_schedule` |
| SC-03 | Weekly active students | >= 80% of enrolled | System data: session logs |
| SC-04 | Teacher satisfaction | >= 4/5 overall score | Post-pilot interview (T5.5 Appendix C) |
| SC-05 | System uptime (school hours) | >= 99% | Grafana monitoring: `up{job="maestro-backend"}` |
| SC-06 | Safeguarding incidents missed | 0 | Audit trail + teacher feedback |
| SC-07 | Student questionnaire mean | >= 3.5/5.0 on all items | T5.5 Appendix B questionnaire |

### 1.3 Go/No-Go Decision Criteria

The pilot proceeds ONLY if all prerequisites in Section 2 are marked complete. The pilot is terminated early if any rollback trigger in Section 9 fires.

**Go decision**: Requires unanimous approval from Director (MSTR-01), CTA (MSTR-02), CPA (MSTR-03), Privacy (MSTR-16), QA Sentinel (MSTR-20), and Human (Daniele).

**Post-pilot decision framework**: Section 10.

---

## 2. Prerequisites and Sign-off Checklist

Every item must have an owner and verification evidence before the pilot begins.

### 2.1 Legal and Privacy

| # | Prerequisite | Owner | Evidence | Status |
|---|---|---|---|---|
| P-01 | DPO of school has reviewed and approved DPIA | DPO / Dirigente Scolastico | Written DPO opinion letter | PENDING |
| P-02 | Dirigente Scolastico (school principal) has signed off on MAESTRO adoption | Daniele | Signed authorisation letter | PENDING |
| P-03 | Parental consent forms collected (all 5 granular consents, F14.3) | Referent teacher + Admin IT | Signed paper forms archived securely; digital consent records created via `POST /api/v1/students/{id}/consent` | PENDING |
| P-04 | Student privacy information notice distributed | Referent teacher | Signed receipt or classroom distribution log | PENDING |
| P-05 | Family privacy information notice distributed | Referent teacher | Signed receipt or postal tracking | PENDING |
| P-06 | Family information meeting held | Referent teacher + Daniele | Meeting minutes with attendance list | PENDING |
| P-07 | DPA formalised with Anthropic, OpenAI, Hetzner, Scaleway | Daniele | Signed DPA documents | PENDING |
| P-08 | Garante Privacy pre-pilot actions completed (from `garante-alignment-checklist.md`) | MSTR-16 + DPO | Checklist items 1.1, 1.3, 1.8, 1.9, 7.4 resolved | PENDING |
| P-09 | School privacy register updated to include MAESTRO | DPO / Admin IT | Updated register entry | PENDING |
| P-10 | Minimum 15-day consent collection period observed | Referent teacher | Date proof: forms distributed >= 15 days before pilot start | PENDING |

### 2.2 Technical

| # | Prerequisite | Owner | Evidence | Status |
|---|---|---|---|---|
| P-11 | Infrastructure deployed and health-checked on Hetzner | MSTR-12 (DevOps) | `curl -sf https://<domain>/api/v1/health` returns 200; Grafana dashboard shows all green | PENDING |
| P-12 | Security pen-test gate MET (0 critical, 0 high post-remediation) | MSTR-13 (Security) | `security-pentest-report.md`: gate criterion confirmed | PASS |
| P-13 | Accessibility conditional pass (0 critical, 0 high post-fix) | MSTR-17 (UX) | `accessibility-audit-report.md`: conditional pass confirmed | PASS |
| P-14 | DR plan tested (at least 1 backup + restore cycle) | MSTR-12 (DevOps) | DR test report in `.maestro/tests/dr-backup-verify-<date>.md` | PENDING |
| P-15 | Monitoring and alerting operational (Grafana + Mimir + alerts) | MSTR-12 (DevOps) | Alert rules firing on test conditions; ServiceDown alert verified | PENDING |
| P-16 | EU data residency self-assessment completed | MSTR-12 + MSTR-16 | Signed attestation per `eu-residency-architecture.md` Section 5 | PENDING |
| P-17 | Rollback plan verified (infrastructure teardown tested) | MSTR-12 | Documented rollback test | PENDING |
| P-18 | Keycloak configured: school realm, teacher/admin accounts, student accounts | MSTR-12 | User list in Keycloak admin console | PENDING |
| P-19 | TLS certificate operational (Let's Encrypt via Caddy) | MSTR-12 | `https://<domain>` accessible without errors | PENDING |

### 2.3 Pedagogical

| # | Prerequisite | Owner | Evidence | Status |
|---|---|---|---|---|
| P-20 | Teacher training completed (2 sessions, 3h total) | Daniele + Referent teacher | Signed attendance sheet; training materials delivered | PENDING |
| P-21 | Pedagogical efficacy report approved | MSTR-22 (Pedagogy) | `pedagogical-efficacy-report.md`: APPROVED WITH FINDINGS | PASS |
| P-22 | F-02 finding fixed (retention check cancellation on regression) | MSTR-08 (Backend) | Code merged, CI passing, git diff | PENDING |
| P-23 | F-05 finding fixed (quiz quality framework: teacher review flag) | MSTR-08 (Backend) + MSTR-10 (AI/ML) | Code merged, CI passing | PENDING |
| P-24 | Safeguarding system operational (9 rules + 25 patterns + wellbeing keywords) | MSTR-10 + MSTR-19 | Safeguarding test suite passing | PASS |
| P-25 | Bias audit mitigations applied (BSA-01 lacuna colour, BSA-02 gamification regex, BSA-04 ableist patterns, BSA-05 alert routing, BSA-06 PII check, BSA-12 quiz retry, BSA-17 quiz feedback) | MSTR-09/10/13/19 | Code merged, bias test suite passing | PENDING |

### 2.4 Safeguarding and Wellbeing

| # | Prerequisite | Owner | Evidence | Status |
|---|---|---|---|---|
| P-26 | Wellbeing referent (referente scolastico) identified and briefed | Dirigente Scolastico | Name, contact, and written acknowledgement of role | PENDING |
| P-27 | Teacher briefed on wellbeing detection limitations (Italian-only, BSA-03) | Daniele | Training session log; teacher acknowledges limitation | PENDING |
| P-28 | Wellbeing escalation path tested (system alert -> teacher notification -> referent) | MSTR-12 + Referent teacher | End-to-end test with synthetic alert | PENDING |
| P-29 | Safeguarding fallback message reviewed and approved by teacher | Referent teacher | Written approval of fallback text | PENDING |

### 2.5 Audit Trail

| # | Prerequisite | Owner | Evidence | Status |
|---|---|---|---|---|
| P-30 | GAP-1 fixed (heatmap access audit logging) | MSTR-08 | Code merged, CI passing | PENDING |
| P-31 | GAP-2 fixed (safeguarding block event persistence) | MSTR-08 | Code merged, CI passing | PENDING |
| P-32 | Audit trail end-to-end validation passed | MSTR-16 | `audit-trail-validation-report.md`: PASS | PASS |

---

## 3. Timeline (8-Week Pilot)

### Week 0: Pre-Pilot (T-14 to T-0)

| Day | Activity | Owner |
|---|---|---|
| T-14 | Infrastructure deployed on Hetzner; health check passed | MSTR-12 |
| T-14 | Keycloak realm configured; teacher and admin accounts created | MSTR-12 |
| T-13 | DR backup + restore test completed | MSTR-12 |
| T-12 | Monitoring dashboards operational; alert rules verified | MSTR-12 |
| T-10 | EU residency self-assessment signed | MSTR-12 + MSTR-16 |
| T-10 | Teacher Training Session 1 (1.5h): system overview, dashboard navigation, heatmap interpretation, override mechanics (20-char motivation) | Daniele |
| T-8 | Teacher Training Session 2 (1.5h): safeguarding alerts, wellbeing protocol, lesson upload, concept mapping review, FAQ | Daniele |
| T-7 | Family information meeting at school | Daniele + Referent teacher |
| T-7 | Consent forms and privacy notices distributed to families | Referent teacher |
| T-5 | Teacher uploads first curriculum unit for pilot | Referent teacher |
| T-3 | Concept mapping reviewed and confirmed by teacher via dashboard | Referent teacher |
| T-2 | Student accounts created in Keycloak (post-consent collection) | Admin IT |
| T-1 | Consent records entered into system via API | Admin IT |
| T-1 | Rollback plan tested; documented | MSTR-12 |
| T-0 | **GO/NO-GO DECISION** -- all prerequisites verified | All signatories |

### Weeks 1-2: Gradual Onboarding

| Day | Activity | Owner |
|---|---|---|
| W1 Day 1 | Classroom introduction (teacher-led, 30 min): what MAESTRO does, how it works, what it does NOT do (not a substitute for studying, not grading) | Referent teacher |
| W1 Day 1 | App installation on student devices (mobile) + first login verification | Admin IT + Referent teacher |
| W1 Day 1 | Cohort 1 (5 students) begins: onboarding quiz (content-adaptation profile, F3), explore mastery map | Students |
| W1 Day 2 | Cohort 2 (5 students) onboarded | Students |
| W1 Day 3 | Cohort 3 (5 students) onboarded | Students |
| W1 Day 4 | Cohort 4 (5 students) onboarded | Students |
| W1 Day 5 | Cohort 5 (remaining students) onboarded; all students active | Students |
| W1-W2 | Close monitoring: Daniele checks Grafana daily, teacher checks dashboard daily, any issues logged immediately | Daniele + Referent teacher |
| W1-W2 | Pre-test administered for Phase A unit (T5.5 protocol) | Referent teacher |
| W2 | First verification uploaded by teacher; MAESTRO generates per-student review documents | Referent teacher |
| W2 | Teacher reviews first batch of generated content for quality; provides feedback | Referent teacher |
| W2 End | **Checkpoint 1**: engagement metrics reviewed (sessions, active users). If < 50% engagement, investigate and resolve blockers | Daniele + Referent teacher |

### Weeks 3-6: Full Operation

| Activity | Frequency | Owner |
|---|---|---|
| Students use MAESTRO for recovery missions, quizzes, retention checks | Daily (self-paced) | Students |
| Teacher monitors dashboard heatmap, reviews alerts, performs overrides as needed | Daily | Referent teacher |
| Teacher uploads new verifications as curriculum progresses | Per curriculum unit | Referent teacher |
| Daniele monitors technical metrics (uptime, latency, LLM costs, error rates) | Daily | Daniele |
| Weekly teacher check-in (15 min call or in-person) | Weekly | Daniele + Referent teacher |
| Student questionnaire administered (mid-pilot, Week 4) | Once | Referent teacher |
| Content quality spot-check (5 random generated documents reviewed) | Weekly | Referent teacher |
| LLM cost review against budget | Weekly | Daniele |
| Post-test immediate administered for Phase A unit | Per T5.5 protocol | Referent teacher |
| Pre-test and treatment begin for Phase B unit (crossover) | Per T5.5 protocol | Referent teacher |
| **Checkpoint 2 (Week 4)**: mid-pilot review -- engagement, quality, teacher satisfaction, any incidents | Daniele + Referent teacher |

### Weeks 7-8: Wrap-Up and Measurement

| Day | Activity | Owner |
|---|---|---|
| W7 | Post-test immediate administered for Phase B unit | Referent teacher |
| W7 | Student questionnaire administered (end-of-pilot, Week 8) | Referent teacher |
| W7 | Data collection freeze: no new verifications uploaded after this point | Referent teacher |
| W7 | Teacher interview (semi-structured, 30 min, T5.5 Appendix C) | Daniele |
| W8 | Post-test delayed (D+21) administered for Phase A unit | Referent teacher |
| W8 | Efficacy data export and pseudonymisation for analysis | MSTR-16 + Daniele |
| W8 | System usage statistics compiled | MSTR-12 |
| W8 | Pilot wrap-up meeting with school (Dirigente, teacher, DPO) | Daniele |
| W8+1 | Post-pilot retention checks continue firing if students are still using the system | System (automatic) |
| W8+2 | **Post-pilot decision meeting** (Section 10) | All stakeholders |

---

## 4. Stakeholder Responsibilities

### 4.1 School-Side Stakeholders

| Stakeholder | Responsibilities |
|---|---|
| **Dirigente Scolastico** | Overall school approval for MAESTRO adoption; DPO liaison; authorise consent collection; sign off on pilot start; point of contact for institutional communication |
| **Referent Teacher** | Daily operations: dashboard monitoring, heatmap review, content quality spot-checks, override authority (with 20-char motivation per CLAUDE.md), wellbeing escalation first responder, administer pre/post tests, distribute/collect consent forms, classroom introduction |
| **Admin IT** | Device management (ensure student devices can access the platform), network configuration (whitelist MAESTRO domain), Keycloak account creation, consent record entry via API, handle erasure requests |
| **DPO** | Review and approve DPIA, oversee consent process, serve as contact for families on privacy matters, liaison with Garante if required, review data breach procedures |
| **Wellbeing Referent (Referente scolastico)** | Receive high/critical wellbeing escalation alerts, interface with external services (ASL, servizi sociali) if needed, brief teacher on protocols |
| **Students** | Complete onboarding quiz, use MAESTRO for recovery missions, complete questionnaires, report any issues to teacher |
| **Parents/Guardians** | Provide or deny granular consent, attend information meeting, use communication channel for questions, exercise rights (access, rectification, erasure) |

### 4.2 MAESTRO-Side Stakeholders

| Stakeholder | Responsibilities |
|---|---|
| **Daniele (Product Owner / Human)** | System support, bug fixes, data review, teacher training delivery, weekly check-ins, LLM cost monitoring, escalation endpoint, final decision authority |
| **MSTR-12 (DevOps)** | Infrastructure monitoring, incident response, backup verification, DR drill execution |
| **MSTR-13 (Security)** | Security incident response, credential rotation if needed |
| **MSTR-16 (Privacy)** | GDPR compliance oversight, breach notification drafting, erasure procedure support |

---

## 5. Teacher Training Plan

### 5.1 Overview

| Item | Detail |
|---|---|
| Total duration | 2 sessions, 3 hours total |
| Format | In-person at school (or video call if distance) |
| Delivered by | Daniele |
| Materials provided | Cheat sheet (PDF), video walkthrough (screen recording), support contact card |

### 5.2 Session 1: System Overview (1.5 hours)

| Block | Duration | Content |
|---|---|---|
| 1. What MAESTRO does | 15 min | Value proposition, six-state mastery model, the "lacuna as open door" philosophy, what MAESTRO is NOT (not a grading tool, not a teacher replacement) |
| 2. Dashboard navigation | 20 min | Login, sidebar, class overview, student list, alerts page |
| 3. Heatmap interpretation | 20 min | Reading the class heatmap: colours, icons, labels, worst-state rollup, identifying patterns (single-student vs class-wide lacunae) |
| 4. Override mechanics | 15 min | When to override, how to write a 20-char motivation, previewing transitions (F4.4), understanding the audit trail |
| 5. Q&A + hands-on practice | 20 min | Teacher uses a staging instance with synthetic data |

### 5.3 Session 2: Safety and Operations (1.5 hours)

| Block | Duration | Content |
|---|---|---|
| 1. Safeguarding alerts | 20 min | How wellbeing detection works, what triggers alerts, urgency levels (low/medium/high/critical), where alerts appear in the dashboard, what to do when you receive one |
| 2. Wellbeing protocol | 15 min | Escalation path: system alert -> teacher reviews -> referent if high/critical. Limitation: detection is Italian-only (BSA-03). Teacher must be attentive to non-Italian expressions of distress |
| 3. Lesson upload + concept mapping | 20 min | Upload a lesson document, review system-generated concept mapping, confirm/reject mappings, understanding macro/micro nodes |
| 4. Content quality review | 15 min | Viewing generated review documents, understanding the 4-block structure, what to do if content quality is poor (regenerate, report) |
| 5. FAQ and support | 20 min | How to contact Daniele, what constitutes an emergency vs a bug report, data breach procedure overview |

### 5.4 Materials Provided

1. **Cheat sheet (1 page, PDF)**: quick-reference card with login URL, key dashboard actions, override steps, alert response checklist, support contact
2. **Video walkthrough (15 min)**: screen recording of a complete teacher workflow from lesson upload through heatmap review and override
3. **Support contact card**: Daniele's phone/email, expected response times (same business day for non-urgent, 1 hour for safeguarding/security during school hours)

---

## 6. Student Onboarding

### 6.1 Classroom Introduction (Day 1, 30 min, teacher-led)

1. **What MAESTRO is**: "A personal study companion that helps you review topics you find difficult, in the way that works best for you"
2. **What MAESTRO is NOT**: "Not a grading tool. Not replacing your teacher. Not comparing you to anyone"
3. **How it works**: show mastery map on projector (with synthetic data), explain states with encouraging language (lacuna = "something to review", not "failure")
4. **Privacy**: "Your data is yours. Your parents gave consent for specific things. You can always ask to have your data deleted"
5. **Rules**: "No one can see your map except you and your teacher. There are no leaderboards or competitions"

### 6.2 App Setup

| Step | Action | Support |
|---|---|---|
| 1 | Download MAESTRO app from App Store / Google Play (or TestFlight / APK for pilot) | Admin IT provides installation instructions |
| 2 | Login with Keycloak credentials (provided by Admin IT on paper, individually) | Teacher assists in classroom |
| 3 | Verify login successful; see empty mastery map | Teacher confirms on dashboard |
| 4 | Complete onboarding quiz (content-adaptation profile, 5-10 min, F3) | Self-paced in class |
| 5 | Explore mastery map (guided, teacher walks through on projector) | Teacher |
| 6 | First low-stakes quiz (familiarisation, no grade impact) | Self-paced |

### 6.3 Accessibility Accommodations (DSA/BES Students)

- Font size adjustable via profile screen (12-24pt range)
- All mastery states use colour + icon + text label (never colour alone, WCAG 1.4.1)
- No timed quizzes (WCAG 2.2.1)
- Teacher can adjust individual student settings via override if needed
- Content tone always encouraging per safeguarding rules
- Teacher briefed to provide additional support to DSA/BES students during onboarding

---

## 7. Data Collection Protocol

### 7.1 Quantitative Data (System-Generated)

| Metric | Source Table | Collection Method | Privacy |
|---|---|---|---|
| State transitions per student per concept | `kmm.state_transition_log` | Automatic (system) | Pseudonymised for analysis |
| Quiz scores and pass/fail rates | `kmm.state_transition_log` + `content.quiz_response` | Automatic | Pseudonymised for analysis |
| Retention check results (D+7 pass rate) | `kmm.retention_schedule` | Automatic | Pseudonymised for analysis |
| Engagement: sessions per week, time-on-task | Application logs | Automatic | Pseudonymised for analysis |
| Content adaptation profile distribution | `core.student_profile` | Automatic | Pseudonymised for analysis |
| LLM cost per student per day | `audit.llm_audit_log` | Automatic | Aggregated (no PII) |
| Safeguarding block rate and fallback rate | Application logs + `audit.audit_log` (post GAP-2 fix) | Automatic | Aggregated (no PII) |
| Wellbeing alert count and urgency distribution | `safeguarding.wellbeing_alerts` | Automatic | Access restricted to teacher + referent |
| Teacher override count and motivations | `kmm.state_transition_log` WHERE `trigger_type='override_docente'` | Automatic | Teacher-identifiable (by design) |

### 7.2 Qualitative Data

| Instrument | Timing | Participants | Method |
|---|---|---|---|
| Student questionnaire (5-item Likert, T5.5 Appendix B) | Week 4 (mid-pilot) + Week 8 (end-pilot) | All consenting students | Digital form, anonymous, in Italian |
| Teacher interview (semi-structured, T5.5 Appendix C) | Week 7 (end-pilot) | Referent teacher | 30-min interview, audio recorded with consent, transcribed and anonymised |
| Teacher weekly check-in notes | Weekly (W1-W8) | Referent teacher + Daniele | Brief notes on issues, observations, suggestions |

### 7.3 Pre/Post Tests (Efficacy Measurement)

Per T5.5 protocol (within-subject crossover design):

| Test | When | Authored By | Administered Via |
|---|---|---|---|
| Pre-test (Unit X and Unit Y) | Before instruction begins for each unit | Teacher (NOT AI-generated) | Paper or digital |
| Post-test immediate | 1 day after review/recovery phase | Teacher | Paper or digital |
| Post-test delayed | D+21 after recovery phase | Teacher | Paper or digital |

### 7.4 Privacy Controls for Data Collection

- All analysis uses pseudonymised student IDs (MAESTRO `student_pseudo_id`)
- The mapping from pseudo-ID to real identity is held ONLY by the school
- Raw data stays on the MAESTRO platform (Hetzner EU)
- Only aggregated statistics leave the platform for reporting
- Individual student data is NEVER shared outside the school without explicit consent
- Right to erasure applies to all collected data (stored procedure `core.execute_right_to_erasure`)

---

## 8. Success Metrics (Detailed)

### 8.1 Primary Metric: Knowledge Retention Improvement

| Measure | Formula | Target |
|---|---|---|
| Pre-post immediate delta (treatment vs control) | Cohen's d (paired) on `post_immediate - pre` | d >= 0.3 |
| Pre-post delayed delta (treatment vs control) | Cohen's d (paired) on `post_delayed - pre` | d >= 0.3 (stretch: d >= 0.5) |

Analysis method: Paired t-test or Wilcoxon signed-rank (if normality assumption fails). Effect size with 95% CI. Per T5.5 Section 7.

### 8.2 Secondary Metrics

| Metric | Target | Source |
|---|---|---|
| D+7 retention check pass rate | >= 70% | `kmm.retention_schedule` |
| Weekly active students (any session in the week) | >= 80% | Application logs |
| Recovery mission initiation rate (% lacunae where student starts within 48h) | >= 60% | `kmm.state_transition_log` |
| Time lacuna -> consolidato (median) | <= 21 days | `kmm.state_transition_log` |
| Quiz first-attempt pass rate | >= 50% | `kmm.state_transition_log` |
| Regression rate (regressions / total da_consolidare+consolidato) | < 20% | `kmm.state_transition_log` |

### 8.3 Teacher Metrics

| Metric | Target | Source |
|---|---|---|
| Teacher overall satisfaction | >= 4/5 | Post-pilot interview |
| Teacher recommends continued use | Yes | Post-pilot interview Q7 |
| Override frequency | Monitored (no target -- descriptive) | `kmm.state_transition_log` |

### 8.4 Technical Metrics

| Metric | Target | Source |
|---|---|---|
| Uptime during school hours (08:00-16:00 CET, Mon-Sat) | >= 99% | Grafana `up{job="maestro-backend"}` |
| API P95 latency (non-LLM endpoints) | <= 500ms | Grafana Mimir |
| LLM content generation P95 latency | <= 30s | `audit.llm_audit_log` |
| LLM monthly cost | <= EUR 400 | Grafana LLM cost dashboard |
| Safeguarding block rate | < 5% (if > 5%, investigate) | Application logs |
| Zero critical/high security incidents | 0 | Incident log |

### 8.5 Safeguarding Metrics

| Metric | Target | Source |
|---|---|---|
| Unblocked harmful content delivered to minors | 0 (mandatory) | Audit trail + teacher feedback |
| Wellbeing alerts generated and teacher-acknowledged | 100% acknowledged within SLA | `safeguarding.wellbeing_alerts` |
| Safeguarding fallback rate | < 1% | Application logs |

---

## 9. Risk Management and Rollback

### 9.1 Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Residual Risk |
|---|---|---|---|---|---|
| PR-01 | Safeguarding failure (inappropriate content delivered to minor) | Low | Critical | 3-layer defence (prompt, regex, gate); fallback on triple failure; teacher content review | Very Low |
| PR-02 | Data breach (PII exposure) | Very Low | Critical | Encryption at rest, TLS, pseudonymisation, RBAC, EU residency | Very Low |
| PR-03 | Low student engagement (< 50% active) | Medium | High | Gradual onboarding, teacher encouragement, mid-pilot check, investigation and UX iteration | Medium |
| PR-04 | Teacher abandonment (stops using dashboard) | Low | High | Weekly check-ins, responsive bug fixes, training materials | Low |
| PR-05 | LLM cost overrun | Medium | Medium | Budget alerts at 80%/100%, cache optimisation, tiered routing | Low |
| PR-06 | Infrastructure outage during school hours | Low | Medium | DR plan (RTO <= 4h), monitoring alerts (2-min detection), LLM fallback | Low |
| PR-07 | Consent withdrawal mid-pilot (multiple families) | Low | Medium | Graceful degradation per consent; student simply stops using MAESTRO; data erased | Low |
| PR-08 | Wellbeing false negative (non-Italian distress undetected) | Medium | High | Teacher briefed on limitation (BSA-03); organisational mitigation; V1 multilingual keywords | Medium |
| PR-09 | Bias in generated content | Medium | Medium | 25+ safeguarding patterns, bias audit mitigations applied, quarterly manual audit protocol | Low |
| PR-10 | School network blocks MAESTRO domain | Low | Medium | Pre-pilot network test; Admin IT whitelists domain | Very Low |

### 9.2 Rollback Triggers

The pilot MUST be terminated early if any of the following conditions are met:

| Trigger | Detection | Decision Maker |
|---|---|---|
| Any safeguarding incident where inappropriate content is delivered to a student and teacher reports harm | Teacher report + audit trail review | Daniele (immediate) |
| >= 3 unresolved safeguarding system failures (triple fallback with no content served) in a single week | Application logs | Daniele + Referent teacher |
| Data breach involving student PII | Security monitoring or external report | Daniele + MSTR-13 (immediate) |
| Student engagement < 50% of enrolled students after Week 3 (despite intervention) | System data | Daniele + Referent teacher |
| Teacher formally requests termination | Written request | Daniele (mandatory compliance) |
| Dirigente Scolastico or DPO orders termination | Written order | Daniele (mandatory compliance) |
| Garante Privacy intervention or order | Official communication | Daniele (mandatory compliance) |
| Critical security vulnerability discovered with no immediate fix | Security assessment | Daniele + MSTR-13 |

### 9.3 Rollback Procedure

If a rollback trigger fires:

1. **Immediate (within 1 hour)**:
   - Disable student access: set `MAESTRO_MAINTENANCE_MODE=true`, restart backend
   - Notify teacher: "Il sistema MAESTRO e' temporaneamente sospeso per [motivo]. Gli studenti possono continuare le lezioni normalmente senza il sistema."
   - Notify Dirigente Scolastico

2. **Within 24 hours**:
   - Export all student data for the school (pseudonymised analysis dataset + raw data for the school's own records)
   - Generate deletion certificates for any erasure requests
   - Draft communication for families if the incident involves data or safeguarding

3. **Within 72 hours**:
   - If data breach: notify Garante per DR plan Section 5.3 (72-hour window)
   - Notify families of termination and the reason (age-appropriate language)
   - Retain infrastructure for data export/erasure processing; do not destroy data immediately

4. **Within 30 days**:
   - Complete all data erasure requests
   - Generate final pilot report documenting what happened and lessons learned
   - Archive all audit trail data (immutable, retained per DPIA retention schedule)
   - Decommission infrastructure

### 9.4 Communication Plan for Premature Termination

| Audience | Channel | Template |
|---|---|---|
| Teacher | Phone call (immediate) + email | "Sospensione temporanea/definitiva di MAESTRO: [motivo]. Le lezioni proseguono normalmente." |
| Dirigente Scolastico | Email (formal) | "Comunicazione di [sospensione/termine] del progetto pilota MAESTRO: [motivo], [azioni intraprese], [prossimi passi]." |
| Families | Letter via school (formal) | "Informativa sulla conclusione anticipata del progetto MAESTRO: [motivo], [stato dei dati del figlio/a], [come esercitare i diritti]." |
| DPO | Email | DPIA status update with incident details |

---

## 10. Post-Pilot

### 10.1 Efficacy Analysis

Per T5.5 protocol (within-subject crossover):

1. **Primary analysis**: Paired t-test (or Wilcoxon) on pre-post delta, treatment vs control. Effect size d with 95% CI.
2. **Secondary analyses**: Retention rates, state progression, engagement metrics (descriptive).
3. **Sequence effect check**: Compare treatment delta for Group Alpha (control-first) vs Group Beta (treatment-first).
4. **Subgroup exploration**: Content-adaptation profile influence on outcomes (exploratory, underpowered).

Timeline: Internal report within 2 weeks of pilot completion (T5.5 Section 10.1).

### 10.2 Decision Framework

| Outcome | Decision |
|---|---|
| SC-01 met (d >= 0.3) + SC-02-07 all met + teacher recommends | **Scale**: plan V1 multi-school deployment (3 schools, 6 classes) |
| SC-01 met (d >= 0.3) + some SC-02-07 missed + teacher conditional | **Iterate**: fix identified issues, re-pilot with same school next semester |
| SC-01 not met (d < 0.3) + SC-06 met (0 safeguarding incidents) | **Iterate with model review**: CPA + LSS review pedagogical model, adjust content generation, re-pilot |
| Any safeguarding incident (SC-06 failed) | **Halt**: root cause analysis before any re-deployment |
| Teacher does not recommend continued use | **Review**: understand why, address concerns, decide whether to iterate or pivot |

### 10.3 V1 Feature Prioritisation (Informed by Pilot)

The pilot will generate data to prioritise V1 features:

| Signal from Pilot | Feature Decision |
|---|---|
| High override frequency by teacher | Improve diagnostic accuracy (F4) or content quality (F5) |
| Low engagement after Week 3 | Implement gamification (F7) with anti-pattern safeguards |
| Bilingual students underperform | Prioritise Bilingual Composer (F13) improvements |
| High regression rate | Review retention scheduling parameters (FSRS for V2) |
| Teacher requests multimodal content | Prioritise podcast/visual/game agents (F10) |
| Wellbeing alerts from non-Italian students | Implement multilingual wellbeing keywords (BSA-03) |
| Quiz quality concerns from teacher | Implement teacher question bank (F-04) and review queue (F-05) |

### 10.4 Research Ethics Report

If pilot data is used for any publication or external presentation:

1. Full anonymisation (no pseudo-IDs, only aggregate statistics)
2. School name anonymised unless school gives explicit written permission
3. Ethics board review if required by publication venue
4. Families informed per consent (e) if their anonymised data contributes to research output
5. Report filed in `.maestro/tests/pilot-efficacy-report.md`

---

## 11. Escalation Paths

Mirroring CLAUDE.md governance, adapted for pilot operations:

### 11.1 Technical Escalation

```
Student/Teacher reports issue
    |
    v
Daniele (first responder, same business day)
    |
    +-- Bug fix: patch and deploy
    +-- Infrastructure issue: escalate to MSTR-12 (DevOps)
    +-- Security issue: escalate to MSTR-13 (Security)
    |
    v (if unresolved in 24h during school week)
External support (Hetzner, Anthropic, OpenAI)
```

### 11.2 Safeguarding Escalation

```
Student input detected by wellbeing keywords
    |
    v
System creates wellbeing alert (safeguarding.wellbeing_alerts)
    |
    +-- Low urgency: logged, no notification
    +-- Medium urgency: teacher notified via dashboard
    +-- High urgency: teacher + wellbeing referent notified
    +-- Critical urgency: teacher + wellbeing referent notified (URGENT flag)
    |
    v (if wellbeing referent determines external services needed)
External services (ASL, servizi sociali, forze dell'ordine)
```

### 11.3 Privacy Escalation

```
Any privacy concern (from teacher, student, family, or DPO)
    |
    v
DPO (first point of contact for privacy matters)
    |
    +-- Consent question: resolved by DPO
    +-- Erasure request: Admin IT executes stored procedure + DPO confirms
    +-- Data breach: DPO + Daniele -> Garante notification within 72h (if required)
    +-- Garante inquiry: DPO leads response with DPIA documentation
```

### 11.4 Pedagogical Escalation

```
Teacher concern about content quality, accuracy, or tone
    |
    v
Daniele (collect specifics: which content, what issue)
    |
    +-- Content inaccuracy: review generated document, fix prompt or source material
    +-- Tone concern: review safeguarding patterns, add regex if needed
    +-- Model concern (e.g., state machine behaviour unexpected): escalate to CPA (MSTR-03)
    |
    v (if CPA determines model adjustment needed)
CPA + LSS review -> ADR if model change required (per CLAUDE.md governance)
```

---

## 12. Appendices

### Appendix A: Infrastructure Checklist (Day of Deployment)

```
[ ] Hetzner app server provisioned (CCX33, fsn1, DE)
[ ] Hetzner monitoring server provisioned (CX22, fsn1, DE)
[ ] PostgreSQL volume attached and formatted (50 GB)
[ ] Docker images pulled from GHCR
[ ] docker-compose up -d -- all services healthy
[ ] Keycloak realm configured: maestro realm, student/teacher/admin roles
[ ] Caddy reverse proxy with TLS (Let's Encrypt) operational
[ ] Grafana dashboards provisioned from git
[ ] Alert rules loaded: ServiceDown, HighP95Latency, DatabaseConnectionPoolExhaustion, LLMHighLatency, LLMMonthlyBudgetWarning, LLMMonthlyBudgetCritical
[ ] Backup script configured: daily 02:00 UTC to Scaleway fr-par
[ ] WAL archiving enabled and tested
[ ] Scaleway S3 buckets created: maestro-backups-production, maestro-materials-production
[ ] DNS A record pointing to Hetzner server IP
[ ] Health endpoint returns 200: curl -sf https://<domain>/api/v1/health
[ ] Redis cache operational
[ ] Keycloak login flow tested (student, teacher, admin roles)
[ ] EU residency self-assessment completed and signed
```

### Appendix B: Consent Collection Summary Template

```
MAESTRO PILOT -- RIEPILOGO CONSENSI RACCOLTI
Classe: ______________  Data: ______________

Totale studenti iscritti: ____
Totale moduli restituiti: ____
Totale moduli NON restituiti (studente non usa MAESTRO): ____

| Consenso | SI | NO |
|----------|----|----|
| (a) Profilazione adattamento | __ | __ |
| (b) Lingua nativa (Art. 9) | __ | __ |
| (c) Comunicazioni famiglia | __ | __ |
| (d) Storico cross-anno | __ | __ |
| (e) Ricerca aggregata | __ | __ |

Studenti < 14 anni: ____ (firma solo genitore)
Studenti 14-17 anni: ____ (doppia firma)
Studenti 18+ anni: ____ (firma autonoma)

Firma Admin IT: ____________________  Data: ____________
```

### Appendix C: Weekly Check-In Template

```
MAESTRO PILOT -- CHECK-IN SETTIMANALE
Settimana: __ / 8
Data: ______________

1. Studenti attivi questa settimana: __ / __ totali
2. Nuove verifiche caricate: __
3. Override effettuati: __
4. Alert di benessere ricevuti: __
5. Problemi tecnici segnalati: __
6. Feedback del docente (testo libero):
   _____________________________________________
7. Azioni per la prossima settimana:
   _____________________________________________

Firma docente: ____________________
Firma Daniele: ____________________
```

### Appendix D: Incident Response Quick Reference

| Incident Type | First Action | Notify | SLA |
|---|---|---|---|
| System down | Check Grafana; restart docker compose | Teacher (if school hours) | RTO <= 4h |
| Slow performance | Check Redis, check LLM latency | None (unless sustained > 1h) | Investigate same day |
| Safeguarding alert | Review in dashboard | Teacher auto-notified | Acknowledge within 1 school day |
| Content quality issue | Review generated document | Daniele | Fix within 2 school days |
| Security concern | Isolate system, rotate credentials | Daniele + MSTR-13 | Contain within 30 min |
| Data breach | Follow DR plan S10 | Daniele + DPO + Garante (72h) | Immediate containment |
| Consent withdrawal | Admin IT updates system | DPO | Process within 7 business days |
| Erasure request | Admin IT runs stored procedure | DPO | Complete within 30 days (target 24h) |

---

## 13. Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-05-20 | MSTR-01 (Programme Director) | Initial draft |

**Required approvals for pilot start**:

| Approver | Role | Signature | Date |
|---|---|---|---|
| MSTR-01 | Programme Director | | |
| MSTR-02 | Chief Technical Architect | | |
| MSTR-03 | Chief Pedagogical Architect | | |
| MSTR-16 | Privacy & Compliance Engineer | | |
| MSTR-20 | QA Sentinel | | |
| Daniele | Human / Product Owner | | |
| Dirigente Scolastico | School Principal | | |
| DPO | Data Protection Officer | | |

---

*This document synthesises all MAESTRO project deliverables (Phases 1-6) into a comprehensive launch-ready plan. It must be read in conjunction with the referenced documents for full technical, privacy, and pedagogical detail.*
