# Specifiche Schermate — MAESTRO v1.0

**Versione:** v1.0
**Allineato a:** MAESTRO_use_cases_v1.md, MAESTRO_requisiti_v0.3.md
**Convenzione ID:** `SCR-<area>-<NN>` — Aree: ST (Studente), DOC (Docente), FAM (Famiglia), AS (Admin), COR (Coordinatore)
**Colori semaforo di riferimento:** grigio (#9E9E9E), bianco (#FFFFFF), rosso (#E53935), arancione (#FB8C00), giallo (#FDD835), verde (#43A047)

---

## Principi di design trasversali

- **Mai solo colore**: ogni stato è rappresentato da colore + icona + testo (F9.3, daltonismo)
- **Font adattabile**: default (Inter), OpenDyslexic, Atkinson Hyperlegible (F9.1)
- **Dimensione testo**: 12-24pt, regolabile dall'utente (F9.4)
- **Temi**: chiaro, scuro, seppia (F9.5)
- **Alto contrasto**: modalità dedicata (F9.2)
- **Navigazione tastiera completa**: tutti gli elementi interattivi raggiungibili con Tab (N5)
- **Screen reader**: ARIA labels su tutti gli elementi, live regions per aggiornamenti dinamici (N5)
- **Tono dei rossi**: sempre accompagnato da missione di recupero — "una porta aperta, non un marchio" (N3)
- **Nessun confronto tra studenti**: in nessuna schermata student-facing

---

# A. App Studente (Mobile-first)

### SCR-ST-01 — Login e prima attivazione

**Use case**: UC-ST-00 | **Requisiti**: F14.6 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Schermata di accesso per lo studente. In prima attivazione presenta il flusso di accettazione termini e conferma consenso. Per accessi successivi, login diretto.

**Header**
- Logo MAESTRO (centrato)
- Nessun menu (pre-autenticazione)

**Area principale — Login**
- **Username** — text field — placeholder "Il tuo nome utente" — obbligatorio
- **Password** — password field — placeholder "La tua password" — obbligatorio, icona mostra/nascondi
- **Bottone "Accedi"** — primary button — azione: autenticazione — disabilitato se campi vuoti
- **Link "Accedi con la tua scuola"** — link — azione: redirect a SSO scolastico (V1: attivo; MVP: nascosto se SSO non configurato)
- **Link "Hai dimenticato la password?"** — link — azione: redirect a IT scuola

**Area principale — Prima attivazione (post-login, se account in stato "attesa attivazione")**
- **Titolo** — "Benvenuto in MAESTRO!" — h1
- **Termini d'uso** — scrollable text area — linguaggio per minori, non legalese
- **Checkbox "Ho letto e accetto i termini d'uso"** — checkbox — obbligatorio per procedere
- **Riepilogo consenso** — card read-only — mostra le 5 categorie con stato concesso/negato (registrato dalla famiglia)
- **Checkbox "Ho preso visione del consenso"** — checkbox — obbligatorio
- **Bottone "Inizia"** — primary button — azione: attiva account, redirect a onboarding (UC-ST-01)

**Variazioni di stato**
- *Login standard*: solo form username/password
- *Prima attivazione*: form login + flusso termini/consenso
- *Credenziali errate*: banner errore "Credenziali non valide" (generico, no dettagli)
- *Account sospeso*: banner "Contatta la segreteria della tua scuola"
- *Consenso mancante*: banner "Il consenso della tua famiglia non è ancora stato registrato"
- *Troppi tentativi (>5)*: banner "Attendi 15 minuti prima di riprovare"

**Accessibilità (F9)**
- Etichette ARIA su tutti i campi — aria-label="Nome utente", aria-label="Password"
- Focus automatico sul primo campo al caricamento
- Messaggio di errore collegato al campo con aria-describedby
- Bottone "Accedi" raggiungibile con Tab+Invio

**Comportamento bilingue (F13)**
- Se lingua nativa valorizzata e consenso (b): termini d'uso mostrati anche in traduzione

---

### SCR-ST-02 — Onboarding e profilazione

**Use case**: UC-ST-01 | **Requisiti**: F3.1–F3.5 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Quiz interattivo di 5-10 minuti che presenta lo stesso concetto in 4 modalità per determinare il profilo di learning style.

**Header**
- Logo MAESTRO (piccolo, angolo sinistro)
- **Progress bar** — orizzontale — mostra avanzamento (es. "Passo 2 di 5")
- **Bottone "Salta"** — text button — azione: salta al passo successivo (il sistema registra non-interazione)

**Area principale — Schermata benvenuto (primo step)**
- **Titolo** — "Scopriamo come preferisci studiare!" — h1
- **Sottotitolo** — "Non è un test con voto, è solo per capire cosa funziona meglio per te." — body
- **Bottone "Iniziamo!"** — primary button — azione: avvia il primo concetto

**Area principale — Step concetto (step 2-5)**
- **Titolo concetto** — es. "Cos'è una variabile?" — h2
- **4 card modalità** — layout griglia 2×2:
  - **Card "Leggi"** — icona libro — azione: espande un breve testo esplicativo
  - **Card "Ascolta"** — icona cuffia — azione: avvia audio breve (30-60s)
  - **Card "Guarda"** — icona occhio — azione: mostra immagine/diagramma
  - **Card "Prova"** — icona mano — azione: mostra mini-esercizio interattivo
- Ogni card traccia: apertura, tempo di permanenza, completamento
- **Bottone "Avanti"** — primary button — azione: passa al concetto successivo — abilitato dopo interazione con almeno 1 card

**Area principale — Risultato (ultimo step)**
- **Titolo** — "Ecco il tuo profilo di apprendimento" — h1
- **Radar chart** — 5 assi: visivo, uditivo, cinestesico, riflessivo, sociale — con etichette e valori %
- **Descrizione testuale** — es. "Ti piace imparare guardando e facendo. Preferisci spiegazioni visive e pratiche."
- **Dropdown "Tono preferito"** — opzioni: Confidenziale ("tu, frasi brevi"), Neutro ("tu, tono calmo"), Formale ("lei, frasi articolate")
- **Toggle "Lunghezza"** — opzioni: Sintesi (2-3 concetti) / Approfondimento (6-8 concetti)
- **Bottone "Va bene così"** — primary button — azione: salva profilo, redirect a home
- **Link "Voglio modificare"** — text link — azione: rende editabili i parametri del radar

**Variazioni di stato**
- *Consenso (a) negato*: il quiz è semplificato (nessun tracciamento comportamentale); profilo neutro
- *Step interrotto*: al prossimo accesso riprende dal punto interrotto
- *Audio non disponibile*: card "Ascolta" mostra badge "Non disponibile"

**Accessibilità (F9)**
- Card navigabili da tastiera con Tab
- Radar chart ha descrizione testuale equivalente per screen reader
- Audio ha trascrizione disponibile

---

### SCR-ST-03 — Home Dashboard studente

**Use case**: navigazione centrale | **Requisiti**: F11.6, F7.5 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Schermata principale dello studente. Mostra lo stato attuale dell'apprendimento, le azioni prioritarie e gli accessi rapidi.

**Header**
- Logo MAESTRO (angolo sinistro)
- **Nome studente** — testo — angolo destro
- **Icona profilo** — avatar — azione: redirect a SCR-ST-09 (Profilo)
- **Icona notifiche** — badge con conteggio — azione: apre pannello notifiche

**Sezione "Le tue missioni"** (card carousel orizzontale)
- Per ogni lacuna aperta o in recupero:
  - **Nome concetto** — testo bold
  - **Stato** — badge con colore + icona + testo (es. 🔴 "Lacuna" oppure 🟠 "In recupero")
  - **Azione suggerita** — testo (es. "Inizia il recupero" o "Completa il quiz")
  - **Bottone azione** — primary — azione: redirect a SCR-ST-06 (Missione) o SCR-ST-07 (Quiz)
- Se nessuna lacuna: messaggio "Nessuna missione aperta — sei in pari!" con icona celebrativa

**Sezione "La tua mappa"** (mini-preview)
- **Grafo semplificato** — soli macro-nodi con colori semaforo — navigabile con tap
- **Bottone "Vedi mappa completa"** — azione: redirect a SCR-ST-04

**Sezione "Ultimi documenti"** (lista verticale, max 3)
- Per ogni documento recente: titolo concetto, data, tipo (ripasso/quiz/percorso)
- **Bottone "Apri"** — azione: redirect a SCR-ST-08

**Footer fisso** (tab bar)
- **Home** (icona casa) — schermata attuale
- **Mappa** (icona grafo) — redirect a SCR-ST-04
- **Profilo** (icona persona) — redirect a SCR-ST-09

**Variazioni di stato**
- *Primo accesso (post-onboarding)*: sezione missioni vuota, messaggio di benvenuto "Il tuo docente caricherà presto i materiali"
- *Gamification attiva (V1)*: sezione aggiuntiva con streak, XP, livello
- *Notifiche retention check*: badge rosso su icona notifiche

**Accessibilità (F9)**
- Tutte le sezioni hanno heading levels corretti (h2, h3)
- Card carousel navigabile con swipe e con frecce tastiera
- Colori semaforo sempre accompagnati da icona + testo

**Comportamento bilingue (F13)**
- Nomi dei concetti in doppia lingua se bilinguismo attivo

---

### SCR-ST-04 — Mappa della conoscenza

**Use case**: UC-ST-13 | **Requisiti**: F11.1–F11.3, F11.11 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Visualizzazione interattiva della mappa della conoscenza dello studente. Grafo navigabile con nodi colorati per stato semaforo.

**Header**
- **Bottone back** — azione: torna alla home
- **Titolo** — "La tua mappa" — h1
- **Toggle granularità** (solo per triennio) — segmented control "Macro" / "Micro" — azione: espande/comprime micro-nodi

**Area principale**
- **Grafo interattivo** — nodi disposti gerarchicamente (albero o grafo a forza)
- Ogni nodo mostra:
  - **Nome concetto** — testo (troncato se lungo, espandibile con tap)
  - **Icona stato** — cerchio colorato + icona interna (vedi legenda)
  - **Etichetta stato** — testo sotto l'icona (es. "Consolidato")
- **Archi prerequisito** — linee direzionali tra nodi
- **Zoom** — pinch-to-zoom (mobile), scroll (desktop)
- **Pan** — drag per navigare
- **Tap su nodo** — apre SCR-ST-05 (Dettaglio nodo)

**Legenda** (collassabile, angolo in basso)
- Grigio + cerchio vuoto = "Non introdotto"
- Bianco + cerchio con bordo = "Introdotto"
- Rosso + X = "Lacuna"
- Arancione + freccia = "In recupero"
- Giallo + spunta bordo = "Da consolidare"
- Verde + spunta piena = "Consolidato"

**Variazioni di stato**
- *Biennio*: toggle granularità non visibile; solo macro-nodi
- *Triennio macro*: solo macro-nodi; tap su macro mostra conteggio micro per stato
- *Triennio micro*: macro-nodi espansi con micro-nodi figli
- *Nessun nodo*: messaggio "Il tuo docente sta preparando il programma"

**Accessibilità (F9)**
- Mappa esplorabile da tastiera: Tab tra nodi, Invio per aprire dettaglio, frecce per navigazione
- Ogni nodo ha aria-label con: nome concetto + stato testuale
- Zoom accessibile con +/- da tastiera
- Legenda sempre visibile come testo (non solo tooltip)

**Comportamento bilingue (F13)**
- Nomi concetti in doppia lingua se bilinguismo attivo

---

### SCR-ST-05 — Dettaglio nodo

**Use case**: da UC-ST-13 | **Requisiti**: F11.5, F11.6 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Pannello dettaglio per un singolo nodo della mappa. Mostra stato, cronologia, materiali e azioni disponibili.

**Header**
- **Bottone back** — azione: torna alla mappa
- **Nome concetto** — h1
- **Badge stato** — colore + icona + testo (es. 🔴 "Lacuna")

**Sezione "Stato attuale"**
- **Indicatore grande** — cerchio colorato con icona e testo stato
- **Data ultimo aggiornamento** — "Ultimo aggiornamento: 15/05/2026"

**Sezione "Cronologia"** (timeline verticale)
- Per ogni transizione: data, stato precedente → stato nuovo, causa (es. "Errore in verifica PHP del 12/05")
- Override docente evidenziati con icona speciale e motivazione visibile

**Sezione "Azioni"** (visibile solo per stati `lacuna` e `in_recupero`)
- **Bottone "Avvia recupero"** (se `lacuna`) — primary — azione: redirect a SCR-ST-06
- **Bottone "Continua il percorso"** (se `in_recupero`) — primary — azione: redirect a SCR-ST-06
- **Bottone "Vai al quiz"** (se `in_recupero` con percorso completato) — primary — azione: redirect a SCR-ST-07

**Sezione "Materiali disponibili"**
- Lista: documento di ripasso, segmento lezione (con timestamp), esercizi
- Per ogni materiale: icona tipo, titolo, bottone "Apri"

**Accessibilità (F9)**
- Timeline navigabile da tastiera
- Ogni voce cronologia ha ARIA label completo

---

### SCR-ST-06 — Missione di recupero

**Use case**: UC-ST-15 | **Requisiti**: F11.6, F11.7 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Percorso di studio personalizzato per chiudere una lacuna. Presenta gli step in sequenza con barra di avanzamento.

**Header**
- **Bottone back** — azione: torna alla mappa (lo stato resta `in_recupero`)
- **Titolo** — "Missione: [nome concetto]" — h1
- **Progress bar** — orizzontale — "Step 2 di 4"

**Area principale — Lista step**
- Per ogni step del percorso:
  - **Icona tipo** — 📄 documento / 🎧 audio / 🎬 video lezione / ✏️ esercizio
  - **Titolo step** — es. "Leggi la spiegazione" o "Guarda il segmento della lezione"
  - **Stato step** — completato (spunta verde) / corrente (evidenziato) / futuro (grigio)
  - **Tap** — apre il contenuto dello step (SCR-ST-08 per documento, player per video/audio)
- Ultimo step: **"Quiz di chiusura"** — icona quiz — tap redirect a SCR-ST-07

**Bottone fisso in basso**
- **"Ho completato, vai al quiz"** — primary button — azione: redirect a SCR-ST-07 — abilitato solo se almeno 1 step di studio completato

**Variazioni di stato**
- *Primo tentativo*: tutti gli step iniziali
- *Secondo tentativo (50-79% al quiz)*: step diversi dal primo tentativo (articolazione variata)
- *Percorso in corso (interrotto)*: riprende dall'ultimo step completato

**Accessibilità (F9)**
- Lista step navigabile da tastiera
- Stato di ogni step comunicato via screen reader

---

### SCR-ST-07 — Mini-quiz di chiusura

**Use case**: UC-ST-16 | **Requisiti**: F11.8, F11.9 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Quiz di 3-5 domande mirate al micro-nodo per verificare la chiusura della lacuna.

**Header**
- **Titolo** — "Quiz: [nome concetto]" — h1
- **Progress** — "Domanda 2 di 5"

**Area principale — Domanda singola**
- **Testo domanda** — h2 — in lingua ufficiale del corso
- **Opzioni risposta** — radio button (scelta singola) o checkbox (scelta multipla)
  - 4 opzioni per domanda
  - Tap seleziona, secondo tap deseleziona
- **Bottone "Conferma"** — primary — azione: registra risposta, passa a domanda successiva

**Area principale — Risultato (dopo ultima domanda)**
- **Punteggio** — grande, centrato — es. "4 su 5 — 80%"
- **Messaggio**:
  - >=80%: "Ottimo lavoro! Ora consolidiamo nel tempo." (sfondo verde chiaro)
  - 50-79%: "Ci sei quasi! Proviamo con un altro approccio." (sfondo giallo chiaro)
  - <50%: "Non preoccuparti, ne parliamo con il prof." (sfondo arancione chiaro, MAI rosso)
- **Stato nodo aggiornato** — badge con nuovo stato (giallo `da_consolidare` o arancione `in_recupero`)
- **Dettaglio per domanda** — lista espandibile: domanda, risposta data, risposta corretta, spiegazione breve
- **Bottone "Torna alla mappa"** — azione: redirect a SCR-ST-04
- **Bottone "Riprova con un nuovo percorso"** (solo se 50-79%) — azione: redirect a SCR-ST-06 con nuova articolazione

**Variazioni di stato**
- *Quiz in corso*: una domanda alla volta, progress bar avanza
- *Risultato positivo (>=80%)*: festivo ma non esagerato
- *Risultato parziale (50-79%)*: incoraggiante, propone alternativa
- *Risultato negativo (<50%)*: rassicurante, non punitivo

**Accessibilità (F9)**
- Opzioni radio navigabili con frecce tastiera
- Risultato annunciato da screen reader
- Colore sfondo risultato mai solo colore: sempre accompagnato da icona e testo

**Comportamento bilingue (F13)**
- Quiz in lingua ufficiale (F13.19) — no traduzione durante valutazione
- "Lettura assistita" in lingua nativa disponibile SOLO durante lo studio, non nel quiz

---

### SCR-ST-08 — Documento di ripasso

**Use case**: UC-ST-02 | **Requisiti**: F5.1–F5.5 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Visualizzazione del documento di ripasso personalizzato con la struttura a 4 blocchi.

**Header**
- **Bottone back** — azione: torna alla schermata precedente
- **Titolo concetto** — h1
- **Bottone "Perché questo?"** — icona info — azione: apre SCR-ST-10 (Spiegabilità)

**Area principale**
- **Blocco 1 — "Il tuo errore"** — card con bordo giallo — mostra il codice errato dello studente con highlighting giallo — etichetta "ERRATO" per accessibilità
- **Blocco 2 — "Perché succede"** — card — spiegazione con analogia personalizzata (es. sportiva, videoludica)
- **Blocco 3 — "Come si fa giusto"** — card con bordo verde — mostra il codice corretto con highlighting verde — etichetta "CORRETTO"
- **Blocco 4 — "Ricordati"** — card evidenziata — regola da memorizzare, in formato conciso

**Layout bilingue** (se attivo)
- Ogni blocco è diviso in due colonne: sinistra = lingua ufficiale, destra = lingua nativa
- Termini tecnici in entrambe le lingue con originale in parentesi

**Barra azioni in basso**
- **Bottone "Ascolta"** — icona cuffia — azione: avvia versione audio (V1) — MVP: nascosto se non disponibile
- **Bottone "Esercizio"** — icona matita — azione: apre esercizio guidato correlato

**Variazioni di stato**
- *Monolingue*: layout a colonna singola
- *Bilingue*: layout a due colonne
- *Documento non ancora generato*: indicatore di caricamento con messaggio "Stiamo preparando il tuo documento..."
- *Documento modificato dal docente*: badge "Rivisto dal Prof." in alto

**Accessibilità (F9)**
- Code blocks con etichette "ERRATO" e "CORRETTO" (non solo colore)
- Font adattabile: rispetta la scelta di profilo
- Contenuto leggibile da screen reader in ordine logico

---

### SCR-ST-09 — Profilo e preferenze

**Use case**: UC-ST-07 | **Requisiti**: F3.4–F3.6, F8, F9, F13.9 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Pannello completo per consultare e modificare il profilo di apprendimento e le preferenze di accessibilità.

**Header**
- **Bottone back** — azione: torna alla home
- **Titolo** — "Il mio profilo" — h1

**Sezione "Come preferisco studiare"**
- **Radar chart** — 5 assi (visivo, uditivo, cinestesico, riflessivo, sociale) — interattivo: tap su asse per modificare
- **Descrizione testuale** — riassunto in linguaggio naturale
- **Link "Modifica manualmente"** — apre slider per ogni dimensione

**Sezione "Preferenze contenuti"**
- **Tono** — segmented control — Confidenziale / Neutro / Formale
- **Lunghezza** — segmented control — Sintesi / Approfondimento
- **Canale preferito** — segmented control — Testo / Audio / Misto — con opzione "Forzare solo questo canale"

**Sezione "Accessibilità"**
- **Font** — dropdown — Default (Inter) / OpenDyslexic / Atkinson Hyperlegible
- **Dimensione testo** — slider — 12pt ← → 24pt — con anteprima live
- **Tema** — segmented control — Chiaro / Scuro / Seppia
- **Alto contrasto** — toggle on/off
- **Animazioni ridotte** — toggle on/off (F9.7)
- **Anteprima** — box che mostra testo campione con le impostazioni correnti

**Sezione "Bilinguismo" (se consenso b attivo)**
- **Lingua nativa** — read-only — es. "Ucraino"
- **Toggle bilinguismo** — on/off — stato attuale evidenziato
- **Descrizione** — "Se attivo, i contenuti saranno in italiano e ucraino"

**Sezione "Gamification" (V1)**
- **Toggle gamification** — on/off
- **Descrizione** — "Se disattivi, XP, badge e streak scompaiono. Il tuo progresso didattico resta intatto."

**Sezione "I miei dati"**
- **Link "Richiedi cancellazione dati"** — azione: redirect a SCR-ST-14

**Bottone fisso in basso**
- **"Salva modifiche"** — primary — azione: salva tutte le preferenze — disabilitato se nulla è cambiato

**Accessibilità (F9)**
- Tutti i controlli navigabili da tastiera
- Slider dimensione testo con step da tastiera (frecce)
- Radar chart ha descrizione testuale alternativa

---

### SCR-ST-10 — Pannello spiegabilità

**Use case**: UC-ST-06 | **Requisiti**: N7 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Pannello sovrapposto (bottom sheet) che spiega perché un contenuto è stato mostrato allo studente.

**Area principale**
- **Titolo** — "Perché ti sto mostrando questo?" — h2
- **Sezione "Concetti coinvolti"** — lista di nodi KG con stato — es. "Sessione PHP (Lacuna)"
- **Sezione "Il tuo profilo"** — riassunto: "Preferisci spiegazioni visive con tono confidenziale"
- **Sezione "Cosa è successo"** — timeline breve delle transizioni recenti — es. "12/05: errore in verifica → lacuna"
- **Link "Spiegami più semplicemente"** — azione: riformula con linguaggio più semplice
- **Bottone "Chiudi"** — azione: chiude il pannello

**Accessibilità (F9)**
- Pannello annunciato come dialog da screen reader
- Focus trap: Tab rimane nel pannello fino a chiusura
- Chiudibile con Esc

---

### SCR-ST-14 — Richiesta oblio dati

**Use case**: UC-ST-11 | **Requisiti**: F14.9, N1 | **Priorità**: MVP | **Piattaforma**: Mobile

**Descrizione**
Flusso di richiesta cancellazione dati con doppia conferma.

**Area principale**
- **Titolo** — "Cancellazione dei tuoi dati" — h1
- **Spiegazione** — testo in linguaggio per minori: "Se procedi, verranno eliminati: il tuo profilo, la cronologia, la mappa, i documenti, gli audio. Solo dati anonimi (se il consenso lo prevede) verranno conservati."
- **Checkbox "Ho capito le conseguenze"** — obbligatorio
- **Bottone "Richiedi cancellazione"** — danger button (rosso) — azione: prima conferma
- **Dialog di conferma** — "Sei sicuro? Questa azione è irreversibile." — bottoni "Annulla" (secondary) e "Conferma cancellazione" (danger)
- **Messaggio post-conferma** — "La tua richiesta è stata inoltrata. Verrà elaborata entro 30 giorni."

**Accessibilità (F9)**
- Dialog di conferma annunciato da screen reader
- Bottone danger ha aria-label descrittivo

---

# B. Dashboard Docente (Web)

### SCR-DOC-01 — Login docente

**Use case**: UC-DOC-00 | **Requisiti**: F14.6 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Schermata di accesso per il docente. Supporta credenziali locali e SSO scolastico.

**Header**
- Logo MAESTRO (sinistra) + label "Docente" (destra)
- Nessun menu (pre-autenticazione)

**Area principale — Login**
- **Email / Username** — text field — placeholder "La tua email o username" — obbligatorio
- **Password** — password field — placeholder "La tua password" — obbligatorio, icona mostra/nascondi
- **Bottone "Accedi"** — primary button — azione: autenticazione — disabilitato se campi vuoti
- **Link "Accedi con SSO scolastico"** — link — azione: redirect a IdP scolastico
- **Link "Password dimenticata?"** — link — azione: email di reset

**Note**
- Al primo accesso, redirect a wizard setup corso (SCR-DOC-03)
- Se docente ha più classi, dopo login viene mostrata la selezione classe

---

### SCR-DOC-02 — Home dashboard docente

**Use case**: — (navigazione centrale) | **Requisiti**: F12.7, F11.14, F12.1, F16.1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Schermata principale del docente. Offre una vista d'insieme dello stato delle classi assegnate con indicatori rapidi sulle lacune.

**Header**
- Logo MAESTRO (sinistra)
- **Selettore classe** — dropdown — lista classi assegnate — es. "3AI — Informatica"
- **Icona notifiche** — badge con contatore — es. "3 studenti in rosso da >7gg"
- **Avatar/Menu utente** — dropdown: Profilo, Impostazioni, Logout

**Sidebar (sempre visibile)**
- Icona Home (Dashboard) — attiva
- Icona Classe (Vista classe)
- Icona Lezioni (Upload lezione)
- Icona Verifiche (Upload verifica)
- Icona KG (Editor KG) — V1
- Icona Impostazioni

**Area principale**
- **Card "Panoramica classe"** — statistiche aggregate:
  - Numero studenti totali
  - Distribuzione stati: N consolidato / N da consolidare / N in recupero / N lacuna / N introdotto
  - **Barra orizzontale segmentata** — colori + icone per ogni stato — proporzionale
- **Card "Alert lacune"** — lista studenti con stato lacuna da >N giorni:
  - Riga: nome studente (anonimizzato se impostazione attiva) — concetto — giorni in lacuna — bottone "Vedi mappa"
  - Ordinamento per anzianità (più vecchi prima)
- **Card "Attività recenti"** — feed cronologico:
  - Upload lezione (data, argomento)
  - Override effettuata (data, studente, nodo, motivazione)
  - Verifica caricata (data, classe)
- **Card "Prossimi suggerimenti"** — suggerimenti dal sistema:
  - "3 studenti hanno lacune su SQL JOIN — consigliata una lezione di rinforzo"
  - "Verifica prevista su array — 5 studenti non hanno ancora consolidato"

**Accessibilità (F9)**
- Sidebar navigabile con Tab e frecce
- Card annunciate come regions con aria-label
- Alert lacune annunciato con aria-live="polite"

---

### SCR-DOC-03 — Setup corso

**Use case**: UC-DOC-17, UC-DOC-09, UC-DOC-12 | **Requisiti**: F17.1, F17.2, F17.3, F1.6, F13.1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Wizard guidato per la configurazione iniziale di un corso. Viene proposto al primo accesso o alla creazione di un nuovo corso.

**Wizard — Step 1: Info corso**
- **Nome corso** — text field — es. "Informatica" — obbligatorio
- **Classe** — text field — es. "3AI" — obbligatorio
- **Anno scolastico** — dropdown — es. "2025-2026" — obbligatorio
- **Materia** — dropdown — lista materie supportate — obbligatorio
- **Livello scolastico** — dropdown — opzioni: "Secondaria di primo grado", "Biennio secondaria di secondo grado", "Triennio secondaria di secondo grado", "Post-diploma/ITS", "Formazione professionale" — obbligatorio (F1.6)
- **Lingua ufficiale** — dropdown — default: Italiano — obbligatorio (F13.1)
- **Bottone "Avanti"** — primary button

**Wizard — Step 2: Knowledge graph iniziale**
- **Opzione A** — "Usa modello standard per [materia]" — radio — carica KG predefinito
- **Opzione B** — "Carica il mio programma" — radio — abilita upload file (PDF/DOCX)
- **Opzione C** — "Parti da zero" — radio — KG vuoto, costruisci da lezioni
- **Anteprima KG** — visualizzazione grafo in sola lettura (se opzione A) — nodi = concetti, archi = prerequisiti
- **Bottone "Indietro"** — secondary button
- **Bottone "Avanti"** — primary button

**Wizard — Step 3: Iscrizione studenti**
- **Opzione A** — "Importa da registro elettronico" — radio — V1 (non disponibile MVP)
- **Opzione B** — "Carica file CSV" — radio — abilita upload CSV — formato: nome, cognome, email_famiglia
- **Opzione C** — "Aggiungi manualmente" — radio — tabella inline editabile
- **Tabella studenti** — colonne: Nome, Cognome, Email famiglia, Stato (attesa consenso / attivo) — inline editing
- **Bottone "Indietro"** — secondary button
- **Bottone "Completa setup"** — primary button — azione: crea corso, invia notifiche famiglie per consenso

**Note**
- Lo step 3 invia automaticamente le richieste di consenso alle famiglie (UC-FAM-01)
- Il corso rimane in stato "in preparazione" fino a >=1 studente attivo

---

### SCR-DOC-04 — Upload lezione

**Use case**: UC-DOC-01 | **Requisiti**: F2.1, F2.7, F2.8 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Schermata per il caricamento di materiale didattico (appunti, slide, registrazioni). Avvia il pipeline di ingestion e concept mapping.

**Header**
- Breadcrumb: Dashboard > Upload lezione

**Area principale**
- **Titolo lezione** — text field — es. "Lezione 12: SQL JOIN" — obbligatorio
- **Data lezione** — date picker — default: oggi — obbligatorio
- **Argomento/Modulo** — dropdown — lista nodi KG di livello alto — obbligatorio
- **Zona upload** — drag & drop + bottone "Scegli file":
  - Formati accettati: PDF, DOCX, PPTX, MP3, MP4, WAV
  - Dimensione massima: 500MB (audio/video), 50MB (documenti)
  - Barra di progresso upload
- **Note aggiuntive** — textarea — facoltativo — "Aggiungi indicazioni per il sistema"
- **Bottone "Carica e analizza"** — primary button — azione: avvia ingestion pipeline

**Area post-upload (sostituisce form dopo upload)**
- **Stato pipeline** — stepper orizzontale:
  1. Upload completato ✓
  2. Trascrizione in corso... / Completata ✓ (solo audio/video)
  3. Estrazione concetti in corso... / Completata ✓
  4. Mapping al KG in corso... / Completata ✓
- **Anteprima concetti estratti** — lista badge — es. "SQL JOIN", "INNER JOIN", "LEFT JOIN"
- **Link "Rivedi trascrizione"** — azione: apre SCR-DOC-05
- **Link "Valida mapping"** — azione: apre SCR-DOC-06

**Accessibilità (F9)**
- Zona drag & drop attivabile anche via tastiera (Enter/Space)
- Stepper annunciato con aria-live per progressi
- Formati accettati dichiarati come testo, non solo come tooltip

---

### SCR-DOC-05 — Editor trascrizione

**Use case**: UC-DOC-02 | **Requisiti**: F2.2, F2.3 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Editor per la revisione della trascrizione automatica di una lezione audio/video.

**Header**
- Breadcrumb: Dashboard > Upload lezione > Trascrizione

**Area principale**
- **Player audio/video** — mini player in alto — play/pause, seek, velocità (0.5x-2x)
- **Trascrizione** — textarea ricca — testo con timestamp — editabile
  - Evidenziazione sincronizzata: il paragrafo corrente si evidenzia durante la riproduzione
  - Click su paragrafo: player salta a quel timestamp
- **Pannello laterale destro** — "Concetti rilevati":
  - Lista badge per ogni concetto estratto dal paragrafo selezionato
  - Possibilità di aggiungere/rimuovere concetti manualmente

**Footer**
- **Bottone "Salva trascrizione"** — primary button
- **Bottone "Rigenera trascrizione"** — secondary button — azione: riavvia trascrizione da zero
- **Bottone "Annulla"** — text button

---

### SCR-DOC-06 — Validazione mapping concetti

**Use case**: UC-DOC-03 | **Requisiti**: F2.4 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Il docente rivede e valida il mapping automatico tra i concetti estratti dalla lezione e i nodi del Knowledge Graph.

**Header**
- Breadcrumb: Dashboard > Upload lezione > Validazione mapping

**Area principale — Vista split**
- **Colonna sinistra: Concetti estratti**
  - Lista di concetti — ogni riga: nome concetto, frammento di testo sorgente, confidence % del sistema
  - Icona stato: ✓ (mappato), ⚠ (suggerito, da validare), ✗ (non mappato)
  - Azione per riga: click per selezionare e mappare
- **Colonna destra: Knowledge Graph**
  - Visualizzazione grafo interattiva (zoom, pan)
  - Nodi evidenziati in base al mapping corrente
  - Click su nodo: seleziona come target per il concetto selezionato a sinistra
  - **Bottone "+ Nuovo nodo"** — azione: crea nuovo nodo nel KG (dialog con nome, descrizione, prerequisiti)

**Barra azioni**
- **Bottone "Accetta tutti i suggerimenti"** — secondary button — azione: conferma tutti i mapping suggeriti
- **Bottone "Salva mapping"** — primary button — azione: salva mapping validato
- **Contatore** — "12/15 concetti mappati"

**Accessibilità (F9)**
- Mapping eseguibile anche senza interazione grafo: lista testuale dei nodi KG come alternativa
- Stato mapping annunciato per screen reader

---

### SCR-DOC-07 — Upload verifica

**Use case**: UC-DOC-04 | **Requisiti**: F4.1, F4.2, F4.4, F4.6 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Caricamento di una verifica con associazione domande-concetti e inserimento voti per studente.

**Header**
- Breadcrumb: Dashboard > Verifiche > Upload

**Step 1: Definizione verifica**
- **Titolo verifica** — text field — es. "Verifica SQL — Novembre 2025" — obbligatorio
- **Data verifica** — date picker — obbligatorio
- **Tipo** — dropdown — "Scritta", "Orale", "Pratica" — obbligatorio

**Step 2: Domande e mapping**
- **Tabella domande** — inline editing:
  - Colonne: # domanda, Testo breve, Concetti associati (multi-select da KG), Peso (punti)
  - **Bottone "+ Aggiungi domanda"** — azione: nuova riga
  - **Bottone "Importa da file"** — azione: upload PDF/DOCX della verifica, estrazione automatica domande

**Step 3: Voti studenti**
- **Tabella voti** — inline editing:
  - Righe: studenti della classe
  - Colonne: Nome studente, Voto complessivo, per ogni domanda: punteggio ottenuto/massimo
  - Celle editabili con validazione (0 ≤ punteggio ≤ peso)
  - **Indicatore visivo** — celle con punteggio < 60% in arancione, < 40% in rosso
- **Bottone "Importa voti da CSV"** — azione: upload file CSV

**Step 4: Conferma**
- **Riepilogo** — media classe, distribuzione voti, concetti più problematici
- **Anteprima transizioni** — "Questa verifica causerà N transizioni di stato:" — lista
- **Bottone "Conferma e applica"** — primary button — azione: registra voti, trigger transizioni stato

**Accessibilità (F9)**
- Tabelle navigabili con tastiera (Tab tra celle, Enter per editare)
- Indicatore cromatico accompagnato da icona (⚠ per arancione, ✗ per rosso)

---

### SCR-DOC-08 — Vista classe / Heatmap

**Use case**: UC-DOC-06 | **Requisiti**: F11.14, F12.1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Vista aggregata della classe con heatmap delle lacune. Il docente visualizza lo stato di padronanza di ogni studente su ogni macro-argomento.

**Header**
- Breadcrumb: Dashboard > Classe > Heatmap
- **Selettore vista** — toggle: "Heatmap" | "Lista" — default: Heatmap
- **Filtro stato** — multi-select chips: tutti, lacuna, in_recupero, da_consolidare, consolidato
- **Filtro argomento** — dropdown: tutti / singolo macro-argomento

**Area principale — Vista Heatmap (default)**
- **Griglia** — righe: studenti (nome/ID), colonne: macro-concetti del KG
- **Celle** — colore + icona per stato:
  - Grigio (#9E9E9E) + icona cerchio vuoto = non_introdotto
  - Bianco (#FFFFFF) + icona cerchio mezzo = introdotto
  - Rosso (#E53935) + icona ✗ = lacuna
  - Arancione (#FB8C00) + icona freccia su = in_recupero
  - Giallo (#FDD835) + icona orologio = da_consolidare
  - Verde (#43A047) + icona ✓ = consolidato
- **Hover su cella** — tooltip: "Mario R. — SQL JOIN — lacuna da 5 giorni — 2 missioni tentate"
- **Click su cella** — redirect a SCR-DOC-09 (mappa studente singolo)
- **Riga riepilogativa in fondo** — "% classe in consolidato per argomento"

**Area principale — Vista Lista (alternativa)**
- **Tabella** — colonne: Studente, Argomento, Stato attuale, Giorni in stato, Ultima attività
- Ordinabile per ogni colonna
- Filtrabile

**Barra azioni**
- **Bottone "Esporta CSV"** — secondary button — azione: scarica vista corrente
- **Bottone "Suggerimenti sistema"** — azione: apre pannello con insight:
  - "5 studenti su 22 hanno lacuna su SQL GROUP BY — suggerita lezione di rinforzo"
  - "Maria sta consolidando tutti i concetti del modulo 3 — possibile avanzamento rapido"

**Accessibilità (F9)**
- Heatmap disponibile anche come tabella (toggle "Lista")
- Colori mai come unico indicatore (icone + testo tooltip)
- Screen reader: griglia annunciata come tabella con scope row/col

---

### SCR-DOC-09 — Mappa studente singolo (vista docente)

**Use case**: UC-DOC-14 | **Requisiti**: F12.2, F11.5 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Il docente visualizza la mappa della conoscenza di un singolo studente. Simile a SCR-ST-04 ma con controlli aggiuntivi (override, cronologia completa).

**Header**
- Breadcrumb: Dashboard > Classe > [Nome studente]
- **Nome studente** — h1
- **Badge** — stato complessivo: "12/20 consolidato — 3 lacune attive"
- **Bottone "Override nodo"** — secondary button — azione: apre SCR-DOC-10

**Area principale — Mappa**
- **Grafo interattivo** — come SCR-ST-04 ma con più informazioni per nodo:
  - Zoom, pan, filtri per stato
  - Nodi: colore + icona + label concetto
  - Click su nodo: pannello dettaglio a destra
- **Pannello dettaglio nodo (destra)**
  - Nome concetto, stato attuale, data ultima transizione
  - **Cronologia completa** — timeline di tutte le transizioni:
    - "15/10: introdotto (lezione 5)"
    - "22/10: lacuna (verifica — punteggio 2/10)"
    - "25/10: in_recupero (missione avviata)"
    - "28/10: da_consolidare (quiz 8/10)"
  - **Punteggi** — ultimo quiz, ultima verifica
  - **Bottone "Override"** — azione: apre dialog override per questo nodo

**Accessibilità (F9)**
- Timeline navigabile con tastiera
- Alternativa testuale alla mappa disponibile (lista filtrata)

---

### SCR-DOC-10 — Override stato nodo

**Use case**: UC-DOC-16 | **Requisiti**: F11.12 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Dialog per il docente per forzare la transizione di stato di un nodo del KG di uno studente.

**Dialog modale**
- **Titolo** — "Override stato nodo" — h2
- **Info nodo** — read-only: Studente, Concetto, Stato attuale
- **Nuovo stato** — dropdown — opzioni: tutti i 6 stati
  - Se transizione non standard (es. lacuna → consolidato), warning: "Transizione non standard — richiede motivazione dettagliata"
- **Motivazione** — textarea — obbligatorio — min 20 caratteri — placeholder "Spiega il motivo dell'override (es. verifica orale, progetto...)"
- **Evidenze** — upload file facoltativo — es. foto del compito, audio registrazione orale
- **Checkbox "Confermo che questa modifica riflette la mia valutazione professionale"** — obbligatorio
- **Bottone "Applica override"** — primary button — azione: registra transizione con flag override=true + motivazione + author
- **Bottone "Annulla"** — secondary button

**Note**
- Ogni override viene registrata nell'audit log con: timestamp, docente, studente, nodo, stato_da, stato_a, motivazione, evidenze
- L'override è irreversibile (ma si può fare un nuovo override per tornare indietro)

---

### SCR-DOC-11 — Editor Knowledge Graph

**Use case**: UC-DOC-10 | **Requisiti**: F1.2, F1.4 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Editor visuale per modificare la struttura del Knowledge Graph del corso.

**Header**
- Breadcrumb: Dashboard > Knowledge Graph > Editor
- **Selettore corso** — dropdown (se docente ha più corsi)
- **Statistiche** — "N nodi — M archi — K studenti impattati"

**Area principale — Editor grafo**
- **Canvas grafo** — visualizzazione interattiva con zoom, pan, minimap
  - Nodi draggabili per riposizionamento
  - Archi = frecce direzionali (prerequisito → successore)
  - Colori nodi: in base a copertura lezioni (verde = coperto, grigio = non coperto)
- **Click su nodo** — pannello proprietà a destra:
  - Nome concetto — editabile
  - Descrizione — editabile
  - Livello tassonomia — dropdown (ricordare, comprendere, applicare, analizzare)
  - Prerequisiti — lista con bottone "Aggiungi prerequisito" (seleziona altro nodo)
  - Lezioni collegate — lista read-only
  - **Bottone "Elimina nodo"** — danger button — dialog conferma con impatto: "Questo nodo è presente nella mappa di N studenti"
- **Click su arco** — dialog: rimuovi relazione

**Toolbar**
- **Bottone "+ Nuovo nodo"** — azione: crea nodo vuoto, posizionabile
- **Bottone "+ Nuovo arco"** — azione: modalità "collega" — click nodo A, click nodo B
- **Bottone "Layout automatico"** — azione: riorganizza posizioni nodi
- **Bottone "Importa programma"** — azione: upload PDF/DOCX, estrazione automatica concetti
- **Bottone "Salva"** — primary button
- **Bottone "Annulla modifiche"** — secondary button

**Accessibilità (F9)**
- Lista testuale alternativa al grafo visuale
- Tutte le operazioni eseguibili anche senza mouse

---

### SCR-DOC-12 — Iscrizione studenti

**Use case**: UC-DOC-12 | **Requisiti**: F14.5 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Gestione dell'elenco studenti di una classe. Aggiunta, rimozione, invio richieste consenso.

**Header**
- Breadcrumb: Dashboard > Classe > Studenti

**Area principale**
- **Tabella studenti** — colonne:
  - Nome e Cognome
  - Email famiglia
  - Stato consenso — badge: "Attesa", "Concesso", "Parziale", "Negato"
  - Stato account — badge: "Attesa attivazione", "Attivo", "Sospeso"
  - Data iscrizione
  - Azioni: "Reinvia consenso", "Dettaglio", "Rimuovi"
- **Filtri** — per stato consenso, per stato account
- **Cerca** — text field — cerca per nome

**Barra azioni**
- **Bottone "+ Aggiungi studente"** — azione: dialog con Nome, Cognome, Email famiglia
- **Bottone "Importa CSV"** — azione: upload CSV
- **Bottone "Rinvia tutte le richieste di consenso in attesa"** — secondary button

**Note**
- Uno studente non può accedere finché almeno il consenso base non è concesso
- La rimozione di uno studente non cancella i dati — il docente non ha autorità per farlo (vedi UC-AS-05)

---

### SCR-DOC-13 — Gestione contenuti generati

**Use case**: UC-DOC-08 | **Requisiti**: F15.1–F15.4, F12.5 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Il docente visualizza e gestisce i contenuti generati dal sistema (documenti di ripasso, missioni, quiz) per la propria classe.

**Header**
- Breadcrumb: Dashboard > Contenuti generati
- **Filtri** — per tipo (documento/missione/quiz/podcast), per concetto, per studente, per stato (attivo/archiviato)

**Area principale**
- **Tabella contenuti** — colonne:
  - Tipo — icona + label
  - Titolo/Concetto
  - Studente destinatario
  - Data generazione
  - Stato — badge: "Attivo", "Completato", "Archiviato"
  - Azioni: "Anteprima", "Archivia", "Rigenera"
- **Click "Anteprima"** — pannello laterale con contenuto completo
- **Click "Rigenera"** — dialog: "Vuoi rigenerare questo contenuto? Il precedente verrà archiviato."

---

### SCR-DOC-14 — Pannello override in massa

**Use case**: UC-DOC-16 (variante) | **Requisiti**: F11.12 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Override di stato su più studenti contemporaneamente (es. dopo una verifica orale di recupero per un gruppo).

**Header**
- Breadcrumb: Dashboard > Override > Gruppo

**Area principale**
- **Selezione studenti** — checkbox list — filtrabile per stato del concetto
- **Selezione concetto** — dropdown dal KG
- **Stato attuale** — read-only, mostrato per ogni studente selezionato
- **Nuovo stato** — dropdown — unico per tutto il gruppo
- **Motivazione** — textarea — min 20 caratteri — obbligatoria
- **Bottone "Applica a N studenti"** — primary button — dialog conferma: "Stai per modificare lo stato di N studenti sul concetto X. Confermi?"

---

### SCR-DOC-15 — Report lacune e copertura

**Use case**: UC-DOC-11 | **Requisiti**: F2.12, F12.1 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Report analitico sulle lacune della classe e sulla copertura del programma.

**Header**
- Breadcrumb: Dashboard > Report

**Area principale**
- **Sezione "Copertura programma"**
  - Barra di progresso: "68% del KG coperto da almeno una lezione"
  - Lista concetti non coperti — con suggerimento: "Questi concetti non sono stati ancora trattati in nessuna lezione"
- **Sezione "Analisi lacune"**
  - Grafico a barre: top 10 concetti con più studenti in lacuna
  - Per ogni barra: label concetto, numero studenti, % classe
- **Sezione "Trend temporale"**
  - Line chart: % studenti in consolidato nel tempo (settimana per settimana)
  - Overlay: eventi (lezioni, verifiche) come marker sulla timeline
- **Sezione "Studenti a rischio"**
  - Lista studenti con >3 lacune attive o lacune persistenti >14 giorni
  - Per ogni studente: nome, numero lacune, concetti, giorni medi in lacuna

**Barra azioni**
- **Bottone "Esporta PDF"** — scarica report
- **Bottone "Condividi con coordinatore"** — V1 — invia report a SCR-COR-01

---

### SCR-DOC-16 — Alert e notifiche docente

**Use case**: UC-DOC-19 | **Requisiti**: F16.1, F16.2 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Centro notifiche del docente con alert sullo stato della classe.

**Header**
- Breadcrumb: Dashboard > Notifiche

**Area principale**
- **Lista notifiche** — ordinate per data (più recenti prima):
  - Icona tipo: ⚠ alert lacuna, 📋 verifica, 📤 upload, 🔄 override, ✅ consolidamento
  - Testo: "Mario R. ha una lacuna su SQL JOIN da 7 giorni — nessuna missione completata"
  - Data/ora
  - Stato: letta/non letta
  - Azione rapida: "Vedi mappa studente", "Vedi dettaglio"
- **Filtri** — per tipo, per stato letta/non letta, per studente
- **Bottone "Segna tutte come lette"** — text button

**Impostazioni notifiche (sezione collassabile)**
- **Alert lacuna** — dopo N giorni — slider (default: 7)
- **Alert missione non iniziata** — dopo N giorni — slider (default: 3)
- **Report settimanale** — toggle on/off — giorno: dropdown (default: lunedì)
- **Canale** — checkbox: in-app, email

---

# C. Portale Famiglia (Web, mobile-responsive)

### SCR-FAM-01 — Registrazione consenso

**Use case**: UC-FAM-00 | **Requisiti**: F14.3, N1 | **Priorità**: MVP | **Piattaforma**: Web (link da email)

**Descrizione**
La famiglia riceve un link via email e registra i 5 consensi granulari per il proprio figlio. Non richiede creazione account.

**Header**
- Logo MAESTRO (centrato)
- Label "Portale Famiglia"

**Area principale**
- **Titolo** — "Consenso per l'uso di MAESTRO" — h1
- **Identificazione** — read-only: Nome studente, Classe, Scuola, Docente
- **Introduzione** — testo in linguaggio chiaro (non legalese): "MAESTRO è un compagno di studio che aiuta [Nome] a individuare e colmare le lacune. Per funzionare, ha bisogno del vostro consenso su alcune funzionalità."

**Sezione consensi — 5 card, una per consenso:**

**Card (a) — Profilazione stile di apprendimento**
- **Titolo** — "Analisi dello stile di apprendimento"
- **Spiegazione** — "Analizziamo come [Nome] impara meglio (visivo, uditivo, pratico) per personalizzare i contenuti. Esempio: se preferisce schemi, riceverà più infografiche."
- **Cosa raccogliamo** — lista: risposte al questionario, interazioni con i contenuti
- **Base giuridica** — "Art. 6(1)(a) GDPR — consenso esplicito"
- **Toggle on/off** — default: off — label: "Acconsento" / "Non acconsento"
- **Conseguenza se negato** — testo rosso: "Senza questo consenso, i contenuti non saranno personalizzati"

**Card (b) — Lingua madre (dato Art. 9)**
- **Titolo** — "Contenuti nella lingua madre"
- **Spiegazione** — "Se [Nome] parla anche un'altra lingua, possiamo generare spiegazioni bilingui (italiano + lingua madre). Questo dato è considerato sensibile dal GDPR."
- **Toggle on/off** — default: off
- **Se acceso** — dropdown lingua: Ucraino, Arabo (MVP); altre (V1+)
- **Conseguenza se negato** — "I contenuti saranno solo in italiano"

**Card (c) — Comunicazioni alla famiglia**
- **Titolo** — "Report mensile alla famiglia"
- **Spiegazione** — "Vi inviamo un report mensile con i progressi di [Nome]: concetti consolidati, aree da migliorare, attività svolte."
- **Toggle on/off** — default: off
- **Se acceso** — email di recapito: text field (pre-compilato da iscrizione)
- **Conseguenza se negato** — "Non riceverete report periodici"

**Card (d) — Storico cross-anno**
- **Titolo** — "Continuità tra anni scolastici"
- **Spiegazione** — "Manteniamo la mappa della conoscenza di [Nome] da un anno all'altro, così il nuovo docente può riprendere da dove si era arrivati."
- **Toggle on/off** — default: off
- **Conseguenza se negato** — "La mappa verrà azzerata ad ogni anno scolastico"

**Card (e) — Ricerca anonima**
- **Titolo** — "Dati anonimi per migliorare il sistema"
- **Spiegazione** — "Usiamo dati completamente anonimi (non riconducibili a [Nome]) per migliorare gli algoritmi. Esempio: 'il 30% degli studenti ha difficoltà con SQL JOIN'."
- **Toggle on/off** — default: off
- **Conseguenza se negato** — "Nessun dato, nemmeno anonimo, verrà usato per la ricerca"

**Footer**
- **Checkbox "Ho letto e compreso tutte le informazioni"** — obbligatorio
- **Link "Informativa privacy completa (PDF)"** — download
- **Bottone "Registra consenso"** — primary button — azione: salva, invia conferma email, notifica docente
- **Testo** — "Potrai modificare le tue scelte in qualsiasi momento accedendo a questo portale."

**Accessibilità (F9)**
- Card navigabili con Tab
- Toggle annunciati come switch con stato (attivo/disattivo)
- Conseguenze annunciate da screen reader quando toggle cambia stato

---

### SCR-FAM-02 — Report mensile famiglia

**Use case**: UC-FAM-02 | **Requisiti**: F11.16, F14.3(c) | **Priorità**: V1 | **Piattaforma**: Web (link da email) + PDF allegato

**Descrizione**
Report mensile sui progressi dello studente, visibile via web e scaricabile come PDF. Accessibile solo se consenso (c) concesso.

**Header**
- Logo MAESTRO + "Report Famiglia"
- Nome studente, Classe, Mese di riferimento

**Area principale**
- **Sezione "Panoramica mese"**
  - Numero concetti consolidati nel mese
  - Numero lacune risolte
  - Numero missioni completate
  - Confronto con mese precedente (trend freccia ↑ ↓ →) — mai confronto con altri studenti
- **Sezione "Mappa sintetica"**
  - Versione semplificata della mappa — solo macro-argomenti
  - Per ogni argomento: stato sintetico (consolidato / in corso / da iniziare) — colore + icona + testo
- **Sezione "Attività svolte"**
  - Lista riassuntiva: "Ha completato 5 missioni di recupero, 12 quiz, 3 sessioni di ripasso"
  - Frequenza d'uso: "Ha usato MAESTRO 4 giorni su 7 in media"
- **Sezione "Aree di attenzione"**
  - Concetti dove lo studente ha lacune persistenti
  - Tono: mai allarmista, orientato all'azione — "Su SQL JOIN serve ancora un po' di lavoro — le missioni di recupero sono disponibili"
- **Sezione "Suggerimenti"**
  - "Incoraggiate [Nome] a completare le missioni di recupero sui concetti evidenziati"
  - Non include mai suggerimenti didattici specifici (competenza del docente)

**Footer**
- **Bottone "Scarica PDF"** — azione: download report
- **Link "Modifica consenso"** — redirect a SCR-FAM-04
- **Link "Richiedi cancellazione dati"** — redirect a SCR-FAM-03

---

### SCR-FAM-03 — Richiesta oblio (famiglia)

**Use case**: UC-FAM-03 | **Requisiti**: F14.9, N1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
La famiglia richiede la cancellazione dei dati del proprio figlio. Flusso con doppia conferma e spiegazione delle conseguenze.

**Header**
- Logo MAESTRO + "Portale Famiglia"

**Area principale**
- **Titolo** — "Cancellazione dati di [Nome studente]" — h1
- **Spiegazione** — "Se procedete, verranno eliminati permanentemente:
  - Profilo e preferenze di apprendimento
  - Mappa della conoscenza e cronologia
  - Tutti i contenuti generati (documenti, audio, quiz)
  - Storico interazioni e progressi

  Se il consenso (e) è stato dato, i dati anonimi aggregati non verranno rimossi (non sono riconducibili a [Nome])."
- **Checkbox "Comprendiamo le conseguenze della cancellazione"** — obbligatorio
- **Bottone "Richiedi cancellazione"** — danger button
- **Dialog conferma** — "Questa azione è irreversibile. Tutti i progressi di [Nome] andranno persi. Sei sicuro?"
  - **Bottone "Annulla"** — secondary
  - **Bottone "Conferma cancellazione"** — danger
- **Post-conferma** — "La richiesta è stata registrata. Verrà elaborata entro 30 giorni. Riceverete conferma via email."

---

### SCR-FAM-04 — Aggiornamento consenso

**Use case**: UC-FAM-04 | **Requisiti**: F14.3 | **Priorità**: V2 | **Piattaforma**: Web

**Descrizione**
La famiglia modifica i consensi precedentemente concessi. Accessibile in qualsiasi momento.

**Header**
- Logo MAESTRO + "Portale Famiglia"

**Area principale**
- **Titolo** — "Gestione consensi per [Nome studente]" — h1
- **5 card consenso** — stessa struttura di SCR-FAM-01, ma:
  - Toggle pre-impostato sullo stato attuale
  - Data ultimo aggiornamento per ogni consenso
  - Se si revoca un consenso, warning: "La revoca ha effetto immediato. I contenuti personalizzati basati su questo consenso non saranno più disponibili."
- **Sezione "Storico modifiche"** — timeline: "12/10/2025: consenso (a) concesso — 15/11/2025: consenso (c) revocato — ..."

**Footer**
- **Bottone "Salva modifiche"** — primary button — azione: aggiorna consensi, notifica sistema, ricalcola contenuti disponibili
- **Link "Informativa privacy completa (PDF)"**

---

# D. Pannello Admin IT (Web)

### SCR-AS-01 — Login Admin IT

**Use case**: UC-AS-00 | **Requisiti**: F14.6 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Schermata di accesso dedicata all'amministratore IT della scuola.

**Header**
- Logo MAESTRO + label "Amministrazione"

**Area principale**
- **Email** — text field — obbligatorio
- **Password** — password field — obbligatorio — icona mostra/nascondi
- **Bottone "Accedi"** — primary button
- **Link "SSO Admin"** — azione: redirect a IdP scolastico con ruolo admin

**Note**
- Account admin creato in fase di onboarding scuola (fuori scope MVP — provisioning manuale)
- MFA obbligatorio per ruolo admin (TOTP o WebAuthn)

---

### SCR-AS-02 — Dashboard gestione utenze

**Use case**: UC-AS-02 | **Requisiti**: F14, N2 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Dashboard principale dell'admin IT per la gestione di tutti gli utenti del sistema (docenti, studenti, famiglie).

**Header**
- Logo MAESTRO + "Amministrazione"
- **Menu** — Utenze (attivo), Audit Log, Configurazione, SSO

**Area principale**
- **Tabs** — "Docenti" | "Studenti" | "Famiglie"

**Tab Docenti**
- **Tabella** — colonne: Nome, Email, Classi assegnate, Stato (attivo/sospeso/da attivare), Ultimo accesso, Azioni
- Azioni: "Modifica", "Sospendi/Riattiva", "Reset password"
- **Bottone "+ Nuovo docente"** — dialog: Nome, Cognome, Email, Classi — invio credenziali via email

**Tab Studenti**
- **Tabella** — colonne: Nome, Classe, Docente, Stato consenso, Stato account, Ultimo accesso, Azioni
- Azioni: "Dettaglio", "Sospendi", "Avvia cancellazione" (redirect SCR-AS-05)
- **Filtri** — per classe, per stato consenso, per stato account
- **Cerca** — text field

**Tab Famiglie**
- **Tabella** — colonne: Email, Studente associato, Stato consenso, Ultimo accesso, Azioni
- Azioni: "Reinvia link consenso", "Dettaglio"

**Barra azioni**
- **Bottone "Import massivo"** — azione: redirect SCR-AS-07
- **Bottone "Esporta utenze CSV"** — secondary button

---

### SCR-AS-03 — Creazione studente (admin)

**Use case**: UC-AS-05 | **Requisiti**: F14.2 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Form per la creazione di un singolo studente da parte dell'admin (alternativa all'iscrizione da parte del docente).

**Header**
- Breadcrumb: Amministrazione > Utenze > Nuovo studente

**Area principale**
- **Nome** — text field — obbligatorio
- **Cognome** — text field — obbligatorio
- **Classe** — dropdown — lista classi disponibili — obbligatorio
- **Docente** — dropdown — auto-selezionato in base alla classe
- **Email famiglia** — email field — obbligatorio — validazione formato
- **Lingua madre** — dropdown — facoltativo — "Da compilare solo se la famiglia lo consente"
- **Note** — textarea — facoltativo

**Footer**
- **Bottone "Crea e invia consenso"** — primary button — azione: crea account in stato "attesa consenso", invia email alla famiglia
- **Bottone "Crea senza inviare"** — secondary button — azione: crea account, non invia email (utile per import parziale)
- **Bottone "Annulla"** — text button

---

### SCR-AS-04 — Audit log

**Use case**: UC-AS-03 | **Requisiti**: F14.10, N1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Registro completo e immutabile di tutti gli eventi di sistema rilevanti per compliance e debugging.

**Header**
- Breadcrumb: Amministrazione > Audit Log

**Filtri (barra superiore)**
- **Data da/a** — date range picker
- **Tipo evento** — multi-select: login, logout, consenso, override, cancellazione, upload, generazione, errore, admin_action
- **Attore** — text field — cerca per nome o ruolo
- **Soggetto** — text field — cerca per nome studente (se autorizzato)

**Area principale**
- **Tabella log** — colonne:
  - Timestamp — formato ISO 8601
  - Tipo evento — badge colorato
  - Attore — nome + ruolo (es. "Prof. Rossi [docente]")
  - Soggetto — nome studente o "sistema" o "classe 3AI"
  - Descrizione — testo breve (es. "Override stato nodo: SQL JOIN → consolidato")
  - Dettagli — icona expand per JSON completo
- **Paginazione** — 50 righe per pagina
- **Ordinamento** — per timestamp (default: desc)

**Barra azioni**
- **Bottone "Esporta CSV"** — scarica log filtrato
- **Bottone "Esporta JSON"** — scarica log filtrato in formato JSON (per integrazione)
- **Contatore** — "Mostrando 1-50 di 12.345 eventi"

**Note**
- L'audit log è append-only: nessun record può essere modificato o cancellato
- Retention: come da policy DPIA (default 5 anni dopo fine rapporto scolastico)
- L'admin vede tutti gli eventi; il docente vede solo quelli relativi alle proprie classi

---

### SCR-AS-05 — Cancellazione studente (right to erasure)

**Use case**: UC-AS-08 | **Requisiti**: F14.9, N1 | **Priorità**: MVP | **Piattaforma**: Web

**Descrizione**
Esecuzione della cancellazione dati di uno studente. Solo l'admin può eseguire materialmente la cancellazione (il docente e la famiglia possono solo richiederla).

**Header**
- Breadcrumb: Amministrazione > Cancellazione dati

**Area principale**
- **Richieste pendenti** — tabella:
  - Studente, Classe, Richiedente (famiglia/studente), Data richiesta, Stato (pendente/in elaborazione/completata)
  - Azione: "Esegui cancellazione"

**Dialog "Esegui cancellazione"**
- **Riepilogo** — "Stai per cancellare tutti i dati di [Nome studente]"
- **Checklist automatica** — sistema verifica:
  - Profilo utente — da eliminare
  - Mappa della conoscenza — da eliminare
  - Cronologia transizioni — da eliminare
  - Contenuti generati — da eliminare
  - Interazioni e log (dati personali) — da eliminare
  - Dati anonimi aggregati — mantenuti (se consenso e)
  - Audit log entries — pseudonimizzare (sostituire nome con hash)
- **Checkbox "Confermo di aver verificato la legittimità della richiesta"** — obbligatorio
- **Bottone "Esegui cancellazione"** — danger button
- **Conferma** — "Cancellazione in corso... Completata. Certificato di cancellazione generato."
- **Link "Scarica certificato"** — PDF con: data, hash di verifica, dati cancellati, dati mantenuti (anonimi), firma digitale sistema

---

### SCR-AS-06 — Configurazione SSO

**Use case**: UC-AS-01 | **Requisiti**: F14.6, N2 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Configurazione dell'integrazione SSO con l'identity provider della scuola.

**Header**
- Breadcrumb: Amministrazione > Configurazione > SSO

**Area principale**
- **Stato SSO** — badge: "Non configurato" / "Configurato" / "Errore"
- **Protocollo** — dropdown: SAML 2.0, OpenID Connect — obbligatorio
- **Identity Provider URL** — text field — es. "https://idp.scuola.edu.it" — obbligatorio
- **Client ID** — text field — obbligatorio
- **Client Secret** — password field — obbligatorio — mascherato dopo salvataggio
- **Certificate** — upload file (.pem, .crt) o textarea per incollare — obbligatorio per SAML
- **Mapping attributi** — tabella:
  - MAESTRO field → IdP attribute
  - email → (text field, es. "mail")
  - nome → (text field, es. "givenName")
  - cognome → (text field, es. "sn")
  - ruolo → (text field, es. "memberOf") + mapping valori

**Barra azioni**
- **Bottone "Test connessione"** — azione: verifica raggiungibilità IdP — risultato inline
- **Bottone "Salva configurazione"** — primary button
- **Bottone "Disabilita SSO"** — danger button (se configurato)

---

### SCR-AS-07 — Import massivo utenze

**Use case**: UC-AS-04 | **Requisiti**: F14.2 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Import di docenti e studenti in blocco via file CSV.

**Header**
- Breadcrumb: Amministrazione > Import massivo

**Step 1: Upload file**
- **Tipo import** — radio: "Docenti", "Studenti"
- **Zona upload** — drag & drop + bottone "Scegli file" — formato: CSV (UTF-8)
- **Link "Scarica template CSV"** — download file template con header e riga di esempio

**Step 2: Anteprima e validazione**
- **Tabella anteprima** — prime 10 righe del CSV
- **Report validazione**:
  - N righe valide
  - N righe con warning (es. email formato dubbio) — dettaglio espandibile
  - N righe con errori (es. campi obbligatori mancanti) — dettaglio espandibile
- **Opzione** — "Importa solo righe valide" / "Correggi e ricarica" — radio

**Step 3: Conferma**
- **Riepilogo** — "Verranno creati N account [docente/studente]. Per gli studenti, verranno inviate N richieste di consenso alle famiglie."
- **Bottone "Importa"** — primary button
- **Barra di progresso** — durante l'importazione
- **Report finale** — N creati, N saltati, N errori — scaricabile come CSV

---

# E. Dashboard Coordinatore (Web)

### SCR-COR-01 — Dashboard coordinatore

**Use case**: UC-COR-01 | **Requisiti**: F12.1, F11.14 | **Priorità**: V1 | **Piattaforma**: Web

**Descrizione**
Vista aggregata per il coordinatore scolastico su più classi e docenti. Permette di identificare trend e problematiche trasversali.

**Header**
- Logo MAESTRO + "Coordinatore"
- **Selettore** — dropdown: "Tutte le classi" / singola classe / singolo docente
- **Periodo** — date range: ultimo mese / ultimo trimestre / anno scolastico

**Area principale**
- **Card "Panoramica istituto"**
  - Numero classi attive su MAESTRO
  - Numero studenti totali attivi
  - % media consolidamento (aggregata)
  - Trend: freccia rispetto al periodo precedente

- **Card "Classi a confronto"** (mai confronto tra studenti — solo tra classi)
  - Tabella: Classe, Docente, N studenti, % consolidato, N lacune attive, Trend
  - Ordinabile per ogni colonna
  - Click su riga: espande dettaglio con top 5 concetti problematici

- **Card "Concetti critici trasversali"**
  - Grafico a barre orizzontali: concetti con più lacune aggregate tra tutte le classi
  - Per ogni barra: nome concetto, N studenti con lacuna, N classi coinvolte

- **Card "Utilizzo piattaforma"**
  - Metriche: accessi docenti/settimana, accessi studenti/settimana, contenuti generati, missioni completate
  - Line chart: trend accessi nel tempo

- **Card "Alert"**
  - Classi con calo significativo di consolidamento
  - Docenti con bassa attività (nessun upload da >2 settimane)
  - Studenti con lacune critiche persistenti (>3 settimane)

**Barra azioni**
- **Bottone "Esporta report"** — PDF/CSV
- **Bottone "Invia report a dirigente"** — V2 — email con riepilogo

**Accessibilità (F9)**
- Grafici con alternativa tabellare
- Card navigabili con tastiera

---

# F. Componenti trasversali

### Componente: Selettore lingua interfaccia

**Presente in**: tutte le schermate (footer o header)
- **Dropdown lingua** — Italiano (default), Ucraino, Arabo — cambia solo la lingua UI, non i contenuti didattici
- I contenuti didattici bilingui dipendono dal consenso (b) e dal profilo studente

### Componente: Selettore accessibilità

**Presente in**: tutte le schermate (icona ingranaggio accessibilità nel footer)
- **Font** — dropdown: Inter (default), OpenDyslexic, Atkinson Hyperlegible
- **Dimensione testo** — slider: 12pt — 24pt
- **Tema** — radio: Chiaro, Scuro, Seppia
- **Alto contrasto** — toggle on/off
- **Animazioni ridotte** — toggle on/off
- Le preferenze sono salvate nel profilo utente e persistono tra sessioni

### Componente: Barra di stato connessione

**Presente in**: App Studente (mobile)
- **Indicatore offline** — banner giallo in alto: "Sei offline — i contenuti scaricati sono disponibili"
- **Sincronizzazione** — icona rotante durante sync, checkmark quando completata
- **Coda azioni** — contatore: "3 azioni in attesa di sincronizzazione"

---

# G. Riepilogo schermate per area

| Area | ID | Schermata | Priorità |
|---|---|---|---|
| **Studente** | SCR-ST-01 | Login e prima attivazione | MVP |
| | SCR-ST-02 | Onboarding profilazione | MVP |
| | SCR-ST-03 | Home dashboard studente | MVP |
| | SCR-ST-04 | Mappa della conoscenza | MVP |
| | SCR-ST-05 | Dettaglio nodo | MVP |
| | SCR-ST-06 | Missione di recupero | MVP |
| | SCR-ST-07 | Mini-quiz di chiusura | MVP |
| | SCR-ST-08 | Documento di ripasso | MVP |
| | SCR-ST-09 | Profilo e preferenze | MVP |
| | SCR-ST-10 | Pannello spiegabilità | MVP |
| | SCR-ST-11 | Player podcast | V1 |
| | SCR-ST-12 | Quest e gamification | V1 |
| | SCR-ST-13 | Heatmap personale | V1 |
| | SCR-ST-14 | Richiesta oblio dati | MVP |
| **Docente** | SCR-DOC-01 | Login docente | MVP |
| | SCR-DOC-02 | Home dashboard docente | MVP |
| | SCR-DOC-03 | Setup corso | MVP |
| | SCR-DOC-04 | Upload lezione | MVP |
| | SCR-DOC-05 | Editor trascrizione | MVP |
| | SCR-DOC-06 | Validazione mapping concetti | MVP |
| | SCR-DOC-07 | Upload verifica | MVP |
| | SCR-DOC-08 | Vista classe / Heatmap | MVP |
| | SCR-DOC-09 | Mappa studente singolo | MVP |
| | SCR-DOC-10 | Override stato nodo | V1 |
| | SCR-DOC-11 | Editor Knowledge Graph | V1 |
| | SCR-DOC-12 | Iscrizione studenti | MVP |
| | SCR-DOC-13 | Gestione contenuti generati | V1 |
| | SCR-DOC-14 | Pannello override in massa | V1 |
| | SCR-DOC-15 | Report lacune e copertura | V1 |
| | SCR-DOC-16 | Alert e notifiche docente | MVP |
| **Famiglia** | SCR-FAM-01 | Registrazione consenso | MVP |
| | SCR-FAM-02 | Report mensile famiglia | V1 |
| | SCR-FAM-03 | Richiesta oblio (famiglia) | MVP |
| | SCR-FAM-04 | Aggiornamento consenso | V2 |
| **Admin IT** | SCR-AS-01 | Login admin IT | MVP |
| | SCR-AS-02 | Dashboard gestione utenze | MVP |
| | SCR-AS-03 | Creazione studente (admin) | MVP |
| | SCR-AS-04 | Audit log | MVP |
| | SCR-AS-05 | Cancellazione studente | MVP |
| | SCR-AS-06 | Configurazione SSO | V1 |
| | SCR-AS-07 | Import massivo utenze | V1 |
| **Coordinatore** | SCR-COR-01 | Dashboard coordinatore | V1 |

**Totale**: 42 schermate — 29 MVP, 12 V1, 1 V2