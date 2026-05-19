# MAESTRO — Project Memory

> Questo file cattura lo stato operativo del progetto e fornisce a ogni nuova sessione di Claude il contesto necessario per riprendere il lavoro. Aggiornare a ogni milestone significativa.

**Ultimo aggiornamento**: 2026-05-18
**Fase corrente**: Phase 2 COMPLETATA — Phase 3 (Compliance & Safety) pronta a partire
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

## Prossima fase: Phase 3 — Compliance & Safety

Tutti i blocchi di Phase 2 sono risolti. I task di Phase 3 sono:

| Task | Soggetto | Owner | Bloccato da | Pronto? |
|---|---|---|---|---|
| T3.1 | DPIA + consent design (5 consensi granulari) | MSTR-16 | T2.4 | SI |
| T3.2 | Safeguarding policies + content moderation | MSTR-19 | T2.3 | SI |
| T3.3 | Accessibility design system (WCAG 2.1 AA) | MSTR-17 | T2.5 | SI |
| T3.4 | Bilingual ops MVP (ucraino + arabo) | MSTR-18 | T2.3, T2.5 | SI |
| T3.5 | Security architecture (authn/authz, encryption, audit, pseudonymisation) | MSTR-13 | T2.5, T3.1 | Parziale (aspetta T3.1) |

**Strategia di esecuzione**: T3.1, T3.2, T3.3, T3.4 in parallelo. T3.5 parte dopo T3.1.

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
      task_dag.yaml                     — DAG 32 task, 6 fasi (T1.1-T2.5 completati)
    schemas/
      handoff.json                      — Schema JSON per handoff inter-agente
    dpia/                               — (vuoto — da popolare in T3.1)
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
6. Per lanciare Phase 3: creare un team con gli agenti MSTR-16, MSTR-19, MSTR-17, MSTR-18, MSTR-13
