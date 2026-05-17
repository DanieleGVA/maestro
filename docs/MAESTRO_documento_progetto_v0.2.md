# Progetto MAESTRO
## Sistema di accompagnamento personalizzato per studenti di Informatica

**Requisiti funzionali e non funzionali — v0.2**
**Autore:** assistente didattico — partendo dall'esperienza di valutazione della verifica PHP 5AI (I.T.E.T. Pantanelli-Monnet) del 15/05/2026
**Continuità:** estende l'impianto concettuale del progetto MAESTRO sviluppato per l'ITT di Ostuni; integra l'iterazione v0.1 con il modello di mappa della conoscenza dinamica, il ciclo di chiusura delle lacune e la macro-area anagrafica/consenso/iscrizione.

### Changelog v0.1 → v0.2

- **F1** esteso con livello scolastico del corso e granularità dei nodi (macro/micro), con default adattivo (F1.6–F1.10).
- **F11** fortemente espanso: macchina a stati semaforo a sei stati, ciclo di chiusura della lacuna, retention check, override docente tracciato, aggregazione macro/micro, heatmap temporale (F11.1–F11.13).
- Nuovo gruppo **F14 — Anagrafica, consenso e iscrizione**, prima trasversalmente implicito e ora esplicitato.
- **Architettura concettuale** aggiornata con due nuovi componenti: *Knowledge Map Manager* e *Identity & Consent Manager*.
- **KPI** ampliati con metriche sul ciclo di chiusura (§8.7).
- **Roadmap** MVP estesa per coprire il ciclo di chiusura (F11) e l'anagrafica/consenso (F14).
- **Rischi** integrati: mismatch di granularità, abuso dell'override.
- **Open question** consolidate: decay temporale rinviato fuori v0.2.

---

## 1. Sintesi esecutiva

**MAESTRO** è un sistema multi-agente che affianca ogni studente di Informatica lungo il suo percorso scolastico. Non si limita a misurare i risultati: a partire dal programma del corso e dal materiale didattico, genera per ogni studente un **percorso personalizzato di comprensione**, articolato in più modalità (testo, audio, gioco, dialogo), nella forma e nel linguaggio che funzionano meglio per *quel* ragazzo.

Il modello mentale di riferimento è l'esperienza concreta condotta sulla classe 5AI: data una verifica di PHP (Autenticazione e Sessioni), per ciascuno dei nove studenti è stato prodotto un rapporto di valutazione *e* un documento di ripasso personalizzato, con i loro errori specifici evidenziati e spiegati con analogie, tono leggero, codice giusto a fronte. MAESTRO generalizza questo schema, lo automatizza e lo rende continuativo su tutto l'arco dell'anno scolastico.

Al centro della v0.2 c'è la **mappa della conoscenza per studente × corso**: una rappresentazione viva, a stato semaforo, della padronanza di ogni concetto del programma. Le lacune non sono solo segnalate: vengono **chiuse attraverso un ciclo formale** — rilevamento, approfondimento ad-hoc, mini-quiz di verifica, retention check nel tempo. La cronologia delle lacune e dei recuperi è preservata, generando una heatmap temporale che racconta il percorso di apprendimento dello studente.

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

---

## 3. Esperienza di riferimento (caso 5AI)

Per ancorare i requisiti al concreto, sintetizzo cosa ha funzionato nell'esperimento di partenza:

- **Stessa verifica, nove report diversi.** Ogni studente ha ricevuto un rapporto specifico sui *suoi* errori, evidenziati visivamente sul *suo* codice.
- **Documenti di ripasso a triplice struttura** per ogni concetto: (1) cosa è successo nel tuo codice, (2) analogia quotidiana, (3) codice corretto, (4) la regola da ricordare.
- **Analogie personalizzate**: la pizzeria per spiegare i result handle, il braccialetto della discoteca per le sessioni, i barattoli del riso e della pasta per le chiavi sfalsate.
- **Tono leggero** anche su voti gravemente insufficienti, mai offensivo, sempre orientato al "ti aspetto al prossimo round".
- **Codice giallo evidenziato** invece di voto in rosso: l'attenzione visiva sull'errore, non sulla bocciatura.

MAESTRO replica e automatizza questo schema, lo espande a quattro canali (testo, podcast a due voci, gioco, dialogo) e — novità della v0.2 — lo chiude in un **ciclo formale**: ogni errore rilevato attiva un percorso di recupero, di cui si misura l'esito.

---

## 4. Attori e personas

| Attore | Descrizione | Bisogno primario |
|---|---|---|
| **Studente** (utente principale, 13-19 anni) | Frequenta corsi di Informatica. Profilo di apprendimento eterogeneo. | Capire i concetti che gli sfuggono nel modo che funziona per lui; chiudere le lacune con un percorso chiaro. |
| **Docente** | Insegna Informatica, prepara verifiche, valuta. | Strumento che lo libera dalla correzione massiva, gli mostra dove la classe arranca, gli permette di intervenire chirurgicamente. |
| **Famiglia** | Genitori/tutori legali dello studente minorenne. | Trasparenza, controllo sui dati del figlio, visione dei progressi. Possibilità di firmare un consenso granulare. |
| **Coordinatore didattico** | Dirige il corso, integra il piano. | Dati aggregati di classe per orientare la didattica. |
| **Amministratore di sistema** | IT della scuola. | Gestione utenti, integrazioni (registro elettronico, AD/SSO), conformità, ciclo di vita degli account. |

### Personas studente di riferimento

- **Marta, 16, "la visiva"**: prende appunti con mappe e colori, fa fatica con i testi lunghi, ricorda meglio se vede.
- **Riccardo, 17, "l'ascoltatore"**: studia mentre cammina, ascolta podcast, gli piacciono i dialoghi e le storie.
- **Davide, 16, "il pratico"**: capisce mentre fa, salta i preamboli, vuole subito un esempio funzionante.
- **Gabriele, 15, "il riflessivo"**: ha bisogno di tempo, rilegge, predilige la spiegazione passo-passo.
- **Stefano, 16, "il sociale"**: impara discutendo, vuole confrontarsi, gli piace il gioco di squadra.
- **Olena, 15, "la non-italofona"**: arrivata dall'Ucraina otto mesi fa, parla russo come prima lingua e ucraino in famiglia, sta imparando l'italiano. Capisce i concetti tecnici se può vederli/sentirli anche in una lingua che padroneggia.
- **Francesca, 14, "la prima superiore"**: è all'inizio del biennio. Ha bisogno di una mappa della conoscenza che non la spaventi con un albero troppo dettagliato. La sua vista di default è macro; le lacune vengono comunicate con linguaggio piano.

Le cinque modalità (visiva, uditiva, cinestesica, riflessiva, sociale) sono i poli del modello di profilazione. Olena rappresenta un asse trasversale (bilinguismo). Francesca rappresenta l'altro asse trasversale: il **livello scolastico**, che determina la granularità della mappa.

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

Componenti chiave introdotti dalla v0.2:

- **Identity & Consent Manager**: gestisce anagrafica studente, consensi granulari della famiglia, iscrizioni ai corsi, ciclo di vita dell'account (creazione, attivazione, sospensione, oblio). Espone audit log GDPR-compliant.
- **Knowledge Map Manager**: gestisce per ogni coppia (studente, nodo del KG) lo stato corrente, la cronologia delle transizioni, i retention check programmati, gli override docente. È il motore del ciclo di chiusura della lacuna.

Stack tecnologico di riferimento (a titolo indicativo, da validare):
- LLM frontier (Claude, GPT) per gli agent generativi
- TTS multi-voce (ElevenLabs, OpenAI TTS, Azure Neural Voices) per il podcast
- Vector DB (Pinecone/Weaviate) per il materiale didattico
- Knowledge graph (Neo4j) per la mappa concettuale del curriculum
- State store relazionale o time-series per il Knowledge Map Manager (PostgreSQL + tabelle di cronologia, oppure time-series tipo TimescaleDB)
- Frontend mobile-first (React Native o Flutter)
- Backend orchestrazione (LangGraph o framework agentico equivalente)

---

## 6. Requisiti funzionali

### F1 — Ingestione del programma di studio e modello del knowledge graph

| ID | Requisito |
|---|---|
| F1.1 | Il sistema importa il programma ufficiale del corso (es. linee guida MIUR per ITT articolazione Informatica) in formato strutturato. |
| F1.2 | Il sistema costruisce un **knowledge graph** dei concetti: ogni concetto è un nodo, gli archi rappresentano prerequisiti ("per capire X serve Y"). |
| F1.3 | Ogni concetto è classificato per livello di difficoltà (base, intermedio, avanzato) e per anno scolastico. |
| F1.4 | Il programma può essere aggiornato dal docente con nuovi nodi/archi senza riavvio del sistema. |
| F1.5 | Esempio per Informatica: nodi come "Variabile", "Tipo di dato", "Sessione PHP", "Query SQL", "Sanificazione input"… ognuno con prerequisiti espliciti. |
| F1.6 | Ogni corso è associato a un **livello scolastico** definito in fase di setup, scelto dall'elenco: *secondaria di primo grado*, *biennio della secondaria di secondo grado*, *triennio della secondaria di secondo grado*, *post-diploma/ITS*, *formazione professionale*. Il livello scolastico è un attributo del corso, non dello studente. |
| F1.7 | Ogni nodo del knowledge graph espone un attributo di **granularità** appartenente a uno di due livelli: *macro-nodo* (concetto strutturante, leggibile da studente e famiglia) e *micro-nodo* (sotto-concetto fine, usato dall'engine diagnostico e dal docente). I micro-nodi sono **figli logici** di un macro-nodo. La padronanza di un macro è derivata dalla padronanza dei suoi micro secondo la regola di rollup in F11.8. |
| F1.8 | La **granularità di default per la visualizzazione** dipende dal livello scolastico del corso. Per secondaria di primo grado e biennio: vista predefinita macro per studente e famiglia, micro per docente. Per triennio e post-diploma: studente può scegliere macro o micro, docente sempre micro. La logica è non sopraffare lo studente più giovane con un albero troppo dettagliato. |
| F1.9 | Il docente può **personalizzare la granularità** di default per il proprio corso, anche in deroga al default per livello (es. un docente di biennio particolarmente metodico può scegliere di mostrare anche i micro-nodi agli studenti). |
| F1.10 | Esempio applicato al concetto "Algoritmo". Macro-nodo: *Concetto di algoritmo*. Micro-nodi figli: *Definizione di algoritmo*, *Proprietà: finitezza*, *Proprietà: determinatezza*, *Proprietà: non ambiguità*, *Rappresentazione: pseudocodice*, *Rappresentazione: diagramma di flusso*. Per uno studente di prima superiore appare solo il macro-nodo nella propria mappa; per uno di quinta appaiono tutti i micro-nodi. |

### F2 — Caricamento delle lezioni e indicizzazione del materiale didattico

**F2-A. Lezioni del docente (fonte primaria autoritativa)**

| ID | Requisito |
|---|---|
| F2.1 | Il docente carica le proprie **lezioni** in formati diversi: video di lezione in aula, registrazione audio asincrona, slide annotate, dispense personali, scheda di lezione preparata, screencast con codice live. |
| F2.2 | Per i contenuti audio e video il sistema produce **trascrizione automatica** con timestamp e identificazione del parlante (docente / studente intervenuto). |
| F2.3 | La trascrizione è editabile dal docente in un'interfaccia di rifinitura rapida: correzione di termini tecnici, nomi propri, formule e codice. |
| F2.4 | Ogni lezione è collegata ai nodi del knowledge graph tramite **mapping concettuale automatico assistito, validato dal docente**: "in questa lezione il concetto X è trattato dal minuto 12:30 al 28:15". Ciò permette il deep-link da qualunque punto del percorso di studio. |
| F2.5 | Le lezioni del docente godono di **priorità autoriale**: quando MAESTRO genera contenuti personalizzati, attinge prima alla lezione del docente, poi al manuale, poi a fonti esterne. La voce e l'impostazione del docente prevalgono sempre. |
| F2.6 | Le lezioni alimentano direttamente il percorso di formazione: ogni nuova lezione caricata aggiorna automaticamente le quest, gli esercizi e i materiali di ripasso pertinenti agli argomenti trattati. |
| F2.7 | Possibilità di caricamento in batch (una cartella di lezioni di un intero modulo) o lezione per lezione (uso giornaliero). |
| F2.8 | Il docente può annotare la lezione con metadati: livello di difficoltà, granularità (macro/micro), prerequisiti, esercizi di consolidamento suggeriti. |

**F2-B. Materiali didattici complementari**

| ID | Requisito |
|---|---|
| F2.9 | Caricamento di libro di testo, dispense terze, esercizi, codice di esempio, articoli, link esterni. |
| F2.10 | Il sistema indicizza tutti i materiali in un vector store e li collega ai nodi del knowledge graph. |
| F2.11 | Per ogni concetto il sistema mira ad avere almeno **tre fonti diverse**: lezione del docente + manuale + esercizio (per permettere triangolazione e varietà di esposizione). |
| F2.12 | Il sistema rileva le **lacune di copertura**: concetti del programma per cui non c'è ancora materiale e li segnala al docente. |
| F2.13 | Rispetto del copyright: i materiali sono ad uso interno; le citazioni nelle generazioni rispettano le regole di fair use; le lezioni del docente rimangono di sua proprietà intellettuale e non escono dal perimetro dell'istituto. |

### F3 — Profilazione learning style

| ID | Requisito |
|---|---|
| F3.1 | Onboarding leggero (5-10 minuti): mini-quiz che propone lo stesso concetto in 4 modalità diverse e misura quale funziona meglio. |
| F3.2 | Profilo come **vettore continuo**, non come etichetta rigida: ogni studente è una miscela delle cinque modalità (visivo, uditivo, cinestesico, riflessivo, sociale). |
| F3.3 | Il profilo evolve nel tempo in base al comportamento osservato (cosa lo studente apre, cosa completa, dove abbandona). |
| F3.4 | Lo studente può forzare le sue preferenze ("voglio solo podcast questo mese"). |
| F3.5 | Il profilo include preferenze accessorie: tono (formale/informale), preferenze cromatiche, font, lunghezza preferita. |
| F3.6 | Il profilo è trasparente: lo studente vede sempre il proprio profilo corrente e può modificarlo. |

### F4 — Diagnostica formativa post-verifica

| ID | Requisito |
|---|---|
| F4.1 | Il docente carica una verifica corretta (o il sistema la corregge in modalità assistita). |
| F4.2 | Il sistema mappa ogni errore di ogni studente al **micro-nodo concettuale** corrispondente nel knowledge graph (precisione massima, non al macro). |
| F4.3 | Ogni errore mappato attiva una transizione di stato sul Knowledge Map Manager (vedi F11.3–F11.4): il micro-nodo passa a `lacuna`. |
| F4.4 | Output minimo per il docente: rapporto di valutazione classico (come quelli prodotti nell'esperimento 5AI), con codice evidenziato e tabella per task, **più** la lista delle transizioni di stato avvenute per ogni studente. |
| F4.5 | Output per lo studente: documento di ripasso personalizzato (F5) + aggiornamento immediato della propria mappa della conoscenza. |

### F5 — Generazione di documenti testuali personalizzati

| ID | Requisito |
|---|---|
| F5.1 | Per ogni gap concettuale viene generato un blocco con la struttura *errore tuo → perché succede → come si fa giusto → ricordati*. |
| F5.2 | Le analogie sono **selezionate dal profilo dello studente**: se gli piace lo sport, l'analogia è sportiva; se gioca a videogame, è videoludica; se ama cucinare, è in cucina. |
| F5.3 | Il codice errato è mostrato evidenziato (giallo) accanto al codice giusto (verde). |
| F5.4 | Lunghezza variabile in base al profilo: chi preferisce la sintesi riceve 2-3 concetti per documento; chi preferisce l'approfondimento ne riceve 6-8. |
| F5.5 | Tono adattivo: confidenziale, neutro, o formale a seconda della preferenza. |

### F6 — Generazione di podcast a due voci (stile NotebookLM)

| ID | Requisito |
|---|---|
| F6.1 | Per ogni concetto-target il sistema genera un audio di 4-8 minuti in cui due AI speaker (un "esperto" e un "curioso") discutono il tema con tono colloquiale e analogie. |
| F6.2 | Lo studente sceglie le **voci** tra una libreria (es. due studenti, due divulgatori, una coppia comica, due personaggi storici di pura fantasia). |
| F6.3 | Lo speaker "curioso" pone le domande che lo studente probabilmente si farebbe; lo speaker "esperto" risponde con analogie e esempi. |
| F6.4 | L'audio si può ascoltare in app o scaricare in MP3. |
| F6.5 | Trascrizione sincronizzata sempre disponibile (accessibilità). |
| F6.6 | Variante "monologo" per chi preferisce una sola voce. |
| F6.7 | Variante "dibattito": le due voci sono in disaccordo deliberato, e lo studente deve giudicare chi ha ragione (modalità critica). |
| F6.8 | Velocità di riproduzione regolabile (0.75x – 2x). |

### F7 — Layer di gamification

| ID | Requisito |
|---|---|
| F7.1 | **Skill tree**: il knowledge graph è visualizzabile come albero di abilità; ogni nodo sbloccato è una piccola conquista. |
| F7.2 | **XP e livelli**: ogni esercizio completato dà XP; gli XP fanno salire di livello la "carriera" dello studente in Informatica. |
| F7.3 | **Badge tematici**: "Risolutore di SQL", "Domatore di sessioni", "Cacciatore di bug"… badge per traguardi specifici. Badge speciale "Chiudi-lacune" per chi porta in verde un certo numero di nodi precedentemente in rosso. |
| F7.4 | **Streak**: giorni consecutivi di attività (con notifica gentile, mai pressante; possibilità di "freeze" per pause legittime). |
| F7.5 | **Quest giornaliere e settimanali**: piccoli obiettivi mirati ai gap dello studente, generate automaticamente a partire dalle lacune attualmente aperte (stato `lacuna` o `in_recupero`). |
| F7.6 | **Modalità cooperativa di classe**: quest da risolvere in squadra, dove ogni studente porta competenze diverse. |
| F7.7 | **Anti-pattern espliciti**: NESSUNA classifica pubblica individuale, NESSUN paragone tra studenti, NESSUN meccanismo addittivo (notifiche martellanti, FOMO, ricompense variabili). |
| F7.8 | Lo studente può **disattivare la gamification** in qualsiasi momento senza perdere il progresso didattico. |

### F8 — Adattamento del linguaggio personale

| ID | Requisito |
|---|---|
| F8.1 | Tre registri base: **confidenziale** (tu, frasi brevi, qualche battuta), **neutro** (tu, frasi medie, formale ma calmo), **formale** (lei, frasi articolate). |
| F8.2 | Adattamento di livello lessicale: se lo studente è in difficoltà, vocabolario semplificato; se è avanzato, terminologia tecnica precisa. |
| F8.3 | Inserimento di **riferimenti culturali** legati ai suoi interessi (musica, film, sport, videogame, libri) per ancorare i concetti. |
| F8.4 | Multilinguismo: italiano default, ma inglese, francese, arabo, spagnolo per studenti di seconda generazione o BES linguistici (cfr. F13). |
| F8.5 | Eliminazione automatica di gergo o riferimenti non age-appropriate. |

### F9 — Accessibilità visiva (font, colori, dislessia)

| ID | Requisito |
|---|---|
| F9.1 | Font selezionabili: predefinito (Calibri/Inter), **dislessia-friendly** (OpenDyslexic, Atkinson Hyperlegible). |
| F9.2 | Modalità ad alto contrasto. |
| F9.3 | Codifica cromatica coerente per gli stati della mappa: vedi F11.3. Mai dipendere SOLO dal colore (sempre icona/testo a supporto, per i daltonici). |
| F9.4 | Dimensione testo regolabile 12-24pt. |
| F9.5 | Modalità chiara, scura, e seppia per la lettura prolungata. |
| F9.6 | Conformità WCAG 2.1 AA su tutti i materiali generati. |

### F10 — Articolazione multimodale dei contenuti

| ID | Requisito |
|---|---|
| F10.1 | Per ogni concetto, esistono almeno **quattro "articolazioni"**: testo, audio (podcast), visuale (diagramma/animazione), pratica (esercizio guidato). |
| F10.2 | Lo studente può passare da un'articolazione all'altra mantenendo il contesto ("ascolta il podcast su questa parte"). |
| F10.3 | Il sistema propone l'articolazione predominante in base al profilo, ma le mostra tutte. |
| F10.4 | Articolazione "metacognitiva": un quinto canale dove lo studente *spiega a voce* il concetto al sistema (rubber duck debugging), e il sistema verifica la solidità. |

### F11 — Mappa della conoscenza e ciclo di chiusura delle lacune

*Pezzo centrale della v0.2. Sostituisce e amplia la sezione "Tracciamento progressi" della v0.1.*

#### F11-A. Visualizzazione della mappa della conoscenza

| ID | Requisito |
|---|---|
| F11.1 | Per ogni studente × corso esiste una **mappa della conoscenza** visualizzabile come grafo navigabile o albero. Ogni nodo è colorato secondo il proprio stato corrente (F11.3). |
| F11.2 | La granularità della vista si adatta al livello scolastico del corso (F1.8) ma può essere ricommutata dallo studente di triennio (macro ↔ micro). Lo studente di biennio vede solo la vista macro. |
| F11.3 | Macchina a stati a **sei stati** per coppia (studente, nodo): `non_introdotto` (grigio), `introdotto` (bianco), `lacuna` (**rosso**), `in_recupero` (arancione), `da_consolidare` (**giallo**), `consolidato` (**verde**). |

#### F11-B. Eventi e transizioni di stato

| ID | Requisito |
|---|---|
| F11.4 | Transizioni di stato canoniche: <br>• mapping errore in verifica (F4.2) → `lacuna`<br>• avvio di un percorso di approfondimento da parte dello studente (F11.6) → `in_recupero`<br>• esito positivo del mini-quiz di chiusura → `da_consolidare`<br>• tutti i retention check positivi (F11.10) → `consolidato`<br>• errore in verifica successiva su un nodo già in `da_consolidare` o `consolidato` → **regressione** a `lacuna`. |
| F11.5 | Ogni transizione è registrata nella cronologia dello studente con: timestamp, stato precedente, stato successivo, causa (evento), evidenza (riferimento a verifica/quiz/retention check). |

#### F11-C. Ciclo di chiusura della lacuna (scenario primario)

| ID | Requisito |
|---|---|
| F11.6 | **Avvio dell'approfondimento**: una lacuna identificata (rosso) genera automaticamente nella dashboard dello studente una "missione" di recupero. Lo studente la avvia dichiarativamente. Lo stato passa a `in_recupero`. |
| F11.7 | **Generazione del percorso ad-hoc**: il sistema genera un percorso di studio mirato al micro-nodo specifico, articolato in base al profilo learning style dello studente (F3). Il percorso può includere documento testuale, podcast, esercizio guidato, video segmento della lezione del docente (F2.4). |
| F11.8 | **Mini-quiz di chiusura**: a valle del percorso, il sistema somministra un mini-quiz di 3-5 domande mirate al micro-nodo. Il quiz è generato dal Diagnostic Agent attingendo a banca domande del docente o, in mancanza, a una banca generata automaticamente con validazione retroattiva del docente. |
| F11.9 | **Esito del mini-quiz**: <br>• ≥80% di risposte corrette → stato passa a `da_consolidare`, parte la sequenza di retention check (F11.10)<br>• 50-79% → resta in `in_recupero`, sistema propone un secondo giro del percorso variando l'articolazione (canale diverso, analogia diversa)<br>• <50% → resta in `lacuna`, scatta alert per il docente (F11.13) suggerendo intervento personale. |
| F11.10 | **Retention check programmati**: dopo il passaggio a `da_consolidare`, il sistema programma tre retention check a **D+3, D+7, D+21**. Ogni retention check è un mini-quiz adattivo (3-5 domande). Tre esiti positivi → `consolidato`. Un esito negativo → regressione a `lacuna` e nuovo ciclo. |

#### F11-D. Aggregazione macro/micro, override docente, heatmap

| ID | Requisito |
|---|---|
| F11.11 | **Aggregazione macro**: lo stato di un macro-nodo è derivato dagli stati dei suoi micro-nodi figli secondo la regola dello **stato peggiore** (più conservativa, didatticamente più onesta). Esempio: un macro è `lacuna` se almeno un suo micro è `lacuna`, indipendentemente dagli altri. Il macro è `consolidato` solo quando tutti i micro sono `consolidato`. |
| F11.12 | **Override docente** (UC-DOC-16): il docente può forzare manualmente lo stato di un nodo per uno studente. Ogni override è **tracciato in audit log obbligatorio** con: identità docente, timestamp, stato precedente, stato forzato, **motivazione testuale obbligatoria** (es. "verifica orale superata in classe il 15/05"). La cronologia visibile allo studente mostra l'override come transizione esplicita. Gli override non concorrono ai KPI di consolidamento autonomo (§8.7). |
| F11.13 | **Heatmap temporale**: per ogni studente è disponibile una vista (nodo × tempo) → stato che mostra l'evoluzione della padronanza nel tempo. La heatmap permette al docente e allo studente di leggere la storia di apprendimento: lacune chiuse rapidamente, lacune persistenti, regressioni, pattern di apprendimento. |
| F11.14 | **Heatmap di classe**: aggregazione delle heatmap individuali per il docente, con possibilità di filtrare per macro-area del programma e per periodo. |

#### F11-E. Alert, spaced repetition, output famiglia

| ID | Requisito |
|---|---|
| F11.15 | **Alert su lacune persistenti**: una lacuna in stato `lacuna` o `in_recupero` da più di 14 giorni genera un alert per il docente. Tre regressioni sullo stesso nodo entro 30 giorni → alert con suggerimento di cambio canale (se finora era stato proposto in testo, prova podcast; se era podcast, prova esercizio pratico). |
| F11.16 | **Report mensile per la famiglia**: 1 pagina, leggibile da non addetti, con: numero macro-aree consolidate nel mese, numero lacune chiuse, lacune attualmente aperte (riassunto narrativo, non lista di sigle), tono incoraggiante. Nessun confronto con altri studenti. Nessun valore numerico assoluto fuori contesto. |

> **Nota fuori scope v0.2**: il **decay temporale** dello stato `consolidato` (es. ritorno a `da_consolidare` dopo N mesi di non esposizione al concetto) non è oggetto di v0.2. Il modello dati prevede comunque la registrazione di `last_seen` e `last_reinforced` per abilitare il decay in una futura iterazione senza migrazione dati. <br><br> **Nota fuori scope v0.2**: la doppia dimensione di padronanza (concettuale vs lessicale-tecnica in lingua ufficiale) per studenti bilingui non è oggetto di v0.2. Il mini-quiz di chiusura è somministrato in lingua ufficiale del corso. Rimando a futura iterazione di F13.

### F12 — Dashboard docente

| ID | Requisito |
|---|---|
| F12.1 | Vista classe: heatmap dei nodi su tutti gli studenti, per individuare i gap di gruppo. |
| F12.2 | Vista studente: mappa della conoscenza completa con cronologia, ma con privacy graduata (il docente vede gli stati concettuali e gli esiti dei mini-quiz, non i dati comportamentali fini come "quanti minuti ha passato sul podcast il sabato sera"). |
| F12.3 | Generazione assistita di verifiche bilanciate sul programma e sui gap di classe. |
| F12.4 | Suggerimenti di tagliando didattico: "questa settimana il 60% della classe ha lacune attive su X, conviene una lezione dedicata". |
| F12.5 | Il docente può sempre **modificare o cancellare** un contenuto generato da MAESTRO. La parola finale è sua. |
| F12.6 | Pannello override: vista riepilogativa di tutti gli override effettuati dal docente, con motivazione e stato risultante (per autoverifica del docente stesso). |

### F13 — Lingua ufficiale del corso e bilinguismo per studenti non italofoni

> Estensione e specializzazione di F8. Tratta separatamente perché ha implicazioni trasversali su tutti i canali di output (testo, audio, gioco, dialogo) e introduce un componente architetturale dedicato (Bilingual Composer).

**F13-A. Lingua ufficiale del corso**

| ID | Requisito |
|---|---|
| F13.1 | Ogni corso ha **una lingua ufficiale** definita dal docente in fase di setup (italiano nelle scuole italiane; in scuole internazionali può essere inglese, francese, ecc.). |
| F13.2 | La lingua ufficiale è quella di: materiali del docente, prove di verifica, voti, registro elettronico, comunicazioni ufficiali alla famiglia, **mini-quiz di chiusura delle lacune** (F11.8). |
| F13.3 | La lingua ufficiale può variare per corso anche all'interno della stessa scuola (es. un corso CLIL di Informatica in inglese). |
| F13.4 | Tutte le generazioni AI predefinite per un corso avvengono nella sua lingua ufficiale, salvo F13-B (bilinguismo). |

**F13-B. Lingua nativa parallela dello studente**

| ID | Requisito |
|---|---|
| F13.5 | Nel profilo studente è previsto il campo **lingua nativa** (opzionale, valorizzato per studenti non italofoni o di seconda generazione che lo richiedono). Valorizzazione richiede consenso esplicito della famiglia (cfr. F14.3). |
| F13.6 | Libreria di lingue native supportate al rilascio: **ucraino, russo, albanese, arabo, rumeno, urdu, bengalese, cinese mandarino, spagnolo, francese, tagalog, polacco** (le 12 lingue di immigrazione più diffuse nelle scuole italiane). La libreria è estensibile via configurazione. |
| F13.7 | Quando la lingua nativa è valorizzata, **tutti i contenuti personalizzati** prodotti per quello studente sono generati in **doppia lingua, sempre in parallelo**: la lingua ufficiale del corso resta primaria, la lingua nativa la affianca. |
| F13.8 | Il bilinguismo **non sostituisce mai** la lingua ufficiale: obiettivo dichiarato è facilitare la comprensione del concetto e contemporaneamente l'acquisizione del lessico tecnico nella lingua ufficiale. |
| F13.9 | Lo studente può **disattivare** il bilinguismo in qualsiasi momento (es. quando il suo italiano è diventato fluente) e può **riattivarlo** se serve per un argomento specifico. |

**F13-C. Formati di affiancamento per canale**

| ID | Requisito |
|---|---|
| F13.10 | **Documento testuale**: layout a due colonne (sinistra = lingua ufficiale, destra = lingua nativa). I termini tecnici sono presenti in entrambe le lingue con il termine originale tra parentesi per favorire l'acquisizione. |
| F13.11 | **Podcast a due voci**: variante "cross-language" dove una voce parla la lingua ufficiale e l'altra commenta e riprende in lingua nativa. Non è una traduzione meccanica ma un dialogo bilingue. In alternativa: versione duplicata, una in lingua ufficiale e una in lingua nativa, su due tracce. |
| F13.12 | **Gamification**: quest e badge hanno descrizione bilingue. Mini-glossario tecnico bilingue per ogni concetto del knowledge graph (badge "lessico tecnico" come riconoscimento esplicito). |
| F13.13 | **Dialogo chatbot**: lo studente può scrivere in entrambe le lingue; il sistema risponde sempre in entrambe, con la risposta in lingua ufficiale come primaria. |
| F13.14 | **Animazioni e diagrammi**: etichette nei diagrammi in doppia lingua quando lo spazio lo consente; sottotitoli sempre disponibili nei video. |

**F13-D. Localizzazione culturale (oltre la sola traduzione)**

| ID | Requisito |
|---|---|
| F13.15 | Le **analogie didattiche** sono localizzate sulla cultura d'origine quando appropriato. Si mantiene sempre anche il riferimento al contesto italiano per favorire l'integrazione. |
| F13.16 | Vietato il ricorso a stereotipi nazionali o regionali. Le localizzazioni sono validate da revisori madrelingua. |

**F13-E. Qualità della traduzione e tutela dell'apprendimento**

| ID | Requisito |
|---|---|
| F13.17 | Per ogni lingua nativa supportata, **revisione qualitativa da parte di un revisore madrelingua** almeno una volta per anno scolastico, con campionamento dei contenuti generati. |
| F13.18 | Glossario tecnico controllato per ogni lingua: termini specifici della materia con traduzione consolidata, per evitare oscillazioni terminologiche. |
| F13.19 | Le **prove di verifica** e i **mini-quiz di chiusura** (F11.8) restano nella lingua ufficiale; lo studente può chiedere una "lettura assistita" in lingua nativa **durante lo studio**, mai durante una valutazione formale. |
| F13.20 | Il sistema rileva quando uno studente legge sistematicamente solo la colonna in lingua nativa e ignora quella ufficiale: in quel caso suggerisce esercizi di transizione mirati per consolidare il lessico tecnico nella lingua ufficiale e non ostacolare l'integrazione scolastica. |
| F13.21 | La lingua nativa è **dato sensibile** (riconducibile all'origine etnica): trattamento conforme a N1 e F14.3.b. |

### F14 — Anagrafica, consenso e iscrizione

*Macro-area nuova in v0.2. Copre il ciclo di vita dello studente in MAESTRO: dalla creazione alla cancellazione, passando per consenso e iscrizione al corso. È la precondizione di tutti gli altri flussi.*

| ID | Requisito |
|---|---|
| F14.1 | Il ciclo di vita di uno studente in MAESTRO è: **creazione anagrafica → consenso famiglia → iscrizione al corso → prima attivazione → utilizzo → eventuali aggiornamenti (passaggio di classe, ecc.) → eventuale sospensione → cancellazione/oblio**. I primi tre passaggi possono avvenire in qualsiasi ordine ma tutti e tre devono essere completati prima dell'attivazione. |
| F14.2 | **Creazione anagrafica**: in MVP la creazione avviene manualmente da parte dell'IT scolastico tramite form (UC-AS-05). In V2 è prevista l'importazione massiva e la sincronizzazione periodica con il registro elettronico (Argo, ClasseViva, Spaggiari). Ogni studente ha un identificativo interno univoco, separato dall'identità sul registro. |
| F14.3 | **Consenso al trattamento dei dati**: requisito GDPR per minori (Art. 8). Consenso del genitore/tutore per studenti <14 anni, consenso assistito 14-18. Il consenso è **granulare**: lo schema prevede consensi separati per: <br>(a) profilazione comportamentale per learning style (F3)<br>(b) valorizzazione lingua nativa, categoria particolare Art. 9 GDPR (F13)<br>(c) comunicazioni periodiche alla famiglia (F11.16)<br>(d) conservazione storico apprendimento oltre l'anno scolastico<br>(e) eventuale uso aggregato anonimo per fini di ricerca didattica. |
| F14.4 | In MVP il consenso è acquisito in modalità **amministrata** (modulo cartaceo firmato registrato dall'IT scolastico). In V1 è prevista la modalità **self-service** via link/QR con identità verificata del genitore (SPID o codice di attivazione monouso). |
| F14.5 | **Iscrizione al corso**: separazione concettuale tra anagrafica (uno studente, un'identità) e iscrizione (rapporto studente-corso-anno). Un docente può iscrivere studenti alle proprie classi (UC-DOC-12) e rimuoverli (UC-DOC-13). In MVP: uno studente è iscritto a un solo corso (Informatica). In V2: iscrivibile a più corsi. Il modello dati prevede già la relazione 1:N fin dall'MVP per evitare migrazioni successive. |
| F14.6 | **Prima attivazione** (UC-ST-00): accesso con credenziali una tantum o SSO scolastico, accettazione termini d'uso adattati per minori (linguaggio chiaro, non legalese), conferma del consenso registrato dalla famiglia. A valle dell'attivazione lo studente entra nel flusso di onboarding learning style (UC-ST-01). |
| F14.7 | **Aggiornamenti anagrafici**: passaggio di classe a inizio anno scolastico, cambio scuola, cambio dati anagrafici. La cronologia di apprendimento (F11) è **preservata** attraverso il passaggio di classe; il knowledge graph del nuovo corso può essere diverso e gli stati vengono ri-mappati ove possibile. |
| F14.8 | **Sospensione**: uno studente può essere sospeso (uscita per malattia lunga, trasferimento provvisorio) preservando i dati per N giorni configurabili (default 90). Durante la sospensione non si genera materiale; alla riattivazione si riprende dallo stato precedente. |
| F14.9 | **Cancellazione/oblio**: richiesta della famiglia, sempre accolta. Cancellazione completa dei dati riconducibili allo studente: profilo, cronologia, mappa della conoscenza, audio, documenti generati, override docente. È conservato in forma aggregata anonima solo se previsto da consenso F14.3.e. |
| F14.10 | **Audit log**: ogni operazione di anagrafica, consenso, iscrizione, sospensione, cancellazione è registrata in audit log immutabile con identità dell'operatore, timestamp, dato precedente, dato nuovo. |

---

## 7. Requisiti non funzionali

### N1 — Privacy e protezione dei minori

- Conformità **GDPR**, base giuridica chiara per il trattamento di minori (Art. 8): consenso genitoriale per <14, consenso assistito 14-18.
- Dati personali in chiaro **mai inviati agli LLM esterni**: pseudonimizzazione obbligatoria nei prompt.
- **Diritto all'oblio totale**: lo studente (e la famiglia) può richiedere l'eliminazione completa del profilo e dei dati derivati (F14.9).
- Residenza dei dati: server UE.
- Retention policies esplicite per ogni categoria di dato.
- **Audit log di tutte le operazioni** sul ciclo di vita dell'account (F14.10) e degli **override** sulla mappa della conoscenza (F11.12).
- Conformità con il **Garante Privacy** italiano e con le linee guida MIUR/Ministero Istruzione su intelligenza artificiale a scuola.
- **Lingua nativa come dato sensibile** (F13): poiché è riconducibile all'origine etnica, è trattata come categoria particolare ai sensi dell'Art. 9 GDPR. Acquisizione solo con consenso esplicito della famiglia, separato dal consenso generale al servizio (F14.3.b). Mai esposta nelle dashboard di classe a vista di compagni; visibile al docente in forma aggregata e solo se funzionale alla didattica.

### N2 — Sicurezza

- Autenticazione SSO con il registro elettronico/SSO scolastico.
- Crittografia end-to-end dei materiali sensibili.
- Audit log di ogni accesso a dati di un minore.
- Penetration test annuale.
- Disaster recovery RPO ≤ 24h, RTO ≤ 4h.

### N3 — Etica e benessere

- **Safeguarding agent** che valida ogni output prima della consegna allo studente:
  - Nessun linguaggio offensivo, anche in modalità confidenziale.
  - Nessun riferimento a confronti con compagni.
  - Rilevamento di pattern di disagio (frustrazione persistente, abbandono, picchi negativi) → alert al docente e attivazione di un percorso di supporto.
- **Mai sostituire un professionista**: se uno studente accenna a difficoltà psicologiche, il sistema non improvvisa terapia, ma facilita l'aggancio con il referente scolastico (psicologo, coordinatore).
- Tono SEMPRE incoraggiante, anche nei casi di insufficienza grave e di lacuna ripetuta.
- Nessun nudging manipolativo: niente dark pattern, niente FOMO artificiale, niente scarcity ingannevole.
- La **mappa con stati semaforo** non diventa fonte di stress: la presentazione visiva del rosso è accompagnata sempre dalla "missione" di recupero — il rosso è una porta aperta, non un marchio.

### N4 — Performance

- Generazione di un documento di ripasso completo (testo + audio): ≤ 60 secondi.
- Generazione di un percorso di approfondimento personalizzato (F11.7): ≤ 30 secondi.
- Generazione di un mini-quiz di chiusura (F11.8): ≤ 15 secondi.
- Risposta in chat agente di tutoring: ≤ 3 secondi P95.
- Disponibilità 99.5% in orario scolastico (8:00-16:00 nei giorni feriali).

### N5 — Accessibilità

- Conformità WCAG 2.1 AA.
- Supporto screen reader (NVDA, JAWS, VoiceOver).
- Sottotitoli e trascrizioni per ogni contenuto audio.
- Navigazione tastiera completa.
- La mappa della conoscenza è esplorabile da tastiera; gli stati sono comunicati anche testualmente (non solo dal colore).
- Test con utenti reali con disabilità cognitive (BES, DSA) prima del rilascio.

### N6 — Inclusività linguistica e culturale

- Italiano standard come default; supporto multilingua per le seconde generazioni.
- Analogie e riferimenti culturali **diversificati** e non stereotipati: il calcio non è l'unico sport, la pizza non è l'unico cibo, la trap non è l'unica musica.
- Test di bias periodici sul linguaggio generato (gender bias, bias geografico Nord/Sud, bias socio-economico).

### N7 — Trasparenza e spiegabilità

- Lo studente può sempre chiedere "perché mi stai mostrando questo?" e ottenere una spiegazione comprensibile.
- Il docente vede sempre quali nodi del KG il sistema sta usando per ogni decisione, e quali transizioni di stato sono avvenute e per quale ragione.
- **Audit trail completo**: chi ha generato cosa, quando, con quale prompt e modello; tutti gli override docente con motivazione (F11.12); tutte le operazioni di anagrafica/consenso (F14.10).
- I limiti del sistema sono dichiarati esplicitamente: non promettere di "sostituire" lo studio, ma di affiancarlo.

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
- % studenti che dichiarano di sentirsi "meno ansiosi" sulle verifiche di Informatica
- Tasso di abbandono volontario
- Numero di interventi del Safeguarding Agent per categoria

### 8.4 KPI di efficienza docente
- Ore risparmiate dal docente nella correzione
- % di docenti che dichiarano la dashboard "utile" o "molto utile" (semestrale)

### 8.5 KPI per il bilinguismo e l'inclusione (F13)
- Tempo medio di onboarding di uno studente non italofono fino al primo concetto consolidato (target: ≤ 2 settimane)
- Δ punteggio tra verifica N e N+1 per studenti con lingua nativa valorizzata (≥ Δ medio di classe)
- % di concetti per cui lo studente bilingue passa autonomamente dalla colonna nativa a quella ufficiale
- NPS specifico degli studenti bilingue
- Tasso di disattivazione spontanea del bilinguismo a fine anno (alto = buon segnale)

### 8.6 KPI per il caricamento e l'uso delle lezioni del docente (F2-A)
- % di lezioni svolte in aula effettivamente caricate in MAESTRO entro 7 giorni
- % di contenuti generati per studenti che attingono primariamente alle lezioni del docente
- Qualità percepita dal docente delle trascrizioni automatiche (CSAT, target ≥ 4/5)

### 8.7 KPI sul ciclo di chiusura delle lacune (F11)
- **Tempo medio rosso → verde** per studente (target: ≤ 21 giorni dopo il rilevamento)
- **% lacune chiuse** entro 7 / 14 / 30 giorni
- **Tasso di regressione**: % di nodi che riaprono dopo aver raggiunto `da_consolidare` o `consolidato` (target: < 15%)
- **% consolidamenti autonomi** vs forzati via override docente (target: ≥ 90% autonomi)
- **Numero medio di lacune aperte** contemporaneamente per studente (target: < 4)
- **Tasso di chiusura al primo tentativo** del mini-quiz (target: ≥ 60%)
- **Lacune persistenti**: numero di nodi in stato `lacuna` o `in_recupero` da più di 14 giorni (target: ridurre del 50% trimestre su trimestre)

### 8.8 Target di riferimento (12 mesi dopo rilascio)
- +20% sul Δ punteggio verifica N→N+1
- 80% adozione attiva tra gli studenti della scuola pilota
- 70% NPS studenti
- 50% riduzione del tempo docente sulla correzione
- 75% delle lacune rilevate effettivamente portate a `consolidato` entro 30 giorni

---

## 9. Roadmap

### MVP (6 mesi) — "Il caso 5AI scalato con ciclo di chiusura"
Coperti integralmente:
- F1 (compresi F1.6–F1.10: livello scolastico e granularità)
- F2 (A+B) operativo: il docente può caricare lezioni audio/video con trascrizione automatica e mapping concettuale
- F4 diagnostica formativa con transizioni di stato sul KMM
- F5 generazione documenti testuali personalizzati
- **F11 ciclo di chiusura completo**: macchina a stati, mini-quiz, almeno un retention check (D+7), heatmap dello studente in vista base, aggregazione macro/micro, override docente tracciato
- **F14 anagrafica, consenso, iscrizione** in versione amministrata
- F13 in versione minima: lingua ufficiale di corso definibile, bilinguismo per 2 lingue pilota (ucraino e arabo), layout a due colonne solo nei documenti testuali
- Dashboard docente base con vista classe e vista studente
- 1 scuola pilota, 1 classe, 1 docente

KPI focus: efficacia del documento di ripasso, tempo medio rosso → giallo, % lacune chiuse entro 14 giorni, qualità trascrizione lezioni, indicatori di inclusione per studenti bilingui.

### V1 (12 mesi) — "Multimodale e adattivo"
- F6 podcast a due voci (incluso cross-language bilingue)
- F7 gamification con quest e badge bilingui, badge "Chiudi-lacune"
- F9 accessibilità completa
- **F11 completo**: tutti e tre i retention check (D+3, D+7, D+21), heatmap di classe, alert lacune persistenti, override docente con pannello dedicato
- **F14 in modalità self-service** via SPID/QR
- F11 spaced repetition completo
- Estensione bilinguismo a 6 lingue (aggiunte: russo, albanese, rumeno, cinese mandarino) con revisori madrelingua a contratto
- 3 scuole pilota, 6 classi

### V2 (18-24 mesi) — "Ecosistema"
- F10 articolazione completa (animazioni, simulazioni)
- F12 completo (dashboard docente avanzata, generazione verifiche)
- Bilinguismo a regime su tutte le 12 lingue di F13.6
- Integrazione registri elettronici (Argo, ClasseViva, Spaggiari) per importazione massiva anagrafica
- Modello federato per uso multi-scuola
- Studente iscritto a più corsi (anagrafica + iscrizione separate ora effettivamente sfruttate)
- Doppia dimensione di padronanza per studenti bilingui (concettuale vs lessicale-tecnica)
- Eventuale decay temporale (open question)
- Apertura ad altre materie (matematica, fisica) — vedi §11

---

## 10. Rischi e mitigazione

| Rischio | Impatto | Probabilità | Mitigazione |
|---|---|---|---|
| LLM produce errori didattici (allucinazioni) | Alto | Medio | RAG su materiale ufficiale, validazione docente sempre obbligatoria, segnalazione facile da parte dello studente |
| Resistenza dei docenti (timore di sostituzione) | Alto | Alto | Co-progettazione, posizionamento esplicito come "strumento del docente". Quick win sul carico di correzione |
| Famiglie diffidenti sui dati dei minori | Alto | Alto | Privacy by design, trasparenza totale, opt-in granulare (F14.3), comunicazione chiara |
| Studenti che si appoggiano per copiare i compiti | Medio | Alto | Modalità "no completion"; rilevamento intent di copiatura |
| Bias culturale nelle analogie | Medio | Medio | Bias audit periodico, libreria di analogie diversificata, feedback diretto |
| Gamification che induce ansia o dipendenza | Alto | Medio | Anti-pattern espliciti, opt-out totale, monitoraggio benessere |
| Carico cognitivo eccessivo (troppa scelta) | Medio | Medio | Default intelligenti dal profilo; lo studente non deve configurare nulla per iniziare |
| Dipendenza tecnologica → perdita di autonomia | Alto | Medio | Modalità "autopilot off" periodica |
| Costi LLM elevati a regime | Medio | Alto | Caching aggressivo, modelli misti, batch generation overnight |
| Bassa qualità della traduzione in lingue meno diffuse | Alto | Medio | Revisione madrelingua periodica, glossario tecnico controllato |
| Stigma per lo studente bilingue | Medio | Medio | Modalità di lettura privata; il bilinguismo non appare in proiezioni di classe |
| Studente legge solo la colonna nativa | Alto | Medio | Rilevamento comportamentale (F13.20), esercizi di transizione |
| Lezioni del docente di qualità eterogenea | Medio | Alto | Strumenti di assistenza alla preparazione, formazione docenti |
| **Mismatch di granularità** (studente di biennio sopraffatto da micro-nodi) | Alto | Medio | Default per livello scolastico (F1.8), test usabilità con classi reali, revisione semestrale |
| **Override docente abusato** (uso per chiudere lacune senza prova oggettiva, per "ripulire" la heatmap) | Alto | Medio | Motivazione obbligatoria (F11.12), audit log visibile al coordinatore, KPI distinto "consolidamenti autonomi vs forzati" (§8.7) per rendere visibile il pattern, formazione esplicita |
| **Mappa della conoscenza percepita come strumento di sorveglianza** dello studente | Alto | Medio | Tono positivo dei messaggi sui rossi, presentazione del rosso sempre con la missione di recupero allegata, no esposizione comparativa, controllo dello studente sulla condivisione |
| **Lacuna non rilevata** (errore di mapping del Diagnostic Agent: lo studente sbaglia ma il sistema non se ne accorge) | Alto | Medio | Validazione docente obbligatoria sui mapping in fase di setup di una verifica nuova, feedback loop su falsi negativi, KPI di copertura |

---

## 11. Considerazioni di estensibilità

Sebbene MAESTRO sia nato per l'Informatica, l'architettura non lo lega a una materia specifica. Le componenti riusabili in altre discipline:

- **Knowledge graph del programma con granularità adattiva**: applicabile a qualunque materia con prerequisiti gerarchici.
- **Mappa della conoscenza a stati e ciclo di chiusura**: pienamente trasversale; è probabilmente la parte più riusabile del sistema.
- **Diagnostica dell'errore**: richiede strutture diverse per discipline non procedurali (analisi del testo per Italiano, costruzione geometrica per Geometria).
- **Articolazione multimodale, gamification, accessibilità, podcast, bilinguismo**: trasversali.
- **Anagrafica, consenso, iscrizione (F14)**: completamente indipendenti dalla materia.

Materie più affini per pilot V2/V3:
1. Matematica (struttura logica simile, errori meccanici ben identificabili, micro-nodi naturali)
2. Fisica
3. Lingue straniere (Duolingo come benchmark di gamification)

---

## 12. Riferimenti e ispirazioni

- **NotebookLM** (Google) — formato podcast a due voci
- **Khanmigo** (Khan Academy) — tutoring conversazionale, principio "non risolvere ma far ragionare"
- **Duolingo** — gamification non tossica, spaced repetition, modello a corone/stati di abilità
- **Anki** e **SuperMemo** — algoritmi di spaced repetition (SM-2, FSRS) come riferimento per F11.10
- **Bloom 2-sigma problem** (B. Bloom, 1984) — la giustificazione scientifica del tutoring personalizzato
- **Lavoro pregresso su MAESTRO per l'ITT di Ostuni**
- **WCAG 2.1** — standard di accessibilità
- **GDPR Art. 8 e Art. 9** — trattamento dati dei minori e categorie particolari
- **Linee guida MIUR sull'IA a scuola** (in evoluzione)

---

## 13. Open question per la fase successiva

1. **Scelta del LLM principale**: frontier proprietario vs open source self-hosted.
2. **Modello di rilascio**: SaaS dell'editore, on-premise per istituto, o ibrido.
3. **Pricing per la scuola**: gratuito per studenti, a carico della scuola, o cofinanziato (PNRR, fondi MIUR).
4. **Governance**: chi possiede i dati di apprendimento e in particolare la cronologia degli stati.
5. **Certificazioni**: serve una certificazione MIUR specifica per software didattico con AI.
6. **Studio di efficacia**: studio randomizzato su 2 classi (una con MAESTRO, una di controllo) prima di scalare oltre il MVP.
7. **Banca domande per i mini-quiz** (F11.8): chi la cura? Docente, casa editrice, banca generata da AI con validazione retroattiva? Decisione architetturale rinviata.
8. **Regola di aggregazione macro/micro** (F11.11): la regola "stato peggiore" è didatticamente corretta? Validare con docenti pilota. Alternativa da testare: media pesata sui prerequisiti.
9. **Decay temporale** (rinviato fuori v0.2): da affrontare in V2 dopo aver osservato dati reali sul tasso di regressione.
10. **Doppia dimensione di padronanza per bilingui** (rinviato fuori v0.2): da affrontare quando il bilinguismo MVP sarà maturato in V1.

---

*Documento di lavoro v0.2. Da iterare con docenti, studenti pilota e team tecnico.*
