# Data Retention Schedule -- MAESTRO

**Documento**: Registro dei periodi di conservazione per categoria di dato
**Versione**: 1.0
**Data**: 2026-05-20
**Autore**: MSTR-16 (Privacy & Compliance Engineer)
**Riferimenti**: GDPR Art. 5(1)(e), F14.9, HLD-004, ADR-004, CLAUDE.md
**Base normativa**: GDPR (storage limitation), D.Lgs. 196/2003, DPR 445/2000 (conservazione documentale pubblica)

---

## 1. Principi generali

1. **Storage limitation** (Art. 5(1)(e) GDPR): i dati personali sono conservati solo per il tempo necessario al raggiungimento delle finalita' per le quali sono trattati.
2. **No soft-delete**: la cancellazione e' definitiva. Non esistono flag "deleted" che preservano i dati (CLAUDE.md governance rule).
3. **Granularita' per categoria**: ogni categoria di dato ha il proprio periodo di conservazione e la propria procedura di eliminazione/anonimizzazione.
4. **Partitioning per gestione**: le tabelle time-series (audit, transizioni) sono partizionate per mese tramite pg_partman, facilitando il drop di partizioni scadute.

---

## 2. Schedule di conservazione

### 2.1 Dati identificativi (PII)

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Base giuridica conservazione |
|---|---|---|---|---|---|
| Nome, cognome, email studente (cifrati) | `core.student` | Durata iscrizione + 90 giorni grace period | Fine iscrizione O richiesta erasure | Cancellazione tramite `core.execute_right_to_erasure` | Art. 6(1)(e) compito pubblico |
| Anno di nascita studente | `core.student` | Durata iscrizione + 90 giorni grace period | Come sopra | Cancellazione (impostato a NULL) | Art. 6(1)(e) |
| School registry ref studente | `core.student` | Durata iscrizione + 90 giorni grace period | Come sopra | Cancellazione (impostato a NULL) | Art. 6(1)(e) |
| Keycloak user ID studente | `core.student` | Durata iscrizione | Fine iscrizione | Cancellazione + disattivazione utente Keycloak | Art. 6(1)(e) |
| Nome, cognome, email docente (cifrati) | `core.teacher` | Durata rapporto di lavoro con la scuola | Fine rapporto di lavoro | Cancellazione previa verifica con la scuola | Art. 6(1)(b) contratto |
| Hash IP address | `audit.audit_log` | 10 anni (parte dell'audit log) | Scadenza audit log | Cancellazione della partizione | Art. 6(1)(c) obbligo legale |
| Hash user agent | `audit.audit_log` | 10 anni | Come sopra | Come sopra | Art. 6(1)(c) |

### 2.2 Dati di profilazione (Consenso a)

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Dipendenza dal consenso |
|---|---|---|---|---|---|
| Profilo adattamento (5 dimensioni) | `core.student.adaptation_profile` | Durata iscrizione (o fino a revoca consenso a) | Revoca consenso (a) O fine iscrizione | Reset a valori default `{20,20,20,20,20}` alla revoca; cancellazione alla fine iscrizione | Consenso (a) |
| Source del profilo | `core.student.adaptation_profile_source` | Come sopra | Come sopra | Reset a "default" | Consenso (a) |
| Preferenza tono | `core.student.tone_preference` | Durata iscrizione | Fine iscrizione | Reset a "neutro" alla revoca; cancellazione a fine iscrizione | Consenso (a) per valori non-default |
| Preferenza lunghezza contenuto | `core.student.content_length_preference` | Durata iscrizione | Fine iscrizione | Come sopra | Consenso (a) per valori non-default |

### 2.3 Lingua nativa (Consenso b -- Art. 9)

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Dipendenza dal consenso |
|---|---|---|---|---|---|
| Codice lingua nativa (ISO 639-1) | `core.student.native_language` | Fino a revoca consenso (b) | Revoca consenso (b) | **Cancellazione immediata** (SET NULL) -- non aspetta fine anno | Consenso (b) -- obbligatorio |
| Flag bilinguismo attivo | `core.student.bilingualism_active` | Come sopra | Come sopra | Reset a FALSE | Consenso (b) |

**Nota critica**: la cancellazione della lingua nativa e' l'unico caso in cui la cancellazione avviene immediatamente alla revoca, senza grace period, data la natura sensibile del dato (Art. 9).

### 2.4 Dati di apprendimento (KMM)

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Dipendenza dal consenso |
|---|---|---|---|---|---|
| Stato padronanza per nodo | `kmm.student_node_state` | Durata iscrizione (o cross-anno se consenso d) | Fine iscrizione (se no consenso d) O richiesta erasure | Cancellazione completa | Consenso (d) per cross-anno |
| Cronologia transizioni di stato | `kmm.state_transition_log` | Durata iscrizione (o cross-anno se consenso d) | Come sopra | Cancellazione O anonimizzazione (se consenso e) | Consenso (d) per cross-anno, consenso (e) per anonimizzazione |
| Retention schedule | `kmm.retention_schedule` | Fino a completamento o cancellazione studente | Completamento check O fine iscrizione | Cancellazione | Nessuno (funzionale) |
| Teacher override | `kmm.teacher_override` | Durata iscrizione studente | Fine iscrizione O richiesta erasure | Cancellazione | Nessuno (documentale) |
| Punteggi quiz | In `kmm.state_transition_log.quiz_score` | Come transizioni | Come transizioni | Come transizioni | Come transizioni |

### 2.5 Contenuti generati

| Dato | Tabella DB / Storage | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Dipendenza dal consenso |
|---|---|---|---|---|---|
| Metadata contenuti generati | `content.generated_content` | Durata iscrizione | Fine iscrizione O richiesta erasure | Cancellazione record DB | Nessuno (funzionale) |
| File generati (PDF, audio) | Scaleway S3 | Durata iscrizione | Fine iscrizione O richiesta erasure | Cancellazione oggetti S3 (async post-DB, con retry) | Nessuno (funzionale) |
| Question bank (quiz generati) | `content.question_bank` | Durata corso (non legata al singolo studente) | Fine corso | Archiviazione o cancellazione a discrezione docente | Nessuno (risorsa corso) |
| Lesson materials (caricati dal docente) | `content.lesson_material` + S3 | Durata corso | Fine corso | Archiviazione a discrezione docente | Nessuno (proprieta' docente) |
| Lesson chunks (embedding) | `content.lesson_chunk` | Durata corso | Fine corso | Cancellazione con il corso | Nessuno (derivato) |
| Prompt templates | `content.prompt_template` (V1) / file (MVP) | Indefinito (risorsa di sistema) | Aggiornamento template | Sovrascrittura (versioning) | Nessuno |

### 2.6 Audit trail

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Note |
|---|---|---|---|---|---|
| Audit log operazioni | `audit.audit_log` | **10 anni** | Scadenza temporale | Drop della partizione mensile | Obbligo conservazione documentale enti pubblici (DPR 445/2000). In caso di erasure studente: pseudonimizzazione (student UUID -> hash), non cancellazione. |
| LLM audit log | `audit.llm_audit_log` | **10 anni** | Scadenza temporale | Drop della partizione mensile | Contiene solo metadata (modello, token, latenza, costo), nessun PII. Il prompt pseudonimizzato e' loggato. |
| Certificati di cancellazione | `audit.deletion_certificate` | **10 anni** dalla cancellazione | Scadenza temporale | Drop | Contiene solo hash studente, non dati identificabili. Necessario per dimostrare compliance. |
| Wellbeing alerts | `safeguarding.wellbeing_alerts` | 5 anni | Scadenza temporale | Anonimizzazione (student_id -> hash) | Dato sensibile (disagio). Conservazione per monitoraggio pattern temporali e accountability. |
| Safeguarding verdicts | `safeguarding.safeguarding_verdicts` | 3 anni | Scadenza temporale | Cancellazione | Dato tecnico (violazioni trovate). Utile per analisi qualita' prompt. |

### 2.7 Consensi

| Dato | Tabella DB | Periodo conservazione | Evento scatenante fine conservazione | Azione alla scadenza | Note |
|---|---|---|---|---|---|
| Record consenso attuale | `core.consent` | Durata iscrizione O fino a erasure | Erasure studente | Cancellazione | -- |
| Storico consensi (append-only) | `core.consent_history` | **10 anni** | Scadenza temporale | Anonimizzazione (student_id -> hash) | Necessario per accountability: dimostrare che il consenso era valido al momento del trattamento. |
| Moduli cartacei (MVP) | Archivio fisico scuola | **10 anni** dalla fine iscrizione | Scadenza temporale | Distruzione sicura (shredding) | Responsabilita' della scuola. |

### 2.8 Dati di sistema e infrastruttura

| Dato | Storage | Periodo conservazione | Azione alla scadenza | Note |
|---|---|---|---|---|
| Log applicativi (Python/FastAPI) | Grafana Loki | 90 giorni | Retention automatica Loki | Nessun PII nei log applicativi (solo pseudo-ID e metadata). |
| Metriche (Prometheus/Grafana) | Grafana | 1 anno | Retention automatica | Dati aggregati, nessun PII. |
| Tracce distribuite (OpenTelemetry) | Grafana Tempo | 30 giorni | Retention automatica Tempo | Nessun PII nelle tracce. |
| Redis cache | Redis | TTL per chiave (max 24h) | Eviction automatica | Nessun PII in cache (solo stato sessione). |
| Backup database | Hetzner volume / S3 | 30 giorni (rolling) | Sovrascrittura rolling | Backup cifrato. In caso di erasure: il backup scadra' naturalmente entro 30 giorni. |

---

## 3. Procedure di eliminazione

### 3.1 Right to erasure (su richiesta famiglia)

**Trigger**: richiesta della famiglia (o studente >= 18) tramite admin IT.
**SLA**: massimo 30 giorni (GDPR Art. 17(1)). Target interno: 24 ore.

**Procedura**:
1. Admin IT riceve richiesta (verbale, email, o lettera)
2. Admin IT verifica identita' del richiedente
3. Admin IT esegue nel sistema: `POST /api/v1/students/{id}/erasure`
4. Il sistema esegue `core.execute_right_to_erasure` (transazione atomica)
5. Il sistema genera il certificato di cancellazione
6. Cleanup asincrono: cancellazione oggetti S3, disattivazione utente Keycloak
7. Admin IT consegna certificato di cancellazione alla famiglia
8. Admin IT annota la richiesta e l'esecuzione nel registro cartaceo

**Dati cancellati**: PII, profilo, KMM state, contenuti generati, notifiche, retention schedule, override, consensi, iscrizioni.
**Dati pseudonimizzati**: audit log (student UUID -> hash SHA-256).
**Dati preservati**: certificato di cancellazione, audit log pseudonimizzato, dati anonimi aggregati (se consenso e era attivo).

### 3.2 Fine anno scolastico (senza consenso d)

**Trigger**: fine anno scolastico per studenti senza consenso (d) alla conservazione cross-anno.
**Timing**: entro 60 giorni dalla fine dell'anno scolastico (settembre).

**Procedura**:
1. Job schedulato identifica studenti con iscrizione `status = 'completed'` e consenso (d) = false
2. Per ciascuno: esecuzione di una cancellazione parziale (KMM state, contenuti, profilo)
3. PII mantenuta per eventuale re-iscrizione l'anno successivo (fino a grace period 90 giorni)
4. Se lo studente non si re-iscrive entro il grace period: erasure completa

### 3.3 Scadenza partizioni audit (automatica)

**Trigger**: partizioni mensili piu' vecchie di 10 anni.
**Procedura**: pg_partman configurato con `retention = '10 years'`. Le partizioni scadute vengono droppate automaticamente dal job pg_cron settimanale.

### 3.4 Revoca singolo consenso

| Consenso revocato | Azione immediata | Azione differita |
|---|---|---|
| (a) Profilazione | Reset profilo a default `{20,20,20,20,20}` | Contenuti futuri generati con profilo neutro |
| (b) Lingua nativa | SET `native_language = NULL`, `bilingualism_active = FALSE` | Nessuna -- cancellazione immediata |
| (c) Comunicazioni famiglia | Stop invio email/report | Nessuna azione aggiuntiva |
| (d) Storico cross-anno | Nessuna azione immediata | A fine anno: cancellazione dati (come 3.2) |
| (e) Ricerca aggregata | Flag rimosso | Dati gia' anonimizzati restano; dati non ancora anonimizzati esclusi dal processo |

---

## 4. Gestione backup e erasure

### 4.1 Problema: erasure vs backup retention

I backup rolling (30 giorni) possono contenere dati di studenti che hanno esercitato il right to erasure dopo la creazione del backup.

**Soluzione MVP**: dato che i backup hanno retention massima di 30 giorni e la richiesta di erasure ha SLA massimo 30 giorni, nel caso peggiore un backup contenente i dati dello studente scadra' entro 60 giorni dalla richiesta. Questo e' accettabile per il pilot MVP.

**Soluzione V1**: backup incrementali con flag "do not restore" per student_id cancellati. In caso di restore da backup, la procedura di restore include un passo di re-esecuzione delle cancellazioni avvenute dopo la data del backup.

### 4.2 Verifica periodica

Job settimanale (pg_cron):
- Verifica che nessun record in `core.student` con `status = 'deleted'` abbia ancora dati PII non cancellati
- Verifica che nessun `student_node_state` esista per studenti con `status = 'deleted'`
- Alert se anomalie trovate

---

## 5. Matrice riepilogativa

| Categoria | Conservazione attiva | Grace period | Post-cancellazione | Totale massimo |
|---|---|---|---|---|
| PII studente | Durata iscrizione | 90 giorni | -- | Iscrizione + 90gg |
| Lingua nativa (Art. 9) | Fino a revoca | **0** (immediato) | -- | Fino a revoca |
| Profilo adattamento | Durata iscrizione | 0 (reset immediato alla revoca) | -- | Iscrizione |
| KMM state | Iscrizione (o cross-anno) | 0 | -- | Iscrizione (o diploma) |
| Contenuti generati | Iscrizione | 0 | -- | Iscrizione |
| Audit log | 10 anni | -- | Pseudonimizzato | 10 anni |
| Consent history | 10 anni | -- | Anonimizzato | 10 anni |
| Wellbeing alerts | 5 anni | -- | Anonimizzato | 5 anni |
| Safeguarding verdicts | 3 anni | -- | Cancellato | 3 anni |
| Log applicativi | 90 giorni | -- | -- | 90 giorni |
| Metriche | 1 anno | -- | -- | 1 anno |
| Backup | 30 giorni rolling | -- | -- | 30 giorni |
| Moduli cartacei | 10 anni dalla fine iscrizione | -- | Distruzione sicura | 10+ anni |

---

## 6. Implementazione tecnica

### 6.1 pg_partman per audit tables

```sql
-- Configurazione pg_partman per retention automatica
SELECT partman.create_parent(
    p_parent_table := 'audit.audit_log',
    p_control := 'created_at',
    p_type := 'range',
    p_interval := '1 month',
    p_premake := 3
);

UPDATE partman.part_config
SET retention = '10 years',
    retention_keep_table = false,
    retention_keep_index = false
WHERE parent_table = 'audit.audit_log';
```

### 6.2 pg_cron per manutenzione

```sql
-- Job settimanale: manutenzione partizioni (crea nuove, droppa scadute)
SELECT cron.schedule(
    'partman_maintenance',
    '0 3 * * 0',  -- Domenica alle 03:00
    $$SELECT partman.run_maintenance()$$
);

-- Job mensile: verifica integrita' cancellazioni
SELECT cron.schedule(
    'verify_erasure_integrity',
    '0 4 1 * *',  -- Primo del mese alle 04:00
    $$
    DO $body$
    DECLARE
        v_orphan_count INT;
    BEGIN
        SELECT COUNT(*) INTO v_orphan_count
        FROM kmm.student_node_state sns
        JOIN core.student s ON sns.student_id = s.id
        WHERE s.status = 'deleted';

        IF v_orphan_count > 0 THEN
            RAISE WARNING 'INTEGRITY: % orphan KMM records for deleted students', v_orphan_count;
            -- In produzione: invia alert a Grafana
        END IF;
    END $body$;
    $$
);
```

### 6.3 Application-level scheduling per fine anno

```python
# Pseudocode per il job di fine anno scolastico
async def end_of_year_cleanup(academic_year: str):
    """
    Eseguito a settembre per l'anno appena concluso.
    Cancella i dati di studenti senza consenso (d).
    """
    students_no_cross_year = await db.fetch_all(
        """
        SELECT s.id
        FROM core.student s
        JOIN core.enrolment e ON s.id = e.student_id
        WHERE e.academic_year = :year
          AND e.status = 'completed'
          AND NOT EXISTS (
              SELECT 1 FROM core.consent c
              WHERE c.student_id = s.id
                AND c.consent_type = 'cross_year_history'
                AND c.granted = true
                AND c.revoked_at IS NULL
          )
        """,
        {"year": academic_year}
    )

    for student in students_no_cross_year:
        await partial_cleanup(student.id)  # KMM, contenuti, profilo
        # PII mantenuta per grace period 90 giorni
```

---

*Documento prodotto per il task T6.3 del DAG MAESTRO. Soggetto a review da MSTR-07 (Data Architect), MSTR-13 (Security), MSTR-02 (CTA).*
