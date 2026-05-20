# Specifica MVP del Safeguarding Agent

**Task**: T3.2 -- Safeguarding policies + content moderation flows
**Autore**: MSTR-19 (Safeguarding & Ethics Specialist)
**Data**: 2026-05-20
**Stato**: Draft
**Revisori richiesti**: MSTR-03 (CPA), MSTR-02 (CTA), MSTR-10 (AI/ML Engineer), MSTR-20 (QA Sentinel)
**Dipendenze**: HLD-001 (Multi-Agent System), HLD-003 (Content Generation), ADR-003 (Orchestrator Pattern)
**Riferimenti normativi**: CLAUDE.md (Minor Safety), N3 (Etica e benessere), N6 (Inclusivita'), F7.7, F7.8, F8.5

---

## 1. Principi

### 1.1 Perche' il Safeguarding e' non negoziabile

Ogni studente che utilizza MAESTRO e' un minore (13-19 anni). Questo singolo fatto determina l'intera architettura di sicurezza dei contenuti. Non si tratta di una funzionalita' opzionale o di un filtro "nice-to-have": il Safeguarding Agent e' un **gate strutturale** nell'orchestratore LangGraph (ADR-003). Nessun edge del grafo collega la generazione di contenuti alla consegna allo studente senza passare per il nodo `safeguarding_gate`.

Questa garanzia e' architetturale, non convenzionale. Non dipende dalla disciplina degli sviluppatori.

### 1.2 Contesto normativo e pedagogico

| Fonte | Vincolo |
|---|---|
| CLAUDE.md -- Minor Safety | Nessun agente genera contenuto senza review del Safeguarding. Nessun confronto pubblico. Nessun FOMO/scarcity/pattern addittivi. |
| N3 (Etica e benessere) | Tono SEMPRE incoraggiante. Errore = materia prima, non colpa. Lacuna = porta aperta, non marchio. Mai sostituire un professionista per disagio psicologico. |
| N6 (Inclusivita') | Analogie diversificate e non stereotipate. Test di bias periodici (genere, geografico Nord/Sud, socio-economico). |
| F7.7 (Anti-pattern gamification) | Nessuna classifica pubblica individuale. Nessun paragone tra studenti. Nessun meccanismo addittivo. |
| F7.8 (Opt-out gamification) | Disattivazione senza perdita di progresso didattico. |
| F8.5 (Age-appropriateness) | Eliminazione automatica di gergo o riferimenti non age-appropriate. |
| GDPR Art. 8 | Trattamento dati di minori richiede consenso del titolare della responsabilita' genitoriale (gestito da Identity & Consent Manager). |

### 1.3 Principio guida

**Nel dubbio, blocca.** Un contenuto bloccato per eccesso di cautela causa solo un ritardo (il sistema rigenera o serve fallback). Un contenuto inappropriato consegnato a un minore causa danno. L'asimmetria di rischio e' netta: il costo di un falso positivo e' trascurabile rispetto al costo di un falso negativo.

---

## 2. System Prompt Rules

Le seguenti 9 regole vengono iniettate nel system prompt di **ogni** agente generativo (Text Agent, Quiz Engine, Bilingual Composer, e futuri Podcast/Game/Visual/Dialog Agent). Sono il primo livello di difesa -- la "formazione" del modello prima della generazione.

### Regola 1: MAI confrontare lo studente con altri studenti

**Testo iniettato nel prompt:**
```
REGOLA 1: MAI confrontare lo studente con altri studenti, direttamente o
indirettamente. Nessun riferimento a medie di classe, percentili, classifiche,
o frasi come "la maggior parte dei compagni". Ogni riferimento e' alla
traiettoria individuale dello studente.
```

**Esempio positivo:**
> "Questo concetto ti ha dato filo da torcere, ma il fatto che tu ci stia lavorando e' gia' un ottimo segnale."

**Esempio negativo (BLOCCATO):**
> "La maggior parte dei tuoi compagni ha capito questo concetto al primo tentativo."
> "Sei l'unico che ha sbagliato questa domanda."
> "Il punteggio medio della classe e' 7.5, tu hai preso 4."

**Razionale:** I confronti sociali in contesto scolastico generano ansia da prestazione, diminuiscono la motivazione intrinseca e possono amplificare dinamiche di bullismo. Per un minore, il peso di un confronto negativo formulato da un sistema "intelligente" e' amplificato dalla percezione di oggettivita' della macchina.

---

### Regola 2: MAI usare tono punitivo, sarcastico o scoraggiante

**Testo iniettato nel prompt:**
```
REGOLA 2: MAI usare tono punitivo, sarcastico, o scoraggiante. Anche per
insufficienza grave e lacune ripetute, il tono e' SEMPRE incoraggiante.
L'errore e' "materia prima, non colpa". Una lacuna e' "una porta aperta"
con la missione di recupero allegata. Usa frasi come "questo concetto ha
bisogno di un altro giro" invece di "hai sbagliato".
```

**Esempio positivo:**
> "Questo concetto ha bisogno di un altro giro. Nessun problema -- proviamo con un approccio diverso."
> "Non ci siamo ancora, ma ogni tentativo ti porta piu' vicino. Vediamo insieme dove si inceppa."

**Esempio negativo (BLOCCATO):**
> "Hai sbagliato di nuovo."
> "Dovresti vergognarti di questo risultato."
> "Nonostante tutti gli aiuti, ancora non riesci."
> "Ma come e' possibile che non capisci questo?" (sarcasmo)

**Razionale:** Il tono punitivo e' il primo fattore di abbandono scolastico nei contesti di difficolta'. N3 richiede esplicitamente che il rosso sia "una porta aperta, non un marchio". Il sistema non e' un giudice: e' un tutor.

---

### Regola 3: MAI usare linguaggio offensivo, discriminatorio, sessista, razzista, omofobo

**Testo iniettato nel prompt:**
```
REGOLA 3: MAI usare linguaggio offensivo, discriminatorio, sessista, razzista,
omofobo, o denigratorio in qualsiasi forma. Questo include insulti
mascherati da ironia e microaggressioni.
```

**Esempio positivo:**
> "Immagina una funzione come un distributore automatico: inserisci un input, ricevi un output."

**Esempio negativo (BLOCCATO):**
> Qualsiasi insulto, parolaccia, slur, termine denigratorio.
> "Come farebbe un vero programmatore..." (implicazione di inferiorita').
> Uso di "mongoloide", "ritardato", "gay" come insulti.

**Razionale:** F8.5 richiede eliminazione automatica di contenuti non age-appropriate. N6 richiede inclusivita'. Il linguaggio offensivo e' categoricamente incompatibile con un ambiente educativo per minori.

---

### Regola 4: MAI usare sfondo rosso per risultati negativi

**Testo iniettato nel prompt:**
```
REGOLA 4: MAI indicare un colore rosso per risultati negativi. I risultati
che necessitano miglioramento usano ARANCIONE. Le lacune sono "porte aperte
verso il recupero", non fallimenti. Questo vale per ogni riferimento a colori
nel testo generato.
```

**Esempio positivo:**
> "Il tuo stato per questo concetto e' arancione -- significa che c'e' spazio per migliorare, e la missione di recupero e' pronta."

**Esempio negativo (BLOCCATO):**
> "Il tuo risultato e' in rosso."
> "La tua performance e' contrassegnata in rosso nel sistema."

**Razionale:** N3 specifica che il rosso e' "una porta aperta, non un marchio". La semantica cromatica del rosso come fallimento e' profondamente radicata nella cultura scolastica italiana. Il sistema usa arancione per "da migliorare" per rompere questa associazione.

**Nota implementativa:** I token di colore del design system (definiti in `phase3-compliance-mvp.md`) usano `#D32F2F` per lo stato `lacuna` a livello di backend, ma il frontend e le descrizioni testuali usano sempre "arancione" nella comunicazione con lo studente.

---

### Regola 5: MAI creare urgenza artificiale (FOMO, scarcity, countdown)

**Testo iniettato nel prompt:**
```
REGOLA 5: MAI creare urgenza artificiale. Nessun FOMO ("i tuoi compagni
stanno avanzando!"), nessuna scarcity ("ultima possibilita'!"), nessun
countdown ("hai solo 3 giorni!"), nessuna colpevolizzazione ("non studi
da 5 giorni!"). Il ritmo dello studente e' il suo ritmo. Le notifiche
sono gentili, mai pressanti.
```

**Esempio positivo:**
> "Quando ti senti pronto, prova il quiz!"
> "C'e' una nuova missione di recupero disponibile per te."

**Esempio negativo (BLOCCATO):**
> "I tuoi compagni hanno gia' completato questa missione!"
> "Ultima possibilita' per guadagnare i punti della settimana!"
> "Non studi da 5 giorni. Stai perdendo terreno."
> "Solo 2 quest rimaste per oggi!"
> "Attenzione: se non completi entro venerdi', perdi lo streak!"

**Razionale:** N3 vieta esplicitamente "nudging manipolativo: niente dark pattern, FOMO, scarcity". F7.7 vieta "meccanismi addittivi (notifiche martellanti, FOMO, ricompense variabili)". I minori sono particolarmente vulnerabili a queste tecniche di persuasione.

---

### Regola 6: MAI sostituirsi a un professionista per disagio psicologico

**Testo iniettato nel prompt:**
```
REGOLA 6: MAI fornire supporto psicologico, terapeutico, o counseling.
Se il contenuto o il contesto suggerisce disagio emotivo o psicologico,
la UNICA risposta appropriata e' facilitare il contatto con il referente
scolastico (psicologo, coordinatore). Non improvvisare supporto emotivo.
Non minimizzare ("non preoccuparti, andrà tutto bene").
```

**Esempio positivo:**
> "Se senti che qualcosa ti preoccupa al di la' dello studio, ricorda che puoi sempre parlare con il tuo referente scolastico. Non sei solo."

**Esempio negativo (BLOCCATO):**
> "Non devi sentirti cosi'. Tutti attraversano momenti difficili." (terapia improvvisata)
> "Prova a rilassarti e pensare positivo." (consiglio pseudo-terapeutico)
> Qualsiasi tentativo di diagnosi, consiglio emotivo, o rassicurazione che va oltre il facilitare il contatto con un professionista.

**Razionale:** N3: "Mai sostituire un professionista: disagio psicologico -> aggancio referente scolastico." Un sistema AI che improvvisa supporto psicologico a un minore crea un rischio diretto di danno. Il sistema facilita, non sostituisce.

---

### Regola 7: Ogni lacuna e' presentata come "porta aperta" con missione di recupero

**Testo iniettato nel prompt:**
```
REGOLA 7: Ogni lacuna e' presentata come un'opportunita', non come un
problema. La formulazione standard e': "Hai una nuova missione di recupero
per [concetto]. E' un'occasione per capire meglio questo argomento."
La missione di recupero e' SEMPRE allegata o referenziata.
```

**Esempio positivo:**
> "Per il concetto 'Sessioni PHP' hai una missione di recupero pronta. E' un percorso pensato apposta per te."

**Esempio negativo (BLOCCATO):**
> "Hai una lacuna in Sessioni PHP." (senza missione allegata)
> "Purtroppo non hai capito le Sessioni PHP." (framing negativo)

**Razionale:** N3: "Il rosso e' una porta aperta, non un marchio: sempre accompagnato dalla missione di recupero." La lacuna senza percorso di recupero e' un'etichetta senza soluzione -- cio' aumenta il senso di impotenza.

---

### Regola 8: I termini tecnici sono sempre spiegati

**Testo iniettato nel prompt:**
```
REGOLA 8: I termini tecnici sono SEMPRE spiegati alla prima occorrenza,
mai dati per scontati. Se il concetto e' complesso, scomponi. Se il
vocabolario e' avanzato, fornisci una glossa.
```

**Esempio positivo:**
> "La funzione `session_start()` inizializza una sessione -- cioe' apre uno 'spazio di memoria' sul server dove puoi salvare informazioni che restano disponibili tra una pagina e l'altra."

**Esempio negativo (BLOCCATO):**
> "Devi chiamare `session_start()` prima di accedere al superglobal." (termini tecnici non spiegati per uno studente che ha una lacuna su questo concetto)

**Razionale:** F8.2 richiede adattamento lessicale. Se lo studente ha una lacuna, per definizione non padroneggia ancora il concetto -- dare per scontata la terminologia contraddice lo scopo del contenuto.

---

### Regola 9: Le analogie sono diversificate e non stereotipate

**Testo iniettato nel prompt:**
```
REGOLA 9: Le analogie sono diversificate (sport, cucina, gaming, vita
quotidiana, tecnologia, scuola) e MAI stereotipate. Nessuno stereotipo
nazionale ("come un tedesco preciso"), regionale ("al Nord si lavora, al
Sud..."), di genere ("come una mamma in cucina"), socio-economico, o
culturale. Varia il dominio delle analogie tra blocchi diversi dello
stesso documento.
```

**Esempio positivo:**
> "Pensa a una variabile come a un'etichetta su un barattolo: il nome del barattolo non cambia, ma puoi mettere dentro cose diverse."
> "Una funzione e' come una ricetta: la scrivi una volta, poi la usi ogni volta che ti serve."

**Esempio negativo (BLOCCATO):**
> "Come un napoletano che si arrangia..." (stereotipo regionale)
> "Come una donna al supermercato che confronta i prezzi..." (stereotipo di genere)
> "Come i cinesi che copiano tutto..." (stereotipo nazionale/razzista)

**Razionale:** N6 richiede "analogie e riferimenti diversificati e non stereotipati. Test di bias periodici (gender, geografico Nord/Sud, socio-economico)." Gli stereotipi nelle analogie sono insidiosi perche' sembrano neutri ("e' solo un esempio!") ma rinforzano pregiudizi, specialmente in minori in fase di formazione della propria identita'.

---

### 2.1 Prompt completo assemblato

Il system prompt viene assemblato concatenando le 9 regole con un preambolo. Ogni agente generativo lo riceve identico:

```python
SAFEGUARDING_SYSTEM_PROMPT = """
REGOLE INVIOLABILI — Il contenuto generato DEVE rispettare TUTTE queste regole.
La violazione di QUALSIASI regola causa il blocco e la rigenerazione del contenuto.

1. MAI confrontare lo studente con altri studenti, direttamente o indirettamente.
   Nessun riferimento a medie di classe, percentili, classifiche, o frasi come
   "la maggior parte dei compagni". Ogni riferimento e' alla traiettoria
   individuale dello studente.

2. MAI usare tono punitivo, sarcastico, o scoraggiante. Anche per insufficienza
   grave e lacune ripetute, il tono e' SEMPRE incoraggiante. L'errore e' "materia
   prima, non colpa". Una lacuna e' "una porta aperta". Usa frasi come "questo
   concetto ha bisogno di un altro giro" invece di "hai sbagliato".

3. MAI usare linguaggio offensivo, discriminatorio, sessista, razzista, omofobo,
   o denigratorio in qualsiasi forma. Questo include insulti mascherati da ironia
   e microaggressioni.

4. MAI indicare un colore rosso per risultati negativi. I risultati che necessitano
   miglioramento usano ARANCIONE. Le lacune sono "porte aperte verso il recupero",
   non fallimenti.

5. MAI creare urgenza artificiale. Nessun FOMO ("i tuoi compagni stanno avanzando!"),
   nessuna scarcity ("ultima possibilita'!"), nessun countdown ("hai solo 3 giorni!"),
   nessuna colpevolizzazione ("non studi da 5 giorni!").

6. MAI fornire supporto psicologico, terapeutico, o counseling. Se il contesto
   suggerisce disagio emotivo, la UNICA risposta e' facilitare il contatto con il
   referente scolastico. Non improvvisare supporto emotivo.

7. Ogni lacuna e' presentata come un'opportunita' con la missione di recupero
   SEMPRE allegata o referenziata. Mai una lacuna senza percorso di recupero.

8. I termini tecnici sono SEMPRE spiegati alla prima occorrenza, mai dati per
   scontati.

9. Le analogie sono diversificate e MAI stereotipate. Nessuno stereotipo nazionale,
   regionale (Nord/Sud), di genere, socio-economico, o culturale. Varia il dominio
   delle analogie tra blocchi diversi.
"""
```

---

## 3. Post-generation check (BLOCKED_PATTERNS)

Dopo che il modello genera il contenuto, un check deterministico in Python verifica l'assenza di pattern proibiti. Questo e' il secondo livello di difesa -- cattura cio' che il modello potrebbe aver generato nonostante le istruzioni nel prompt.

### 3.1 Architettura del check

```python
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ViolationSeverity(Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"
    ALERT = "ALERT"


class ViolationCategory(Enum):
    STUDENT_COMPARISON = "STUDENT_COMPARISON"
    PUNITIVE_TONE = "PUNITIVE_TONE"
    OFFENSIVE_LANGUAGE = "OFFENSIVE_LANGUAGE"
    FOMO_SCARCITY = "FOMO_SCARCITY"
    RED_FRAMING = "RED_FRAMING"
    STEREOTYPE = "STEREOTYPE"
    THERAPY_ATTEMPT = "THERAPY_ATTEMPT"
    AGE_INAPPROPRIATE = "AGE_INAPPROPRIATE"
    GUILT_TRIGGER = "GUILT_TRIGGER"


@dataclass
class Violation:
    category: ViolationCategory
    severity: ViolationSeverity
    pattern: str
    matched_text: str
    description: str


@dataclass
class SafeguardingCheckResult:
    passed: bool
    violations: list[Violation] = field(default_factory=list)
    content: Optional[str] = None  # contenuto originale se passato
```

### 3.2 Pattern bloccanti espansi

Ogni pattern ha un razionale esplicito. I pattern coprono sia italiano standard che possibili varianti colloquiali e output misti italiano/inglese.

```python
BLOCKED_PATTERNS: list[tuple[str, ViolationCategory, ViolationSeverity, str]] = [
    # -----------------------------------------------------------------------
    # CONFRONTO TRA STUDENTI (Regola 1, N3, F7.7)
    # -----------------------------------------------------------------------
    # "peggio/meglio di/degli altri/dei compagni/della classe"
    (
        r"(?i)\b(peggio|meglio)\s+(di|degli?\s+altri|dei\s+compagni|della\s+classe|"
        r"dei\s+tuoi\s+compagni|della\s+media|del\s+resto|rispetto\s+(agli?\s+altri|"
        r"ai\s+compagni))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto diretto con altri studenti (peggio/meglio di...)."
    ),
    # "la maggior parte / quasi tutti / tutti tranne te / solo tu"
    (
        r"(?i)(la\s+maggior\s+parte\b|quasi\s+tutti\b|tutti\s+tranne\s+te\b|"
        r"solo\s+tu\b.*\bnon|sei\s+l['\u2019]unic[oa]\s+(che|a)\s+(non|ha\s+sbagliato))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto implicito con il gruppo classe."
    ),
    # "media della classe / punteggio medio / classifica"
    (
        r"(?i)(media\s+della\s+classe|punteggio\s+medio|classifica\s+"
        r"(di\s+classe|dei\s+voti|degli?\s+studenti)|posizione\s+in\s+classifica)",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Riferimento a statistiche di classe visibili allo studente."
    ),
    # Pattern inglesi (output misto): "compared to", "unlike other students"
    (
        r"(?i)(compared\s+to\s+(other|your)\s+(students|classmates|peers)|"
        r"unlike\s+(other|most)\s+students|most\s+students\s+(get|understand|know))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto con altri studenti in inglese (output misto)."
    ),

    # -----------------------------------------------------------------------
    # TONO PUNITIVO / SCORAGGIANTE (Regola 2, N3)
    # -----------------------------------------------------------------------
    # "sei scarso/incapace/lento/stupido/negato"
    (
        r"(?i)\bsei\s+(scarso|scarsa|incapace|lent[oa]|stupid[oa]|negat[oa]|"
        r"un\s+disastro|un\s+caso\s+perso|irrecuperabile|senza\s+speranza)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Giudizio negativo diretto sulla persona dello studente."
    ),
    # "non sei/sarai mai capace"
    (
        r"(?i)non\s+(sei|sarai)\s+(mai\s+)?(capace|in\s+grado|adatt[oa]|portat[oa])",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Proiezione negativa sulle capacita' future dello studente."
    ),
    # "devi vergognarti / che figuraccia / che delusione / che disastro"
    (
        r"(?i)(devi\s+vergognarti|che\s+figuraccia|che\s+delusione|che\s+disastro|"
        r"dov?resti\s+vergognarti|che\s+vergogna|pessim[oa]\s+risultato)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Linguaggio di vergogna esplicito."
    ),
    # "hai sbagliato" (la formulazione specifica vietata da N3)
    (
        r"(?i)\bhai\s+sbagliato\b(?!\s+a\s+scrivere)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.WARN,
        "Formulazione punitiva 'hai sbagliato'. Preferire 'questo concetto ha bisogno "
        "di un altro giro'. Nota: 'hai sbagliato a scrivere [codice]' e' ammesso nel "
        "blocco 'Il tuo errore' per mostrare l'errore tecnico."
    ),
    # "come e' possibile che non capisci"
    (
        r"(?i)come\s+(e'|\u00e8)\s+possibile\s+che\s+non\s+(capisc|riesc)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Espressione di incredulita' punitiva."
    ),
    # "nonostante tutti gli aiuti / nonostante i tentativi"
    (
        r"(?i)nonostante\s+(tutti\s+gli\s+aiuti|i\s+(tanti\s+)?tentativi|tutto)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Implicazione che lo studente avrebbe dovuto riuscire dato il supporto ricevuto."
    ),

    # -----------------------------------------------------------------------
    # LINGUAGGIO OFFENSIVO / DISCRIMINATORIO (Regola 3, F8.5)
    # -----------------------------------------------------------------------
    # Insulti comuni italiani
    (
        r"(?i)\b(coglion[ei]|stronz[oiae]|cazz[oiae]|minchia|merda|vaffanculo|"
        r"cretino|deficiente|idiota|imbecille|mongoloide|ritardat[oiae]|"
        r"testa\s+di\s+(cazzo|minchia)|porco\s+dio|madonna\s+[a-z]+|"
        r"finocchio|frocio|terrone|polentone)\b",
        ViolationCategory.OFFENSIVE_LANGUAGE,
        ViolationSeverity.BLOCK,
        "Linguaggio offensivo, volgare, o discriminatorio in italiano."
    ),
    # Insulti in inglese (output misto)
    (
        r"(?i)\b(fuck|shit|bitch|asshole|retard|idiot|moron|dumb|stupid\s+kid|"
        r"loser)\b",
        ViolationCategory.OFFENSIVE_LANGUAGE,
        ViolationSeverity.BLOCK,
        "Linguaggio offensivo in inglese (output misto)."
    ),

    # -----------------------------------------------------------------------
    # FOMO / SCARCITY / URGENZA ARTIFICIALE (Regola 5, N3, F7.7)
    # -----------------------------------------------------------------------
    # "ultima possibilita' / ultima chance / ultima occasione"
    (
        r"(?i)(ultim[oa]\s+(possibilit[aà]|chance|occasione|tentativo)|"
        r"non\s+perdere\s+(l['\u2019]occasione|questa\s+opportunit)|"
        r"affrettati|sbrigati|corri|tempo\s+(sta\s+)?scadendo|"
        r"fai\s+in\s+fretta)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Pattern di urgenza artificiale / scarcity."
    ),
    # "i tuoi compagni stanno avanzando / sono gia' piu' avanti"
    (
        r"(?i)(i\s+tuoi\s+compagni\s+(stanno|sono|hanno)|"
        r"gli\s+altri\s+(stanno|sono|hanno)\s+(avanzando|avanti|finito|completato))",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "FOMO basato su confronto con i progressi dei compagni."
    ),
    # "solo N quest/missioni/giorni rimast*"
    (
        r"(?i)solo\s+\d+\s+(quest|missioni?|giorni?|ore|tentativi?)\s+rimast",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Scarcity: riferimento a risorse limitate."
    ),

    # -----------------------------------------------------------------------
    # COLPEVOLIZZAZIONE (Regola 5, N3)
    # -----------------------------------------------------------------------
    # "non studi da N giorni / non entri da / non ti fai vivo"
    (
        r"(?i)(non\s+(studi|entri|ti\s+fai\s+viv[oa]|ti\s+connetti|apri\s+l['\u2019]app)"
        r"\s+da\s+\d+\s+(giorni?|settiman[ae])|stai\s+perdendo\s+terreno|"
        r"stai\s+restando\s+indietro)",
        ViolationCategory.GUILT_TRIGGER,
        ViolationSeverity.BLOCK,
        "Colpevolizzazione per inattivita'. Viola il principio del ritmo individuale."
    ),

    # -----------------------------------------------------------------------
    # RIFERIMENTO A ROSSO PER RISULTATI NEGATIVI (Regola 4, N3)
    # -----------------------------------------------------------------------
    (
        r"(?i)(il\s+tuo\s+risultato\s+(e'|\u00e8)\s+(in\s+)?rosso|"
        r"contrassegnat[oa]\s+in\s+rosso|"
        r"semaforo\s+rosso\s+(per|sul\s+tuo)|"
        r"zona\s+rossa)",
        ViolationCategory.RED_FRAMING,
        ViolationSeverity.BLOCK,
        "Uso del colore rosso per risultati negativi. Usare 'arancione' per 'da migliorare'."
    ),

    # -----------------------------------------------------------------------
    # STEREOTIPI (Regola 9, N6)
    # -----------------------------------------------------------------------
    # Stereotipi regionali Nord/Sud
    (
        r"(?i)(al\s+nord\s+si\s+(lavora|studia)|al\s+sud\s+(non\s+si|si\s+fa\s+poco)|"
        r"come\s+un\s+(napoletano|siciliano|calabrese|meridionale|terroni?)\s+(che|"
        r"furb|arrang)|mentalit[aà]\s+(del\s+sud|meridionale|nordica))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo regionale Nord/Sud."
    ),
    # Stereotipi di genere
    (
        r"(?i)(come\s+una?\s+(mamma|donna|ragazza)\s+(in\s+cucina|che\s+fa\s+la\s+spesa|"
        r"che\s+pulisce)|non\s+(e'|\u00e8)\s+(roba\s+)?da\s+(ragazz[ei]|femmin[ea]|"
        r"maschi[oe])|lavoro\s+da\s+(uomo|donna|maschio|femmina))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo di genere."
    ),
    # Stereotipi nazionali
    (
        r"(?i)(come\s+(un\s+tedesco|i\s+tedeschi)\s+(precis|puntual|efficien)|"
        r"come\s+(un\s+cinese|i\s+cinesi)\s+(copi|lavorano\s+tanto)|"
        r"come\s+(gli?\s+american[io]|un\s+american[oa])\s+(esagera|semplific))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo nazionale."
    ),

    # -----------------------------------------------------------------------
    # TERAPIA IMPROVVISATA (Regola 6, N3)
    # -----------------------------------------------------------------------
    (
        r"(?i)(non\s+devi\s+(sentirti\s+cos[ìi]|preoccuparti|avere\s+paura)|"
        r"tutto\s+andr[aà]\s+bene|"
        r"prova\s+a\s+rilassarti|"
        r"pensa\s+positivo|"
        r"sei\s+(forte|coraggios[oa]),?\s+ce\s+la\s+farai)",
        ViolationCategory.THERAPY_ATTEMPT,
        ViolationSeverity.BLOCK,
        "Tentativo di supporto psicologico improvvisato. Facilitare contatto "
        "con referente scolastico."
    ),

    # -----------------------------------------------------------------------
    # CONTENUTO AGE-INAPPROPRIATE (Regola 3, F8.5)
    # -----------------------------------------------------------------------
    (
        r"(?i)(contenut[oi]\s+(sessual|erot|pornograf)|"
        r"violenza\s+(grafica|esplicita|fisica)|"
        r"uso\s+di\s+(droga|droghe|sostanze\s+stupefacenti)|"
        r"suicid|autolesion)",
        ViolationCategory.AGE_INAPPROPRIATE,
        ViolationSeverity.BLOCK,
        "Contenuto non appropriato per fascia 13-19. "
        "Nota: riferimenti a suicidio/autolesionismo generano anche wellbeing alert."
    ),
]
```

### 3.3 Funzione di check

```python
def safeguarding_post_check(content: str) -> SafeguardingCheckResult:
    """
    Esegue il check deterministico post-generazione.

    Returns:
        SafeguardingCheckResult con passed=True se nessun BLOCK trovato.
        Le violazioni WARN vengono registrate ma non bloccano.
    """
    violations: list[Violation] = []
    has_block = False

    for pattern, category, severity, description in BLOCKED_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            violation = Violation(
                category=category,
                severity=severity,
                pattern=pattern,
                matched_text=match.group(0),
                description=description,
            )
            violations.append(violation)
            if severity == ViolationSeverity.BLOCK:
                has_block = True

    return SafeguardingCheckResult(
        passed=not has_block,
        violations=violations,
        content=content if not has_block else None,
    )
```

### 3.4 Note sulla copertura

- I pattern coprono **italiano standard** e **output misto italiano/inglese** (il modello talvolta produce frasi in inglese anche quando istruito a scrivere in italiano).
- I pattern **non** coprono ucraino o arabo: il contenuto in lingua nativa passa dal Bilingual Composer che opera sul testo gia' validato in italiano. Il Bilingual Composer ha il proprio set di istruzioni di safeguarding nel prompt.
- I pattern usano `(?i)` per case-insensitive matching.
- I pattern gestiscono le varianti dell'apostrofo (ASCII `'` e Unicode `\u2019`) e dell'accento (`e'` vs `\u00e8`).
- I pattern sono **conservativi**: preferiscono falsi positivi (blocco di contenuto innocuo) a falsi negativi (passaggio di contenuto inappropriato).

---

## 4. Wellbeing keyword detection

### 4.1 Scopo

Rilevare, nell'input dello studente (messaggi in chat, risposte aperte, commenti facoltativi), segnali di disagio emotivo che richiedono attenzione umana. Il sistema **non** fornisce supporto psicologico -- facilita il contatto con il referente scolastico.

### 4.2 Keyword list espansa

```python
@dataclass
class WellbeingKeyword:
    phrase: str
    category: str  # frustration, hopelessness, isolation, self_harm_risk
    urgency: str   # low, medium, high, critical
    action: str    # log, alert_teacher, alert_referent


WELLBEING_KEYWORDS: list[WellbeingKeyword] = [
    # --- FRUSTRAZIONE (urgenza: low -> medium) ---
    WellbeingKeyword("non ce la faccio", "frustration", "medium",
                     "alert_teacher"),
    WellbeingKeyword("non ci riesco", "frustration", "low",
                     "log"),
    WellbeingKeyword("non capisco niente", "frustration", "low",
                     "log"),
    WellbeingKeyword("e' troppo difficile", "frustration", "low",
                     "log"),
    WellbeingKeyword("non sono capace", "frustration", "medium",
                     "alert_teacher"),
    WellbeingKeyword("non sono portato", "frustration", "medium",
                     "alert_teacher"),
    WellbeingKeyword("non sono abbastanza", "frustration", "medium",
                     "alert_teacher"),
    WellbeingKeyword("mi viene da piangere", "frustration", "medium",
                     "alert_teacher"),

    # --- DISPERAZIONE / RINUNCIA (urgenza: medium -> high) ---
    WellbeingKeyword("voglio smettere", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("voglio mollare", "hopelessness", "medium",
                     "alert_teacher"),
    WellbeingKeyword("e' inutile", "hopelessness", "medium",
                     "alert_teacher"),
    WellbeingKeyword("tanto non cambiera' niente", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("non servo a niente", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("non vale la pena", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("a che serve", "hopelessness", "medium",
                     "alert_teacher"),
    WellbeingKeyword("tanto sono stupido", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("non ce la faro' mai", "hopelessness", "high",
                     "alert_referent"),
    WellbeingKeyword("non ha senso continuare", "hopelessness", "high",
                     "alert_referent"),

    # --- ISOLAMENTO (urgenza: medium -> high) ---
    WellbeingKeyword("mi sento solo", "isolation", "high",
                     "alert_referent"),
    WellbeingKeyword("mi sento sola", "isolation", "high",
                     "alert_referent"),
    WellbeingKeyword("nessuno mi capisce", "isolation", "high",
                     "alert_referent"),
    WellbeingKeyword("nessuno mi aiuta", "isolation", "medium",
                     "alert_teacher"),
    WellbeingKeyword("non ho amici", "isolation", "high",
                     "alert_referent"),
    WellbeingKeyword("sono sempre da solo", "isolation", "high",
                     "alert_referent"),

    # --- SEGNALI DI RISCHIO (urgenza: critical) ---
    # Nota: il sistema NON gestisce crisi. Facilita il contatto umano.
    WellbeingKeyword("mi fa stare male", "self_harm_risk", "high",
                     "alert_referent"),
    WellbeingKeyword("non voglio piu' andare a scuola", "self_harm_risk", "high",
                     "alert_referent"),
    WellbeingKeyword("mi faccio del male", "self_harm_risk", "critical",
                     "alert_referent"),
    WellbeingKeyword("voglio farla finita", "self_harm_risk", "critical",
                     "alert_referent"),
    WellbeingKeyword("non voglio piu' vivere", "self_harm_risk", "critical",
                     "alert_referent"),
    WellbeingKeyword("mi voglio ammazzare", "self_harm_risk", "critical",
                     "alert_referent"),
    WellbeingKeyword("mi taglio", "self_harm_risk", "critical",
                     "alert_referent"),
]
```

### 4.3 Funzione di detection

```python
def detect_wellbeing_signals(
    student_input: str,
) -> list[WellbeingKeyword]:
    """
    Scansiona l'input dello studente per keyword di wellbeing.
    Restituisce la lista di match ordinata per urgenza (critical > high > medium > low).
    """
    input_lower = student_input.lower()
    # Normalizza apostrofi e accenti
    input_normalized = (
        input_lower
        .replace("\u2019", "'")
        .replace("\u00e8", "e'")
        .replace("\u00e0", "a'")
        .replace("\u00f2", "o'")
        .replace("\u00f9", "u'")
    )

    matches: list[WellbeingKeyword] = []
    for kw in WELLBEING_KEYWORDS:
        if kw.phrase in input_normalized:
            matches.append(kw)

    # Ordina per urgenza
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    matches.sort(key=lambda m: urgency_order.get(m.urgency, 99))

    return matches
```

### 4.4 Flow dell'alert al docente

```
[Input studente] --> [detect_wellbeing_signals()]
     |
     +-- Nessun match --> prosegui normalmente
     |
     +-- Match con urgency "low" --> log in `safeguarding_verdicts`, nessun alert
     |
     +-- Match con urgency "medium" --> ALERT DOCENTE
     |       |
     |       v
     |   [Crea record in `wellbeing_alerts` table]
     |       |
     |       v
     |   [Notifica push al docente nella dashboard (F16.1)]
     |       |
     |       v
     |   [Il docente vede nella sezione "Alert benessere":]
     |       - Studente: [nome]
     |       - Data/ora: [timestamp]
     |       - Segnale rilevato: [frase]
     |       - Categoria: [frustration/hopelessness/isolation]
     |       - Azione suggerita: "Verifica di persona lo stato d'animo dello studente"
     |       - Pulsante: "Preso in carico" (log nell'audit trail)
     |
     +-- Match con urgency "high" --> ALERT DOCENTE + REFERENTE SCOLASTICO
     |       |
     |       v
     |   [Come sopra, piu':]
     |   [Notifica al referente scolastico (psicologo/coordinatore)]
     |   [Azione suggerita: "Contattare lo studente entro 24 ore"]
     |
     +-- Match con urgency "critical" --> ALERT IMMEDIATO REFERENTE
             |
             v
         [Come sopra, piu':]
         [Flag "URGENTE" nella notifica]
         [Azione suggerita: "Contattare lo studente IMMEDIATAMENTE.
          Considerare il coinvolgimento dei servizi scolastici."]
         [Nota: il sistema NON gestisce crisi. Il referente gestisce.]
```

### 4.5 Struttura dati dell'alert

```python
@dataclass
class WellbeingAlert:
    alert_id: str               # UUID
    student_id: str             # ID interno (non pseudo)
    detected_phrase: str        # La frase rilevata
    category: str               # frustration, hopelessness, isolation, self_harm_risk
    urgency: str                # low, medium, high, critical
    context: str                # Contesto della conversazione (ultimi 3 messaggi)
    timestamp: str              # ISO-8601
    notified_teacher: bool
    notified_referent: bool
    acknowledged_by: str | None # chi ha preso in carico
    acknowledged_at: str | None
    resolution_notes: str | None
```

```sql
CREATE TABLE safeguarding.wellbeing_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES core.students(id),
    detected_phrase TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'frustration', 'hopelessness', 'isolation', 'self_harm_risk'
    )),
    urgency TEXT NOT NULL CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    context TEXT,                    -- ultimi 3 messaggi per contesto
    notified_teacher BOOLEAN NOT NULL DEFAULT false,
    notified_referent BOOLEAN NOT NULL DEFAULT false,
    acknowledged_by UUID REFERENCES core.users(id),
    acknowledged_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_wellbeing_alerts_student
    ON safeguarding.wellbeing_alerts (student_id, created_at DESC);
CREATE INDEX idx_wellbeing_alerts_unack
    ON safeguarding.wellbeing_alerts (acknowledged_at)
    WHERE acknowledged_at IS NULL;
```

### 4.6 SLA di risposta

| Urgenza | Notifica a | Entro | SLA presa in carico |
|---|---|---|---|
| low | Solo log | -- | -- |
| medium | Docente | Real-time (push notification) | Entro la giornata scolastica |
| high | Docente + Referente scolastico | Real-time | Entro 24 ore |
| critical | Referente scolastico + Docente | Real-time, flag URGENTE | Immediata (stessa giornata) |

**Nota MVP:** Gli SLA sono indicativi. Il sistema genera la notifica in real-time. La presa in carico e' responsabilita' umana. Il sistema logga se un alert non viene preso in carico entro lo SLA e lo ri-notifica.

---

## 5. Retry e fallback

### 5.1 Logica di retry

Quando il Safeguarding Agent (check deterministico + review LLM) blocca un contenuto, il sistema tenta di rigenerarlo con un prompt modificato.

```
Tentativo 1 (prompt standard)
    |
    --> safeguarding_post_check() + LLM review
    |
    BLOCCATO --> Tentativo 2 (prompt rinforzato)
                    |
                    --> safeguarding_post_check() + LLM review
                    |
                    BLOCCATO --> Tentativo 3 (prompt ultra-conservativo)
                                    |
                                    --> safeguarding_post_check() + LLM review
                                    |
                                    BLOCCATO --> FALLBACK (nessuna generazione LLM)
```

### 5.2 Cosa cambia nel prompt ad ogni retry

```python
RETRY_PROMPT_MODIFICATIONS = {
    1: {
        # Tentativo 2: aggiungi contesto sulla violazione specifica
        "prefix": (
            "ATTENZIONE: il contenuto precedente e' stato bloccato per: "
            "{violation_descriptions}. "
            "Rigenera evitando SPECIFICAMENTE questi pattern. "
        ),
        "temperature_override": 0.3,  # Ridotta per output piu' conservativo
    },
    2: {
        # Tentativo 3: prompt ultra-conservativo
        "prefix": (
            "MODALITA' ULTRA-SICURA. Il contenuto precedente e' stato bloccato "
            "DUE VOLTE. Genera un contenuto ESTREMAMENTE NEUTRO e FATTUALE. "
            "Nessuna analogia, nessun riferimento culturale, nessun humor. "
            "Solo spiegazione tecnica diretta con tono neutro. "
            "Se in dubbio, ometti. "
        ),
        "temperature_override": 0.1,
        "remove_sections": ["analogies", "cultural_references"],
    },
}
```

### 5.3 Struttura dati del retry

```python
@dataclass
class RetryContext:
    attempt_number: int            # 1, 2, 3
    previous_violations: list[Violation]
    prompt_modification: dict
    original_request_id: str


def build_retry_prompt(
    original_prompt: str,
    retry_context: RetryContext,
) -> str:
    """
    Costruisce il prompt per il retry, aggiungendo le informazioni
    sulla violazione precedente e le modifiche al prompt.
    """
    mod = RETRY_PROMPT_MODIFICATIONS.get(retry_context.attempt_number - 1, {})
    prefix = mod.get("prefix", "").format(
        violation_descriptions="; ".join(
            v.description for v in retry_context.previous_violations
        )
    )
    return prefix + original_prompt
```

### 5.4 Fallback dopo 3 tentativi falliti

Se il contenuto viene bloccato dopo il terzo tentativo:

1. **Il contenuto NON viene consegnato allo studente.** Mai consegnare contenuto non validato a un minore.

2. **Viene servito contenuto fallback:**
   - **Prima scelta:** Il segmento della lezione del docente (materiale originale caricato) per il concetto in questione. Recuperato dal vector store con `material_type = 'lesson'`.
   - **Seconda scelta:** Se non esiste materiale del docente per il concetto specifico, viene servito un messaggio generico:

```python
FALLBACK_MESSAGE = {
    "it": (
        "Il contenuto personalizzato per questo argomento non e' disponibile "
        "al momento. Il tuo docente e' stato avvisato e ti fornira' il "
        "materiale di studio. Nel frattempo, puoi consultare gli appunti "
        "della lezione nella sezione 'Materiali'."
    ),
}
```

3. **Il docente riceve un alert:**

```python
@dataclass
class SafeguardingBlockAlert:
    alert_type: str = "content_generation_blocked"
    student_pseudo_id: str = ""
    concept_node_id: str = ""
    concept_label: str = ""
    attempts: int = 3
    violation_summary: list[str] = field(default_factory=list)
    fallback_served: str = ""  # "teacher_lesson" o "generic_message"
    action_required: str = (
        "Il sistema non e' riuscito a generare contenuto sicuro per questo "
        "concetto dopo 3 tentativi. Si prega di verificare il materiale "
        "didattico disponibile per il concetto e, se necessario, fornire "
        "manualmente materiale integrativo."
    )
```

4. **L'evento viene loggato** nella tabella `safeguarding.safeguarding_verdicts` con tutti i dettagli dei 3 tentativi per analisi post-mortem da parte di MSTR-19.

### 5.5 Tabella dei verdetti

```sql
CREATE TABLE safeguarding.safeguarding_verdicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,           -- correlazione col workflow
    content_type TEXT NOT NULL,          -- 'review_document', 'quiz', 'remediation_path'
    attempt_number INT NOT NULL,         -- 1, 2, 3
    verdict TEXT NOT NULL CHECK (verdict IN ('safe', 'blocked', 'warn', 'alert')),
    violations JSONB,                    -- lista di violazioni trovate
    check_method TEXT NOT NULL,          -- 'regex', 'llm', 'regex+llm'
    model_id TEXT,                       -- se LLM usato
    latency_ms INT NOT NULL,
    fallback_served BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_verdicts_request
    ON safeguarding.safeguarding_verdicts (request_id, attempt_number);
CREATE INDEX idx_verdicts_blocked
    ON safeguarding.safeguarding_verdicts (verdict, created_at DESC)
    WHERE verdict = 'blocked';
```

---

## 6. Gamification anti-pattern guard

### 6.1 Pattern vietati

Basato su F7.7, F7.8 e CLAUDE.md (Minor Safety):

| Anti-pattern | Descrizione | Perche' e' vietato |
|---|---|---|
| **Classifica pubblica** | Qualsiasi UI che mostri XP/rank/badge di uno studente ad altri studenti | I confronti sociali creano ansia e competitivita' tossica in contesto scolastico per minori |
| **FOMO** | "I tuoi compagni stanno avanzando!", "Non perdere lo streak!" | Manipolazione emotiva basata sulla paura di essere esclusi |
| **Scarcity** | "Solo 2 quest rimaste oggi!", "Ultima occasione!" | Crea urgenza artificiale che contraddice il principio del ritmo individuale |
| **Countdown** | Timer visibili durante quiz o missioni | Genera ansia da prestazione. Il `time_spent_ms` viene registrato silenziosamente per analytics, MAI mostrato |
| **Ricompense variabili** | Reward casuali ("loot box", gacha) | Meccanismo addittivo (variable-ratio reinforcement schedule) -- vietato per minori |
| **Notifiche martellanti** | Piu' di 1 notifica non richiesta al giorno | Pressione all'uso compulsivo |
| **Guilt trip** | "Non studi da 3 giorni", "Hai perso lo streak" | Colpevolizzazione -- contraddice il tono sempre incoraggiante |
| **Confronto** | Qualsiasi confronto di XP, badge, streak, punteggio tra studenti | Vedi Classifica pubblica |
| **Dark pattern UI** | Opt-out nascosto, doppia negazione, pulsanti ingannevoli | Viola il principio del consenso informato, aggravato dal target minori |

### 6.2 Enforcement tecnico

L'enforcement avviene a **due livelli**: regole nel prompt degli agenti generativi e check deterministico nel post-generation.

#### Livello 1: Prompt del Game Agent (V1) e di tutti gli agenti

Gia' coperto dalle 9 regole di safeguarding (sezione 2), in particolare:
- Regola 1 (mai confrontare)
- Regola 5 (mai FOMO/scarcity/countdown/colpevolizzazione)

#### Livello 2: Pattern regex specifici per gamification

Questi pattern si aggiungono ai `BLOCKED_PATTERNS` della sezione 3 e sono specifici per il contenuto generato dal Game Agent e dalle notifiche:

```python
GAMIFICATION_BLOCKED_PATTERNS: list[tuple[str, ViolationCategory, ViolationSeverity, str]] = [
    # Classifica / ranking
    (
        r"(?i)(sei\s+(al\s+)?(primo|secondo|terzo|ultimo|penultimo)\s+posto|"
        r"la\s+tua\s+posizione\s+(e'|\u00e8)|"
        r"classifica\s+(di\s+classe|settimanale|mensile)|"
        r"sei\s+\d+[°oa]\s+su\s+\d+|"
        r"rank|leaderboard|top\s+\d+)",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Riferimento a classifica o ranking individuale."
    ),

    # Streak pressure / guilt
    (
        r"(?i)(hai\s+perso\s+(lo|il)\s+streak|"
        r"lo\s+streak\s+(sta\s+per\s+)?scad|"
        r"non\s+perdere\s+(lo|il)\s+streak|"
        r"il\s+tuo\s+streak\s+(e'|\u00e8)\s+in\s+pericolo)",
        ViolationCategory.GUILT_TRIGGER,
        ViolationSeverity.BLOCK,
        "Pressione sullo streak. Lo streak freeze (F7.4) deve essere "
        "disponibile e comunicato senza pressione."
    ),

    # Countdown / timer esplicito
    (
        r"(?i)(hai\s+(solo\s+)?\d+\s+(ore|minuti|secondi)\s+(per|rimanenti|rimast)|"
        r"il\s+tempo\s+(sta\s+per\s+)?scad|"
        r"timer|countdown|orologio\s+che\s+scorre)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Countdown o timer esplicito. I quiz non hanno timer visibile."
    ),

    # Ricompensa variabile / gacha
    (
        r"(?i)(premio\s+casual|premio\s+random|sorpresa|"
        r"premi\s+misterios|scatola\s+(misteriosa|a\s+sorpresa)|"
        r"loot\s*box|gacha|reward\s+random)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Meccanismo di ricompensa variabile (addictive pattern)."
    ),
]
```

#### Livello 3: Enforcement architetturale (non solo content-based)

Oltre ai check sul contenuto generato, i seguenti vincoli sono enforced a livello di API:

```python
# Vincoli architetturali (non content-based, enforced nel backend)

GAMIFICATION_ARCHITECTURAL_RULES = {
    # Nessun endpoint espone XP/rank di uno studente ad altri studenti
    "no_public_leaderboard": {
        "enforcement": "API design -- nessun endpoint /api/v1/leaderboard",
        "check": "Code review + test di integrazione",
    },

    # Game Agent non ha accesso allo stato di altri studenti
    "no_cross_student_access": {
        "enforcement": "Il Game Agent riceve solo student_id singolo, "
                       "nessuna query multi-studente",
        "check": "Schema di input del Game Agent non accetta liste di student_id",
    },

    # Opt-out preserva progresso
    "opt_out_preserves_progress": {
        "enforcement": "Quando gamification_enabled=false, i dati XP/badge/streak "
                       "restano nel DB. Le API restituiscono payload vuoto. "
                       "Se riattivato, i dati precedenti sono ripristinati.",
        "check": "Test di integrazione: opt-out -> opt-in -> verifica dati",
    },

    # Notifiche: max 1 non richiesta al giorno
    "notification_throttle": {
        "enforcement": "Rate limiter sulle notifiche gamification: "
                       "max 1/giorno per studente",
        "check": "Test unitario sul notification throttler",
    },
}
```

---

## 7. Integrazione orchestratore

### 7.1 Posizione nel grafo LangGraph

Il Safeguarding Agent e' un nodo obbligatorio nel `StateGraph` dell'orchestratore (HLD-001, ADR-003). La sua posizione e':

```
[Content Orchestrator]
        |
        v
[Text Agent / Quiz Engine / Bilingual Composer]   <-- nodi generativi
        |
        v
[safeguarding_gate]   <-- NODO OBBLIGATORIO
        |
        +-- SAFE --> [deliver_to_student]
        |
        +-- BLOCKED --> [safeguarding_block_handler]
        |                   |
        |                   v
        |               [retry con prompt modificato]
        |                   |
        |                   v
        |               [safeguarding_gate] (re-review)
        |                   |
        |                   +-- SAFE --> [deliver_to_student]
        |                   +-- BLOCKED (2x) --> [fallback_handler]
        |                                            |
        |                                            v
        |                                        [serve teacher material]
        |                                        [alert teacher]
        |
        +-- ALERT (wellbeing) --> [deliver_to_student]
                                       |
                                       v
                                  [wellbeing_alert_handler]
                                       |
                                       v
                                  [notifica docente/referente]
```

### 7.2 Nodi che precedono il safeguarding_gate

| Nodo | Output rilevante |
|---|---|
| `text_agent` | `generated_content: TextDocument` |
| `quiz_engine` | `generated_content: Quiz` |
| `bilingual_composer` | `generated_content: BilingualDocument` |
| `podcast_agent` (V1) | `generated_content: PodcastScript` |
| `game_agent` (V1) | `generated_content: QuestDescriptions` |
| `visual_agent` (V1) | `generated_content: VisualContent` |

### 7.3 Nodi che seguono il safeguarding_gate

| Nodo | Condizione |
|---|---|
| `deliver_to_student` | `safeguarding_verdict.safe == True` |
| `safeguarding_block_handler` | `safeguarding_verdict.safe == False` |
| `wellbeing_alert_handler` | `safeguarding_verdict.wellbeing_alert.detected == True` |
| `feedback_loop` | Dopo `deliver_to_student` |

### 7.4 Garanzia strutturale

**Non esiste un edge nel grafo LangGraph che colleghi un nodo generativo a `deliver_to_student` senza passare per `safeguarding_gate`.** Questa garanzia e' verificabile staticamente ispezionando la definizione del grafo:

```python
# Pseudocodice della definizione del grafo (verificabile)
graph = StateGraph(MaestroState)

# ... definizione nodi ...

# Dopo ogni nodo generativo, OBBLIGATORIO safeguarding_gate
graph.add_edge("text_agent", "safeguarding_gate")
graph.add_edge("quiz_engine", "safeguarding_gate")
graph.add_edge("bilingual_composer", "safeguarding_gate")

# Conditional edge dal safeguarding
graph.add_conditional_edges(
    "safeguarding_gate",
    route_safeguarding_verdict,
    {
        "safe": "deliver_to_student",
        "blocked": "safeguarding_block_handler",
        "alert": "deliver_with_alert",
    }
)

# NON ESISTE: graph.add_edge("text_agent", "deliver_to_student")
# NON ESISTE: graph.add_edge("quiz_engine", "deliver_to_student")
```

### 7.5 Cosa succede se il Safeguarding Agent e' non disponibile

Il Safeguarding Agent e' classificato come **critical** (HLD-001, Sezione 8.1):

1. Se il LLM usato per la review non e' disponibile: **applica solo il check deterministico** (regex). Il contenuto passa solo se il check deterministico trova zero violazioni. Soglia piu' alta del normale (zero tolerance).

2. Se anche il check deterministico fallisce (errore di sistema): **blocca la consegna**. Nessun contenuto non revisionato arriva a un minore.

3. In entrambi i casi: il docente viene avvisato che il safeguarding opera in modalita' degradata.

### 7.6 Nodo safeguarding nel MaestroState

```python
# Campi di MaestroState relativi al safeguarding
class MaestroState(TypedDict):
    # ... altri campi ...

    # Output del safeguarding gate
    safeguarding_verdict: Optional[SafeguardingVerdict]

    # Contesto retry
    safeguarding_retry_count: int          # 0, 1, 2
    safeguarding_previous_violations: list[dict]

    # Wellbeing
    wellbeing_alerts_triggered: list[dict]
```

```python
@dataclass
class SafeguardingVerdict:
    safe: bool
    issues: list[dict]      # [{category, severity, description, location}]
    check_methods_used: list[str]  # ["regex", "llm"] o ["regex"] (degraded)
    wellbeing_alert: Optional[WellbeingAlertInfo]
    latency_ms: int
    model_id: Optional[str]  # None se solo regex


@dataclass
class WellbeingAlertInfo:
    detected: bool
    category: Optional[str]
    urgency: Optional[str]
    recommended_action: Optional[str]
```

---

## 8. Metriche e monitoring

### 8.1 Metriche da loggare

| Metrica | Tipo | Descrizione | Alert threshold |
|---|---|---|---|
| `maestro.safeguarding.block_rate` | Gauge | % contenuti bloccati su totale generati | >5% (indica problema di qualita' nei prompt) |
| `maestro.safeguarding.block_rate_by_category` | Gauge per categoria | % blocchi per categoria (comparison, tone, offensive...) | >2% per qualsiasi categoria |
| `maestro.safeguarding.retry_rate` | Gauge | % contenuti che richiedono almeno 1 retry | >10% |
| `maestro.safeguarding.fallback_rate` | Gauge | % contenuti che vanno in fallback (3 tentativi falliti) | >1% (critico) |
| `maestro.safeguarding.latency_ms` | Histogram | Latenza del check safeguarding (regex + LLM) | P95 >5s per review doc, >3s per quiz |
| `maestro.safeguarding.wellbeing_alerts_total` | Counter | Numero totale di wellbeing alert generati | >3/giorno per classe (escalation a CPA) |
| `maestro.safeguarding.wellbeing_alerts_by_urgency` | Counter per urgenza | Alert suddivisi per urgenza | Qualsiasi "critical" genera notifica immediata |
| `maestro.safeguarding.wellbeing_unack_count` | Gauge | Alert non presi in carico | >0 per >24h (ri-notifica) |
| `maestro.safeguarding.degraded_mode_active` | Boolean gauge | 1 se il safeguarding opera solo con regex (LLM non disponibile) | >0 per >5 min |
| `maestro.safeguarding.most_blocked_pattern` | Top-N | Pattern regex che blocca piu' spesso | Per analisi qualitativa (no alert automatico) |

### 8.2 Dashboard docente (MVP minima)

Il docente vede nella propria dashboard una sezione "Sicurezza e benessere" con:

| Elemento | Contenuto |
|---|---|
| **Alert benessere** | Lista degli alert non presi in carico, ordinati per urgenza. Per ciascuno: studente, frase rilevata, categoria, data/ora, pulsante "Preso in carico". |
| **Contenuti bloccati** | Contatore dei contenuti bloccati nell'ultima settimana. Se >0, lista dei concetti per cui la generazione ha fallito con link per fornire materiale integrativo. |
| **Stato safeguarding** | Indicatore: "Operativo" (verde) / "Modalita' ridotta" (arancione, solo regex) / "Non disponibile" (rosso, bloccante). |

### 8.3 Dashboard interna (per MSTR-19, MSTR-03, DevOps)

Pannelli Grafana aggiuntivi (non visibili al docente):

| Pannello | Metriche |
|---|---|
| **Block rate trend** | Tasso di blocco nel tempo (giornaliero/settimanale) con breakdown per categoria |
| **Pattern frequency** | Heatmap dei pattern regex piu' frequentemente attivati |
| **Retry funnel** | Tentativo 1 -> 2 -> 3 -> fallback, con conversion rate |
| **Wellbeing trend** | Numero di alert per categoria nel tempo |
| **Latency distribution** | Distribuzione della latenza del check safeguarding |
| **Degraded mode events** | Timeline degli eventi in cui il safeguarding ha operato senza LLM |

---

## 9. Limiti MVP e roadmap V1

### 9.1 Cosa NON copre il MVP

| Limitazione MVP | Rischio residuo | Piano V1 |
|---|---|---|
| **Nessun ML classifier** | I pattern regex non catturano tono punitivo sottile, sarcasmo mascherato, stereotipi impliciti | Introdurre un classificatore ML fine-tuned per tono e stereotipi come pre-filtro prima del check LLM |
| **Nessun pattern temporale** | Non rileva: regressione ripetuta (3+ sullo stesso concetto), inattivita' prolungata post-lacuna, uso notturno | Implementare query periodiche su KMM + engagement metrics (gia' specificate in HLD-001 Sezione 7.3 e HLD-003 Sezione 8.3) |
| **Nessuna escalation automatica** | L'alert al referente scolastico richiede che il docente lo inoltri manualmente (tranne per urgenza high/critical) | Canale di notifica diretto al referente scolastico per tutti gli alert high/critical, senza intermediazione del docente |
| **Wellbeing solo su keyword** | Non rileva disagio espresso con parafrasi, eufemismi, o in lingue diverse dall'italiano | ML sentiment analysis + supporto multilingua per detection |
| **Bias audit non automatizzato** | La verifica di bias nelle analogie e nel tono e' affidata al check LLM, non a un processo strutturato | Pipeline automatizzata: campionamento periodico di contenuti generati + classificatore di bias + report trimestrale |
| **Quiz-specific check limitato** | Il check sui quiz verifica solo pattern testuali, non la validita' pedagogica delle domande | Analisi psicometrica (item difficulty, discrimination index) a partire dai dati di risposta degli studenti |
| **Single-language detection** | I pattern regex coprono solo italiano + inglese | Estendere i pattern a ucraino e arabo per il contenuto bilingue |
| **Nessun feedback dal docente sul safeguarding** | Il docente non puo' segnalare falsi positivi/negativi per migliorare il sistema | Pulsante "Segnala errore safeguarding" con feedback loop ai pattern e al prompt |
| **Nessun monitoring notturno** | Il check `student_age < 16 AND hour >= 21` non e' implementato in MVP | Implementare come scheduled check nel Feedback Loop Agent |

### 9.2 Roadmap V1 dettagliata

#### ML Classifier (pre-filtro)

```
[Contenuto generato]
        |
        v
[ML Pre-Filter]  <-- NUOVO V1: classificatore leggero (~100ms)
        |
        +-- Probabilita' violazione > 0.7 --> [Regex check + LLM review]
        +-- Probabilita' violazione < 0.3 --> [Regex check solo] (risparmio LLM)
        +-- 0.3-0.7 --> [Regex check + LLM review]
        |
        v
[Safeguarding verdict]
```

Il classificatore viene fine-tuned su:
- Contenuti bloccati durante il MVP (dataset reale di violazioni)
- Dataset sintetico di contenuti sicuri e non sicuri generati con variazioni delle 9 regole
- Validazione manuale da MSTR-19 + MSTR-22

#### Pattern temporali (wellbeing avanzato)

```python
# Scheduled job (nightly) -- V1
TEMPORAL_WELLBEING_CHECKS = {
    "repeated_regression": {
        "query": """
            SELECT student_id, node_id, COUNT(*) as regression_count
            FROM kmm.kmm_transitions
            WHERE new_state = 'lacuna'
              AND prev_state IN ('da_consolidare', 'consolidato', 'in_recupero')
              AND created_at > NOW() - INTERVAL '30 days'
            GROUP BY student_id, node_id
            HAVING COUNT(*) >= 3
        """,
        "action": "alert_teacher",
        "message": "Lo studente ha avuto {count} regressioni sul concetto "
                   "'{concept}' negli ultimi 30 giorni. Potrebbe servire un "
                   "approccio diverso.",
    },
    "extended_inactivity": {
        "query": """
            SELECT s.id as student_id,
                   MAX(fe.created_at) as last_activity,
                   NOW() - MAX(fe.created_at) as inactivity_days
            FROM core.students s
            LEFT JOIN engagement.feedback_events fe ON s.id = fe.student_id
            WHERE EXISTS (
                SELECT 1 FROM kmm.student_node_states sns
                WHERE sns.student_id = s.id AND sns.state = 'lacuna'
            )
            GROUP BY s.id
            HAVING NOW() - MAX(fe.created_at) > INTERVAL '7 days'
        """,
        "action": "alert_teacher",
        "message": "Lo studente non accede al sistema da {days} giorni e "
                   "ha lacune aperte. Una verifica di persona potrebbe essere utile.",
    },
    "quiz_abandonment": {
        "query": """
            SELECT student_id, COUNT(*) as abandoned_count
            FROM engagement.quiz_sessions
            WHERE completed = false
              AND created_at > NOW() - INTERVAL '14 days'
            GROUP BY student_id
            HAVING COUNT(*) >= 3
        """,
        "action": "alert_teacher",
        "message": "Lo studente ha abbandonato {count} quiz nelle ultime "
                   "2 settimane. Potrebbe essere in difficolta' o frustrato.",
    },
    "late_night_usage": {
        "query": """
            SELECT s.id as student_id,
                   COUNT(*) as late_sessions
            FROM core.students s
            JOIN engagement.feedback_events fe ON s.id = fe.student_id
            WHERE EXTRACT(HOUR FROM fe.created_at AT TIME ZONE 'Europe/Rome') >= 23
              AND s.birth_date > NOW() - INTERVAL '16 years'  -- under 16
              AND fe.created_at > NOW() - INTERVAL '7 days'
            GROUP BY s.id
            HAVING COUNT(*) >= 2
        """,
        "action": "alert_teacher",
        "message": "Lo studente (under 16) ha avuto {count} sessioni "
                   "dopo le 23:00 nell'ultima settimana.",
    },
}
```

#### Escalation automatica (V1)

```
Alert urgency "high" o "critical"
        |
        v
[Notifica diretta al referente scolastico]
        |
        v
[Notifica parallela al docente]
        |
        v
[Se non preso in carico entro SLA:]
        |
        v
[Re-notifica + escalation al coordinatore]
```

#### Bias audit harness (V1)

Processo trimestrale:

1. **Campionamento**: estrarre 200 contenuti generati random (stratificati per tipo, concetto, profilo studente)
2. **Classificazione automatica**: passare ogni contenuto per un classificatore di bias (genere, geografia, socio-economico, culturale, eta')
3. **Review manuale**: 50 contenuti (25% del campione) revisionati manualmente da MSTR-19 + MSTR-22
4. **Report**: tasso di bias per categoria, trend rispetto al trimestre precedente, azioni correttive
5. **Remediation**: findings alimentano aggiornamenti ai prompt templates e ai pattern regex

---

## Appendice A: Checklist di implementazione MVP

- [ ] System prompt safeguarding (9 regole) iniettato in tutti gli agenti generativi
- [ ] `BLOCKED_PATTERNS` implementati in `safeguarding/checks.py`
- [ ] `GAMIFICATION_BLOCKED_PATTERNS` implementati e uniti ai BLOCKED_PATTERNS
- [ ] `safeguarding_post_check()` funzione implementata e testata
- [ ] `WELLBEING_KEYWORDS` implementate in `safeguarding/wellbeing.py`
- [ ] `detect_wellbeing_signals()` funzione implementata e testata
- [ ] Nodo `safeguarding_gate` nel grafo LangGraph con conditional edges
- [ ] Retry logic (max 2 retry con prompt modificato)
- [ ] Fallback handler (serve materiale docente o messaggio generico)
- [ ] Tabella `safeguarding.safeguarding_verdicts` creata nel DDL
- [ ] Tabella `safeguarding.wellbeing_alerts` creata nel DDL
- [ ] Alert docente per wellbeing (push notification nella dashboard)
- [ ] Alert docente per contenuto bloccato dopo fallback
- [ ] Sezione "Sicurezza e benessere" nella dashboard docente
- [ ] Metriche OpenTelemetry per block_rate, wellbeing_alerts, latency
- [ ] Test unitari: ogni pattern regex ha almeno 2 test (match + non-match)
- [ ] Test di integrazione: workflow completo generate -> safeguarding -> deliver
- [ ] Test di integrazione: workflow fallback (3 blocchi -> fallback)

---

## Appendice B: Mapping requisiti -> sezioni del documento

| Requisito | Sezione |
|---|---|
| N3 (Etica e benessere) | 1, 2 (tutte le regole), 3, 4, 5, 6 |
| N6 (Inclusivita') | 2 (Regola 9), 3.2 (pattern stereotipi), 9.2 (bias audit) |
| F7.7 (Anti-pattern gamification) | 6 |
| F7.8 (Opt-out gamification) | 6 (enforcement architetturale) |
| F8.5 (Age-appropriateness) | 2 (Regola 3), 3.2 (pattern offensivi e age-inappropriate) |
| CLAUDE.md Minor Safety | 1, 2, 7 (garanzia strutturale) |
| ADR-003 (Orchestrator) | 7 (integrazione nel grafo LangGraph) |
| HLD-001 Sezione 3.10 | 7 (nodo safeguarding), 5 (retry/fallback) |
| HLD-001 Sezione 7 | 4 (wellbeing detection), 8 (metriche) |
| HLD-003 Sezione 8 | 3 (post-generation check), 5 (retry nel content pipeline) |

---

*Documento versione 1.0. Task T3.2 del DAG MAESTRO. Soggetto a review da MSTR-03 (CPA), MSTR-02 (CTA), MSTR-10 (AI/ML Engineer), MSTR-20 (QA Sentinel).*
