# MAESTRO — Project Memory

> Questo file cattura lo stato operativo del progetto e fornisce a ogni nuova sessione di Claude il contesto necessario per riprendere il lavoro. Aggiornare a ogni milestone significativa.

**Ultimo aggiornamento**: 2026-05-20
**Fase corrente**: Phase 3 COMPLETATA — Phase 4 (Implementation) pronta a partire
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

### Prossima fase: Phase 4 — Implementation (MVP ridotto)

I task di Phase 4 MVP sono (vedi task_dag.yaml):
- T4.1: Backend orchestration + agent framework (MSTR-08) — dipende da T2.5, T3.5
- T4.2: KG ingestion pipeline + concept mapping (MSTR-11) — dipende da T2.2, T2.4
- T4.3: Content generation services (MSTR-10) — dipende da T2.3, T3.2
- T4.4: Knowledge Map Manager + state store (MSTR-08) — dipende da T2.4, T3.5
- T4.6: Student mobile app MVP (MSTR-09) — dipende da T2.5, T3.3, T4.1
- T4.7: Teacher dashboard (MSTR-09) — dipende da T2.5, T3.3, T4.1, T4.4

Rimandati a V1: T4.5 (F14 admin path), T4.8 (bilingual MVP)

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
      task_dag.yaml                     — DAG 32 task, 6 fasi (T1.1-T3.5 completati, T3.1+T3.4 deferred V1)
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

  src/                                  — (vuoto — codice da Phase 4)
  tests/                                — (vuoto — test da Phase 5)
  infra/                                — (vuoto — IaC da Phase 6)
```

---

## Come riprendere il lavoro

1. Claude legge automaticamente `CLAUDE.md` (governance) e `MEMORY.md` (questo file) all'avvio
2. Per contesto architetturale: leggere `docs/architecture/production-HLD.md` (panoramica), poi gli HLD specifici se serve dettaglio
3. Per lo stato dei task: leggere `.maestro/tasks/task_dag.yaml`
4. Per le decisioni prese: leggere gli ADR in `.maestro/decisions/`
5. Per i requisiti: leggere `docs/MAESTRO_requisiti_v0.3.md`
6. Per lanciare Phase 4: creare un team con MSTR-08 (backend), MSTR-11 (data engineer), MSTR-10 (AI/ML), MSTR-09 (frontend). T4.1+T4.2 partono in parallelo, T4.3 dipende da T3.2, T4.4 da T3.5, T4.6 da T4.1, T4.7 da T4.1+T4.4
