# Progetto MAESTRO
## Sistema di accompagnamento personalizzato per studenti di Informatica

**Requisiti funzionali e non funzionali — v0.3**
**Autore:** Team agentico MAESTRO (MSTR-01, MSTR-02, MSTR-03 con contributi di MSTR-15..19)
**Continuità:** consolida v0.2 + catalogo use case v1.0 (58 UC) + specifiche schermate v1.0 (42 schermate) + architettura team agentico v1.0 (23 agenti)

### Changelog v0.2 → v0.3

**Nuovi requisiti aggiunti:**

- **F15 — Ciclo di vita del contenuto generato**: nuovo gruppo che copre la gestione, archiviazione e rigenerazione dei contenuti prodotti dal sistema (emerso da UC-DOC-08, UC-DOC-09, SCR-DOC-13).
- **F16 — Notifiche e alert**: nuovo gruppo che sistematizza i meccanismi di notifica per docente, studente e famiglia (emerso da UC-DOC-19, SCR-DOC-16, SCR-ST-03).
- **F17 — Setup corso e onboarding docente**: nuovo gruppo che formalizza il wizard di configurazione iniziale (emerso da SCR-DOC-03, UC-DOC-17).
- **N8 — Offline e sincronizzazione**: nuovo requisito non funzionale per la modalità offline dell'app studente (emerso da SCR-ST componente barra connessione).
- **N9 — Internazionalizzazione UI**: requisito non funzionale per la localizzazione dell'interfaccia, distinto dal bilinguismo didattico F13 (emerso da SCR componente selettore lingua).

**Requisiti raffinati:**

- **F3** esteso con dettagli sul radar chart a 5 assi, il quiz interattivo a 4 modalità, e i vincoli di durata (da SCR-ST-02, UC-ST-01).
- **F4** raffinato con il flusso step-by-step di upload verifica: definizione domande, mapping, inserimento voti, conferma con anteprima transizioni (da SCR-DOC-07, UC-DOC-04).
- **F5** raffinato con vincoli di layout bilingue a due colonne e struttura 4 blocchi esplicita (da SCR-ST-08, UC-ST-02).
- **F7** suddiviso in F7-A (gamification) e F7-B (diagnostica e heatmap) per chiarezza; heatmap docente spostata da F12 a F7-B per coerenza con F11.
- **F9** esteso con requisiti specifici di design system: colori hex, componente selettore accessibilità, anteprima live (da SCR principi di design).
- **F11** raffinato con vincoli temporali espliciti per retention check MVP (almeno D+7) e regole precise di transizione (da UC-ST-16, UC-SYS-09, UC-SYS-12).
- **F12** raffinato con sidebar permanente, card-based layout, selettore classe, alert inline (da SCR-DOC-02, SCR-DOC-08).
- **F14** esteso con flusso di prima attivazione (da UC-ST-00, SCR-ST-01), import massivo CSV (da SCR-AS-07, UC-AS-04), e certificato di cancellazione (da SCR-AS-05).
- **N1** esteso con requisiti di pseudonimizzazione nell'audit log post-cancellazione (da SCR-AS-05).
- **N2** esteso con MFA obbligatorio per admin (da SCR-AS-01) e configurazione SSO dettagliata (da SCR-AS-06).
- **N4** aggiornato con latenza di generazione per ogni tipo di contenuto (da UC-SYS-01, UC-SYS-10, UC-SYS-11).
- **N7** raffinato con struttura del pannello di spiegabilità: 3 sezioni + riformulazione semplificata (da SCR-ST-10, UC-ST-06).

**Requisiti rimossi o rimandati:**

- Nessun requisito rimosso.
- **Decay temporale** confermato fuori scope v0.3 (come da v0.2 §13.9).
- **Doppia dimensione di padronanza per bilingui** confermato fuori scope v0.3 (come da v0.2 §13.10).

**Tracciabilità aggiunta:**

- Ogni requisito ora referenzia gli UC e le SCR corrispondenti.
- Matrice di tracciabilità completa in §14.

---

## 1. Sintesi esecutiva

**MAESTRO** è un sistema multi-agente che affianca ogni studente di Informatica lungo il suo percorso scolastico. Non si limita a misurare i risultati: a partire dal programma del corso e dal materiale didattico, genera per ogni studente un **percorso personalizzato di comprensione**, articolato in più modalità (testo, audio, gioco, dialogo), nella forma e nel linguaggio che funzionano meglio per *quel* ragazzo.

Il modello mentale di riferimento è l'esperienza concreta condotta sulla classe 5AI dell'I.T.E.T. Pantanelli-Monnet: data una verifica di PHP (Autenticazione e Sessioni), per ciascuno dei nove studenti è stato prodotto un rapporto di valutazione *e* un documento di ripasso personalizzato, con i loro errori specifici evidenziati e spiegati con analogie, tono leggero, codice giusto a fronte. MAESTRO generalizza questo schema, lo automatizza e lo rende continuativo su tutto l'arco dell'anno scolastico.

Al centro del sistema c'è la **mappa della conoscenza per studente × corso**: una rappresentazione viva, a stato semaforo a sei colori, della padronanza di ogni concetto del programma. Le lacune non sono solo segnalate: vengono **chiuse attraverso un ciclo formale** — rilevamento, approfondimento ad-hoc, mini-quiz di verifica, retention check nel tempo.

La v0.3 consolida i requisiti v0.2 con le evidenze emerse dalla progettazione dettagliata di **58 use case** (40 esterni + 18 di sistema), **42 schermate** (30 MVP + 12 V1), e dall'architettura del team di sviluppo a 23 agenti. I nuovi gruppi funzionali (F15 ciclo di vita dei contenuti, F16 notifiche, F17 setup corso) colmano le lacune emerse durante la progettazione delle interfacce e dei flussi operativi.

**Obiettivo primario:** spostare la valutazione da *strumento di giudizio* a *strumento di apprendimento*, con un ciclo continuo che chiude le lacune invece di limitarsi a contarle.

---

## 2. Vision e principi guida

### 2.1 Vision
Ogni studente di Informatica delle scuole superiori italiane ha diritto a un percorso di apprendimento che si adatti al *suo* modo di imparare, non viceversa. MAESTRO è il tutor che hanno gli studenti privilegiati, reso accessibile a chiunque, qualunque sia il punto di partenza.

### 2.2 Principi guida

1. **Personalizzazione, non standardizzazione.** Stesso curriculum, stesso obiettivo finale, percorsi diversi.
2. **Comprensione, non punteggio.** Il voto è un sottoprodotto, non l'obiettivo.
3. **Tono incoraggiante, mai punitivo.** L'errore è materia prima, non colpa.
4. **Lo studente sceglie il proprio canale.** Il sistema propone, lo studente decide.
5. **Le lacune si chiudono, non si conteggiano.** Ogni rosso ha diritto a un percorso esplicito per diventare verde.
6. **Privacy by design.** I dati dei minori sono trattati come dati sensibili da subito.
7. **Spiegabilità.** Lo studente (e la famiglia) può sempre sapere *perché* il sistema gli sta proponendo una certa cosa.
8. **Il docente resta al centro.** MAESTRO è un'estensione del docente, non un sostituto. Quando interviene direttamente (override), il sistema lo traccia con trasparenza.
9. **Profilo come adattamento, non come etichetta.** Il vettore learning style è un *profilo di adattamento dei contenuti*, non una classificazione rigida del tipo di apprendimento dello studente (cfr. nota LSS in §6 F3).

---

## 3. Esperienza di riferimento (caso 5AI)

Per ancorare i requisiti al concreto, sintetizzo cosa ha funzionato nell'esperimento di partenza:

- **Stessa verifica, nove report diversi.** Ogni studente ha ricevuto un rapporto specifico sui *suoi* errori, evidenziati visivamente sul *suo* codice.
- **Documenti di ripasso a triplice struttura** per ogni concetto: (1) cosa è successo nel tuo codice, (2) analogia quotidiana, (3) codice corretto, (4) la regola da ricordare.
- **Analogie personalizzate**: la pizzeria per spiegare i result handle, il braccialetto della discoteca per le sessioni, i barattoli del riso e della pasta per le chiavi sfalsate.
- **Tono leggero** anche su voti gravemente insufficienti, mai offensivo, sempre orientato al "ti aspetto al prossimo round".
- **Codice giallo evidenziato** invece di voto in rosso: l'attenzione visiva sull'errore, non sulla bocciatura.

MAESTRO replica e automatizza questo schema, lo espande a cinque canali (testo, podcast a due voci, visuale, gioco, dialogo) e lo chiude in un **ciclo formale**: ogni errore rilevato attiva un percorso di recupero, di cui si misura l'esito.

---

## 4. Attori e personas

| Attore | Descrizione | Bisogno primario | UC di riferimento |
|---|---|---|---|
| **Studente** (13-19 anni) | Frequenta corsi di Informatica. Profilo di apprendimento eterogeneo. | Capire i concetti che gli sfuggono nel modo che funziona per lui; chiudere le lacune con un percorso chiaro. | UC-ST-00..16, SCR-ST-01..14 |
| **Docente** | Insegna Informatica, prepara verifiche, valuta. | Strumento che lo libera dalla correzione massiva, gli mostra dove la classe arranca, gli permette di intervenire chirurgicamente. | UC-DOC-01..19, SCR-DOC-01..16 |
| **Famiglia** | Genitori/tutori legali dello studente minorenne. | Trasparenza, controllo sui dati del figlio, visione dei progressi. Consenso granulare. | UC-FAM-00..04, SCR-FAM-01..04 |
| **Coordinatore didattico** | Dirige il corso, integra il piano. | Dati aggregati di classe per orientare la didattica. | UC-COR-01, SCR-COR-01 |
| **Admin IT scuola** | IT della scuola. | Gestione utenti, integrazioni (SSO), conformità, ciclo di vita degli account. | UC-AS-01..08, SCR-AS-01..07 |

### Personas studente di riferimento

- **Marta, 16, "la visiva"**: prende appunti con mappe e colori, fa fatica con i testi lunghi, ricorda meglio se vede.
- **Riccardo, 17, "l'ascoltatore"**: studia mentre cammina, ascolta podcast, gli piacciono i dialoghi e le storie.
- **Davide, 16, "il pratico"**: capisce mentre fa, salta i preamboli, vuole subito un esempio funzionante.
- **Gabriele, 15, "il riflessivo"**: ha bisogno di tempo, rilegge, predilige la spiegazione passo-passo.
- **Stefano, 16, "il sociale"**: impara discutendo, vuole confrontarsi, gli piace il gioco di squadra.
- **Olena, 15, "la non-italofona"**: arrivata dall'Ucraina, parla russo e ucraino in famiglia, sta imparando l'italiano. Capisce i concetti tecnici se può vederli/sentirli anche in una lingua che padroneggia.
- **Francesca, 14, "la prima superiore"**: è all'inizio del biennio. Ha bisogno di una mappa della conoscenza che non la spaventi con un albero troppo dettagliato. La sua vista di default è macro.

Le cinque modalità (visiva, uditiva, cinestesica, riflessiva, sociale) sono i poli del modello di profilazione. Olena rappresenta l'asse trasversale del bilinguismo. Francesca rappresenta l'asse del **livello scolastico**, che determina la granularità della mappa.

---

## 5. Architettura concettuale

Sistema **multi-agente** orchestrato. Ogni agente è specializzato; un orchestrator coordina il flusso.

```
                    ┌─────────────────────────┐
                    │   ORCHESTRATOR (LLM)    │
                    └────────────┬────────────┘
                                 │
   ┌────────────────┬────────────┼────────────┬────────────────┐
   │                │            │            │                │
   ▼                ▼            ▼            ▼                ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│Curriculum│  │ Student  │  │Diagnostic│  │ Identity │  │Knowledge Map │
│Ingestion │  │ Profiler │  │  Agent   │  │& Consent │  │  Manager     │
│  Agent   │  │  Agent   │  │ (verif)  │  │ Manager  │  │ (stati,      │
│          │  │          │  │          │  │          │  │  ciclo,      │
│          │  │          │  │          │  │          │  │  heatmap)    │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
     │             │             │             │               │
     ▼             ▼             ▼             ▼               ▼
┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐
│Knowledge │ │ Learning   │ │Errors &  │ │ Anagrafe │ │ State store     │
│Graph     │ │ Profile    │ │Concepts  │ │ + Cons.  │ │ × studente      │
│(con      │ │ Vector     │ │ Dataset  │ │  ledger  │ │ × nodo          │
│livelli,  │ │            │ │          │ │          │ │ + cronologia    │
│granul.)  │ │            │ │          │ │          │ │ + audit override│
└──────────┘ └────────────┘ └──────────┘ └──────────┘ └─────────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │  CONTENT ORCHESTRATOR        │
                  └──────────────┬───────────────┘
        ┌────────────┬───────────┼────────────┬─────────────┐
        ▼            ▼           ▼            ▼             ▼
   ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
   │ Text    │ │ Podcast  │ │ Visual  │ │ Game     │ │ Dialog   │
   │ Agent   │ │ Agent    │ │ Agent   │ │ Agent    │ │ Agent    │
   │         │ │ (2 voci) │ │(colors/ │ │ (XP,quest│ │ (Q&A     │
   │         │ │          │ │ fonts)  │ │ ,badge)  │ │ chatbot) │
   └────┬────┘ └────┬─────┘ └────┬────┘ └────┬─────┘ └────┬─────┘
        │           │            │            │            │
        └───────────┴────────────┼────────────┴────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │  BILINGUAL COMPOSER          │
                  │  (lingua ufficiale corso +   │
                  │   lingua nativa studente,    │
                  │   se valorizzata in profilo) │
                  └──────────────┬───────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │  SAFEGUARDING AGENT          │
                  │  (moderazione, benessere,    │
                  │   adeguatezza per minori)    │
                  └──────────────┬───────────────┘
                                 ▼
                          [studente / docente]
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │  FEEDBACK LOOP AGENT         │
                  │  (aggiorna profilo, stato    │
                  │   nodi, KG, retention check) │
                  └──────────────────────────────┘
```

### Componenti chiave

- **Identity & Consent Manager**: gestisce anagrafica studente, consensi granulari della famiglia, iscrizioni ai corsi, ciclo di vita dell'account (creazione, attivazione, sospensione, oblio). Espone audit log GDPR-compliant.
- **Knowledge Map Manager (KMM)**: gestisce per ogni coppia (studente, nodo del KG) lo stato corrente, la cronologia delle transizioni, i retention check programmati, gli override docente. È il motore del ciclo di chiusura della lacuna.
- **Content Orchestrator**: coordina la generazione dei contenuti attraverso i 5 canali, rispettando priorità autoriale (lezione docente > manuale > fonti esterne), profilo learning style, e vincoli di bilinguismo.
- **Safeguarding Agent**: valida ogni output prima della consegna allo studente. Blocca contenuti inadatti, rileva pattern di disagio, filtra stereotipi.

### Stack tecnologico di riferimento (input per revalidation — T1.2)

- LLM frontier (Claude, GPT) per gli agent generativi
- TTS multi-voce (ElevenLabs, OpenAI TTS, Azure Neural Voices) per il podcast
- Vector DB (Pinecone/Weaviate) per il materiale didattico
- Knowledge graph (Neo4j) per la mappa concettuale del curriculum
- State store relazionale (PostgreSQL + tabelle di cronologia o TimescaleDB) per il KMM
- Frontend mobile-first (React Native o Flutter)
- Backend orchestrazione (LangGraph o framework agentico equivalente)
- Infrastruttura EU-only (cloud region EU)

> **Nota v0.3**: Ogni componente dello stack è soggetto a revalidation nel task T1.2 (Tech stack revalidation). I nomi di prodotto qui indicati sono riferimenti, non decisioni.

---

## 6. Requisiti funzionali

### F1 — Ingestione del programma di studio e modello del knowledge graph

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F1.1 | Il sistema importa il programma ufficiale del corso (es. linee guida MIUR per ITT articolazione Informatica) in formato strutturato. | UC-DOC-10 | SCR-DOC-11 | MVP |
| F1.2 | Il sistema costruisce un **knowledge graph** dei concetti: ogni concetto è un nodo, gli archi rappresentano prerequisiti ("per capire X serve Y"). Il grafo deve essere un DAG valido (nessun ciclo). | UC-DOC-10 | SCR-DOC-11 | MVP |
| F1.3 | Ogni concetto è classificato per livello di difficoltà (base, intermedio, avanzato) e per anno scolastico. | UC-DOC-10 | SCR-DOC-11 | MVP |
| F1.4 | Il programma può essere aggiornato dal docente con nuovi nodi/archi senza riavvio del sistema. L'aggiornamento è immediato e le mappe degli studenti riflettono le modifiche. | UC-DOC-10 | SCR-DOC-11 | MVP |
| F1.5 | Esempio per Informatica: nodi come "Variabile", "Tipo di dato", "Sessione PHP", "Query SQL", "Sanificazione input"… ognuno con prerequisiti espliciti. | — | — | MVP |
| F1.6 | Ogni corso è associato a un **livello scolastico**: *secondaria di primo grado*, *biennio secondaria di secondo grado*, *triennio secondaria di secondo grado*, *post-diploma/ITS*, *formazione professionale*. | UC-DOC-17 | SCR-DOC-03 | MVP |
| F1.7 | Ogni nodo del KG espone un attributo di **granularità**: *macro-nodo* (concetto strutturante) e *micro-nodo* (sotto-concetto fine). I micro-nodi sono **figli logici** di un macro-nodo. La padronanza di un macro è derivata dalla padronanza dei suoi micro (F11.11). | UC-ST-13, UC-SYS-14 | SCR-ST-04 | MVP |
| F1.8 | La **granularità di default** dipende dal livello scolastico: biennio → macro per studenti; triennio → scelta studente (macro/micro); docente sempre micro. | UC-DOC-17, UC-ST-07, UC-SYS-15 | SCR-ST-04, SCR-DOC-03 | MVP |
| F1.9 | Il docente può **personalizzare la granularità** in deroga al default (es. docente di biennio mostra anche micro). | UC-DOC-17 | SCR-DOC-03 | MVP |
| F1.10 | Esempio: macro-nodo *Concetto di algoritmo*; micro-nodi: *Definizione*, *Proprietà: finitezza*, *Proprietà: determinatezza*, *Rappresentazione: pseudocodice*, *Rappresentazione: diagramma di flusso*. | — | — | MVP |

### F2 — Caricamento delle lezioni e indicizzazione del materiale didattico

**F2-A. Lezioni del docente (fonte primaria autoritativa)**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F2.1 | Il docente carica lezioni in formati diversi: video, audio, slide annotate, dispense, screencast. Formati: PDF, DOCX, PPTX, MP3, MP4, WAV. Dimensione max: 500MB (audio/video), 50MB (documenti). | UC-DOC-01 | SCR-DOC-04 | MVP |
| F2.2 | Per audio e video: **trascrizione automatica** con timestamp e identificazione del parlante. | UC-DOC-02 | SCR-DOC-05 | MVP |
| F2.3 | Trascrizione editabile dal docente: correzione di termini tecnici, nomi propri, formule, codice. Player sincronizzato con trascrizione (click su frase → salta al timestamp). | UC-DOC-02 | SCR-DOC-05 | MVP |
| F2.4 | Ogni lezione è collegata ai nodi KG tramite **mapping concettuale automatico assistito, validato dal docente**: "in questa lezione il concetto X è trattato dal minuto 12:30 al 28:15". Vista split: concetti estratti a sinistra, KG a destra. | UC-DOC-03 | SCR-DOC-06 | MVP |
| F2.5 | Le lezioni del docente godono di **priorità autoriale**: attinge prima alla lezione del docente, poi al manuale, poi a fonti esterne. | UC-SYS-01, UC-SYS-10 | — | MVP |
| F2.6 | Le lezioni alimentano direttamente il percorso: ogni nuova lezione aggiorna automaticamente quest, esercizi e materiali di ripasso. | — | — | MVP |
| F2.7 | Upload in batch (cartella di un intero modulo) o lezione per lezione. | UC-DOC-01 | SCR-DOC-04 | MVP |
| F2.8 | Il docente annota la lezione con metadati: livello di difficoltà, granularità, prerequisiti, esercizi suggeriti. | UC-DOC-01 | SCR-DOC-04 | MVP |

**F2-B. Materiali didattici complementari**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F2.9 | Caricamento di libro di testo, dispense terze, esercizi, codice di esempio, articoli, link esterni. | — | — | MVP |
| F2.10 | Il sistema indicizza tutti i materiali in un vector store e li collega ai nodi del KG. | — | — | MVP |
| F2.11 | Per ogni concetto: almeno **tre fonti diverse** (lezione + manuale + esercizio). | — | — | MVP |
| F2.12 | Il sistema rileva le **lacune di copertura**: concetti senza materiale, segnalati al docente. | UC-DOC-11 | SCR-DOC-15 | V1 |
| F2.13 | Rispetto del copyright: uso interno, fair use, proprietà intellettuale del docente preservata. | — | — | MVP |

### F3 — Profilazione learning style

> **Nota LSS (v0.3)**: Il concetto di "learning styles" come tratto fisso è contestato nella letteratura (Pashler et al. 2009, Newton 2015). In MAESTRO, F3 è da intendersi come **profilo di adattamento dei contenuti**: un vettore continuo che influenza la presentazione, non una classificazione del tipo di studente. Questa riformulazione è richiesta dal task T1.3 (Pedagogical model validation).

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F3.1 | Onboarding leggero (5-10 minuti): quiz interattivo che presenta lo stesso concetto in 4 modalità diverse (testo, audio, immagine, esercizio pratico) per 3-5 concetti. Il sistema registra quale modalità viene aperta, il tempo di permanenza, quale viene completata. | UC-ST-01 | SCR-ST-02 | MVP |
| F3.2 | Profilo come **vettore continuo a 5 dimensioni** (visivo, uditivo, cinestesico, riflessivo, sociale), non come etichetta rigida. Rappresentato visivamente come radar chart a 5 assi con valori percentuali. | UC-ST-01 | SCR-ST-02, SCR-ST-09 | MVP |
| F3.3 | Il profilo evolve nel tempo in base al comportamento osservato (cosa lo studente apre, cosa completa, dove abbandona). | UC-SYS-03 | — | V1 |
| F3.4 | Lo studente può forzare le sue preferenze ("voglio solo podcast questo mese"). Forzatura via sezione "Canale preferito" nel profilo. | UC-ST-07 | SCR-ST-09 | MVP |
| F3.5 | Il profilo include preferenze accessorie: tono (confidenziale/neutro/formale), lunghezza (sintesi 2-3 concetti / approfondimento 6-8 concetti). | UC-ST-01, UC-ST-07 | SCR-ST-02, SCR-ST-09 | MVP |
| F3.6 | Il profilo è trasparente: lo studente vede il proprio radar chart, la descrizione testuale, e può modificare ogni parametro. | UC-ST-07 | SCR-ST-09 | MVP |
| F3.7 | **[NUOVO v0.3]** Se il consenso (a) è negato dalla famiglia, il quiz di profilazione è semplificato (nessun tracciamento comportamentale); il profilo è impostato su valori neutri e i contenuti sono uniformi. | UC-ST-01 ext. | SCR-ST-02 | MVP |

### F4 — Diagnostica formativa post-verifica

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F4.1 | Il docente carica una verifica corretta: definisce titolo, data, tipo (scritta/orale/pratica), struttura domande con testo, concetti associati dal KG, e peso in punti. Supporta import da file (PDF/DOCX) con estrazione automatica domande. | UC-DOC-04 | SCR-DOC-07 | MVP |
| F4.2 | Il sistema mappa ogni errore di ogni studente al **micro-nodo concettuale** corrispondente nel KG. Ogni mapping ha un punteggio di confidenza: >=80% proposto automatico; <80% segnalato "incerto" al docente. | UC-DOC-04, UC-SYS-02 | SCR-DOC-07 | MVP |
| F4.3 | Ogni errore mappato attiva una transizione di stato: il micro-nodo passa a `lacuna` (F11.4). | UC-SYS-09 | — | MVP |
| F4.4 | Output docente: rapporto di valutazione con codice evidenziato, tabella per task, lista transizioni di stato, riepilogo media classe e distribuzione voti, concetti più problematici, anteprima delle transizioni prima della conferma. | UC-DOC-04 | SCR-DOC-07 | MVP |
| F4.5 | Output studente: documento di ripasso personalizzato (F5) + aggiornamento immediato della mappa della conoscenza. | UC-DOC-04 | SCR-ST-03, SCR-ST-08 | MVP |
| F4.6 | **[NUOVO v0.3]** Inserimento voti per studente: tabella inline editabile (studente × domanda), con validazione (0 ≤ punteggio ≤ peso), indicatore visivo per punteggi bassi (<60% arancione, <40% rosso), e possibilità di import voti da CSV. | UC-DOC-04 | SCR-DOC-07 | MVP |

### F5 — Generazione di documenti testuali personalizzati

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F5.1 | Per ogni gap concettuale: blocco con struttura **"Il tuo errore" → "Perché succede" → "Come si fa giusto" → "Ricordati"**. Il blocco "errore" ha bordo giallo con etichetta "ERRATO"; il blocco "giusto" ha bordo verde con etichetta "CORRETTO". | UC-ST-02, UC-SYS-01 | SCR-ST-08 | MVP |
| F5.2 | Le analogie sono **selezionate dal profilo**: sportive, videoludiche, culinarie, musicali, ecc. Devono essere diversificate (non sempre lo stesso tipo). | UC-SYS-01 | SCR-ST-08 | MVP |
| F5.3 | Il codice errato è mostrato evidenziato in giallo accanto al codice corretto in verde. Etichette testuali "ERRATO"/"CORRETTO" per accessibilità (non solo colore). | UC-ST-02 | SCR-ST-08 | MVP |
| F5.4 | Lunghezza variabile in base al profilo: sintesi (2-3 concetti) o approfondimento (6-8). | UC-ST-02, UC-SYS-01 | SCR-ST-08 | MVP |
| F5.5 | Tono adattivo: confidenziale ("tu", frasi brevi), neutro ("tu", tono calmo), formale ("lei", frasi articolate). | UC-ST-02, UC-SYS-01 | — | MVP |
| F5.6 | **[NUOVO v0.3]** Layout bilingue: se bilinguismo attivo, ogni blocco è diviso in due colonne (sinistra = lingua ufficiale, destra = lingua nativa). Termini tecnici in entrambe le lingue con originale in parentesi. | UC-SYS-05 | SCR-ST-08 | MVP |
| F5.7 | **[NUOVO v0.3]** Documento modificato dal docente: badge visibile "Rivisto dal Prof." in alto. | UC-DOC-08 | SCR-ST-08 | MVP |

### F6 — Generazione di podcast a due voci

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F6.1 | Per ogni concetto-target: audio 4-8 minuti con due AI speaker ("esperto" e "curioso") con tono colloquiale e analogie. | UC-ST-03 | SCR-ST-11 | V1 |
| F6.2 | Lo studente sceglie le **voci** tra una libreria. | UC-ST-03 | SCR-ST-11 | V1 |
| F6.3 | Lo speaker "curioso" pone le domande probabili; l'"esperto" risponde con analogie. | UC-ST-03 | — | V1 |
| F6.4 | L'audio si ascolta in app o scarica in MP3. | UC-ST-03 | SCR-ST-11 | V1 |
| F6.5 | Trascrizione sincronizzata sempre disponibile (accessibilità). | UC-ST-03 | SCR-ST-11 | V1 |
| F6.6 | Variante "monologo" per chi preferisce una sola voce. | — | — | V1 |
| F6.7 | Variante "dibattito": voci in disaccordo deliberato, studente giudica chi ha ragione. | — | — | V2 |
| F6.8 | Velocità di riproduzione regolabile (0.75x – 2x). | UC-ST-03 | SCR-ST-11 | V1 |

### F7 — Layer di gamification

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F7.1 | **Skill tree**: il KG è visualizzabile come albero di abilità; ogni nodo sbloccato è una conquista. | UC-ST-04 | SCR-ST-12 | V1 |
| F7.2 | **XP e livelli**: ogni esercizio completato dà XP; gli XP fanno salire di livello. | UC-ST-04 | SCR-ST-12 | V1 |
| F7.3 | **Badge tematici**: "Risolutore di SQL", "Domatore di sessioni", "Cacciatore di bug", "Chiudi-lacune". | UC-ST-04 | SCR-DOC-02, SCR-ST-12 | V1 |
| F7.4 | **Streak**: giorni consecutivi di attività. Notifica gentile, mai pressante. Possibilità di "freeze". | UC-ST-04 | SCR-ST-12 | V1 |
| F7.5 | **Quest giornaliere e settimanali**: obiettivi mirati alle lacune aperte (`lacuna` o `in_recupero`). | UC-ST-04 | SCR-ST-03 | V1 |
| F7.6 | **Modalità cooperativa di classe**: quest da risolvere in squadra. | UC-ST-04 | — | V2 |
| F7.7 | **Anti-pattern espliciti**: NESSUNA classifica pubblica individuale, NESSUN paragone tra studenti, NESSUN meccanismo addittivo (notifiche martellanti, FOMO, ricompense variabili). | UC-ST-04 | — | V1 |
| F7.8 | Lo studente può **disattivare la gamification** senza perdere il progresso didattico. Toggle nel profilo con spiegazione: "XP, badge e streak scompaiono. Il tuo progresso resta intatto." | UC-ST-10 | SCR-ST-09 | V1 |

### F8 — Adattamento del linguaggio personale

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F8.1 | Tre registri base: **confidenziale** (tu, frasi brevi, qualche battuta), **neutro** (tu, frasi medie), **formale** (lei, frasi articolate). Selezionabile dall'utente con segmented control. | UC-ST-07 | SCR-ST-09, SCR-ST-02 | MVP |
| F8.2 | Adattamento di livello lessicale: se lo studente è in difficoltà, vocabolario semplificato; se avanzato, terminologia tecnica. | — | — | MVP |
| F8.3 | Inserimento di **riferimenti culturali** legati ai suoi interessi. | — | — | MVP |
| F8.4 | Multilinguismo: italiano default; supporto multilingua per studenti non italofoni (cfr. F13). | UC-ST-08 | — | MVP |
| F8.5 | Eliminazione automatica di gergo o riferimenti non age-appropriate. | UC-SYS-04 | — | MVP |

### F9 — Accessibilità visiva e design system

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F9.1 | Font selezionabili: Inter (default), **OpenDyslexic**, **Atkinson Hyperlegible**. Dropdown nel componente selettore accessibilità. | UC-ST-07 | SCR-ST-09, comp. accessibilità | MVP |
| F9.2 | Modalità ad alto contrasto (toggle on/off). | UC-ST-07 | SCR-ST-09, comp. accessibilità | MVP |
| F9.3 | Codifica cromatica per gli stati della mappa con colori hex di riferimento: grigio (#9E9E9E), bianco (#FFFFFF), rosso (#E53935), arancione (#FB8C00), giallo (#FDD835), verde (#43A047). Mai dipendere SOLO dal colore: sempre colore + icona + testo. | UC-ST-13 | SCR-ST-04, principi design | MVP |
| F9.4 | Dimensione testo regolabile 12-24pt con slider e anteprima live. | UC-ST-07 | SCR-ST-09, comp. accessibilità | MVP |
| F9.5 | Modalità chiara, scura, e seppia (radio selector). | UC-ST-07 | SCR-ST-09, comp. accessibilità | MVP |
| F9.6 | Conformità WCAG 2.1 AA su tutti i materiali generati. | — | tutti | MVP |
| F9.7 | **[NUOVO v0.3]** Animazioni ridotte: toggle on/off nel selettore accessibilità. | — | comp. accessibilità | MVP |
| F9.8 | **[NUOVO v0.3]** Le preferenze di accessibilità sono salvate nel profilo utente e persistono tra sessioni. | UC-ST-07 | SCR-ST-09 | MVP |

### F10 — Articolazione multimodale dei contenuti

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F10.1 | Per ogni concetto: almeno **quattro articolazioni**: testo, audio (podcast), visuale (diagramma/animazione), pratica (esercizio guidato). | — | — | V2 |
| F10.2 | Lo studente passa da un'articolazione all'altra mantenendo il contesto. | UC-ST-12 | SCR-ST-08 | V1 |
| F10.3 | Il sistema propone l'articolazione predominante in base al profilo, ma le mostra tutte. | — | — | MVP |
| F10.4 | Articolazione "metacognitiva": lo studente *spiega a voce* il concetto al sistema (rubber duck), il sistema verifica. | UC-ST-09 | — | V2 |

### F11 — Mappa della conoscenza e ciclo di chiusura delle lacune

#### F11-A. Visualizzazione della mappa della conoscenza

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F11.1 | Per ogni studente × corso: **mappa della conoscenza** come grafo navigabile o albero. Ogni nodo colorato secondo stato. Navigazione: zoom (pinch-to-zoom mobile, scroll desktop), pan (drag), tap su nodo apre dettaglio. | UC-ST-13 | SCR-ST-04 | MVP |
| F11.2 | Granularità adattiva: biennio → solo macro; triennio → toggle macro/micro (segmented control). | UC-ST-13, UC-SYS-15 | SCR-ST-04 | MVP |
| F11.3 | Macchina a stati a **sei stati**: `non_introdotto` (grigio), `introdotto` (bianco), `lacuna` (rosso), `in_recupero` (arancione), `da_consolidare` (giallo), `consolidato` (verde). | UC-ST-13 | SCR-ST-04, SCR-ST-05 | MVP |

#### F11-B. Eventi e transizioni di stato

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F11.4 | Transizioni canoniche: mapping errore → `lacuna`; avvio recupero → `in_recupero`; quiz >=80% → `da_consolidare`; tutti retention check positivi → `consolidato`; errore su nodo `da_consolidare`/`consolidato` → regressione a `lacuna`. Transizioni non standard (es. `lacuna` → `consolidato`) richiedono motivazione dettagliata. | UC-SYS-09, UC-SYS-12, UC-ST-16 | SCR-DOC-10 | MVP |
| F11.5 | Ogni transizione registrata con: timestamp, stato precedente, stato successivo, causa (evento), evidenza (riferimento a verifica/quiz/retention check). Visualizzabile come timeline verticale con icone per tipo. | UC-SYS-12 | SCR-ST-05, SCR-DOC-09 | MVP |

#### F11-C. Ciclo di chiusura della lacuna

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F11.6 | **Avvio dell'approfondimento**: lacuna genera "missione di recupero" nella dashboard. Lo studente la avvia dichiarativamente. Stato → `in_recupero`. Presentazione come lista di step con barra di avanzamento. | UC-ST-15 | SCR-ST-03, SCR-ST-06 | MVP |
| F11.7 | **Percorso ad-hoc**: documento testuale + segmento lezione docente + eventuale esercizio. Articolazione scelta in base al profilo. Secondo tentativo: articolazione variata. | UC-SYS-10 | SCR-ST-06 | MVP |
| F11.8 | **Mini-quiz di chiusura**: 3-5 domande mirate al micro-nodo. Fonte: banca del docente (priorità 1) o banca generata (priorità 2). Quiz in lingua ufficiale del corso. | UC-ST-16, UC-SYS-11 | SCR-ST-07 | MVP |
| F11.9 | **Esito quiz**: >=80% → `da_consolidare` + retention check; 50-79% → `in_recupero` + percorso variato; <50% → `lacuna` + alert docente. Feedback per ogni domanda sempre visibile (risposta data, risposta corretta, spiegazione). Tono sempre incoraggiante, anche per <50% (MAI sfondo rosso per risultato negativo, usare arancione). | UC-ST-16 | SCR-ST-07 | MVP |
| F11.10 | **Retention check programmati**: dopo `da_consolidare`, tre check a **D+3, D+7, D+21**. MVP: almeno D+7. Ogni retention check: mini-quiz adattivo 3-5 domande. Tre positivi → `consolidato`. Un negativo → regressione a `lacuna`. | UC-SYS-13 | — | MVP (D+7), V1 (D+3, D+21) |

#### F11-D. Aggregazione, override, heatmap

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F11.11 | **Aggregazione macro**: stato macro = **stato peggiore** dei micro figli (regola conservativa). Macro è `consolidato` solo quando tutti i micro sono `consolidato`. | UC-SYS-14 | SCR-ST-04 | MVP |
| F11.12 | **Override docente**: forzatura manuale dello stato. Audit log obbligatorio con: identità docente, timestamp, stato precedente, stato forzato, motivazione testuale (min 20 caratteri), evidenze facoltative (upload file). Dialog modale con conferma. Override in massa su più studenti (V1). Non concorrono ai KPI di consolidamento autonomo. | UC-DOC-16 | SCR-DOC-10, SCR-DOC-14 | V1 (singolo), V1 (massa) |
| F11.13 | **Heatmap temporale studente**: griglia (nodo × tempo) → stato. Visualizzazione evoluzione padronanza. | UC-ST-14 | SCR-ST-13 | V1 |
| F11.14 | **Heatmap di classe**: griglia (studente × macro-concetto) → stato con colore + icona. Hover mostra dettaglio. Click apre mappa studente. Vista alternativa come tabella. Riga riepilogativa con % consolidato per argomento. | UC-DOC-06, UC-DOC-15 | SCR-DOC-08 | MVP (statica), V1 (temporale) |

#### F11-E. Alert, retention, output famiglia

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F11.15 | **Alert lacune persistenti**: lacuna >14 giorni → alert docente. Tre regressioni entro 30 giorni → suggerimento cambio canale. | UC-DOC-19 | SCR-DOC-16 | V1 |
| F11.16 | **Report mensile famiglia**: 1 pagina, non tecnico, incoraggiante. Contenuto: macro-aree consolidate, lacune chiuse/aperte (riassunto narrativo), attività svolte, frequenza d'uso, suggerimenti. Nessun confronto. Disponibile via web e PDF. Solo se consenso (c). | UC-FAM-02, UC-SYS-16 | SCR-FAM-02 | V1 |

> **Nota fuori scope v0.3**: decay temporale rinviato a V2. Il modello dati prevede `last_seen` e `last_reinforced`.

### F12 — Dashboard docente

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F12.1 | Vista classe: heatmap (F11.14) con selettore classe, filtri per stato e argomento. | UC-DOC-06 | SCR-DOC-08 | MVP |
| F12.2 | Vista studente: mappa completa con cronologia + privacy graduata (il docente vede stati e esiti quiz, NON dati comportamentali fini). | UC-DOC-14 | SCR-DOC-09 | MVP |
| F12.3 | Generazione assistita di verifiche bilanciate sul programma e sui gap di classe. | UC-DOC-05 | — | V2 |
| F12.4 | Suggerimenti di tagliando didattico: "il 60% della classe ha lacune su X, consigliata lezione dedicata". | UC-DOC-06 | SCR-DOC-02 | V1 |
| F12.5 | Il docente può sempre **modificare o cancellare** un contenuto generato. La parola finale è sua. | UC-DOC-08 | SCR-DOC-13 | MVP |
| F12.6 | Pannello override: vista riepilogativa di tutti gli override effettuati. | UC-DOC-18 | SCR-DOC-14 | V1 |
| F12.7 | **[NUOVO v0.3]** Home dashboard docente: card panoramica classe (distribuzione stati con barra segmentata), card alert lacune (lista studenti in lacuna con anzianità), card attività recenti (feed cronologico), card suggerimenti sistema. Sidebar con navigazione permanente. | — | SCR-DOC-02 | MVP |

### F13 — Lingua ufficiale del corso e bilinguismo

**F13-A. Lingua ufficiale del corso**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F13.1 | Ogni corso ha **una lingua ufficiale** definita dal docente in fase di setup (default: italiano). | UC-DOC-09 | SCR-DOC-03 | MVP |
| F13.2 | La lingua ufficiale è quella di: materiali, verifiche, voti, comunicazioni ufficiali, **mini-quiz di chiusura**. | UC-SYS-11 | — | MVP |
| F13.3 | La lingua ufficiale può variare per corso (es. CLIL in inglese). | UC-DOC-09 | — | MVP |
| F13.4 | Tutte le generazioni AI avvengono nella lingua ufficiale, salvo F13-B. | UC-SYS-01 | — | MVP |

**F13-B. Lingua nativa parallela**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F13.5 | Campo **lingua nativa** nel profilo (opzionale). Richiede consenso esplicito (b) della famiglia. | UC-ST-08, UC-FAM-00 | SCR-ST-09, SCR-FAM-01 | MVP |
| F13.6 | Libreria lingue supportate MVP: **ucraino, arabo**. V1: +russo, albanese, rumeno, cinese mandarino. V2: full 12 lingue. | UC-ST-08 | — | MVP |
| F13.7 | Con lingua nativa valorizzata: contenuti in **doppia lingua, sempre in parallelo**. | UC-SYS-05 | SCR-ST-08 | MVP |
| F13.8 | Il bilinguismo **non sostituisce mai** la lingua ufficiale. | — | — | MVP |
| F13.9 | Lo studente può **disattivare/riattivare** il bilinguismo. Toggle nel profilo. | UC-ST-08 | SCR-ST-09 | MVP |

**F13-C. Formati per canale**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F13.10 | **Testo**: layout a due colonne (sinistra = ufficiale, destra = nativa). Termini tecnici in entrambe le lingue. | UC-SYS-05 | SCR-ST-08 | MVP |
| F13.11 | **Podcast**: variante cross-language (una voce per lingua) o due tracce separate. | UC-ST-03 | — | V1 |
| F13.12 | **Gamification**: quest e badge con descrizione bilingue. Mini-glossario tecnico bilingue. | UC-ST-04 | — | V1 |
| F13.13 | **Chatbot**: studente scrive in entrambe le lingue; sistema risponde in entrambe. | — | — | V2 |
| F13.14 | **Diagrammi**: etichette in doppia lingua. Sottotitoli nei video. | — | — | V1 |

**F13-D. Localizzazione culturale**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F13.15 | Analogie localizzate sulla cultura d'origine quando appropriato. Sempre anche riferimento al contesto italiano. | UC-SYS-01 | — | MVP |
| F13.16 | Vietato ricorso a stereotipi nazionali/regionali. Localizzazioni validate da revisori madrelingua. | — | — | MVP |

**F13-E. Qualità della traduzione**

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F13.17 | Revisione madrelingua almeno una volta per anno scolastico, con campionamento. | — | — | V1 |
| F13.18 | Glossario tecnico controllato per ogni lingua. | UC-SYS-05 | — | MVP |
| F13.19 | Verifiche e mini-quiz restano nella lingua ufficiale. "Lettura assistita" in lingua nativa solo durante lo studio, mai durante valutazione formale. | UC-ST-16, UC-SYS-11 | SCR-ST-07 | MVP |
| F13.20 | Rilevamento lettura squilibrata (solo colonna nativa): suggerimento esercizi di transizione. | UC-SYS-08 | — | V1 |
| F13.21 | Lingua nativa = dato sensibile (Art. 9 GDPR). Mai esposta nelle dashboard di classe. | UC-FAM-00 | SCR-FAM-01 | MVP |

### F14 — Anagrafica, consenso e iscrizione

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F14.1 | Ciclo di vita: creazione → consenso → iscrizione → attivazione → utilizzo → aggiornamenti → sospensione → cancellazione. | UC-ST-00, UC-AS-05 | SCR-ST-01, SCR-AS-03 | MVP |
| F14.2 | **Creazione**: MVP manuale (form IT). V1: import CSV con validazione anteprima (righe valide/warning/errori). V2: sincronizzazione registro elettronico. Ogni studente ha ID interno univoco separato dall'identità sul registro. | UC-AS-05, UC-AS-04 | SCR-AS-03, SCR-AS-07 | MVP |
| F14.3 | **Consenso granulare** (5 categorie): (a) profilazione, (b) lingua nativa Art. 9, (c) comunicazioni famiglia, (d) storico cross-anno, (e) ricerca anonima. Ogni card mostra: titolo, spiegazione in linguaggio chiaro, cosa si raccoglie, base giuridica, toggle on/off, conseguenza se negato. | UC-FAM-00 | SCR-FAM-01, SCR-FAM-04 | MVP |
| F14.4 | MVP: consenso **amministrato** (modulo cartaceo). V1: **self-service** via link/QR da email con SPID o codice monouso. | UC-FAM-00 | SCR-FAM-01 | MVP |
| F14.5 | **Iscrizione**: separazione anagrafica/iscrizione. MVP: 1 corso per studente. V2: più corsi. Modello dati 1:N fin dall'MVP. Inizializzazione mappa: tutti i nodi a `non_introdotto`. | UC-DOC-12 | SCR-DOC-12 | MVP |
| F14.6 | **Prima attivazione**: credenziali una tantum o SSO; accettazione termini in linguaggio per minori; conferma presa visione consenso; redirect a onboarding. | UC-ST-00 | SCR-ST-01 | MVP |
| F14.7 | **Aggiornamenti**: passaggio di classe, cambio scuola, cambio dati. Cronologia preservata. | UC-AS-06 | — | V1 |
| F14.8 | **Sospensione**: preserva dati per N giorni configurabili (default 90). Nessuna generazione durante sospensione. Ripristino dallo stato precedente. | UC-AS-07 | — | V1 |
| F14.9 | **Cancellazione/oblio**: sempre accolta (Art. 17 GDPR). Cancellazione atomica di tutti i dati identificabili. Audit log della cancellazione preservato con dati pseudonimizzati (nome → hash). Dati anonimi aggregati preservati solo se consenso (e). Certificato di cancellazione generato (PDF con data, hash, elenco dati cancellati/mantenuti). Max 30 giorni. | UC-AS-08, UC-FAM-03, UC-ST-11 | SCR-AS-05, SCR-FAM-03, SCR-ST-14 | MVP |
| F14.10 | **Audit log**: immutabile, append-only. Ogni operazione registrata con: identità operatore, timestamp, dato precedente, dato nuovo. Export CSV/JSON. Retention: da policy DPIA. | UC-AS-03 | SCR-AS-04 | MVP |

### F15 — Ciclo di vita del contenuto generato [NUOVO v0.3]

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F15.1 | Il docente visualizza e gestisce tutti i contenuti generati per la propria classe: documenti, missioni, quiz, podcast. Filtrabile per tipo, concetto, studente, stato. | UC-DOC-08 | SCR-DOC-13 | V1 |
| F15.2 | Il docente può visualizzare l'anteprima completa di ogni contenuto in un pannello laterale. | UC-DOC-08 | SCR-DOC-13 | V1 |
| F15.3 | Il docente può **rigenerare** un contenuto: il precedente viene archiviato, il nuovo lo sostituisce. Dialog di conferma. | UC-DOC-08 | SCR-DOC-13 | V1 |
| F15.4 | Il docente può **archiviare** un contenuto: non più visibile allo studente. | UC-DOC-08 | SCR-DOC-13 | V1 |
| F15.5 | Ogni operazione su un contenuto è registrata in audit log. | UC-DOC-08 | — | MVP |

### F16 — Notifiche e alert [NUOVO v0.3]

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F16.1 | Centro notifiche docente: lista ordinata per data, con icona tipo (alert lacuna, verifica, upload, override, consolidamento), testo descrittivo, stato letta/non letta, azione rapida. | UC-DOC-19 | SCR-DOC-16 | MVP |
| F16.2 | Configurazione notifiche docente: soglia alert lacuna (default 7 giorni), soglia missione non iniziata (default 3 giorni), report settimanale (toggle + giorno), canale (in-app, email). | UC-DOC-19 | SCR-DOC-16 | MVP |
| F16.3 | Notifiche studente: badge su icona nella home dashboard con conteggio. Notifiche per: nuove missioni, retention check disponibili, contenuti nuovi. | — | SCR-ST-03 | MVP |
| F16.4 | Notifiche famiglia: email per report mensile, conferma consenso, richiesta oblio. Solo se consenso (c) per le comunicazioni periodiche. | UC-FAM-02, UC-FAM-00 | SCR-FAM-02 | V1 |

### F17 — Setup corso e onboarding docente [NUOVO v0.3]

| ID | Requisito | UC | SCR | Priorità |
|---|---|---|---|---|
| F17.1 | Wizard guidato in 3 step: (1) Info corso (nome, classe, anno, materia, livello scolastico, lingua ufficiale), (2) Knowledge graph iniziale (modello standard / upload programma / da zero), (3) Iscrizione studenti (import CSV / manuale / da registro V1). | UC-DOC-17, UC-DOC-09, UC-DOC-12 | SCR-DOC-03 | MVP |
| F17.2 | Anteprima KG in sola lettura nello step 2 (se opzione modello standard). | — | SCR-DOC-03 | MVP |
| F17.3 | Lo step 3 invia automaticamente le richieste di consenso alle famiglie. Il corso resta "in preparazione" fino a >=1 studente attivo. | UC-DOC-12 | SCR-DOC-03 | MVP |

---

## 7. Requisiti non funzionali

### N1 — Privacy e protezione dei minori

- Conformità **GDPR**, base giuridica chiara per minori (Art. 8): consenso genitoriale per <14, consenso assistito 14-18.
- Dati personali in chiaro **mai inviati agli LLM esterni**: pseudonimizzazione obbligatoria nei prompt.
- **Diritto all'oblio totale** (F14.9): eliminazione completa, cancellazione atomica, certificato di cancellazione.
- **[NUOVO v0.3]** Post-cancellazione: audit log entries pseudonimizzate (nome → hash), non cancellate.
- Residenza dei dati: server UE.
- Retention policies esplicite per ogni categoria di dato.
- Audit log di tutte le operazioni (F14.10) e degli override (F11.12).
- Conformità con il **Garante Privacy** italiano e linee guida MIUR su IA a scuola.
- Lingua nativa come dato sensibile (Art. 9): acquisizione solo con consenso esplicito (b), mai esposta nelle dashboard di classe.

### N2 — Sicurezza

- Autenticazione SSO con registro elettronico/SSO scolastico (SAML 2.0 o OpenID Connect). Configurazione: IdP URL, Client ID/Secret, Certificate, mapping attributi.
- **[NUOVO v0.3]** MFA obbligatorio per ruolo admin (TOTP o WebAuthn).
- Crittografia end-to-end dei materiali sensibili.
- Audit log di ogni accesso a dati di un minore.
- Penetration test annuale.
- Disaster recovery RPO ≤ 24h, RTO ≤ 4h.

### N3 — Etica e benessere

- **Safeguarding Agent** valida ogni output prima della consegna:
  - Nessun linguaggio offensivo, anche in modalità confidenziale.
  - Nessun confronto con compagni.
  - Rilevamento pattern di disagio → alert docente + percorso di supporto.
- Mai sostituire un professionista: disagio psicologico → aggancio referente scolastico.
- Tono SEMPRE incoraggiante, anche per insufficienza grave e lacuna ripetuta.
- Nessun nudging manipolativo: niente dark pattern, FOMO, scarcity.
- Il rosso è "una porta aperta, non un marchio": sempre accompagnato dalla missione di recupero. Mai sfondo rosso per risultati negativi dei quiz (usare arancione).
- Nessun confronto tra studenti in nessuna schermata student-facing.

### N4 — Performance

| Operazione | Latenza target | UC di riferimento |
|---|---|---|
| Documento di ripasso completo (testo + eventuale audio) | ≤ 60 secondi | UC-SYS-01 |
| Percorso di approfondimento personalizzato | ≤ 30 secondi | UC-SYS-10 |
| Mini-quiz di chiusura (generazione) | ≤ 15 secondi | UC-SYS-11 |
| Risposta in chat agente di tutoring | ≤ 3 secondi P95 | — |
| Disponibilità in orario scolastico (8:00-16:00 feriali) | 99.5% | — |

### N5 — Accessibilità

- Conformità WCAG 2.1 AA.
- Supporto screen reader (NVDA, JAWS, VoiceOver). ARIA labels su tutti gli elementi, live regions per aggiornamenti dinamici.
- Sottotitoli e trascrizioni per ogni contenuto audio.
- Navigazione tastiera completa: tutti gli elementi interattivi raggiungibili con Tab. Mappa della conoscenza esplorabile con Tab + Invio + frecce.
- Test con utenti reali con disabilità cognitive (BES, DSA) prima del rilascio.
- **[NUOVO v0.3]** Focus trap nei dialog modali (Tab rimane nel pannello fino a chiusura, Esc per chiudere).

### N6 — Inclusività linguistica e culturale

- Italiano standard come default; supporto multilingua per le seconde generazioni.
- Analogie e riferimenti **diversificati** e non stereotipati.
- Test di bias periodici sul linguaggio generato (gender, geografico Nord/Sud, socio-economico).

### N7 — Trasparenza e spiegabilità

- **Pannello spiegabilità** su ogni contenuto generato (bottone "Perché questo?"): 3 sezioni — (1) concetti KG coinvolti con stato, (2) riassunto profilo learning style, (3) timeline transizioni recenti. Link "Spiegami più semplicemente" per riformulazione. Pannello come bottom sheet (mobile) o dialog (web).
- Il docente vede quali nodi KG il sistema usa per ogni decisione.
- **Audit trail completo**: chi ha generato cosa, quando, con quale prompt e modello; override con motivazione; operazioni anagrafica/consenso.
- Limiti del sistema dichiarati esplicitamente.

### N8 — Offline e sincronizzazione [NUOVO v0.3]

- L'app studente mobile deve supportare una modalità offline limitata: i contenuti già scaricati (documenti di ripasso, quiz completati) restano accessibili.
- Indicatore visivo di stato connessione: banner "Sei offline — i contenuti scaricati sono disponibili".
- Sincronizzazione al ripristino della connessione: icona rotante durante sync, checkmark al completamento.
- Coda azioni: contatore "N azioni in attesa di sincronizzazione".

### N9 — Internazionalizzazione UI [NUOVO v0.3]

- L'interfaccia utente (non i contenuti didattici) è disponibile in: Italiano (default), Ucraino, Arabo.
- Selettore lingua presente in tutte le schermate (footer o header).
- Distinto dal bilinguismo didattico (F13): la lingua UI è la lingua dell'interfaccia; il bilinguismo è la lingua dei contenuti generati.

---

## 8. KPI e misurazione

### 8.1 KPI di adozione
- % studenti che usano MAESTRO almeno 2 volte a settimana
- Minuti medi/settimana per studente
- % docenti che generano almeno 1 verifica al mese tramite la dashboard

### 8.2 KPI di apprendimento
- Δ punteggio tra verifica N e verifica N+1 nei concetti specificamente ripassati
- % di concetti consolidati dopo 1 mese (spaced repetition retention)
- Riduzione del gap tra studenti più forti e più deboli della classe (varianza intra-classe)

### 8.3 KPI di benessere
- Net Promoter Score studente trimestrale
- % studenti che dichiarano di sentirsi "meno ansiosi" sulle verifiche
- Tasso di abbandono volontario
- Numero di interventi del Safeguarding Agent per categoria

### 8.4 KPI di efficienza docente
- Ore risparmiate nella correzione
- % di docenti che dichiarano la dashboard "utile" o "molto utile" (semestrale)

### 8.5 KPI per il bilinguismo e l'inclusione (F13)
- Tempo medio onboarding studente non italofono fino al primo concetto consolidato (target: ≤ 2 settimane)
- Δ punteggio verifica per studenti con lingua nativa valorizzata (≥ Δ medio di classe)
- % concetti per cui lo studente bilingue passa dalla colonna nativa a quella ufficiale
- NPS specifico studenti bilingue
- Tasso di disattivazione spontanea del bilinguismo a fine anno (alto = buon segnale)

### 8.6 KPI per le lezioni del docente (F2-A)
- % lezioni caricate entro 7 giorni dalla lezione in aula
- % contenuti generati che attingono alle lezioni del docente
- CSAT qualità trascrizioni (target ≥ 4/5)

### 8.7 KPI sul ciclo di chiusura (F11)
- **Tempo medio rosso → verde**: target ≤ 21 giorni
- **% lacune chiuse** entro 7 / 14 / 30 giorni
- **Tasso di regressione**: % nodi che riaprono (target: < 15%)
- **% consolidamenti autonomi** vs override (target: ≥ 90% autonomi)
- **Lacune aperte** contemporaneamente per studente (target: < 4)
- **Tasso chiusura al primo tentativo** quiz (target: ≥ 60%)
- **Lacune persistenti**: nodi in `lacuna`/`in_recupero` >14gg (target: ridurre 50% trimestre su trimestre)

### 8.8 Target (12 mesi dopo rilascio)
- +20% Δ punteggio verifica N→N+1
- 80% adozione attiva studenti scuola pilota
- 70% NPS studenti
- 50% riduzione tempo docente sulla correzione
- 75% lacune portate a `consolidato` entro 30 giorni

---

## 9. Roadmap

### MVP (6 mesi) — "Il caso 5AI scalato con ciclo di chiusura"

Coperti integralmente:
- F1 (con granularità e livello scolastico)
- F2 (A+B) con trascrizione e mapping
- F3 profilazione (come profilo di adattamento, non classificazione)
- F4 diagnostica formativa con transizioni di stato
- F5 documenti testuali personalizzati
- F8 adattamento linguaggio
- F9 accessibilità base + design system
- **F11** ciclo di chiusura: macchina a stati, mini-quiz, retention check D+7, heatmap studente base, aggregazione macro/micro, override docente tracciato
- **F14** anagrafica, consenso, iscrizione (versione amministrata)
- F13 bilinguismo minimo: lingua ufficiale, 2 lingue pilota (ucraino, arabo), layout due colonne testo
- **F15** gestione contenuti base (modifica/cancella)
- **F16** notifiche docente e studente
- **F17** wizard setup corso
- Dashboard docente base con vista classe e vista studente
- N1-N9 tutti presenti in forma base
- **42 schermate**: 30 MVP
- **58 use case**: 29 MVP
- 1 scuola pilota, 1 classe, 1 docente

### V1 (12 mesi) — "Multimodale e adattivo"
- F6 podcast a due voci (con cross-language)
- F7 gamification con quest, badge, streak
- F11 completo: tutti i retention check (D+3, D+7, D+21), heatmap di classe temporale, alert lacune, override pannello dedicato, override in massa
- F14 self-service via SPID/QR
- Estensione bilinguismo a 6 lingue con revisori madrelingua
- F12 dashboard docente avanzata
- 3 scuole pilota, 6 classi
- **12 schermate V1 aggiuntive**

### V2 (18-24 mesi) — "Ecosistema"
- F10 articolazione completa (animazioni, simulazioni, rubber duck)
- F12 completo (generazione verifiche)
- Bilinguismo a regime 12 lingue
- Integrazione registri elettronici
- Modello federato multi-scuola
- Studente iscritto a più corsi
- Doppia dimensione di padronanza per bilingui
- Eventuale decay temporale
- Apertura ad altre materie

---

## 10. Rischi e mitigazione

| # | Rischio | Impatto | Prob. | Mitigazione |
|---|---|---|---|---|
| R1 | LLM produce errori didattici (allucinazioni) | Alto | Medio | RAG su materiale ufficiale, validazione docente, segnalazione studente |
| R2 | Resistenza dei docenti (timore sostituzione) | Alto | Alto | Co-progettazione, quick win su carico correzione |
| R3 | Famiglie diffidenti sui dati dei minori | Alto | Alto | Privacy by design, opt-in granulare (F14.3), comunicazione chiara |
| R4 | Studenti copiano i compiti | Medio | Alto | No completion mode, rilevamento intent |
| R5 | Bias culturale nelle analogie | Medio | Medio | Bias audit periodico, libreria diversificata, feedback |
| R6 | Gamification induce ansia/dipendenza | Alto | Medio | Anti-pattern F7.7, opt-out F7.8, monitoraggio benessere |
| R7 | Carico cognitivo eccessivo | Medio | Medio | Default dal profilo, zero configurazione necessaria per iniziare |
| R8 | Dipendenza tecnologica | Alto | Medio | Modalità "autopilot off" periodica |
| R9 | Costi LLM elevati | Medio | Alto | Caching, modelli misti, batch generation overnight |
| R10 | Bassa qualità traduzione lingue minori | Alto | Medio | Revisione madrelingua, glossario controllato |
| R11 | Stigma per studente bilingue | Medio | Medio | Modalità privata, bilinguismo non in proiezioni classe |
| R12 | Studente legge solo colonna nativa | Alto | Medio | Rilevamento F13.20, esercizi transizione |
| R13 | Lezioni docente qualità eterogenea | Medio | Alto | Assistenza preparazione, formazione |
| R14 | Mismatch granularità (biennio) | Alto | Medio | Default per livello F1.8, test usabilità |
| R15 | Override abusato | Alto | Medio | Motivazione obbligatoria, audit, KPI distinto §8.7 |
| R16 | Mappa percepita come sorveglianza | Alto | Medio | Tono positivo, rosso + missione, no comparazione |
| R17 | Lacuna non rilevata (falso negativo mapping) | Alto | Medio | Validazione docente obbligatoria, feedback loop |
| R18 | **[NUOVO v0.3]** Wizard setup corso abbandonato | Medio | Medio | Progresso salvato, ripresa dal punto interrotto |
| R19 | **[NUOVO v0.3]** Overload notifiche docente | Medio | Alto | Soglie configurabili F16.2, raggruppamento intelligente |

---

## 11. Considerazioni di estensibilità

L'architettura non lega MAESTRO a una materia specifica. Componenti riusabili:

- Knowledge graph con granularità adattiva: trasversale
- Mappa della conoscenza a stati e ciclo di chiusura: trasversale
- Diagnostica dell'errore: richiede strutture diverse per discipline non procedurali
- Articolazione multimodale, gamification, accessibilità, podcast, bilinguismo: trasversali
- Anagrafica, consenso, iscrizione (F14): indipendenti dalla materia

Materie pilota V2/V3: Matematica, Fisica, Lingue straniere.

---

## 12. Riferimenti e ispirazioni

- **NotebookLM** (Google) — formato podcast a due voci
- **Khanmigo** (Khan Academy) — tutoring conversazionale
- **Duolingo** — gamification non tossica, spaced repetition
- **Anki / SuperMemo** — algoritmi spaced repetition (SM-2, FSRS) per F11.10
- **Bloom 2-sigma problem** (1984) — giustificazione tutoring personalizzato
- **Pashler et al. (2009), Newton (2015)** — critica "learning styles" come tratto fisso → base per riformulazione F3 in v0.3
- **WCAG 2.1** — standard accessibilità
- **GDPR Art. 8, Art. 9** — trattamento dati minori e categorie particolari
- **Linee guida MIUR sull'IA a scuola** (in evoluzione)

---

## 13. Open question per la fase successiva

### Da v0.2 — stato aggiornamento

| # | Domanda | Stato v0.3 | Responsabile |
|---|---|---|---|
| OQ1 | LLM principale: proprietario vs open source | Aperta — da T1.2 | MSTR-02 + MSTR-16 |
| OQ2 | Modello rilascio: SaaS / on-premise / ibrido | Aperta — post pilota | MSTR-01 + MSTR-02 |
| OQ3 | Pricing per la scuola | Fuori scope team — escalate a Daniele | — |
| OQ4 | Governance dati di apprendimento | Aperta — da DPIA T3.1 | MSTR-16 + MSTR-01 |
| OQ5 | Certificazione MIUR per software didattico con AI | Da T3.1 | MSTR-16 |
| OQ6 | Studio di efficacia randomizzato | Da T5.5 | MSTR-22 + MSTR-15 |
| OQ7 | Banca domande mini-quiz: fonte | Aperta — da T1.3 | MSTR-03 + MSTR-15 |
| OQ8 | Rollup macro/micro: "stato peggiore" vs alternativa | Da validare in T1.3 | MSTR-03 + MSTR-15 |
| OQ9 | Decay temporale | Confermato fuori scope v0.3, data model ready | — |
| OQ10 | Doppia padronanza bilingui | Confermato fuori scope v0.3 | — |

### Nuove da v0.3

| # | Domanda | Responsabile |
|---|---|---|
| OQ11 | Daniele agisce come DPO liaison o serve DPO esterno? | MSTR-01 → Daniele |
| OQ12 | Scuola pilota: 5AI I.T.E.T. Pantanelli-Monnet confermata? | MSTR-01 → Daniele |
| OQ13 | Tool PM: Linear vs Jira — da scegliere prima di fine Phase 1 | MSTR-23 |
| OQ14 | Tool docs: Confluence vs Notion — da scegliere prima di fine Phase 1 | MSTR-23 |
| OQ15 | Effort Router downshift a "low" — validare dopo prima Phase 4 | MSTR-23 |

---

## 14. Matrice di tracciabilità

### F → UC → SCR

| Requisito | Use Case MVP | Use Case V1/V2 | Schermate |
|---|---|---|---|
| **F1** KG e programma | UC-DOC-10, UC-DOC-17, UC-SYS-14, UC-SYS-15 | — | SCR-DOC-03, SCR-DOC-11, SCR-ST-04 |
| **F2** Lezioni e materiali | UC-DOC-01, UC-DOC-02, UC-DOC-03 | UC-DOC-11 | SCR-DOC-04, SCR-DOC-05, SCR-DOC-06 |
| **F3** Profilazione | UC-ST-01, UC-ST-07 | UC-SYS-03 | SCR-ST-02, SCR-ST-09 |
| **F4** Diagnostica | UC-DOC-04, UC-SYS-02, UC-SYS-09 | — | SCR-DOC-07 |
| **F5** Documenti testo | UC-ST-02, UC-SYS-01 | — | SCR-ST-08 |
| **F6** Podcast | — | UC-ST-03 | SCR-ST-11 |
| **F7** Gamification | — | UC-ST-04, UC-ST-10 | SCR-ST-12, SCR-ST-03 |
| **F8** Linguaggio | UC-ST-07, UC-SYS-04 | — | SCR-ST-09 |
| **F9** Accessibilità | UC-ST-07 | — | SCR-ST-09, comp. accessibilità, tutti |
| **F10** Multimodale | — | UC-ST-12, UC-ST-09 | — |
| **F11** Mappa e ciclo | UC-ST-13, UC-ST-15, UC-ST-16, UC-SYS-09..12, UC-SYS-14 | UC-DOC-06, UC-DOC-15, UC-DOC-16, UC-DOC-18, UC-DOC-19, UC-SYS-13, UC-SYS-18 | SCR-ST-04..07, SCR-DOC-08..10, SCR-DOC-14 |
| **F12** Dashboard docente | UC-DOC-08, UC-DOC-14 | UC-DOC-05, UC-DOC-06, UC-DOC-18 | SCR-DOC-02, SCR-DOC-08, SCR-DOC-09, SCR-DOC-13 |
| **F13** Bilinguismo | UC-ST-08, UC-SYS-05, UC-FAM-00 | UC-SYS-08 | SCR-ST-08, SCR-ST-09, SCR-FAM-01 |
| **F14** Anagrafica | UC-ST-00, UC-AS-05, UC-AS-08, UC-DOC-12, UC-FAM-00, UC-FAM-03, UC-ST-11 | UC-AS-01, UC-AS-04, UC-AS-06, UC-AS-07, UC-FAM-04 | SCR-ST-01, SCR-AS-01..07, SCR-FAM-01..04 |
| **F15** Contenuti | UC-DOC-08 | — | SCR-DOC-13 |
| **F16** Notifiche | — | UC-DOC-19 | SCR-DOC-16, SCR-ST-03 |
| **F17** Setup corso | UC-DOC-17, UC-DOC-09, UC-DOC-12 | — | SCR-DOC-03 |
| **N1** Privacy | UC-FAM-00, UC-AS-03, UC-AS-08, UC-FAM-03, UC-ST-11 | — | SCR-FAM-01, SCR-AS-04, SCR-AS-05 |
| **N2** Sicurezza | UC-AS-02, UC-AS-03 | UC-AS-01 | SCR-AS-01, SCR-AS-06 |
| **N3** Etica | UC-SYS-04 | UC-SYS-06 | SCR-ST-07 (tono risultati) |
| **N4** Performance | UC-SYS-01, UC-SYS-10, UC-SYS-11 | — | — |
| **N5** Accessibilità | — | — | tutti |
| **N6** Inclusività | UC-SYS-04 | UC-SYS-08 | — |
| **N7** Spiegabilità | UC-ST-06 | — | SCR-ST-10 |
| **N8** Offline | — | — | comp. connessione |
| **N9** i18n UI | — | — | comp. lingua |

---

## 15. Riepilogo quantitativo v0.3

| Categoria | v0.2 | v0.3 | Delta |
|---|---|---|---|
| Gruppi funzionali | F1–F14 | F1–F17 | +3 |
| Requisiti funzionali | ~95 | ~120 | +25 |
| Requisiti non funzionali | N1–N7 | N1–N9 | +2 |
| Use case coperti | — | 58 (29 MVP + 23 V1 + 6 V2) | nuovo |
| Schermate coperte | — | 42 (29 MVP + 12 V1 + 1 V2) | nuovo |
| Personas | 7 | 7 | = |
| KPI | 25 | 25 | = |
| Rischi | 17 | 19 | +2 |
| Open questions | 10 | 15 | +5 |

---

*Documento di lavoro v0.3. Task T1.1 del DAG MAESTRO. Da ratificare con QA Sentinel (MSTR-20) prima di sbloccare Phase 2.*
