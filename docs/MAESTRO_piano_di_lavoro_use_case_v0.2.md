# Piano di lavoro — Stesura degli Use Case per MAESTRO

**Versione:** v0.2
**Allineato al documento di progetto:** MAESTRO_documento_progetto_v0.2.md
**Aggiornamenti rispetto alla v0.1:**
- Aggiunta macro-area UC **Anagrafica, consenso e iscrizione** (10 UC)
- Aggiunta macro-area UC **Mappa della conoscenza e ciclo di chiusura** (12 UC), con accorpamento di UC-ST-05 e UC-DOC-07 della v0.1 (assorbiti dai nuovi UC più specifici)
- Nuova **Fase 4-bis** dedicata al ciclo di chiusura della lacuna
- Standard di qualità integrati: granularità macro/micro, override tracciato, transizioni di stato
- Stima tempi: da 6-8 settimane a **7-9 settimane**

---

## 1. Obiettivo e perimetro

Produrre un **catalogo strutturato di use case** che:
- traduca tutti i requisiti funzionali del documento v0.2 (F1–F14) in scenari attore-sistema;
- mantenga **tracciabilità bidirezionale** verso i requisiti (RF/NF) e verso la roadmap (MVP / V1 / V2);
- copra in via prioritaria il perimetro **MVP**, con summary-level per V1/V2;
- sia **leggibile da non specialisti** (docenti, famiglie, dirigenza), pur restando rigoroso per il team tecnico;
- documenti come **sequence diagram dedicato** il ciclo di chiusura della lacuna, perché è il cuore didattico del sistema.

I requisiti non funzionali (privacy, sicurezza, etica, accessibilità) **non diventano UC separati** ma sono trattati come *vincoli trasversali* citati nelle precondizioni e nei flussi di eccezione (Safeguarding Agent, audit log obbligatorio, override tracciato).

## 2. Approccio metodologico

- **Template Cockburn**: ID, scope, livello, attore primario, stakeholder, precondizioni, trigger, scenario principale, estensioni, post-condizioni, requisiti speciali, riferimenti.
- **Tre livelli di granularità**:
  - *Summary* (cloud, ☁️) — flussi macro per orientamento esecutivo;
  - *User goal* (sea, 🌊) — cuore del catalogo, livello azionabile per il design;
  - *Subfunction* (fish, 🐟) — solo per meccanismi critici (Safeguarding, Bilingual Composer, mapping errore→KG, transizioni di stato del KMM).
- **Tecniche di identificazione**: actor-goal list per ciascuno dei cinque attori, event analysis sui trigger temporali (verifica caricata, retention check D+3/D+7/D+21, lacuna persistente da 14 giorni), state analysis sulla macchina a stati di F11, CRUD analysis sulle entità chiave.
- **Naming convention**: `UC-<attore>-<NN>` per gli UC esterni, `UC-SYS-<NN>` per i flussi interni di sistema.

## 3. Fasi e attività

**Fase 0 — Setup (3-4 giorni).** Template UC condiviso, glossario di dominio (concetto, micro-nodo, macro-nodo, articolazione, stato semaforo, transizione, retention check, lacuna persistente, override tracciato, consenso granulare), naming convention, repository documentale.

**Fase 1 — Identificazione candidati (1 settimana).** Actor-goal list per i cinque attori. Output: lista master di UC candidati (vedi §4).

**Fase 2 — Prioritizzazione (2-3 giorni).** Allineamento con la roadmap: marcatura MVP / V1 / V2 / fuori scope. Validazione rapida con sponsor didattico.

**Fase 3 — Stesura summary-level (1 settimana).** Tutti gli UC del catalogo descritti a livello cloud (3-5 righe ciascuno) per ottenere visione d'insieme prima di scendere nel dettaglio.

**Fase 4 — Dettaglio user-goal MVP (2-3 settimane).** Scrittura completa degli UC del perimetro MVP, con almeno tre scenari alternativi per ciascuno: errore tecnico, intervento safeguarding, opt-out utente.

**Fase 4-bis — Ciclo di chiusura della lacuna (3-5 giorni).** *Sprint dedicato* al flow centrale del sistema, perché attraversa più UC e merita una documentazione coordinata.
- Sequence diagram del ciclo completo: UC-SYS-09 → UC-ST-15 → UC-SYS-10 → UC-SYS-11 + UC-ST-16 → UC-SYS-12 → UC-SYS-13 → stato consolidato
- Dettaglio dei subfunction UC-SYS-09/10/11/12/13
- Diagramma di macchina a stati formale (sei stati, transizioni, eventi)
- Documentazione del comportamento di regressione (errore in verifica successiva → ritorno a `lacuna`)
- Validazione con un docente pilota su uno scenario concreto (es. scenario Francesca / definizione di algoritmo)

**Fase 5 — Subfunction critici residui (1 settimana).** Approfondimento dei meccanismi non coperti in Fase 4-bis: validazione safeguarding, generazione bilingue, mapping errore→nodo micro, gestione override docente con audit, rilevamento di lettura squilibrata in lingua nativa (F13.20).

**Fase 6 — Tracciabilità e copertura (3-4 giorni).** Costruzione della matrice RF ↔ UC; identificazione dei requisiti scoperti o sovracoperti; gap fixing. Particolare attenzione a F11 (la più densa) e F14 (la più trasversale).

**Fase 7 — Validazione con docenti pilota (2 settimane, in parallelo).** Walkthrough degli UC user-goal con due-tre docenti dell'istituto pilota; raccolta feedback su realismo dei flussi, terminologia, casi limite mancanti. **Walkthrough specifico** sul ciclo di chiusura con esempi reali tratti dalle verifiche già somministrate.

**Tempo complessivo indicativo:** **7-9 settimane** per la prima release stabile del catalogo, con la versione "MVP-ready" disponibile attorno alla settimana 5.

## 4. Identificazione iniziale dei candidati UC

Lista di partenza derivata dai requisiti v0.2. Da raffinare in Fase 1. Totale candidati: **~58 UC** (40 esterni + 18 di sistema).

### 4.1 Attore: Studente

| ID | Use case | Riferimenti RF | Priorità |
|---|---|---|---|
| UC-ST-00 | Attivare per la prima volta l'account (post-creazione, pre-profilazione) | F14.6 | MVP |
| UC-ST-01 | Completare onboarding e profilazione learning style | F3.1–F3.5 | MVP |
| UC-ST-02 | Consultare il proprio documento di ripasso personalizzato | F4, F5 | MVP |
| UC-ST-03 | Ascoltare podcast a due voci su un concetto | F6 | V1 |
| UC-ST-04 | Esercitarsi su una quest giornaliera/settimanale | F7.5 | V1 |
| UC-ST-06 | Chiedere "perché mi stai mostrando questo" | N7 | MVP |
| UC-ST-07 | Modificare preferenze di profilo (tono, lunghezza, canale, granularità) | F1.8, F3.4–F3.6, F8 | MVP |
| UC-ST-08 | Attivare/disattivare il bilinguismo | F13.9 | MVP |
| UC-ST-09 | Spiegare a voce un concetto al sistema (rubber duck) | F10.4 | V2 |
| UC-ST-10 | Disattivare la gamification | F7.8 | V1 |
| UC-ST-11 | Richiedere oblio dei propri dati | N1, F14.9 | MVP |
| UC-ST-12 | Passare da articolazione testo ad audio mantenendo il contesto | F10.2 | V1 |
| UC-ST-13 | Consultare la propria mappa della conoscenza (vista semaforo) | F11.1–F11.3, F11.11 | MVP |
| UC-ST-14 | Consultare la heatmap temporale delle proprie lacune | F11.13 | V1 |
| UC-ST-15 | Avviare un percorso di approfondimento su una lacuna | F11.6, F11.7 | MVP |
| UC-ST-16 | Sostenere il mini-quiz di chiusura di una lacuna | F11.8, F11.9 | MVP |

*Note*: UC-ST-05 della v0.1 ("Visualizzare il proprio knowledge graph") è confluito in UC-ST-13, ora più specifico e ricco.

### 4.2 Attore: Docente

| ID | Use case | Riferimenti RF | Priorità |
|---|---|---|---|
| UC-DOC-01 | Caricare una lezione (audio/video/slide) | F2.1, F2.7 | MVP |
| UC-DOC-02 | Rifinire la trascrizione automatica della lezione | F2.2–F2.3 | MVP |
| UC-DOC-03 | Validare il mapping della lezione sui nodi del KG | F2.4 | MVP |
| UC-DOC-04 | Caricare una verifica per diagnostica formativa | F4.1–F4.5 | MVP |
| UC-DOC-05 | Generare una verifica bilanciata sul programma | F12.3 | V2 |
| UC-DOC-06 | Consultare heatmap dei gap di classe | F11.14, F12.1, F12.4 | V1 |
| UC-DOC-08 | Modificare o cancellare un contenuto generato dal sistema | F12.5 | MVP |
| UC-DOC-09 | Definire la lingua ufficiale del corso | F13.1–F13.3 | MVP |
| UC-DOC-10 | Aggiornare il knowledge graph del programma | F1.4, F1.9 | MVP |
| UC-DOC-11 | Visualizzare le lacune di copertura del materiale | F2.12 | V1 |
| UC-DOC-12 | Iscrivere uno studente al proprio corso/classe | F14.5 | MVP |
| UC-DOC-13 | Rimuovere uno studente dal proprio corso | F14.5 | V1 |
| UC-DOC-14 | Consultare la mappa della conoscenza di un singolo studente | F11.1, F12.2 | MVP |
| UC-DOC-15 | Consultare la heatmap delle lacune di classe nel tempo | F11.14 | V1 |
| UC-DOC-16 | Forzare manualmente lo stato di un nodo (override tracciato) | F11.12 | V1 |
| UC-DOC-17 | Configurare livello scolastico e granularità di default del corso | F1.6, F1.8, F1.9 | MVP |
| UC-DOC-18 | Consultare il pannello dei propri override (autoverifica) | F12.6 | V1 |
| UC-DOC-19 | Ricevere e gestire alert su lacune persistenti di classe | F11.15 | V1 |

*Note*: UC-DOC-07 della v0.1 ("Visualizzare il profilo gap di un singolo studente") è confluito in UC-DOC-14, ora più specifico e completo.

### 4.3 Altri attori

| ID | Use case | Attore | Riferimenti RF/NF | Priorità |
|---|---|---|---|---|
| UC-FAM-00 | Registrare il consenso al trattamento dati del minore (granulare) | Famiglia | F14.3, N1 | MVP |
| UC-FAM-02 | Consultare il report mensile sui progressi | Famiglia | F11.16 | V1 |
| UC-FAM-03 | Esercitare diritto all'oblio per il minore | Famiglia | F14.9, N1 | MVP |
| UC-FAM-04 | Aggiornare il consenso (es. valorizzare lingua nativa successivamente) | Famiglia | F14.3, F13.5 | V1 |
| UC-COR-01 | Consultare dati aggregati di corso/classe | Coordinatore | F12.1, F11.14 | V1 |
| UC-AS-01 | Configurare SSO con il registro elettronico | IT scuola | N2 | V1 |
| UC-AS-02 | Gestire utenze e ruoli | IT scuola | N2 | MVP |
| UC-AS-03 | Consultare audit log degli accessi a dati di minori | IT scuola | N1, N2, F14.10 | MVP |
| UC-AS-04 | Importare massivamente studenti dal registro elettronico | IT scuola | F14.2 | V2 |
| UC-AS-05 | Creare manualmente un singolo studente | IT scuola | F14.2 | MVP |
| UC-AS-06 | Aggiornare l'anagrafica studente (passaggio di classe) | IT scuola | F14.7 | V1 |
| UC-AS-07 | Sospendere/disattivare uno studente | IT scuola | F14.8 | V1 |
| UC-AS-08 | Cancellare definitivamente lo studente (oblio) | IT scuola | F14.9 | MVP |

### 4.4 Use case di sistema (subfunction)

| ID | Use case | Riferimenti | Priorità |
|---|---|---|---|
| UC-SYS-01 | Generare un documento di ripasso personalizzato | F5 | MVP |
| UC-SYS-02 | Mappare un errore di verifica al micro-nodo concettuale | F4.2 | MVP |
| UC-SYS-03 | Aggiornare il vettore di learning style sul comportamento osservato | F3.3 | V1 |
| UC-SYS-04 | Validare un output con il Safeguarding Agent | N3 | MVP |
| UC-SYS-05 | Comporre output in doppia lingua (Bilingual Composer) | F13.7–F13.14 | MVP |
| UC-SYS-06 | Rilevare pattern di disagio e attivare alert | N3 | V1 |
| UC-SYS-07 | Pianificare ripasso con spaced repetition | F11.10 | V1 |
| UC-SYS-08 | Rilevare lettura squilibrata sulla colonna lingua nativa | F13.20 | V1 |
| UC-SYS-09 | Rilevare una lacuna e impostare lo stato a `lacuna` | F4.3, F11.4 | MVP |
| UC-SYS-10 | Generare percorso di approfondimento personalizzato per la lacuna | F11.7 | MVP |
| UC-SYS-11 | Generare e somministrare mini-quiz di chiusura | F11.8 | MVP |
| UC-SYS-12 | Aggiornare stato nodo e registrare cronologia delle transizioni | F11.4, F11.5 | MVP |
| UC-SYS-13 | Eseguire retention check programmati (D+3, D+7, D+21) | F11.10 | V1 |
| UC-SYS-14 | Calcolare l'aggregazione macro da micro (regola stato peggiore) | F11.11 | MVP |
| UC-SYS-15 | Adattare la granularità di vista al livello scolastico | F1.8 | MVP |
| UC-SYS-16 | Generare il report mensile per la famiglia | F11.16 | V1 |
| UC-SYS-17 | Tracciare in audit log un override docente | F11.12, N7 | MVP |
| UC-SYS-18 | Rilevare regressione su nodo già a `da_consolidare` o `consolidato` | F11.4 | V1 |

### 4.5 Riepilogo per priorità

| Priorità | UC esterni | UC sistema | Totale |
|---|---|---|---|
| MVP | 19 | 10 | 29 |
| V1 | 16 | 7 | 23 |
| V2 | 5 | 0 | 5 |
| Da valutare | 0 | 1 | 1 |
| **Totale** | **40** | **18** | **58** |

## 5. Standard di qualità

Per ogni UC user-goal richiediamo, prima della chiusura:
- precondizioni **testabili** (non desideri vaghi);
- almeno tre scenari alternativi: errore tecnico, intervento del Safeguarding Agent, opt-out dell'utente;
- linguaggio **indipendente dall'implementazione**;
- riferimenti incrociati ai requisiti F/N coperti;
- almeno un criterio di accettazione misurabile, agganciato dove possibile ai KPI di §8 del documento sorgente.

**Standard aggiuntivi per gli UC che toccano la mappa della conoscenza (F11):**
- esplicitazione dello **stato iniziale** del nodo (precondizione) e dello **stato finale atteso** (post-condizione)
- copertura del caso **regressione**: cosa succede se uno stato `da_consolidare` viene contraddetto da una verifica successiva
- per gli UC con override docente: motivazione obbligatoria, scenario di audit log, scenario in cui il sistema rifiuta un override (es. nodo non ancora introdotto)

**Standard aggiuntivi per gli UC F14 (anagrafica/consenso):**
- esplicitazione della **base giuridica** (GDPR Art. 8 minori; Art. 9 categorie particolari per lingua nativa)
- scenario di **consenso revocato** o **negato**
- scenario di **richiesta oblio** in stato qualsiasi del ciclo di vita

## 6. Deliverable attesi

1. **Catalogo UC master** (foglio di calcolo) con ID, titolo, attore, livello, priorità, stato, requisiti coperti.
2. **Schede UC dettagliate** (una per UC user-goal MVP, sintetiche per gli altri).
3. **Diagramma di macchina a stati** del Knowledge Map Manager (Fase 4-bis).
4. **Sequence diagram** del ciclo di chiusura della lacuna (Fase 4-bis).
5. **Diagrammi UCD** per attore e un diagramma di insieme.
6. **Matrice di tracciabilità RF/NF ↔ UC** con analisi di copertura e gap.
7. **Glossario di dominio** condiviso (esteso con i termini introdotti dalla v0.2: granularità, macro-nodo, micro-nodo, retention check, override tracciato, consenso granulare).
8. **Verbale dei walkthrough** con i docenti pilota (Fase 7).

## 7. Rischi della fase e mitigazione

- **Granularità incoerente** tra autori → adottare il template Cockburn rigidamente; doppia revisione incrociata sui primi 5 UC scritti per allineare lo stile.
- **Drift verso il design** (UC che parlano di componenti tecniche) → review check di linguaggio neutro a fine Fase 4.
- **Sottocopertura dei requisiti non funzionali**, in particolare safeguarding e privacy minori → introdurli esplicitamente come *scenari alternativi obbligatori* su tutti gli UC student-facing.
- **Sovraccarico sui docenti pilota** in Fase 7 → walkthrough in sessioni brevi (max 90 minuti), preceduti da invio del materiale 48h prima.
- **Confusione tra F11 (mappa) e F4 (diagnostica)** → distinguere chiaramente nel template: F4 è il *trigger* (verifica → errore → mapping), F11 è il *gestore di stato* (transizione e ciclo). I due si toccano in UC-SYS-09.
- **Override mal compreso** dagli stakeholder → preparare un esempio canonico nel glossario ("verifica orale superata in classe il 15/05, non registrata da MAESTRO") e usarlo come riferimento nei walkthrough.

## 8. Timeline indicativa

| Settimana | Attività principale |
|---|---|
| 1 | Fase 0 setup, avvio Fase 1 identificazione |
| 2 | Fase 1 (completamento) + Fase 2 prioritizzazione |
| 3 | Fase 3 stesura summary-level |
| 4 | Fase 4 dettaglio MVP (parte 1) |
| 5 | Fase 4 dettaglio MVP (parte 2) + checkpoint MVP-ready |
| 5.5 | Fase 4-bis ciclo di chiusura |
| 6 | Fase 5 subfunction residui |
| 6.5 | Fase 6 tracciabilità |
| 7-8 | Fase 7 validazione docenti pilota (parallela) |
| 9 | Consolidamento finale e release v1.0 del catalogo |

---

*Documento di lavoro v0.2. Da iterare insieme al documento di progetto.*
