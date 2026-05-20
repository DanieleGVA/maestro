# DPIA Slim -- MAESTRO MVP Pilot

**Documento**: Valutazione d'Impatto sulla Protezione dei Dati (DPIA) -- Art. 35 GDPR
**Status**: Draft
**Versione**: 1.0
**Data**: 2026-05-20
**Autore**: MSTR-16 (Privacy & Compliance Engineer)
**Revisori richiesti**: MSTR-02 (CTA), MSTR-13 (Security), MSTR-01 (Director)
**Scope**: MVP Pilot -- 1 scuola, 1 classe (~25 studenti), 1 docente
**Riferimenti normativi**: GDPR (Reg. UE 2016/679), D.Lgs. 196/2003 (Codice Privacy), D.Lgs. 101/2018, Provvedimento Garante n. 529/2025, DM 166/2025 (Linee guida MIM su IA nelle scuole)

---

## 1. Descrizione del Trattamento

### 1.1 Scopo e ambito

MAESTRO e' un sistema di accompagnamento personalizzato per studenti di Informatica nelle scuole superiori italiane. Il sistema analizza i risultati delle verifiche, identifica le lacune nella conoscenza di ogni studente, genera contenuti di recupero personalizzati (testo, quiz) e traccia il progresso della padronanza nel tempo attraverso una mappa della conoscenza a sei stati.

**Finalita' del trattamento:**
- Identificazione personalizzata delle lacune concettuali per ogni studente
- Generazione di contenuti didattici di recupero adattati al profilo dello studente
- Tracciamento del progresso di padronanza (sei stati: non_introdotto, introdotto, lacuna, in_recupero, da_consolidare, consolidato)
- Programmazione di verifiche di consolidamento (retention check)
- Supporto al docente tramite dashboard con heatmap di classe e alert

**Ambito MVP Pilot:**
- 1 istituto scolastico (ITT/ITET)
- 1 classe (~25 studenti, eta' 13-19)
- 1 docente di Informatica
- 1 corso (1 anno scolastico)
- Durata prevista del pilot: 1 quadrimestre

### 1.2 Soggetti interessati

| Categoria | Numerosita' (MVP) | Caratteristiche rilevanti |
|---|---|---|
| Studenti | ~25 | **Tutti minori** (13-19 anni). Alcuni con madrelingua non italiana (ucraino, arabo). |
| Docente | 1 | Docente di Informatica del corso. |
| Personale IT scolastico | 1-2 | Admin IT della scuola (gestione account). |
| Famiglie | ~25 nuclei | Genitori/tutori legali dei minori. Non utenti diretti del sistema nel MVP. |

### 1.3 Categorie di dati trattati

| Categoria | Dati specifici | Base giuridica | Dati speciali (Art. 9) |
|---|---|---|---|
| **Anagrafica studente** | Nome, cognome, email (cifrati con pgcrypto AES-256), anno di nascita (non data completa), anno scolastico, codice registro | Art. 6(1)(e) compito di interesse pubblico + Art. 8 consenso genitoriale | No |
| **Profilo di adattamento** | Vettore a 5 dimensioni (preferenze contenuto: visivo, audio, pratico, lettura, dialogico), tono, lunghezza | Art. 6(1)(a) consenso -- Consenso (a) | No |
| **Lingua nativa** | Codice ISO 639-1 (es. "uk", "ar") | Art. 9(2)(a) consenso esplicito -- **Consenso (b)** | **Si' -- proxy origine etnica** |
| **Dati di apprendimento** | Stato padronanza per concetto (6 stati), punteggi quiz, cronologia transizioni, tentativi, tempo di risposta | Art. 6(1)(e) compito di interesse pubblico | No |
| **Contenuti generati** | Documenti di ripasso personalizzati, quiz, percorsi di recupero | Art. 6(1)(e) compito di interesse pubblico | No |
| **Dati di navigazione** | Hash SHA-256 dell'indirizzo IP, hash SHA-256 dell'user agent | Art. 6(1)(f) legittimo interesse (sicurezza) | No |
| **Anagrafica docente** | Nome, cognome, email (cifrati), ruolo | Art. 6(1)(b) esecuzione contratto di lavoro | No |
| **Audit trail** | Attore, azione, entita', timestamp, valore precedente/nuovo | Art. 6(1)(c) obbligo legale + Art. 6(1)(e) | No |
| **Consensi** | 5 record per studente, ciascuno con stato, data, chi ha concesso, base giuridica | Art. 6(1)(c) obbligo legale (dimostrabilita' del consenso) | No |

### 1.4 Flussi di dati

```
                              +-----------+
                              |  Docente  |
                              +-----+-----+
                                    |
                             Upload lezioni, verifiche, voti
                                    |
                              +-----v---------+
                              |  Next.js      |
                              |  Dashboard    |
                              +-----+---------+
                                    |
                               TLS 1.3
                                    |
                    +---------------v----------------+
                    |       FastAPI + LangGraph       |
                    |       (Hetzner DE)              |
                    +--+---+---+---+---+---+---+--+--+
                       |   |   |   |   |   |   |  |
          +----------+ |   |   |   |   |   |   |  +------+
          |            |   |   |   |   |   |   |         |
    +-----v-----+  +--v---v---v---v---v---v---v--+  +----v----+
    | Keycloak  |  |    PostgreSQL 17            |  |Scaleway |
    | (Auth)    |  |    (Hetzner DE)             |  |   S3    |
    | Hetzner DE|  |  core | kmm | content | kg  |  |(FR/NL) |
    +-----------+  |  audit | safeguarding       |  +---------+
                   +-----+--+--------------------+
                         |  |
                +--------+  +--------+
                |                     |
          +-----v------+       +-----v------+
          | Redis       |      | Grafana    |
          | (cache)     |      | (monit.)   |
          | Hetzner DE  |      | Hetzner DE |
          +-----------+        +------------+

    Boundary LLM (pseudonimizzazione)
    ===================================
          |                    |
    +-----v------+       +----v-------+
    | Claude API |       | OpenAI API |
    | (Anthropic)|       | (embedding |
    |            |       |  + GPT-4o  |
    +------------+       |  mini)     |
                         +------------+
    * Nessun PII attraversa questo boundary *
    * Mapping pseudonimo <-> identita' in memoria, mai persistito *

                              +-----------+
                              | Studente  |
                              +-----+-----+
                                    |
                             React Native + Expo
                                    |
                               TLS 1.3
                                    |
                              +-----v---------+
                              |  FastAPI      |
                              |  (stessi      |
                              |   endpoint)   |
                              +---------------+
```

**Trasferimenti verso terze parti:**

| Destinatario | Dato trasferito | Garanzia | Residenza |
|---|---|---|---|
| Anthropic (Claude API) | Contenuto didattico **pseudonimizzato** -- nessun PII | DPA + SCC | USA (dati pseudonimizzati, non PII) |
| OpenAI (embedding + GPT-4o-mini) | Testo lezione **pseudonimizzato** per embedding e generazione | DPA + SCC | USA (dati pseudonimizzati, non PII) |
| Hetzner Cloud | Tutti i dati (server infrastruttura) | DPA, server in DE | Germania (UE) |
| Scaleway | File (lezioni, audio, PDF generati) | DPA, server in FR/NL | Francia/Paesi Bassi (UE) |

**Nota critica**: nessun dato identificabile dello studente (nome, cognome, email, anno di nascita, codice registro, lingua nativa) viene mai inviato alle API LLM. La pseudonimizzazione e' enforced architetturalmente: il `LLMGateway` intercetta ogni chiamata, applica la sostituzione `nome -> STUDENTE_{hash}`, verifica l'assenza di residui PII (fail-closed), e distrugge il mapping in memoria dopo la de-pseudonimizzazione della risposta.

### 1.5 Periodi di conservazione

Vedi documento dedicato: `.maestro/dpia/data-retention-schedule.md`

Sintesi:

| Categoria | Periodo di conservazione | Azione alla scadenza |
|---|---|---|
| Anagrafica studente (PII) | Durata iscrizione + 90 giorni grace period | Cancellazione o right-to-erasure |
| Profilo di adattamento | Durata iscrizione (o fino a revoca consenso a) | Cancellazione |
| Lingua nativa | Fino a revoca consenso (b) | Cancellazione immediata |
| Dati di apprendimento (KMM) | Durata iscrizione (o cross-anno se consenso d) | Cancellazione o anonimizzazione |
| Contenuti generati | Durata iscrizione | Cancellazione |
| Audit log | 10 anni (obbligo documentale scolastico) | Pseudonimizzazione post-cancellazione studente |
| Consensi | 10 anni (dimostrabilita' per accountability) | Conservazione in forma anonimizzata |
| Dati aggregati anonimi | Indefinito (se consenso e) | Nessuna azione (non identificabili) |

---

## 2. Base Giuridica

### 2.1 Art. 6 -- Liceita' del trattamento

| Trattamento | Base giuridica | Giustificazione |
|---|---|---|
| Raccolta e gestione anagrafica studente | Art. 6(1)(e) -- compito di interesse pubblico | L'istituzione scolastica svolge un compito di interesse pubblico nell'ambito dell'istruzione. Il DPR 249/1998 (Statuto degli studenti) e il D.Lgs. 297/1994 (TU Istruzione) attribuiscono alla scuola il compito di personalizzare l'insegnamento. |
| Profilazione per adattamento contenuti | Art. 6(1)(a) -- consenso | **Consenso (a)** separato, revocabile. Se negato: profilo neutro, contenuti uniformi. |
| Generazione contenuti personalizzati | Art. 6(1)(e) -- compito di interesse pubblico | Funzionale al recupero delle lacune, rientra nel compito didattico. |
| Tracciamento padronanza (KMM) | Art. 6(1)(e) -- compito di interesse pubblico | Documentazione del percorso formativo, prevista dalla normativa scolastica. |
| Comunicazioni alla famiglia | Art. 6(1)(a) -- consenso | **Consenso (c)** separato. Se negato: nessuna comunicazione periodica (resta obbligo informativo legale). |
| Conservazione cross-anno | Art. 6(1)(a) -- consenso | **Consenso (d)** separato. Se negato: dati cancellati a fine anno scolastico. |
| Ricerca aggregata anonima | Art. 6(1)(a) -- consenso | **Consenso (e)** separato. Solo dati anonimizzati. |
| Audit log | Art. 6(1)(c) -- obbligo legale | Obbligo di accountability (Art. 5(2) GDPR), conservazione documentale scolastica. |

### 2.2 Art. 8 -- Consenso dei minori

L'Italia ha fissato a **14 anni** la soglia per il consenso autonomo ai servizi della societa' dell'informazione (Art. 2-quinquies D.Lgs. 101/2018).

| Fascia d'eta' | Regime di consenso |
|---|---|
| < 14 anni | Consenso del titolare della responsabilita' genitoriale **obbligatorio** per tutti i 5 consensi. Lo studente non puo' prestare consenso autonomamente. |
| 14-17 anni | Consenso **assistito**: lo studente puo' esprimere la propria volonta', ma il genitore/tutore deve essere informato e co-firmare. Nella pratica MVP (cartaceo), sia studente che genitore firmano il modulo. |
| 18-19 anni | Consenso autonomo. Raro nella popolazione target (ultimo anno). |

**Implementazione MVP**: i moduli cartacei prevedono:
- Riga firma genitore/tutore (obbligatoria per < 14)
- Riga firma studente (obbligatoria per >= 14)
- Per < 14: la firma del genitore e' sufficiente, lo studente non firma ma il modulo gli viene mostrato

### 2.3 Art. 9 -- Lingua nativa come dato sensibile

La lingua nativa e' trattata come **proxy dell'origine etnica** (Art. 9(1) GDPR). Questo trattamento richiede:

1. **Consenso esplicito** -- Consenso (b), separato dagli altri, con spiegazione chiara del perche' si tratta di dato sensibile
2. **Finalita' specifica**: la lingua nativa serve esclusivamente per:
   - Attivare il Bilingual Composer (documenti in due colonne: italiano + lingua nativa)
   - Glossario bilingue dei termini tecnici
3. **Garanzie aggiuntive**:
   - La lingua nativa e' memorizzata come codice ISO 639-1, mai in testo libero
   - **Mai inviata alle API LLM** (pseudonimizzata come `[RIMOSSO]`)
   - **Mai mostrata in nessuna dashboard di classe** (ne' al docente ne' ad altri studenti)
   - Il docente vede solo la flag "bilinguismo attivo: si/no", non la lingua specifica (per il MVP il docente e' a conoscenza, ma il sistema non espone il dato)
   - Accessibile solo all'applicazione per la composizione bilingue
   - Cancellazione immediata alla revoca del consenso (b)

### 2.4 Normativa italiana specifica

| Norma | Applicazione in MAESTRO |
|---|---|
| D.Lgs. 196/2003 (Codice Privacy) | Complementare al GDPR, specialmente per settore scolastico |
| D.Lgs. 101/2018 | Soglia 14 anni per consenso minori (Art. 2-quinquies) |
| Provvedimento Garante n. 529/2025 | Obblighi per le scuole nel trattamento dati: DPIA obbligatoria per profilazione alunni, regole chiare su chi usa cosa e con quale base giuridica |
| DM 166/2025 (MIM) | Linee guida per uso IA nelle scuole: divieto riconoscimento emozioni, minimizzazione dati, preferenza dati sintetici, trasparenza |
| "La scuola a prova di privacy" (2025) | Vademecum operativo del Garante aggiornato per IA: privacy impact assessment, criteri scelta fornitori/modelli |
| DPR 249/1998 | Statuto degli studenti: diritto alla personalizzazione dell'insegnamento |

---

## 3. Necessita' e Proporzionalita'

### 3.1 Data minimisation

| Dato | Necessita' | Alternativa valutata |
|---|---|---|
| Nome e cognome | Identificazione dello studente nel sistema e nelle comunicazioni docente | Uso di soli pseudonimi: scartato perche' il docente deve riconoscere gli studenti. I nomi sono cifrati at rest. |
| Anno di nascita | Determinazione soglia 14 anni per regime di consenso | Data di nascita completa: scartata. L'anno e' sufficiente. |
| Email | Comunicazioni tecniche (reset password, notifiche MVP) | Non raccolta se non necessaria (nullable nel DB). |
| Lingua nativa (ISO code) | Attivazione composizione bilingue | Solo codice ISO, non testo libero. Non raccolta se consenso (b) negato. |
| Profilo adattamento | Personalizzazione contenuti | Solo 5 dimensioni numeriche + 2 preferenze. Nessun dato biografico. Se consenso (a) negato: profilo neutro di default. |
| Punteggio quiz | Determinazione transizione di stato | Solo punteggio percentuale, non risposte individuali (le risposte sono nel quiz engine, non nel KMM). |
| Hash IP | Audit di sicurezza | Hash SHA-256, non IP grezzo. Impossibile risalire all'IP originale. |
| Contenuti generati | Erogazione del servizio | Collegati allo studente solo per la durata dell'iscrizione. |

### 3.2 Purpose limitation

Ogni dato raccolto e' utilizzato esclusivamente per le finalita' dichiarate. In particolare:

- I dati di apprendimento **non** sono utilizzati per valutazione scolastica formale (il voto resta competenza esclusiva del docente)
- I dati di profilazione **non** sono condivisi con terzi, altre scuole, o enti esterni
- I dati aggregati anonimi (consenso e) sono utilizzabili solo per ricerca educativa interna, **non** per profilazione commerciale
- Le API LLM **non** ricevono mai dati identificabili

### 3.3 Storage limitation

- Ogni categoria di dato ha un periodo di conservazione esplicito (sezione 1.5)
- La cancellazione e' atomica (stored procedure `core.execute_right_to_erasure`)
- Non esistono "soft delete" -- la cancellazione e' definitiva (CLAUDE.md governance rule)
- Partitioning mensile delle tabelle di audit facilita la gestione della retention

---

## 4. Valutazione dei Rischi

### 4.1 Matrice dei rischi

| ID | Rischio | Probabilita' | Impatto | Severita' | Fonte |
|---|---|---|---|---|---|
| R-01 | Accesso non autorizzato ai dati degli studenti | Media | Alto | **ALTO** | Pen-test SEC-001/002 (remediated) |
| R-02 | Fuga di PII verso API LLM esterne | Bassa | Molto Alto | **ALTO** | Architettura pseudonimizzazione |
| R-03 | Contenuto inappropriato generato e consegnato a minore | Bassa | Alto | **MEDIO** | Safeguarding gate architetturale |
| R-04 | Esposizione lingua nativa (Art. 9) in dashboard | Bassa | Alto | **MEDIO** | Design data model |
| R-05 | Violazione del diritto all'oblio (cancellazione incompleta) | Bassa | Alto | **MEDIO** | Stored procedure atomica |
| R-06 | Confronto tra studenti (dati visibili ad altri studenti) | Bassa | Medio | **MEDIO** | RBAC + design UI |
| R-07 | Bias algoritmico nei contenuti generati (genere, geografia, disabilita') | Media | Medio | **MEDIO** | Bias audit BSA-04/07/09 |
| R-08 | Consenso non valido (minore < 14 senza firma genitore) | Bassa | Alto | **MEDIO** | Procedura cartacea MVP |
| R-09 | Manipolazione audit trail | Molto Bassa | Alto | **BASSO** | Trigger immutabilita' + SEC-010 |
| R-10 | Accesso IDOR ai dati di altro studente | Bassa | Medio | **BASSO** | Pen-test SEC-003 (remediated) |
| R-11 | Disagio emotivo non rilevato (wellbeing detection incompleta) | Media | Medio | **MEDIO** | Bias audit BSA-03/11 |
| R-12 | Data breach (esfiltrazione database) | Molto Bassa | Molto Alto | **MEDIO** | Defence in depth |
| R-13 | Rate abuse su API LLM (costi, DoS) | Media | Basso | **BASSO** | Pen-test SEC-007 (V1 planned) |
| R-14 | Default password in configurazione | Bassa | Medio | **BASSO** | Pen-test SEC-008 (V1 planned) |

### 4.2 Dettaglio rischi dal Pen-Test (T5.4)

Il pen-test (`.maestro/tests/security-pentest-report.md`) ha identificato 16 finding:
- **2 Critical** (SEC-001, SEC-002): endpoint KG e Content senza autenticazione -- **REMEDIATED**
- **3 High** (SEC-003, SEC-004, SEC-005): IDOR, header mancanti, CORS permissivo -- **REMEDIATED**
- **5 Medium**: rate limiting (V1), default password (V1), token revocation (V1), hash chain audit (V1), CSP dashboard (V1)
- **4 Low**: dependency, IP hash, error detail, docs endpoint

**Valutazione post-remediation**: 0 critical, 0 high. Le 5 medium residue hanno piani di mitigazione per V1 e non rappresentano un rischio inaccettabile per il pilot MVP (1 scuola, rete scolastica controllata).

### 4.3 Dettaglio rischi dal Bias Audit (T5.6)

Il bias audit (`.maestro/tests/bias-safety-audit-report.md`) ha identificato 18 finding:
- **3 HIGH**: lacuna state rosso in UI (BSA-01), gamification regex mancanti (BSA-02), wellbeing solo italiano (BSA-03)
- **6 MEDIUM**: ableist metaphors (BSA-04), alert teacher_id null (BSA-05), PII residual check (BSA-06), quiz feedback (BSA-17), class heatmap access (BSA-18)
- **8 LOW**: vari gap di copertura regex e design

**Rischi specifici per minori identificati**:
- BSA-01: colore rosso per lacune puo' causare ansia
- BSA-03: studenti non italofoni che esprimono disagio non vengono rilevati
- BSA-07/09: potenziali stereotipi di genere e nazionalita' nei contenuti generati

### 4.4 Rischi specifici da trattamento LLM

| Rischio | Mitigazione |
|---|---|
| LLM memorizza dati studente nel training | I provider (Anthropic, OpenAI) non usano dati API per training. DPA in essere. Nessun PII inviato comunque. |
| LLM genera risposta con PII residuo | Pseudonimizzazione fail-closed: se residuo PII rilevato, chiamata bloccata. Mapping distrutto dopo uso. |
| LLM produce contenuto inappropriato | 3 livelli di difesa: prompt safeguarding (9 regole), check regex deterministico (25+ pattern), retry fino a 3 volte, fallback se tutti falliscono. Gate architetturale non bypassabile. |
| LLM produce contenuto con bias | Regex per stereotipi (genere, geografico, nazionale). Bias audit trimestrale (V1). |

---

## 5. Misure di Mitigazione

### 5.1 Misure tecniche

| Misura | Dettaglio | Rischio mitigato |
|---|---|---|
| **Cifratura at rest (PII)** | pgcrypto `pgp_sym_encrypt` con AES-256 per nome, cognome, email di studenti e docenti | R-12 |
| **Cifratura in transit** | TLS 1.3 su tutte le connessioni (Caddy reverse proxy, HSTS) | R-12 |
| **Pseudonimizzazione LLM** | `LLMGateway` con sostituzione PII, check residui fail-closed, mapping in-memory distrutto dopo uso | R-02 |
| **RBAC** | 3 ruoli Keycloak (student, teacher, admin), matrice RBAC completa, check own-data su tutti gli endpoint student | R-01, R-06, R-10 |
| **Autenticazione** | Keycloak OIDC, JWT RS256, PKCE per client pubblici, MFA TOTP obbligatorio per admin | R-01 |
| **Audit immutabile** | Tabelle append-only con trigger `BEFORE UPDATE/DELETE` che bloccano modifiche | R-09 |
| **Safeguarding gate** | Nodo obbligatorio nel grafo LangGraph, nessun edge da generazione a consegna senza safeguarding | R-03 |
| **Data minimization** | `birth_year` (non DOB), hash IP (non raw), lingua solo come ISO code | R-12 |
| **Right to erasure atomico** | Stored procedure `core.execute_right_to_erasure` in singola transazione con certificato di cancellazione | R-05 |
| **Partitioning** | Tabelle audit e transizioni partizionate per mese (pg_partman) per gestione retention | R-09 |
| **Ruoli DB separati** | `maestro_app` (CRUD), `maestro_readonly` (SELECT), `maestro_erasure` (solo stored procedure erasure) | R-01, R-09 |
| **EU data residency** | Hetzner (Germania) per compute e DB, Scaleway (Francia/Paesi Bassi) per object storage | R-12 |
| **Wellbeing detection** | 31 keyword in 4 categorie (frustrazione, disperazione, isolamento, rischio autolesionismo) con escalation progressiva | R-11 |
| **Security headers** | HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Cache-Control no-store | R-01 |
| **Brute force protection** | Keycloak: lock dopo 5 tentativi, wait 15 minuti | R-01 |
| **Password policy** | 12+ caratteri, complessita', storico 3 password | R-01 |

### 5.2 Misure organizzative

| Misura | Dettaglio | Rischio mitigato |
|---|---|---|
| **Formazione docente** | Prima del pilot: sessione formativa su funzionalita' MAESTRO, interpretazione alert benessere, limitazioni del sistema (es. wellbeing detection solo in italiano) | R-03, R-11 |
| **Referente scolastico** | Identificazione del referente scolastico (psicologo/coordinatore) per ricezione alert high/critical | R-11 |
| **Procedura consenso cartacea** | Moduli cartacei con 5 consensi granulari, firma genitore + studente >= 14, archiviazione sicura dei moduli | R-08 |
| **Procedura erasure documentata** | Procedura scritta per gestione richieste di cancellazione, massimo 30 giorni (target 24 ore) | R-05 |
| **DPO coinvolgimento** | DPO della scuola informato e coinvolto nella review della DPIA | R-08 |
| **Review periodica contenuti** | Il docente puo' visualizzare e rigenerare i contenuti generati (F15.1). Alert in dashboard se safeguarding blocca dopo 3 tentativi. | R-03, R-07 |
| **Informativa privacy** | Informativa separata per studenti (linguaggio per minori) e per famiglie (completa, Art. 13/14 GDPR) | R-08 |

### 5.3 Misure di safeguarding

| Misura | Dettaglio | Rischio mitigato |
|---|---|---|
| **9 regole nel system prompt** | Mai confronto tra studenti, mai tono punitivo, mai linguaggio offensivo, mai rosso per risultati negativi, mai FOMO/scarcity, mai terapia improvvisata, lacuna = porta aperta, termini spiegati, analogie non stereotipate | R-03, R-07 |
| **25+ pattern regex deterministici** | Post-generation check su confronti, tono, offese, FOMO, colpevolizzazione, rosso, stereotipi, terapia, eta'-inappropriato | R-03 |
| **Retry progressivo** | 3 tentativi con temperatura decrescente (0.7 -> 0.3 -> 0.1) e prompt progressivamente piu' conservativo | R-03 |
| **Fallback sicuro** | Se 3 tentativi falliscono: servire materiale del docente o messaggio generico neutro. Mai contenuto non validato. | R-03 |
| **Anti-pattern gamification** | Nessun leaderboard, nessun confronto, nessun FOMO, nessun countdown, nessuna ricompensa variabile, opt-out senza perdita progresso | R-06 |

---

## 6. Diritti degli Interessati

### 6.1 Implementazione dei diritti

| Diritto GDPR | Implementazione MVP | Status | V1 |
|---|---|---|---|
| **Accesso** (Art. 15) | Lo studente vede la propria mappa della conoscenza, il proprio profilo, i propri contenuti. Il docente vede la dashboard di classe. Export CSV/JSON dell'audit log per admin. | Implementato | Self-service export per famiglie |
| **Rettifica** (Art. 16) | Lo studente modifica il proprio profilo (preferenze, tono, lunghezza). L'admin corregge dati anagrafici su richiesta. | Implementato | Self-service per famiglie |
| **Cancellazione** (Art. 17) | Stored procedure atomica `core.execute_right_to_erasure`. Certificato di cancellazione. Max 30 giorni (target 24h). Richiesta via admin IT. | Implementato (procedura documentata) | Self-service via portale famiglia |
| **Limitazione** (Art. 18) | Sospensione account (F14.8): preserva dati, blocca generazione. | V1 (procedura manuale per MVP) | Automatizzato |
| **Portabilita'** (Art. 20) | Export JSON della mappa della conoscenza e cronologia transizioni per studente. | Parziale (API endpoint) | Export completo strutturato |
| **Opposizione** (Art. 21) | Revoca di ciascuno dei 5 consensi, indipendentemente. Il sistema degrada gracefully (es. revoca a: profilo neutro; revoca b: niente bilingue). | Implementato (via admin IT, cartaceo MVP) | Self-service digitale |
| **Decisioni automatizzate** (Art. 22) | Le transizioni di stato sono proposte dal sistema ma confermate dal docente (F4.4: anteprima transizioni). L'override docente e' sempre disponibile (F11.12). Pannello di spiegabilita' per lo studente (N7). | Implementato | -- |

### 6.2 Informativa privacy

Per il pilot MVP sono predisposte due informative:

1. **Informativa per le famiglie** (Art. 13 GDPR): documento completo con identita' titolare/responsabile, finalita', base giuridica, periodo conservazione, diritti, contatti DPO
2. **Informativa per studenti** (linguaggio semplificato, age-appropriate): stessa sostanza ma senza legalese, con esempi concreti ("Cosa facciamo con i tuoi dati", "Come puoi cancellare tutto", "Chi puo' vedere cosa")

Entrambe consegnate contestualmente ai moduli di consenso prima dell'inizio del pilot.

---

## 7. Consultazione

### 7.1 Consultazione preventiva del Garante (Art. 36)

La consultazione preventiva e' richiesta quando "il trattamento presenterebbe un rischio elevato in assenza di misure adottate dal titolare del trattamento per attenuare il rischio" (Art. 36(1)).

**Valutazione**: data la natura del trattamento (profilazione di minori, trattamento Art. 9), la consultazione preventiva sarebbe in linea di principio raccomandata. Tuttavia, le misure di mitigazione implementate (pseudonimizzazione, cifratura, RBAC, safeguarding gate, audit immutabile, erasure atomico) riducono il rischio residuo a livello accettabile.

**Decisione per MVP pilot**: non si procede alla consultazione preventiva per il pilot (1 scuola, ~25 studenti, durata limitata), ma si documenta la DPIA e la si mette a disposizione del Garante su richiesta. Per il roll-out V1 (piu' scuole) sara' necessario rivalutare la necessita' della consultazione preventiva.

### 7.2 DPO

Il DPO della scuola (obbligatorio per gli istituti scolastici pubblici, Art. 37(1)(a) GDPR) deve:
- Ricevere copia di questa DPIA
- Fornire parere formale prima dell'avvio del pilot
- Essere disponibile come punto di contatto per le famiglie
- Essere informato di eventuali data breach

### 7.3 Obblighi informativi verso le famiglie

Prima dell'avvio del pilot:
1. Riunione informativa con le famiglie della classe
2. Consegna informativa privacy + moduli consenso
3. Periodo minimo 15 giorni per restituire i moduli firmati
4. Lo studente che non restituisce il consenso puo' comunque partecipare alle lezioni normali -- non usa MAESTRO

---

## 8. Rischio Residuo

### 8.1 Valutazione complessiva post-mitigazione

| Rischio | Severita' iniziale | Mitigazioni applicate | Rischio residuo |
|---|---|---|---|
| R-01 Accesso non autorizzato | ALTO | Keycloak, RBAC, IDOR fix, security headers | **BASSO** |
| R-02 Fuga PII verso LLM | ALTO | Pseudonimizzazione fail-closed, mapping in-memory | **MOLTO BASSO** |
| R-03 Contenuto inappropriato a minore | MEDIO | 3 livelli safeguarding, retry, fallback, gate architetturale | **BASSO** |
| R-04 Esposizione lingua nativa | MEDIO | Consenso separato, mai in dashboard, pseudonimizzata | **BASSO** |
| R-05 Erasure incompleta | MEDIO | Stored procedure atomica, certificato, S3 cleanup async | **BASSO** |
| R-06 Confronto tra studenti | MEDIO | RBAC own-data, no leaderboard, safeguarding regole 1/5 | **MOLTO BASSO** |
| R-07 Bias algoritmico | MEDIO | 9 regole prompt, regex, bias audit | **BASSO** (gap su ableist metaphors) |
| R-08 Consenso non valido | MEDIO | Procedura cartacea, doppia firma, formazione | **BASSO** |
| R-09 Manipolazione audit | BASSO | Trigger immutabilita', ruoli DB separati | **MOLTO BASSO** |
| R-10 IDOR | BASSO | check_own_data_or_role su tutti gli endpoint | **MOLTO BASSO** |
| R-11 Disagio non rilevato | MEDIO | 31 keyword, escalation, formazione docente. Gap: solo italiano | **BASSO** (con mitigazione organizzativa) |
| R-12 Data breach | MEDIO | Cifratura, TLS, firewall, ruoli, EU residency | **BASSO** |

### 8.2 Accettazione del rischio residuo

Il rischio residuo complessivo per il pilot MVP e' valutato come **BASSO**, con le seguenti condizioni:

1. **Condizione**: il docente deve essere formato sulle limitazioni del sistema (wellbeing detection solo italiano, BSA-03)
2. **Condizione**: i finding BSA-01 (colore rosso), BSA-04 (ableist metaphors), BSA-05 (alert missing teacher_id), BSA-17 (quiz feedback) devono essere corretti prima dell'avvio del pilot
3. **Condizione**: le mitigazioni del pen-test (SEC-001..006) devono essere verificate come applicate
4. **Condizione**: il DPO della scuola deve fornire parere favorevole

### 8.3 Open questions (escalation a Director -> Human)

| # | Domanda | Impatto | Status |
|---|---|---|---|
| A1 | E' necessario nominare un DPO esterno dedicato al progetto MAESTRO, oppure il DPO della scuola e' sufficiente? | Organizzativo | Da verificare con la scuola |
| A2 | La base giuridica Art. 6(1)(e) (compito di interesse pubblico) e' sufficiente per il tracciamento KMM, o serve anche il consenso? | Giuridico | Parere DPO necessario |
| A3 | Il Garante richiede notifica preventiva per l'uso di LLM su dati (pseudonimizzati) di minori nel contesto scolastico? | Compliance | Da verificare con le linee guida DM 166/2025 |
| A4 | Il DM 166/2025 richiede certificazione specifica per i tool IA usati nelle scuole? | Compliance | Da verificare |
| A5 | La conservazione decennale dell'audit log e' compatibile con il principio di storage limitation? | Giuridico | Standard per documentazione scolastica |

---

## Appendice A: Mapping requisiti DPIA

| Requisito MAESTRO | Sezione DPIA |
|---|---|
| F14.3 (5 consensi granulari) | 2.1, 6.1, consent-templates-mvp.md |
| F14.9 (right to erasure) | 5.1, 6.1 |
| F14.10 (audit log) | 5.1 |
| N1 (privacy e protezione minori) | 2, 3, 5 |
| N3 (etica e benessere) | 5.3 |
| Art. 8 GDPR (consenso minori) | 2.2 |
| Art. 9 GDPR (lingua nativa) | 2.3 |
| Art. 35 GDPR (DPIA) | Questo documento |
| Provvedimento Garante 529/2025 | 2.4, garante-alignment-checklist.md |
| DM 166/2025 (MIM) | 2.4, garante-alignment-checklist.md |

---

*Documento prodotto per il task T6.3 del DAG MAESTRO. Soggetto a review da MSTR-02 (CTA), MSTR-13 (Security Engineer), MSTR-01 (Programme Director), e parere del DPO della scuola.*
