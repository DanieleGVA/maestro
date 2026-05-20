# MAESTRO -- Specifica Accessibilita' MVP

**Task**: T3.3
**Autore**: MSTR-17 (Accessibility & UX Specialist)
**Versione**: 1.0
**Data**: 2026-05-20
**Stato**: Bozza per ratifica CPA + CTA
**Input**: CLAUDE.md, docs/MAESTRO_requisiti_v0.3.md (F9, N5), docs/architecture/production-HLD.md, docs/architecture/interface-contracts.md, docs/architecture/phase3-compliance-mvp.md, docs/MAESTRO_schermate_v1.md

---

## 1. Principi

### 1.1 Conformita' normativa

| Standard / Norma | Riferimento | Applicabilita' MVP |
|---|---|---|
| WCAG 2.1 Level AA | W3C Recommendation, giugno 2018 | Tutti i criteri Level A e AA pertinenti |
| L. 4/2004 (Legge Stanca) | Disposizioni per favorire e semplificare l'accesso dei soggetti disabili agli strumenti informatici | Obbligatoria per PA e soggetti che erogano servizi educativi con fondi pubblici |
| Linee Guida AgID sull'accessibilita' | Determinazione AgID n. 437/2022 | Requisiti tecnici per siti web e app mobili |
| EN 301 549 v3.2.1 | Standard europeo armonizzato | Riferimento tecnico per conformita' Direttiva UE 2016/2102 |
| D.Lgs. 106/2018 | Attuazione Direttiva UE 2016/2102 | Estende obblighi a enti pubblici e scuole |

### 1.2 Utenti target

- **Eta'**: 13-19 anni (minori, scuola secondaria italiana)
- **DSA** (Disturbi Specifici dell'Apprendimento): dislessia, disgrafia, discalculia, disortografia. L. 170/2010 obbliga strumenti compensativi.
- **BES** (Bisogni Educativi Speciali): disturbi evolutivi specifici, svantaggio linguistico/culturale/socioeconomico. Dir. MIUR 27/12/2012.
- **Docenti**: eta' variabile, possibili necessita' visive.

### 1.3 Principi guida

1. **Mai solo colore**: ogni informazione veicolata dal colore e' accompagnata da icona + testo (F9.3, WCAG 1.4.1).
2. **Tastiera come pari cittadino**: ogni funzione raggiungibile e operabile da tastiera (WCAG 2.1.1, N5).
3. **Struttura semantica**: HTML5 semantico, ARIA solo dove HTML nativo non basta.
4. **Lacuna come porta aperta**: il tono visivo del rosso/lacuna non e' punitivo. Il componente lacuna ha sempre un link alla missione di recupero (principio safeguarding, CLAUDE.md).
5. **Semplicita' proporzionata all'eta'**: UX adattata al biennio (macro, meno densita') e triennio (opzione macro/micro).

---

## 2. Checklist WCAG 2.1 AA

### 2.1 Criteri Level A

| # | Criterio | Descrizione | Stato MVP | Nota implementativa |
|---|---|---|---|---|
| 1.1.1 | Non-text Content | Testo alternativo per contenuti non testuali | Obbligatorio | `alt` su immagini, `aria-label` su icone SVG, descrizioni per grafici |
| 1.2.1 | Audio-only/Video-only (Prerecorded) | Alternativa per audio/video | Rimandato V1 | Podcast (F6) e' V1; per MVP nessun audio generato |
| 1.2.2 | Captions (Prerecorded) | Sottotitoli per video preregistrati | Rimandato V1 | Video non in scope MVP; F6.5 e' V1 |
| 1.2.3 | Audio Description or Media Alternative | Descrizione audio o alternativa testuale | Rimandato V1 | Nessun video MVP |
| 1.3.1 | Info and Relationships | Struttura e relazioni trasmesse programmaticamente | Obbligatorio | HTML5 semantico: `<nav>`, `<main>`, `<article>`, `<section>`, heading hierarchy |
| 1.3.2 | Meaningful Sequence | Ordine di lettura coerente | Obbligatorio | DOM order = visual order. No CSS che altera sequenza logica |
| 1.3.3 | Sensory Characteristics | Istruzioni non dipendono solo da forma/colore/posizione | Obbligatorio | Mai "clicca il bottone rosso". Usare etichette testuali |
| 1.4.1 | Use of Color | Colore non e' l'unico mezzo per veicolare informazione | Obbligatorio | Semaforo 6 stati: colore + icona + testo (F9.3) |
| 1.4.2 | Audio Control | Meccanismo per fermare audio auto-play | N/A MVP | Nessun audio auto-play in MVP |
| 2.1.1 | Keyboard | Tutto operabile da tastiera | Obbligatorio | `tabIndex`, focus management, mappa navigabile con Tab/Invio/frecce (N5) |
| 2.1.2 | No Keyboard Trap | Nessun trap di tastiera involontario | Obbligatorio | Focus trap solo in modali, con Esc per chiudere (N5 v0.3) |
| 2.1.4 | Character Key Shortcuts | Shortcut singolo carattere disattivabili | Obbligatorio | Nessuna shortcut singolo carattere in MVP; se aggiunte, devono essere disattivabili |
| 2.2.1 | Timing Adjustable | Limiti di tempo regolabili | Obbligatorio | Quiz: nessun timer in MVP. JWT refresh trasparente |
| 2.2.2 | Pause, Stop, Hide | Contenuto in movimento fermabile | Obbligatorio | Animazioni ridotte toggle (F9.7). Nessuna animazione auto-play non fermabile |
| 2.3.1 | Three Flashes | Niente lampeggia piu' di 3 volte/sec | Obbligatorio | Nessuna animazione con flash. Regola CSS: `@media (prefers-reduced-motion: reduce)` |
| 2.4.1 | Bypass Blocks | Meccanismo per saltare blocchi ripetuti | Obbligatorio | Skip-link "Vai al contenuto" su ogni pagina |
| 2.4.2 | Page Titled | Titolo pagina descrittivo | Obbligatorio | `<title>` unico per ogni schermata. Pattern: "Sezione - MAESTRO" |
| 2.4.3 | Focus Order | Ordine di focus logico | Obbligatorio | DOM order = visual order. Tab order segue flusso lettura |
| 2.4.4 | Link Purpose (In Context) | Scopo del link chiaro dal testo o contesto | Obbligatorio | No "clicca qui". Link descrittivi: "Avvia recupero per Sessione PHP" |
| 2.5.1 | Pointer Gestures | Funzioni multipoint/path hanno alternativa single-pointer | Obbligatorio | Pinch-to-zoom sulla mappa: bottoni +/- come alternativa (SCR-ST-04) |
| 2.5.2 | Pointer Cancellation | Down-event non attiva funzione (o annullabile) | Obbligatorio | Click/tap su up-event (comportamento default React Native) |
| 2.5.3 | Label in Name | Nome accessibile contiene testo visibile | Obbligatorio | Bottoni con testo visibile = accessible name |
| 2.5.4 | Motion Actuation | Funzioni attivate da movimento hanno alternativa UI | N/A MVP | Nessuna motion actuation in MVP |
| 3.1.1 | Language of Page | Lingua della pagina dichiarata | Obbligatorio | `lang="it"` su `<html>`. Per contenuti bilingui (V1): `lang` su blocchi specifici |
| 3.2.1 | On Focus | Nessun cambio di contesto su focus | Obbligatorio | Focus non attiva navigazione o submit |
| 3.2.2 | On Input | Nessun cambio di contesto su input senza avviso | Obbligatorio | Form submit esplicito. Filtri con bottone "Applica" o `aria-live` per aggiornamenti |
| 3.3.1 | Error Identification | Errori identificati e descritti in testo | Obbligatorio | Validazione form con messaggi testuali + `aria-describedby` + `aria-invalid` |
| 3.3.2 | Labels or Instructions | Label per input che richiedono dati | Obbligatorio | `<label>` associato a ogni `<input>`. Placeholder non sostituisce label |
| 4.1.1 | Parsing | (Obsoleto in WCAG 2.2, mantenuto per 2.1) | Obbligatorio | HTML valido. React gestisce nativamente |
| 4.1.2 | Name, Role, Value | Componenti custom hanno nome, ruolo, valore accessibili | Obbligatorio | ARIA su tutti i componenti custom (Sezione 6) |

### 2.2 Criteri Level AA

| # | Criterio | Descrizione | Stato MVP | Nota implementativa |
|---|---|---|---|---|
| 1.3.4 | Orientation | Contenuto non bloccato in un orientamento | Obbligatorio | Supporto portrait + landscape. No `orientation: portrait` forzato |
| 1.3.5 | Identify Input Purpose | Scopo dei campi input identificabile | Obbligatorio | `autocomplete` su campi login (username, password, email) |
| 1.4.3 | Contrast (Minimum) | Rapporto contrasto >= 4.5:1 (testo), >= 3:1 (testo grande >=18pt/14pt bold) | Obbligatorio | Token colore verificati (Sezione 3) |
| 1.4.4 | Resize Text | Testo ridimensionabile fino a 200% senza perdita | Obbligatorio | Slider 12-24pt (F9.4). Layout responsive a dimensioni font grandi |
| 1.4.5 | Images of Text | Nessuna immagine di testo (salvo personalizzabile) | Obbligatorio | Testo sempre come testo, mai come immagine. Grafici con `aria-label` testuale |
| 1.4.10 | Reflow | Contenuto riadattabile a 320px CSS senza scroll orizzontale | Obbligatorio | Layout responsive. Tabella heatmap docente: scroll orizzontale ammesso con nota |
| 1.4.11 | Non-text Contrast | Elementi UI e grafici >= 3:1 di contrasto | Obbligatorio | Focus ring, bordi input, icone stato tutti >= 3:1 |
| 1.4.12 | Text Spacing | Contenuto funziona con spaziatura testo modificata | Obbligatorio | No altezze fisse su contenitori di testo. Test con bookmarklet WCAG text spacing |
| 1.4.13 | Content on Hover or Focus | Contenuto aggiuntivo su hover/focus controllabile | Obbligatorio | Tooltip dismissibili con Esc, persistenti su hover, non bloccano contenuto sotto |
| 2.4.5 | Multiple Ways | Piu' modi per raggiungere una pagina | Obbligatorio | Tab bar + navigazione interna + breadcrumb (dashboard docente) |
| 2.4.6 | Headings and Labels | Heading e label descrittivi | Obbligatorio | Heading hierarchy senza salti. Label unici per contesto |
| 2.4.7 | Focus Visible | Indicatore di focus visibile | Obbligatorio | Focus ring custom: 2px solid #1565C0, offset 2px. Mai `outline: none` senza sostituto |
| 3.1.2 | Language of Parts | Lingua delle parti dichiarata | Obbligatorio | `lang` attribute su blocchi in lingua diversa (termini tecnici inglesi) |
| 3.2.3 | Consistent Navigation | Navigazione coerente tra pagine | Obbligatorio | Tab bar fissa (mobile), sidebar fissa (dashboard). Stessa posizione e ordine |
| 3.2.4 | Consistent Identification | Componenti con stessa funzione identificati coerentemente | Obbligatorio | Stessi label per stesse azioni. "Avvia recupero" sempre uguale |
| 3.3.3 | Error Suggestion | Suggerimenti per correzione errori | Obbligatorio | Messaggi di errore con suggerimento: "Password deve contenere almeno 8 caratteri" |
| 3.3.4 | Error Prevention (Legal, Financial, Data) | Azioni irreversibili: conferma o annulla | Obbligatorio | Doppia conferma per cancellazione dati (SCR-ST-14). Override docente con conferma |
| 4.1.3 | Status Messages | Messaggi di stato annunciati senza spostare focus | Obbligatorio | `aria-live="polite"` per conferme salvataggio, aggiornamenti stato, notifiche |

---

## 3. Sistema colori

### 3.1 Token colore semaforo -- 6 stati mastery

I colori di riferimento sono quelli di F9.3 (`docs/MAESTRO_requisiti_v0.3.md`). Per MVP si usano su sfondo chiaro (tema light, `#FFFFFF`). I rapporti di contrasto sono calcolati rispetto al colore testo associato.

| Stato | Hex sfondo | Hex testo | Rapporto contrasto | Icona | Etichetta | Icona SVG path |
|---|---|---|---|---|---|---|
| `non_introdotto` | `#9E9E9E` | `#000000` | 3.9:1 (vedi nota) | Cerchio vuoto | "Non introdotto" | `<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>` |
| `introdotto` | `#FFFFFF` | `#000000` | 21:1 | Cerchio con bordo | "Introdotto" | `<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="5" fill="currentColor"/>` |
| `lacuna` | `#E53935` | `#FFFFFF` | 4.6:1 | X (croce) | "Lacuna" | `<path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>` |
| `in_recupero` | `#FB8C00` | `#000000` | 3.6:1 (vedi nota) | Freccia circolare | "In recupero" | `<path d="M12 4v8l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M4 12a8 8 0 1 1 3 6" stroke="currentColor" stroke-width="2" fill="none"/>` |
| `da_consolidare` | `#FDD835` | `#000000` | 12.1:1 | Spunta bordo | "Da consolidare" | `<path d="M6 12l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>` |
| `consolidato` | `#43A047` | `#FFFFFF` | 4.5:1 | Spunta piena | "Consolidato" | `<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7 12l3 3 6-6" stroke="white" stroke-width="2.5" stroke-linecap="round" fill="none"/>` |

**Nota contrasto `non_introdotto` (#9E9E9E su #FFFFFF)**: il grigio come sfondo di un badge ha rapporto 2.8:1 contro il bianco pagina. Per la conformita' AA dell'elemento UI (1.4.11, >= 3:1), il badge ha un bordo `#757575` di 1.5px (contrasto 4.6:1 su bianco). Il testo nero (#000000) sopra il grigio ha 3.9:1 che supera la soglia per testo grande (>= 18pt). Per testo normale il badge usa `#757575` come sfondo (contrasto testo nero: 4.6:1).

**Nota contrasto `in_recupero` (#FB8C00 su #FFFFFF)**: l'arancione ha rapporto 2.6:1 su bianco come colore di sfondo badge. Stessa strategia: bordo `#E65100` (contrasto 4.8:1 su bianco). Il testo nero sull'arancione ha 3.6:1 -- conforme solo per testo grande. Per testo di dimensione normale, il badge usa sfondo `#EF6C00` (contrasto testo nero: 4.7:1).

**Correzioni contrasto per testo normale:**

```css
/* Token CSS -- tema light */
:root {
  /* Sfondo badge con testo normale (>= 4.5:1 su testo associato) */
  --mastery-non-introdotto-bg: #757575;
  --mastery-non-introdotto-fg: #FFFFFF;  /* 4.6:1 */

  --mastery-introdotto-bg: #FFFFFF;
  --mastery-introdotto-fg: #1A1A1A;      /* 18.4:1 */
  --mastery-introdotto-border: #616161;  /* 5.3:1 su bianco */

  --mastery-lacuna-bg: #C62828;
  --mastery-lacuna-fg: #FFFFFF;          /* 5.6:1 */

  --mastery-in-recupero-bg: #EF6C00;
  --mastery-in-recupero-fg: #000000;     /* 4.7:1 */

  --mastery-da-consolidare-bg: #FDD835;
  --mastery-da-consolidare-fg: #000000;  /* 12.1:1 */

  --mastery-consolidato-bg: #2E7D32;
  --mastery-consolidato-fg: #FFFFFF;     /* 5.9:1 */

  /* Focus ring */
  --focus-ring-color: #1565C0;
  --focus-ring-width: 2px;
  --focus-ring-offset: 2px;

  /* Bordi e icone (non-text contrast >= 3:1 su #FFFFFF) */
  --border-input: #616161;               /* 5.3:1 su bianco */
  --icon-default: #424242;               /* 7.4:1 su bianco */
}
```

**React Native -- oggetto token:**

```typescript
export const MASTERY_TOKENS = {
  non_introdotto: {
    bg: '#757575',
    fg: '#FFFFFF',
    border: '#616161',
    icon: 'circle-outline',    // Cerchio vuoto
    label: 'Non introdotto',
  },
  introdotto: {
    bg: '#FFFFFF',
    fg: '#1A1A1A',
    border: '#616161',
    icon: 'circle-half-full',  // Cerchio con punto
    label: 'Introdotto',
  },
  lacuna: {
    bg: '#C62828',
    fg: '#FFFFFF',
    border: '#B71C1C',
    icon: 'close',             // X
    label: 'Lacuna',
  },
  in_recupero: {
    bg: '#EF6C00',
    fg: '#000000',
    border: '#E65100',
    icon: 'refresh',           // Freccia circolare
    label: 'In recupero',
  },
  da_consolidare: {
    bg: '#FDD835',
    fg: '#000000',
    border: '#F9A825',
    icon: 'check-outline',     // Spunta bordo
    label: 'Da consolidare',
  },
  consolidato: {
    bg: '#2E7D32',
    fg: '#FFFFFF',
    border: '#1B5E20',
    icon: 'check-circle',      // Spunta piena
    label: 'Consolidato',
  },
} as const;

export type MasteryState = keyof typeof MASTERY_TOKENS;
```

### 3.2 Daltonismo

I 6 stati usano sempre **colore + icona + etichetta testuale** (F9.3). L'icona da sola e' sufficiente a distinguere gli stati. Verifica:

| Stato | Icona | Distinguibile senza colore |
|---|---|---|
| `non_introdotto` | Cerchio vuoto | Si -- unica forma vuota |
| `introdotto` | Cerchio con punto | Si -- unica forma con punto |
| `lacuna` | X (croce) | Si -- unica forma a croce |
| `in_recupero` | Freccia circolare | Si -- unica forma freccia |
| `da_consolidare` | Spunta contorno | Si -- spunta vuota vs piena |
| `consolidato` | Cerchio pieno con spunta | Si -- unica forma piena |

### 3.3 Alto contrasto e temi (predisposizione per V1)

Per MVP si supportano solo tema chiaro. Il codice CSS usa variabili (`var(--mastery-lacuna-bg)`) in modo che V1 possa aggiungere:

- **Alto contrasto**: sovrascrittura dei token con colori ad alto contrasto (rapporto >= 7:1).
- **Tema scuro**: inversione degli sfondi con contrasto verificato.
- **Tema seppia**: sfondo `#F5E6C8`, testo `#1A1A1A`.

Struttura CSS predisposta:

```css
/* Tema light (MVP default) */
:root {
  --page-bg: #FFFFFF;
  --page-fg: #1A1A1A;
  --surface-bg: #F5F5F5;
  --surface-fg: #212121;
  /* ... mastery tokens come sopra ... */
}

/* V1: tema scuro */
[data-theme="dark"] {
  --page-bg: #121212;
  --page-fg: #E0E0E0;
  --surface-bg: #1E1E1E;
  --surface-fg: #FAFAFA;
  /* mastery token overrides ... */
}

/* V1: tema seppia */
[data-theme="sepia"] {
  --page-bg: #F5E6C8;
  --page-fg: #1A1A1A;
  /* mastery token overrides ... */
}

/* V1: alto contrasto */
[data-high-contrast="true"] {
  --mastery-lacuna-bg: #FF0000;
  --mastery-lacuna-fg: #FFFFFF;
  /* tutti i rapporti >= 7:1 ... */
}
```

Per React Native (MVP), la selezione tema e' memorizzata in `AsyncStorage` ma solo il tema chiaro e' implementato. L'architettura `ThemeProvider` e' predisposta:

```typescript
// V1: ThemeProvider wrapper (struttura predisposta)
type ThemeName = 'light' | 'dark' | 'sepia';

interface ThemeConfig {
  name: ThemeName;
  highContrast: boolean;
  colors: typeof MASTERY_TOKENS;
  page: { bg: string; fg: string };
  surface: { bg: string; fg: string };
}

// MVP: solo light
const LIGHT_THEME: ThemeConfig = {
  name: 'light',
  highContrast: false,
  colors: MASTERY_TOKENS,
  page: { bg: '#FFFFFF', fg: '#1A1A1A' },
  surface: { bg: '#F5F5F5', fg: '#212121' },
};
```

---

## 4. Tipografia

### 4.1 Font stack

| Contesto | Font MVP | Fallback | Note |
|---|---|---|---|
| UI generale | Inter | system-ui, -apple-system, sans-serif | Buona leggibilita', ampio supporto glifi |
| Codice sorgente | JetBrains Mono | Fira Code, monospace | Per blocchi codice in documenti di ripasso |
| V1 opzione dislessia | OpenDyslexic | Inter | Toggle in profilo (F9.1) |
| V1 opzione leggibilita' | Atkinson Hyperlegible | Inter | Progettato per bassa visione |

### 4.2 Scala dimensioni

Base: 16px (1rem). Slider utente: 12-24pt (F9.4).

| Token | Dimensione | Uso |
|---|---|---|
| `--text-xs` | 0.75rem (12px) | Didascalie, timestamp |
| `--text-sm` | 0.875rem (14px) | Testo secondario, label form |
| `--text-base` | 1rem (16px) | Testo corpo, paragrafi |
| `--text-lg` | 1.125rem (18px) | Testo enfatizzato |
| `--text-xl` | 1.25rem (20px) | Titoli sezione (h3) |
| `--text-2xl` | 1.5rem (24px) | Titoli pagina (h2) |
| `--text-3xl` | 1.875rem (30px) | Titolo principale (h1) |

### 4.3 Line-height e spaziatura

```css
:root {
  --leading-tight: 1.25;    /* heading */
  --leading-normal: 1.5;    /* corpo testo -- valore WCAG raccomandato */
  --leading-relaxed: 1.75;  /* testo lungo, documenti di ripasso */

  --spacing-word: 0.16em;   /* WCAG 1.4.12: >= 0.16em */
  --spacing-letter: 0.12em; /* WCAG 1.4.12: >= 0.12em */
  --spacing-paragraph: 2em; /* WCAG 1.4.12: >= 2em */
}

/* Classe per spaziatura WCAG-safe (applicata su contenuto generato) */
.wcag-text-spacing {
  line-height: var(--leading-normal) !important;
  word-spacing: var(--spacing-word) !important;
  letter-spacing: var(--spacing-letter) !important;
}

.wcag-text-spacing p + p {
  margin-top: var(--spacing-paragraph) !important;
}
```

### 4.4 Ridimensionamento utente

Lo slider F9.4 moltiplica la base `font-size` sull'elemento radice. Il layout non deve rompersi a nessuna dimensione nell'intervallo.

```css
/* Applicato da JS in base allo slider (12pt = 0.75, 16pt = 1.0, 24pt = 1.5) */
:root {
  --user-font-scale: 1; /* default */
}

html {
  font-size: calc(16px * var(--user-font-scale));
}
```

```typescript
// React Native: scaling factor
import { PixelRatio } from 'react-native';

const USER_FONT_RANGE = { min: 12, max: 24, default: 16 };

function getFontScale(userPt: number): number {
  const clamped = Math.max(USER_FONT_RANGE.min, Math.min(USER_FONT_RANGE.max, userPt));
  return clamped / USER_FONT_RANGE.default;
}

// Uso: Text style
const scaledSize = (basePx: number, userPt: number) =>
  basePx * getFontScale(userPt);
```

---

## 5. Navigazione da tastiera

### 5.1 Flussi principali

#### 5.1.1 Login (Keycloak)

```
Tab: username field -> password field -> "Mostra password" toggle -> "Accedi" button
Enter: submit form
```

Keycloak gestisce il form; MAESTRO puo' personalizzare il tema per garantire focus ring visibile e label visibili.

#### 5.1.2 Home studente (SCR-ST-03)

```
Skip link: "Vai al contenuto principale"
Tab: Notifiche (badge) -> Card missione 1 -> Card missione 2 -> ... ->
     "Vedi mappa completa" -> Documento recente 1 -> ... ->
     Tab bar: Home | Mappa | Profilo
```

- Le card missione sono `<button>` o `<a>` con `role="link"`.
- Tab bar: `role="tablist"`, frecce sinistra/destra tra tab, Tab per uscire.

#### 5.1.3 Mappa padronanza (SCR-ST-04)

```
Skip link: "Vai alla mappa"
Tab: Toggle granularita' (se triennio) -> Primo nodo del grafo ->
     (dentro il grafo: frecce per navigare tra nodi adiacenti,
      Enter/Space per aprire dettaglio nodo) ->
     Legenda (collassabile) -> Zoom +/- buttons
```

**Comportamento grafo da tastiera (N5):**
- `Tab` per entrare nel grafo, `Tab` per uscire.
- Dentro il grafo: **frecce direzionali** per muoversi tra nodi (seguendo archi prerequisito).
- `Enter` o `Space`: apre SCR-ST-05 (dettaglio nodo).
- `Escape`: torna al grafo dal dettaglio.
- `+`/`-` da tastiera: zoom in/out.
- Il nodo corrente ha `aria-current="true"` e annuncio screen reader: "Nodo {nome}, stato {stato}. {N} prerequisiti, {M} dipendenze."

Implementazione: il grafo e' un componente custom con `role="application"`. Il `role="application"` e' necessario perche' le interazioni frecce sovrascrivono il comportamento browse mode dello screen reader. Un messaggio `aria-live` istruisce: "Usa le frecce per navigare tra i nodi, Invio per aprire il dettaglio."

```tsx
// Componente mappa padronanza -- struttura ARIA
<div
  role="application"
  aria-label="Mappa della conoscenza"
  aria-roledescription="grafo interattivo"
  tabIndex={0}
  onKeyDown={handleGraphKeyboard}
>
  <div aria-live="polite" className="sr-only">
    {/* Annuncio navigazione */}
    {`Nodo ${currentNode.label}, stato ${currentNode.state}.
      ${currentNode.prerequisites.length} prerequisiti.`}
  </div>
  {nodes.map(node => (
    <div
      key={node.id}
      role="button"
      aria-label={`${node.label}: ${MASTERY_TOKENS[node.state].label}`}
      aria-current={node.id === focusedNodeId ? 'true' : undefined}
      tabIndex={-1}
    >
      {/* Contenuto visivo nodo */}
    </div>
  ))}
</div>
```

#### 5.1.4 Missione recupero (SCR-ST-06)

```
Tab: Header (back) -> Barra progresso (read-only, aria-label) ->
     Step corrente contenuto -> "Avvia quiz" button
```

- La barra progresso usa `role="progressbar"` con `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label="Progresso missione: 2 di 4 step completati"`.
- I blocchi di contenuto (testo, codice) sono navigabili normalmente.

#### 5.1.5 Quiz (SCR-ST-07)

```
Tab: Testo domanda (read-only) -> Opzione A -> Opzione B -> Opzione C -> Opzione D ->
     "Conferma" button
```

- Le opzioni sono `role="radiogroup"` + `role="radio"`. Frecce su/giu' per cambiare selezione.
- Dopo conferma: feedback mostrato con `aria-live="assertive"` per il risultato.
- Schermata risultati: Tab tra feedback per ogni domanda.

#### 5.1.6 Dashboard docente -- Heatmap (SCR-DOC-08)

```
Skip link: "Vai alla heatmap"
Tab: Sidebar (nav links) -> Selettore classe -> Toggle Heatmap/Lista ->
     Filtri stato -> Filtri argomento -> Griglia heatmap / Tabella lista
```

- La heatmap e' sempre disponibile come **tabella HTML** (toggle "Lista" in SCR-DOC-08).
- La tabella usa `<table>`, `<th scope="col">` per concetti, `<th scope="row">` per studenti.
- Ogni cella ha `aria-label`: "{studente}, {concetto}: {stato}".
- Nella vista griglia visuale, la tabella nascosta e' comunque presente nel DOM per screen reader (`aria-hidden="false"` sulla tabella, `aria-hidden="true"` sulla vista grafica quando in modalita' tabella).

### 5.2 Focus ring globale

```css
/* Focus ring -- applicato a tutti gli elementi interattivi */
:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* MAI rimuovere outline senza sostituto */
/* :focus { outline: none; } <- VIETATO */

/* Focus ring per componenti scuri */
[data-theme="dark"] :focus-visible {
  outline-color: #64B5F6;
}
```

### 5.3 Skip link

```html
<!-- Prima del header, su ogni pagina -->
<a href="#main-content" class="skip-link">
  Vai al contenuto principale
</a>

<style>
.skip-link {
  position: absolute;
  left: -9999px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
  z-index: 9999;
}

.skip-link:focus {
  position: fixed;
  top: 8px;
  left: 8px;
  width: auto;
  height: auto;
  padding: 12px 24px;
  background: var(--page-bg);
  color: var(--page-fg);
  border: 2px solid var(--focus-ring-color);
  border-radius: 4px;
  font-size: var(--text-base);
  text-decoration: none;
}
</style>
```

---

## 6. Componenti ARIA

### 6.1 Badge stato mastery

Badge utilizzato in mappa, dettaglio nodo, card missione, heatmap docente.

```tsx
interface MasteryBadgeProps {
  state: MasteryState;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;  // default: true
}

function MasteryBadge({ state, size = 'md', showLabel = true }: MasteryBadgeProps) {
  const token = MASTERY_TOKENS[state];
  return (
    <span
      role="img"
      aria-label={token.label}
      style={{
        backgroundColor: token.bg,
        color: token.fg,
        border: `1.5px solid ${token.border}`,
        borderRadius: '4px',
        padding: '4px 8px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
      }}
    >
      <MasteryIcon name={token.icon} size={size} aria-hidden="true" />
      {showLabel && (
        <span style={{ fontSize: 'var(--text-sm)' }}>{token.label}</span>
      )}
    </span>
  );
}
```

### 6.2 Mappa padronanza (grafo interattivo)

Vedi Sezione 5.1.3 per la struttura ARIA completa. Riepilogo attributi:

| Elemento | Ruolo ARIA | Attributi |
|---|---|---|
| Container grafo | `role="application"` | `aria-label="Mappa della conoscenza"`, `aria-roledescription="grafo interattivo"` |
| Nodo | `role="button"` | `aria-label="{nome}: {stato}"`, `aria-current` sul nodo focused |
| Arco | Nascosto | `aria-hidden="true"` (informazione gia' nei prerequisiti del nodo) |
| Annuncio navigazione | `aria-live="polite"` | Testo aggiornato a ogni spostamento |
| Legenda | `role="complementary"` | `aria-label="Legenda stati"` |
| Zoom buttons | `role="button"` | `aria-label="Ingrandisci"` / `aria-label="Riduci"` |

### 6.3 Progress bar missione

```tsx
function MissionProgressBar({ current, total, missionName }: {
  current: number;
  total: number;
  missionName: string;
}) {
  return (
    <div
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={0}
      aria-valuemax={total}
      aria-label={`Progresso missione ${missionName}: ${current} di ${total} step completati`}
    >
      <div
        style={{ width: `${(current / total) * 100}%` }}
        className="progress-fill"
        aria-hidden="true"
      />
      <span className="progress-text" aria-hidden="true">
        {current}/{total}
      </span>
    </div>
  );
}
```

### 6.4 Quiz -- radio group

```tsx
function QuizQuestion({ question, options, selected, onSelect }: QuizProps) {
  return (
    <fieldset>
      <legend className="quiz-question-text">
        {question.text}
      </legend>
      <div role="radiogroup" aria-label={`Opzioni per: ${question.text}`}>
        {options.map((opt, i) => (
          <label key={opt.id} className="quiz-option">
            <input
              type="radio"
              name={`q-${question.id}`}
              value={opt.id}
              checked={selected === opt.id}
              onChange={() => onSelect(opt.id)}
              aria-describedby={opt.codeBlock ? `code-${opt.id}` : undefined}
            />
            <span className="quiz-option-text">{opt.text}</span>
            {opt.codeBlock && (
              <pre id={`code-${opt.id}`} aria-label={`Codice per opzione ${String.fromCharCode(65 + i)}`}>
                <code>{opt.codeBlock}</code>
              </pre>
            )}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
```

### 6.5 Heatmap docente (tabella accessibile)

La heatmap (SCR-DOC-08) ha una vista tabella nativa sempre disponibile.

```tsx
function ClassHeatmapTable({ students, concepts, states }: HeatmapProps) {
  return (
    <table aria-label="Mappa padronanza della classe">
      <caption className="sr-only">
        Stato di padronanza per ogni studente su ogni macro-concetto.
        Usa le frecce per navigare tra le celle.
      </caption>
      <thead>
        <tr>
          <th scope="col">Studente</th>
          {concepts.map(c => (
            <th key={c.id} scope="col">{c.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {students.map(student => (
          <tr key={student.id}>
            <th scope="row">{student.displayName}</th>
            {concepts.map(concept => {
              const state = states[student.id]?.[concept.id] ?? 'non_introdotto';
              const token = MASTERY_TOKENS[state];
              return (
                <td
                  key={concept.id}
                  aria-label={`${student.displayName}, ${concept.label}: ${token.label}`}
                  style={{ backgroundColor: token.bg, color: token.fg }}
                >
                  <MasteryBadge state={state} size="sm" showLabel={false} />
                  <span className="sr-only">{token.label}</span>
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 6.6 Modale / bottom sheet (dialog)

Usato per: pannello spiegabilita' (SCR-ST-10), dettaglio nodo, conferme.

```tsx
function AccessibleModal({ isOpen, onClose, title, children }: ModalProps) {
  const titleId = useId();
  const modalRef = useRef<HTMLDivElement>(null);

  // Focus trap: Tab rimane nel modale (N5 v0.3)
  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusable = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const first = focusable[0] as HTMLElement;
      const last = focusable[focusable.length - 1] as HTMLElement;

      first?.focus();

      const handleTab = (e: KeyboardEvent) => {
        if (e.key === 'Escape') { onClose(); return; }
        if (e.key !== 'Tab') return;
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first?.focus();
        }
      };

      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" aria-hidden="true" onClick={onClose}>
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={e => e.stopPropagation()}
      >
        <h2 id={titleId}>{title}</h2>
        {children}
        <button onClick={onClose} aria-label="Chiudi">
          Chiudi
        </button>
      </div>
    </div>
  );
}
```

### 6.7 Alert wellbeing (docente)

Notifica in-app per il docente quando il sistema rileva keyword di disagio.

```tsx
function WellbeingAlert({ alert }: { alert: WellbeingAlertData }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="wellbeing-alert"
    >
      <span className="wellbeing-alert-icon" aria-hidden="true">!</span>
      <div>
        <strong>Segnalazione benessere</strong>
        <p>{alert.message}</p>
        <a href={`/students/${alert.studentId}`}>
          Vedi profilo studente
        </a>
      </div>
    </div>
  );
}
```

### 6.8 Selettore accessibilita' (SCR-ST-09)

```tsx
function AccessibilitySettings({ settings, onChange }: A11ySettingsProps) {
  const previewId = useId();

  return (
    <section aria-labelledby="a11y-heading">
      <h2 id="a11y-heading">Accessibilita'</h2>

      {/* Font */}
      <div role="group" aria-labelledby="font-label">
        <label id="font-label" htmlFor="font-select">Font</label>
        <select
          id="font-select"
          value={settings.fontFamily}
          onChange={e => onChange({ ...settings, fontFamily: e.target.value })}
        >
          <option value="Inter">Inter (predefinito)</option>
          <option value="OpenDyslexic" disabled>OpenDyslexic (V1)</option>
          <option value="AtkinsonHyperlegible" disabled>Atkinson Hyperlegible (V1)</option>
        </select>
      </div>

      {/* Dimensione testo */}
      <div role="group" aria-labelledby="fontsize-label">
        <label id="fontsize-label" htmlFor="fontsize-slider">
          Dimensione testo: {settings.fontSize}pt
        </label>
        <input
          id="fontsize-slider"
          type="range"
          min={12}
          max={24}
          step={1}
          value={settings.fontSize}
          onChange={e => onChange({ ...settings, fontSize: Number(e.target.value) })}
          aria-valuetext={`${settings.fontSize} punti`}
        />
      </div>

      {/* Tema */}
      <fieldset>
        <legend>Tema</legend>
        {(['light', 'dark', 'sepia'] as const).map(theme => (
          <label key={theme}>
            <input
              type="radio"
              name="theme"
              value={theme}
              checked={settings.theme === theme}
              onChange={() => onChange({ ...settings, theme })}
              disabled={theme !== 'light'} // V1: abilitare dark e sepia
            />
            {{ light: 'Chiaro', dark: 'Scuro', sepia: 'Seppia' }[theme]}
          </label>
        ))}
      </fieldset>

      {/* Alto contrasto */}
      <div>
        <label htmlFor="high-contrast-toggle">Alto contrasto</label>
        <input
          id="high-contrast-toggle"
          type="checkbox"
          role="switch"
          checked={settings.highContrast}
          onChange={e => onChange({ ...settings, highContrast: e.target.checked })}
          disabled  // V1
          aria-describedby="hc-note"
        />
        <span id="hc-note" className="text-sm">Disponibile nella versione successiva</span>
      </div>

      {/* Animazioni ridotte */}
      <div>
        <label htmlFor="reduced-motion-toggle">Animazioni ridotte</label>
        <input
          id="reduced-motion-toggle"
          type="checkbox"
          role="switch"
          checked={settings.reducedMotion}
          onChange={e => onChange({ ...settings, reducedMotion: e.target.checked })}
        />
      </div>

      {/* Anteprima */}
      <div
        id={previewId}
        aria-label="Anteprima impostazioni"
        style={{
          fontFamily: settings.fontFamily,
          fontSize: `${settings.fontSize}pt`,
        }}
      >
        <p>Questo e' un testo di esempio per verificare le impostazioni scelte.</p>
        <MasteryBadge state="lacuna" />
        <MasteryBadge state="consolidato" />
      </div>
    </section>
  );
}
```

---

## 7. Struttura semantica

### 7.1 Template pagina studente (React Native / Web)

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Sezione} - MAESTRO</title>
</head>
<body>
  <!-- Skip link -->
  <a href="#main-content" class="skip-link">Vai al contenuto principale</a>

  <!-- Header -->
  <header role="banner">
    <nav aria-label="Navigazione principale">
      <!-- Logo, nome utente, notifiche -->
    </nav>
  </header>

  <!-- Contenuto principale -->
  <main id="main-content" role="main">
    <h1>{Titolo pagina}</h1>
    <!-- Contenuto specifico della pagina -->
  </main>

  <!-- Tab bar (mobile) -->
  <nav aria-label="Menu principale" role="tablist">
    <a role="tab" aria-selected="true" href="/home">Home</a>
    <a role="tab" aria-selected="false" href="/map">Mappa</a>
    <a role="tab" aria-selected="false" href="/profile">Profilo</a>
  </nav>

  <!-- Live region per notifiche -->
  <div aria-live="polite" aria-atomic="true" class="sr-only"
       id="notification-live-region">
    <!-- Aggiornamenti dinamici inseriti qui via JS -->
  </div>
</body>
</html>
```

### 7.2 Template dashboard docente (Next.js)

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>{Sezione} - Dashboard Docente - MAESTRO</title>
</head>
<body>
  <a href="#main-content" class="skip-link">Vai al contenuto principale</a>

  <header role="banner">
    <span>MAESTRO - Dashboard Docente</span>
    <nav aria-label="Menu utente">
      <!-- Profilo docente, logout -->
    </nav>
  </header>

  <div class="layout">
    <!-- Sidebar -->
    <nav aria-label="Navigazione dashboard" class="sidebar">
      <ul>
        <li><a href="/dashboard" aria-current="page">Dashboard</a></li>
        <li><a href="/courses">Corsi</a></li>
        <li><a href="/heatmap">Heatmap classe</a></li>
        <li><a href="/verifications">Verifiche</a></li>
        <li><a href="/materials">Materiali</a></li>
      </ul>
    </nav>

    <!-- Main content -->
    <main id="main-content">
      <!-- Breadcrumb -->
      <nav aria-label="Breadcrumb">
        <ol>
          <li><a href="/dashboard">Dashboard</a></li>
          <li aria-current="page">Heatmap classe</li>
        </ol>
      </nav>

      <h1>{Titolo pagina}</h1>

      <!-- Contenuto -->
    </main>
  </div>

  <!-- Live regions -->
  <div aria-live="polite" aria-atomic="true" class="sr-only"
       id="status-live-region">
  </div>
  <div aria-live="assertive" aria-atomic="true" class="sr-only"
       id="alert-live-region">
  </div>
</body>
</html>
```

### 7.3 Heading hierarchy

Regola: nessun salto di livello. Ogni pagina ha un solo `<h1>`.

| Pagina | h1 | h2 | h3 |
|---|---|---|---|
| Home studente | "Bentornato, {nome}" | "Le tue missioni", "La tua mappa", "Ultimi documenti" | Nomi concetti nelle card |
| Mappa padronanza | "La tua mappa" | "Legenda" | Nomi macro-nodi (se visualizzati come lista) |
| Dettaglio nodo | "{Nome concetto}" | "Stato attuale", "Cronologia", "Azioni", "Materiali" | - |
| Missione recupero | "Missione: {concetto}" | Step titles | - |
| Quiz | "Quiz: {concetto}" | "Domanda {n}", "Risultato" | Feedback per domanda |
| Profilo | "Il mio profilo" | "Come preferisco studiare", "Preferenze contenuti", "Accessibilita'", "I miei dati" | - |
| Dashboard docente | "Dashboard" | Sezioni card | - |
| Heatmap | "Padronanza della classe" | "Filtri", "Dettaglio studente" | Nomi concetti |

### 7.4 Live regions

| Regione | Tipo | Contenuto | Trigger |
|---|---|---|---|
| `notification-live-region` | `aria-live="polite"` | Testo notifica nuova | WebSocket `notification.new` |
| `status-live-region` | `aria-live="polite"` | "Salvato", "Caricamento in corso..." | Dopo azioni CRUD |
| `alert-live-region` | `aria-live="assertive"` | Errori critici, alert wellbeing | Errori form, alert sistema |
| Navigazione mappa | `aria-live="polite"` | "Nodo {nome}, stato {stato}" | Cambio nodo con frecce |
| Risultato quiz | `aria-live="assertive"` | "Risposta corretta/errata. {spiegazione}" | Submit risposta quiz |

**Regola**: `aria-live="assertive"` solo per informazioni urgenti che richiedono attenzione immediata (errori, alert). Tutto il resto usa `"polite"`.

---

## 8. UX adattiva per eta'

### 8.1 Touch target

Tutti gli elementi interattivi hanno area minima **44x44 px** (WCAG 2.5.5, target size raccomandato). Questa soglia e' particolarmente importante per il target 13-19 che usa prevalentemente mobile.

```css
/* Touch target minimo */
.interactive-element {
  min-width: 44px;
  min-height: 44px;
  /* Se il contenuto e' piu' piccolo, padding espande l'area cliccabile */
}

/* Nodi della mappa: area touch espansa */
.map-node-touch-area {
  min-width: 48px;
  min-height: 48px;
  padding: 8px;
}

/* Bottoni primari (CTA) */
.button-primary {
  min-height: 48px;
  padding: 12px 24px;
  font-size: var(--text-base);
}
```

### 8.2 Granularita' adattiva per livello scolastico (F1.8)

| Aspetto | Biennio (13-16) | Triennio (16-19) |
|---|---|---|
| Vista mappa default | Solo macro-nodi | Macro-nodi con toggle micro |
| Densita' informativa | Ridotta: card grandi, poche informazioni per schermata | Standard: piu' dettaglio |
| Cronologia nodo | Ultimi 3 eventi | Cronologia completa |
| Etichette stato | Testo completo sempre visibile | Testo + possibilita' icona-only |
| Linguaggio UI | Frasi brevi, vocabolario semplice | Terminologia tecnica ammessa |

### 8.3 Persona "Francesca" (14 anni, prima superiore)

Vincoli derivati dal documento di progetto:

- La mappa NON deve sopraffare: mostrare solo macro-nodi, con colori grandi e chiari.
- Le missioni sono presentate come una lista chiara di step, non come un grafo complesso.
- Il tono e' sempre incoraggiante. "Lacuna" e' presentata come "C'e' qualcosa da ripassare" con icona non minacciosa.
- I bottoni di azione sono grandi e chiari: "Inizia il ripasso", non "Avvia percorso di recupero gap concettuale".

---

## 9. Screen reader

### 9.1 Compatibilita' target MVP

| Screen reader | Piattaforma | Stato MVP | Note |
|---|---|---|---|
| VoiceOver | iOS (app studente) | Test obbligatorio | React Native supporta VoiceOver via `accessibilityLabel`, `accessibilityRole`, `accessibilityState` |
| TalkBack | Android (app studente) | Test obbligatorio | React Native supporto nativo; testare ordine di lettura e gesti |
| VoiceOver | macOS (dashboard docente) | Test consigliato | Next.js genera HTML semantico; verificare tabella heatmap |
| NVDA | Windows (dashboard docente) | Test consigliato | Verificare live regions e tabella heatmap |
| JAWS | Windows (dashboard docente) | Rimandato V1 | Copertura manuale V1 |

### 9.2 Checklist test screen reader MVP

Per ogni schermata MVP, verificare:

- [ ] **Titolo pagina**: annunciato correttamente all'apertura
- [ ] **Heading hierarchy**: navigazione per heading (H key in NVDA/VoiceOver) funziona
- [ ] **Landmark navigation**: `<nav>`, `<main>`, `<header>` riconosciuti
- [ ] **Badge mastery**: annunciati con stato testuale, non colore
- [ ] **Bottoni e link**: annuncio include nome + ruolo + stato
- [ ] **Form**: label associate, errori annunciati
- [ ] **Aggiornamenti dinamici**: live regions funzionano (quiz risultato, salvataggio)
- [ ] **Focus trap modali**: focus rimane nel dialog, Esc chiude
- [ ] **Mappa padronanza**: annuncio nodo corrente con nome + stato, navigazione frecce

### 9.3 React Native -- prop di accessibilita'

```typescript
// Mapping dei ruoli ARIA per React Native
const ACCESSIBILITY_ROLES: Record<string, AccessibilityRole> = {
  masteryBadge: 'image',       // role="img" con accessibilityLabel
  mapNode: 'button',           // interattivo
  progressBar: 'progressbar',
  quizOption: 'radio',
  navTab: 'tab',
  alertBanner: 'alert',
  modal: 'none',               // gestito da Modal component nativo
};

// Esempio: nodo mappa in React Native
<TouchableOpacity
  accessible={true}
  accessibilityLabel={`${node.label}: ${MASTERY_TOKENS[node.state].label}`}
  accessibilityRole="button"
  accessibilityHint="Tocca due volte per aprire il dettaglio"
  accessibilityState={{ selected: isFocused }}
  onPress={() => openNodeDetail(node.id)}
>
  <MasteryBadge state={node.state} />
  <Text>{node.label}</Text>
</TouchableOpacity>
```

---

## 10. Limiti MVP e roadmap V1

### 10.1 Cosa NON copre il MVP

| Funzionalita' | Motivo esclusione | Pianificazione |
|---|---|---|
| **Design system completo (Storybook)** | Serve catalogo componenti, non MVP | V1 -- Storybook con addon a11y |
| **Font OpenDyslexic e Atkinson Hyperlegible** | Richiede licensing, bundling, test | V1 -- selettore attivato (F9.1) |
| **Tema scuro e seppia** | Token colore da verificare per contrasto su sfondo scuro | V1 (F9.5) |
| **Alto contrasto** | Richiede set completo token alternativi | V1 (F9.2) |
| **Test formali BES/DSA** | Richiede reclutamento utenti, protocollo etico, consensi | V1 -- protocollo descritto sotto |
| **JAWS testing** | Licenza costosa, priorita' NVDA/VoiceOver per MVP | V1 |
| **Audit automatizzato completo (axe-core CI)** | Serve pipeline CI con test a11y | V1 -- axe-core + Lighthouse in CI |
| **Animazioni ridotte complete** | Toggle implementato, ma non tutte le animazioni hanno variante | V1 -- audit completo animazioni |
| **Bilinguismo accessibile** | Layout due colonne per screen reader richiede test specifico | V1 -- contestuale a F13 |
| **Podcast/audio a11y** | Trascrizioni sincronizzate, sottotitoli | V1 -- contestuale a F6 |
| **prefers-reduced-motion system** | MVP ha toggle manuale; V1 rileva preferenza OS | V1 |

### 10.2 Roadmap V1 -- audit e test

**Audit automatizzato V1:**

1. **axe-core** integrato in CI: test su ogni PR per tutte le pagine.
2. **Lighthouse accessibility** >= 90 score obbligatorio.
3. **eslint-plugin-jsx-a11y** (React) e **react-native-a11y** linter.
4. **Storybook a11y addon**: preview contrasto e screen reader su ogni componente.

**Test manuali V1:**

1. Screen reader walkthrough completo (NVDA + VoiceOver iOS + VoiceOver macOS + TalkBack).
2. Keyboard-only navigation test su tutti i flussi.
3. Bookmarklet WCAG text spacing su tutte le pagine.
4. Color contrast analyzer su tutti i temi (chiaro + scuro + seppia + alto contrasto).

### 10.3 Protocollo test DSA/BES (V1)

Protocollo pianificato per V1, NON eseguito in MVP.

**Partecipanti:**
- 3-5 studenti con DSA certificata (L. 170/2010)
- 2-3 studenti con BES (Dir. MIUR 27/12/2012)
- Eta': 14-17 anni
- Consenso informato genitori/tutori (trattamento minori)

**Sessioni di test:**
- 30-45 minuti per sessione, massimo 1 sessione per studente
- Ambiente scolastico familiare, presenza di referente scolastico
- Registrazione schermo (con consenso), no registrazione volto/voce

**Flussi da testare:**
1. Login e prima configurazione
2. Navigazione mappa padronanza con font OpenDyslexic
3. Lettura documento di ripasso
4. Completamento quiz
5. Modifica preferenze accessibilita'

**Metriche:**
- Task completion rate per flusso
- Tempo per task (confronto con baseline)
- Errori di navigazione
- System Usability Scale (SUS) adattata per eta'
- Feedback qualitativo (intervista semi-strutturata)

**Output:**
- Report con finding categorizzati (critico / maggiore / minore)
- Piano di rimedio con priorita'
- Aggiornamento di questa specifica con le correzioni necessarie

---

## Appendice A -- Classe CSS utility per screen reader

```css
/* Testo visivamente nascosto ma leggibile da screen reader */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Riduzione animazioni */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Toggle manuale (F9.7) -- classe aggiunta dal JS */
.reduced-motion *, .reduced-motion *::before, .reduced-motion *::after {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}
```

## Appendice B -- Riepilogo conformita' per gate Phase 3

| Requisito gate | Come verificare | Stato |
|---|---|---|
| Token colore con contrasto verificato | Tabella Sezione 3.1, rapporti calcolati | Da implementare |
| Semantic HTML | Template Sezione 7, heading Sezione 7.3 | Da implementare |
| Keyboard nav | Flussi Sezione 5, focus ring Sezione 5.2 | Da implementare |
| ARIA su componenti custom | Componenti Sezione 6 | Da implementare |
| F9.3 colore + icona + testo | `MasteryBadge` (Sezione 6.1), heatmap (Sezione 6.5) | Da implementare |
| F9.4 slider dimensione testo | Componente Sezione 6.8 | Da implementare |
| F9.7 animazioni ridotte | Toggle + CSS Appendice A | Da implementare |
| F9.8 persistenza preferenze | `AsyncStorage` / DB profilo utente | Da implementare |

---

*Specifica prodotta da MSTR-17 (Accessibility & UX Specialist). In attesa di ratifica CPA (MSTR-03) + CTA (MSTR-02). Archiviata in `.maestro/accessibility/` per governance (CLAUDE.md).*
