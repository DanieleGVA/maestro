# MAESTRO — Project Memory

> Questo file cattura lo stato operativo del progetto e fornisce a ogni nuova sessione di Claude il contesto necessario per riprendere il lavoro. Aggiornare a ogni milestone significativa.

**Ultimo aggiornamento**: 2026-05-20
**Fase corrente**: TUTTE LE FASI COMPLETATE (1-6) — Progetto pronto per pilota
**Task DAG**: `.maestro/tasks/task_dag.yaml`

---

## Fasi completate

### Phase 1 — Foundation (COMPLETATA)

| Task | Deliverable | Agente |
|---|---|---|
| T1.1 Requirements v0.3 | `docs/MAESTRO_requisiti_v0.3.md` | MSTR-01 |
| T1.2 Tech stack ADRs | `.maestro/decisions/ADR-001-tech-stack.md` | MSTR-02 |
| T1.3 Pedagogical model | `.maestro/decisions/ADR-002-pedagogical-model.md` | MSTR-03 |

### Phase 2 — Architecture (COMPLETATA)

| Task | Deliverable | Agente |
|---|---|---|
| T2.1 Multi-agent HLD | `docs/architecture/HLD-001-multi-agent-system.md` + `ADR-003-orchestrator-pattern.md` | MSTR-04 |
| T2.2 KG & curriculum | `docs/architecture/HLD-002-knowledge-graph.md` | MSTR-05 |
| T2.3 Content generation | `docs/architecture/HLD-003-content-generation.md` | MSTR-06 |
| T2.4 Data & mastery state | `docs/architecture/HLD-004-data-mastery-state.md` + `ADR-004-data-model.md` | MSTR-07 |
| T2.5 Interface contracts | `docs/architecture/interface-contracts.md` + `docs/architecture/production-HLD.md` + `ADR-005-interface-resolution.md` | MSTR-02 |

### Phase 3 — Compliance & Safety MVP (COMPLETATA)

Scope ridotto per decisione Daniele: DPIA, consenso e bilinguismo rimandati a V1.

| Task | Deliverable | Agente |
|---|---|---|
| T3.1 DPIA + consenso | RIMANDATO A V1 | MSTR-16 |
| T3.2 Safeguarding | `.maestro/safeguarding/safeguarding-mvp-spec.md` (64KB) | MSTR-19 |
| T3.3 Accessibilita' | `.maestro/accessibility/accessibility-mvp-spec.md` (48KB) | MSTR-17 |
| T3.4 Bilinguismo | RIMANDATO A V1 | MSTR-18 |
| T3.5 Security | `.maestro/security/security-mvp-spec.md` (74KB) | MSTR-13 |

### Phase 4 — Implementation MVP (COMPLETATA)

140 file, ~17.800 LOC totali. Backend Python + Mobile React Native + Dashboard Next.js.

| Task | Deliverable | Agente | Stats |
|---|---|---|---|
| T4.1 Backend orchestrator | `src/backend/src/maestro/{orchestrator,agents,api,auth,common,db/models}` | MSTR-08 | LangGraph StateGraph, FastAPI, Keycloak JWT, RBAC, 6 API routers |
| T4.2 KG ingestion | `src/backend/src/maestro/kg/` | MSTR-11 | Apache AGE dual-write, pgvector embeddings, concept mapper, curriculum |
| T4.3 Content generation | `src/backend/src/maestro/{content,llm,safeguarding}/` | MSTR-10 | LLM Gateway + pseudonimizzazione, Text Agent, Quiz Engine, safeguarding checker |
| T4.4 KMM state store | `src/backend/src/maestro/kmm/` | MSTR-08 | 6-state machine, transitions, heatmap worst-state rollup, retention D+7 |
| T4.5 F14 admin path | RIMANDATO A V1 | -- | Dipende da T3.1 |
| T4.6 Student mobile app | `src/mobile/` (25 file TS/TSX) | MSTR-09 | Expo Router, mappa padronanza, quiz, missioni, accessibilita' |
| T4.7 Teacher dashboard | `src/dashboard/` (33 file TS/TSX) | MSTR-09 | Next.js App Router, heatmap classe, override docente, upload lezione, alert wellbeing |
| T4.8 Bilingual MVP | RIMANDATO A V1 | -- | Dipende da T3.4 |

Backend: 68 file Python, ~9.300 LOC, 11 unit test files.
Mobile: 25 file TS/TSX, ~3.800 LOC.
Dashboard: 33 file TS/TSX, ~2.200 LOC.

---

## Decisioni architetturali chiave (sintesi ADR)

### ADR-001 — Tech Stack
- **Database**: PostgreSQL 17 unica istanza — pgvector (embeddings) + Apache AGE (grafo) + relazionale (KMM, F14). ACID su tutti i domini.
- **LLM**: Claude API (primario) + GPT-4o-mini (batch/bassa complessita). Tutti i call passano per LLMGateway con pseudonimizzazione.
- **Backend**: LangGraph (Python) + FastAPI. Durable checkpointing per audit trail.
- **Frontend**: React Native + Expo (app studente) + Next.js (dashboard docente).
- **TTS**: OpenAI TTS per V1 (podcast non in scope MVP).
- **Infrastruttura**: Hetzner Cloud (DE/FI) + Scaleway Object Storage (FR). EU-native, no CLOUD Act. Costo MVP stimato EUR 300-520/mese.
- **Auth**: Keycloak self-hosted (SAML 2.0 + OIDC + TOTP/WebAuthn).
- **Osservabilita**: OpenTelemetry + Grafana stack (Loki + Tempo + Mimir).

### ADR-002 — Modello Pedagogico
- **F3**: "Profilo di adattamento contenuti" (MAI "learning styles"). Vettore continuo 5 dimensioni. Default uniforme se consenso negato.
- **F11**: Macchina a 6 stati validata (Bloom mastery learning, Guskey). Soglia quiz >=80%.
- **Retention**: MVP = D+7 fisso. V1 = D+3/D+7/D+21. V2 = FSRS adattivo. Colonne FSRS presenti dal giorno 1.
- **Rollup (OQ8 RISOLTO)**: worst-state validato + indicatore progresso in UI ("7/10 consolidati").
- **Quiz (OQ7 RISOLTO)**: domande docente prioritarie, AI-generate come backbone. Framework qualita a 5 livelli. Bloom's progressivo per stato.

### ADR-003 — Pattern Orchestratore
- Orchestratore centrale LangGraph StateGraph (non event bus). I gate consenso/safeguarding sono strutturali nel grafo.
- 15 agenti specificati (11 MVP + 4 stub). Agenti stateless, stato in PostgreSQL + Redis.

### ADR-004 — Modello Dati
- 4 schemi PostgreSQL: `core` (identita), `kmm` (padronanza), `content` (materiale generato), `audit` (log immutabili).
- State machine a livello applicativo (non trigger DB).
- Audit log append-only con trigger immutabilita.
- Right-to-erasure: stored procedure atomica con pseudonimizzazione.
- PII crittografati con pgcrypto.

### ADR-005 — Risoluzione Conflitti Inter-HLD
- 7 conflitti tra HLD risolti. Il piu critico: ordinamento canonico degli stati per rollup macro: `lacuna < in_recupero < non_introdotto < introdotto < da_consolidare < consolidato`.

---

## Open Question — Stato

| # | Domanda | Stato | Dove |
|---|---|---|---|
| OQ1 | LLM principale | Deciso: Claude + GPT-4o-mini | ADR-001 |
| OQ2 | Modello rilascio (SaaS/on-prem) | Aperta — post-pilota | — |
| OQ3 | Pricing | Fuori scope — escalare a Daniele | — |
| OQ4 | Governance dati apprendimento | Aperta — da DPIA T3.1 | — |
| OQ5 | Certificazione MIUR | Da T3.1 | — |
| OQ6 | Studio efficacia randomizzato | Da T5.5 | — |
| OQ7 | Banca domande quiz | RISOLTO: teacher-first + AI con 5-layer QC | ADR-002 |
| OQ8 | Rollup macro/micro | RISOLTO: worst-state + display enhancement | ADR-002 |
| OQ9 | Decay temporale | Fuori scope v0.3, data model ready | — |
| OQ10 | Doppia padronanza bilingui | Fuori scope v0.3 | — |
| OQ11 | DPO liaison | Aperta — escalare a Daniele | — |
| OQ12 | Scuola pilota (5AI Pantanelli-Monnet) | Aperta — escalare a Daniele | — |
| OQ13 | Linear vs Jira | Aperta | — |
| OQ14 | Confluence vs Notion | Aperta | — |
| OQ15 | Effort Router thresholds | Validare dopo Phase 4 | — |

---

## Scope MVP vs V1 (decisione Daniele)

DPIA, consenso e bilinguismo rimandati interamente a V1. Il pilota MVP opera senza profilazione personalizzata, senza bilinguismo e con consenso gestito fuori sistema (cartaceo). Spec: `docs/architecture/phase3-compliance-mvp.md`

| Area | MVP | V1 |
|---|---|---|
| DPIA | -- | Documento slim + DPIA formale Garante |
| Consenso | -- | API + template PDF + gate + self-service |
| Erasure | -- | Stored procedure + certificato PDF |
| Bilinguismo | -- | Glossario 200 termini (uk+ar) + Composer + 6 lingue |
| Safeguarding | System prompt rules + regex check + keyword alert | ML classifier, escalation automatica |
| Accessibilita' | Checklist WCAG + token colore + semantic HTML | Design system completo, test BES/DSA |
| Auth | Keycloak basic + 3 ruoli + JWT + MFA admin | SSO registro elettronico, SPID |
| Security | pgcrypto PII + TLS + pseudonimizzazione + audit | Pen-test, Vault, WAF |

**Task rimandati a V1**: T3.1 (DPIA+consenso), T3.4 (bilinguismo), T4.5 (F14 admin path), T4.8 (bilingual MVP)

### Phase 5 — Testing & Verification (COMPLETATA)

6 task completati in parallelo. Remediation applicata per tutti i finding critici e high.

| Task | Deliverable | Agente | Risultato |
|---|---|---|---|
| T5.1 | `src/backend/tests/unit/` (22 file), `tests/integration/` (7 file), `conftest.py` | MSTR-14 | >=80% unit, >=60% integration. Tutti i moduli coperti. |
| T5.2 | `tests/e2e/` (17 file: 6 teacher Playwright + 7 student specs + 4 infra) | MSTR-14 | 105 test cases. Teacher: Playwright. Student: executable specs. |
| T5.3 | `.maestro/tests/accessibility-audit-report.md` + 5 fix nel codice | MSTR-17 | 1 critical + 3 high CORRETTI. Conditional WCAG 2.1 AA pass. |
| T5.4 | `.maestro/tests/security-pentest-report.md` + 5 fix nel codice | MSTR-13 | 2 critical + 3 high CORRETTI (auth su KG/content/KMM routers, IDOR, headers, CORS, input validation). Gate MET. |
| T5.5 | `.maestro/tests/pedagogical-efficacy-report.md` + `pedagogical-test-specs.md` | MSTR-22 | APPROVATO con 2 medium (orphaned retention, quiz validation incompleta), 5 low. Protocollo pilota disegnato. |
| T5.6 | `.maestro/tests/bias-safety-audit-report.md` | MSTR-19 | Rischio MEDIO. 3 HIGH (colore rosso, gamification patterns mancanti, wellbeing solo italiano), 6 MEDIUM, 8 LOW. |

**Remediation applicata post-audit:**
- BSA-01: Colore lacuna da rosso (#C62828) a ambra (#FF8F00) in `src/mobile/theme/tokens.ts` e `src/dashboard/theme/tokens.ts`
- BSA-02: 4 pattern gamification anti-pattern aggiunti a `src/backend/src/maestro/safeguarding/checker.py` (ranking, streak, countdown, variable reward)
- F-02: Cancellazione retention schedule pendenti su regressione a lacuna in `src/backend/src/maestro/kmm/state_machine.py`

### Phase 6 — Deployment (COMPLETATA)

5 task completati in 3 wave.

| Task | Deliverable | Agente | Risultato |
|---|---|---|---|
| T6.1 | `.github/workflows/` (3), `infra/docker/` (5), `infra/monitoring/` (8), `infra/terraform/` (4), `infra/scripts/` (3) | MSTR-12 | 24 file. CI/CD GitHub Actions, Docker, 5 Grafana dashboard, 12 alert rules, Terraform Hetzner+Scaleway. |
| T6.2 | `.maestro/deployment/dr-plan.md`, `eu-residency-architecture.md`, `cost-model.md`, `infra/runbooks/` (4) | MSTR-12 | RPO<=24h, RTO<=4h. 10 scenari failure. EU residency provata a ogni livello. Costo EUR 173-465/mese. |
| T6.3 | `.maestro/dpia/` (4 documenti) | MSTR-16 | DPIA slim (14 rischi, residuale BASSO), 5 template consenso cartaceo, checklist Garante 57 item (70% OK), retention schedule. |
| T6.4 | `.maestro/deployment/audit-trail-validation-report.md`, `audit-reconstruction-queries.sql` | MSTR-16 | PASS. 10/13 eventi loggati. Immutabilita' verificata. 2 gap medi (accesso heatmap, blocchi safeguarding). |
| T6.5 | `.maestro/deployment/pilot-deployment-plan.md`, `launch-readiness-scorecard.md` | MSTR-01 | Piano pilota 8 settimane (32 prerequisiti, timeline settimanale, 11 ruoli, training, rollback). Scorecard: 23 PASS, 4 CONDITIONAL, 13 PENDING, 1 BLOCKED. |

### Stato finale del progetto

Tutte le 6 fasi completate. 32 task nel DAG: 24 completati, 4 deferred a V1 (T3.1, T3.4, T4.5, T4.8), 4 non applicabili.

**Per lanciare il pilota**: risolvere i 13 item PENDING + 1 BLOCKED nel launch readiness scorecard (`.maestro/deployment/launch-readiness-scorecard.md`). Principalmente: DPA sub-processori, deploy infrastruttura, consensi, training docente.

---

## Mappa dei file del progetto

```
maestro/
  CLAUDE.md                     — Governance, regole non negoziabili, team roster
  MEMORY.md                     — QUESTO FILE — stato progetto, decisioni, contesto sessione

  docs/
    MAESTRO_documento_progetto_v0.2.md  — Requisiti originali (F1-F14, N1-N7)
    MAESTRO_requisiti_v0.3.md           — Requisiti consolidati (F1-F17, N1-N9, 120 req, 58 UC, 42 schermate)
    MAESTRO_agent_team_v1.md            — Architettura team agentico (23 agenti, 32 task DAG)
    MAESTRO_use_cases_v1.md             — Catalogo UC completo (58 UC, formato Cockburn)
    MAESTRO_schermate_v1.md             — Specifiche schermate (42 schermate)
    use_cases/                          — UC suddivisi per attore (studente, docente, altri, sistema)
    architecture/
      production-HLD.md                 — *** PARTIRE DA QUI *** — HLD di produzione unificato
      HLD-001-multi-agent-system.md     — 15 agenti, orchestrazione, flussi, safeguarding
      HLD-002-knowledge-graph.md        — Schema KG, ingestion pipeline, concept mapping, DDL
      HLD-003-content-generation.md     — Text agent, prompt templates, bilingue, quiz, caching
      HLD-004-data-mastery-state.md     — KMM state store, modello dati F14, DDL completo
      interface-contracts.md            — 14 contratti tipizzati, REST API, event schemas

  .maestro/
    decisions/
      ADR-001-tech-stack.md             — Stack tecnologico
      ADR-002-pedagogical-model.md      — Modello pedagogico
      ADR-003-orchestrator-pattern.md   — Pattern orchestratore
      ADR-004-data-model.md             — Architettura dati
      ADR-005-interface-resolution.md   — Risoluzione conflitti inter-HLD
    tasks/
      task_dag.yaml                     — DAG 32 task, 6 fasi (T1.1-T4.7 completati, T3.1+T3.4+T4.5+T4.8 deferred V1)
    schemas/
      handoff.json                      — Schema JSON per handoff inter-agente
    safeguarding/
      safeguarding-mvp-spec.md          — Spec safeguarding MVP (T3.2)
    accessibility/
      accessibility-mvp-spec.md         — Spec accessibilita' MVP (T3.3)
    security/
      security-mvp-spec.md              — Spec sicurezza MVP (T3.5)
    dpia/                               — (vuoto — V1, T3.1 deferred)
    handoffs/                           — (vuoto — da popolare durante esecuzione)
    qa_findings/                        — (vuoto — da popolare durante review QA)
    pedagogical/                        — (vuoto — da popolare durante review pedagogico)
    tests/                              — (vuoto — da popolare in Phase 5)

  .claude/
    agents/                             — 23 prompt file per agenti MSTR-01..23
    settings.json                       — Configurazione Claude Code

  src/
    backend/                            — Python backend (FastAPI + LangGraph), 68 file, ~9.3K LOC
      pyproject.toml                    — Dipendenze Python
      src/maestro/
        main.py                         — FastAPI app entry point
        config.py                       — pydantic-settings config
        orchestrator/                   — LangGraph StateGraph + checkpointer (T4.1)
        agents/                         — Agent nodes: diagnostic, content_selector, profiler (T4.1)
        api/v1/                         — 6 FastAPI routers (T4.1)
        auth/                           — Keycloak JWT + RBAC middleware (T4.1)
        db/models/                      — SQLAlchemy ORM (core, audit) (T4.1)
        kg/                             — KG ingestion, embeddings, concept mapper, AGE ops (T4.2)
        content/                        — Text Agent, Quiz Engine, cache (T4.3)
        llm/                            — LLM Gateway + pseudonymizer (T4.3)
        safeguarding/                   — Checker, retry, alerts (T4.3)
        kmm/                            — State machine, heatmap, retention (T4.4)
        common/                         — Audit, exceptions, schemas (T4.1)
      tests/unit/                       — 11 test files
    mobile/                             — React Native + Expo student app, 25 file, ~3.8K LOC (T4.6)
      app/                              — Expo Router pages (login, home, map, quiz, missions, profile)
      components/                       — MasteryMap, NodeCard, QuizView, StateIndicator
      hooks/                            — useAuth, useApi, useStudentState
      theme/                            — Tokens colore, typography, spacing
    dashboard/                          — Next.js teacher dashboard, 33 file, ~2.2K LOC (T4.7)
      app/                              — App Router pages (home, classes, heatmap, students, lessons, alerts)
      components/                       — ClassHeatmap, OverrideModal, StudentMap, Sidebar
      hooks/                            — useAuth, useApi
      theme/                            — Tokens colore
  tests/                                — (vuoto — test E2E da Phase 5)
  infra/                                — (vuoto — IaC da Phase 6)
```

---

## Come riprendere il lavoro

1. Claude legge automaticamente `CLAUDE.md` (governance) e `MEMORY.md` (questo file) all'avvio
2. Per contesto architetturale: leggere `docs/architecture/production-HLD.md` (panoramica), poi gli HLD specifici se serve dettaglio
3. Per lo stato dei task: leggere `.maestro/tasks/task_dag.yaml`
4. Per le decisioni prese: leggere gli ADR in `.maestro/decisions/`
5. Per i requisiti: leggere `docs/MAESTRO_requisiti_v0.3.md`
6. Per lanciare Phase 5: creare un team con MSTR-14 (test), MSTR-17 (accessibility), MSTR-13 (security), MSTR-22 (pedagogical), MSTR-19 (bias). T5.1+T5.5+T5.6 partono in parallelo, T5.2+T5.3 dopo T4.6/T4.7, T5.4 dopo T4.7
