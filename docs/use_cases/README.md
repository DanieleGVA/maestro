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
  - *Summary* (cloud) — flussi macro per orientamento esecutivo;
  - *User goal* (sea) — cuore del catalogo, livello azionabile per il design;
  - *Subfunction* (fish) — solo per meccanismi critici (Safeguarding, Bilingual Composer, mapping errore→KG, transizioni di stato del KMM).
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

I candidati UC sono suddivisi nei seguenti file per attore:

- [UC Studente](UC_studente.md) — 16 UC (UC-ST-*)
- [UC Docente](UC_docente.md) — 18 UC (UC-DOC-*)
- [UC Altri attori](UC_altri_attori.md) — 13 UC (Famiglia, Coordinatore, IT scuola)
- [UC Sistema](UC_sistema.md) — 18 UC subfunction (UC-SYS-*)
- [Riepilogo per priorità](riepilogo_priorita.md)

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
