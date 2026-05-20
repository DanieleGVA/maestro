"""Safeguarding post-generation check.

Implements the deterministic regex-based content check from safeguarding-mvp-spec.md.
This is the second line of defence after the system prompt rules.

Every piece of LLM-generated content passes through this checker BEFORE reaching any student.
"""

import re
from dataclasses import dataclass, field
from enum import Enum


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
class SafeguardingResult:
    passed: bool
    violations: list[Violation] = field(default_factory=list)
    content: str | None = None


# ---------------------------------------------------------------------------
# System prompt safeguarding rules (injected into EVERY LLM call)
# From safeguarding-mvp-spec.md Section 2.1
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_SAFEGUARDING = """\
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


# ---------------------------------------------------------------------------
# BLOCKED_PATTERNS: deterministic regex checks (safeguarding-mvp-spec.md Section 3.2)
# ---------------------------------------------------------------------------
BLOCKED_PATTERNS: list[tuple[str, ViolationCategory, ViolationSeverity, str]] = [
    # -------------------------------------------------------------------
    # CONFRONTO TRA STUDENTI (Regola 1, N3, F7.7)
    # -------------------------------------------------------------------
    (
        r"(?i)\b(peggio|meglio)\s+(di|degli?\s+altri|dei\s+compagni|della\s+classe|"
        r"dei\s+tuoi\s+compagni|della\s+media|del\s+resto|rispetto\s+(agli?\s+altri|"
        r"ai\s+compagni))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto diretto con altri studenti (peggio/meglio di...).",
    ),
    (
        r"(?i)(la\s+maggior\s+parte\b|quasi\s+tutti\b|tutti\s+tranne\s+te\b|"
        r"solo\s+tu\b.*\bnon|sei\s+l['\u2019]unic[oa]\s+(che|a)\s+(non|ha\s+sbagliato))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto implicito con il gruppo classe.",
    ),
    (
        r"(?i)(media\s+della\s+classe|punteggio\s+medio|classifica\s+"
        r"(di\s+classe|dei\s+voti|degli?\s+studenti)|posizione\s+in\s+classifica)",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Riferimento a statistiche di classe visibili allo studente.",
    ),
    (
        r"(?i)(compared\s+to\s+(other|your)\s+(students|classmates|peers)|"
        r"unlike\s+(other|most)\s+students|most\s+students\s+(get|understand|know))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Confronto con altri studenti in inglese (output misto).",
    ),
    # -------------------------------------------------------------------
    # TONO PUNITIVO / SCORAGGIANTE (Regola 2, N3)
    # -------------------------------------------------------------------
    (
        r"(?i)\bsei\s+(scarso|scarsa|incapace|lent[oa]|stupid[oa]|negat[oa]|"
        r"un\s+disastro|un\s+caso\s+perso|irrecuperabile|senza\s+speranza)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Giudizio negativo diretto sulla persona dello studente.",
    ),
    (
        r"(?i)non\s+(sei|sarai)\s+(mai\s+)?(capace|in\s+grado|adatt[oa]|portat[oa])",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Proiezione negativa sulle capacita' future dello studente.",
    ),
    (
        r"(?i)(devi\s+vergognarti|che\s+figuraccia|che\s+delusione|che\s+disastro|"
        r"dov?resti\s+vergognarti|che\s+vergogna|pessim[oa]\s+risultato)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Linguaggio di vergogna esplicito.",
    ),
    (
        r"(?i)\bhai\s+sbagliato\b(?!\s+a\s+scrivere)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.WARN,
        "Formulazione punitiva 'hai sbagliato'. Preferire 'questo concetto ha bisogno "
        "di un altro giro'.",
    ),
    (
        r"(?i)come\s+(e'|\u00e8)\s+possibile\s+che\s+non\s+(capisc|riesc)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Espressione di incredulita' punitiva.",
    ),
    (
        r"(?i)nonostante\s+(tutti\s+gli\s+aiuti|i\s+(tanti\s+)?tentativi|tutto)",
        ViolationCategory.PUNITIVE_TONE,
        ViolationSeverity.BLOCK,
        "Implicazione che lo studente avrebbe dovuto riuscire dato il supporto ricevuto.",
    ),
    # -------------------------------------------------------------------
    # LINGUAGGIO OFFENSIVO / DISCRIMINATORIO (Regola 3, F8.5)
    # -------------------------------------------------------------------
    (
        r"(?i)\b(coglion[ei]|stronz[oiae]|cazz[oiae]|minchia|merda|vaffanculo|"
        r"cretino|deficiente|idiota|imbecille|mongoloide|ritardat[oiae]|"
        r"testa\s+di\s+(cazzo|minchia)|porco\s+dio|madonna\s+[a-z]+|"
        r"finocchio|frocio|terrone|polentone)\b",
        ViolationCategory.OFFENSIVE_LANGUAGE,
        ViolationSeverity.BLOCK,
        "Linguaggio offensivo, volgare, o discriminatorio in italiano.",
    ),
    (
        r"(?i)\b(fuck|shit|bitch|asshole|retard|idiot|moron|dumb|stupid\s+kid|"
        r"loser)\b",
        ViolationCategory.OFFENSIVE_LANGUAGE,
        ViolationSeverity.BLOCK,
        "Linguaggio offensivo in inglese (output misto).",
    ),
    # -------------------------------------------------------------------
    # FOMO / SCARCITY / URGENZA ARTIFICIALE (Regola 5, N3, F7.7)
    # -------------------------------------------------------------------
    (
        r"(?i)(ultim[oa]\s+(possibilit[a\u00e0]|chance|occasione|tentativo)|"
        r"non\s+perdere\s+(l['\u2019]occasione|questa\s+opportunit)|"
        r"affrettati|sbrigati|corri|tempo\s+(sta\s+)?scadendo|"
        r"fai\s+in\s+fretta)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Pattern di urgenza artificiale / scarcity.",
    ),
    (
        r"(?i)(i\s+tuoi\s+compagni\s+(stanno|sono|hanno)|"
        r"gli\s+altri\s+(stanno|sono|hanno)\s+(avanzando|avanti|finito|completato))",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "FOMO basato su confronto con i progressi dei compagni.",
    ),
    (
        r"(?i)solo\s+\d+\s+(quest|missioni?|giorni?|ore|tentativi?)\s+rimast",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Scarcity: riferimento a risorse limitate.",
    ),
    # -------------------------------------------------------------------
    # COLPEVOLIZZAZIONE (Regola 5, N3)
    # -------------------------------------------------------------------
    (
        r"(?i)(non\s+(studi|entri|ti\s+fai\s+viv[oa]|ti\s+connetti|apri\s+l['\u2019]app)"
        r"\s+da\s+\d+\s+(giorni?|settiman[ae])|stai\s+perdendo\s+terreno|"
        r"stai\s+restando\s+indietro)",
        ViolationCategory.GUILT_TRIGGER,
        ViolationSeverity.BLOCK,
        "Colpevolizzazione per inattivita'. Viola il principio del ritmo individuale.",
    ),
    # -------------------------------------------------------------------
    # RIFERIMENTO A ROSSO PER RISULTATI NEGATIVI (Regola 4, N3)
    # -------------------------------------------------------------------
    (
        r"(?i)(il\s+tuo\s+risultato\s+(e'|\u00e8)\s+(in\s+)?rosso|"
        r"contrassegnat[oa]\s+in\s+rosso|"
        r"semaforo\s+rosso\s+(per|sul\s+tuo)|"
        r"zona\s+rossa)",
        ViolationCategory.RED_FRAMING,
        ViolationSeverity.BLOCK,
        "Uso del colore rosso per risultati negativi. Usare 'arancione' per 'da migliorare'.",
    ),
    # -------------------------------------------------------------------
    # STEREOTIPI (Regola 9, N6)
    # -------------------------------------------------------------------
    (
        r"(?i)(al\s+nord\s+si\s+(lavora|studia)|al\s+sud\s+(non\s+si|si\s+fa\s+poco)|"
        r"come\s+un\s+(napoletano|siciliano|calabrese|meridionale|terroni?)\s+(che|"
        r"furb|arrang)|mentalit[a\u00e0]'?\s+(del\s+sud|meridionale|nordica))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo regionale Nord/Sud.",
    ),
    (
        r"(?i)(come\s+una?\s+(mamma|donna|ragazza)\s+(in\s+cucina|che\s+fa\s+la\s+spesa|"
        r"che\s+pulisce)|non\s+(e'|\u00e8)\s+(roba\s+)?da\s+(ragazz[ei]|femmin[ea]|"
        r"maschi[oe])|lavoro\s+da\s+(uomo|donna|maschio|femmina))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo di genere.",
    ),
    (
        r"(?i)(come\s+(un\s+tedesco|i\s+tedeschi)\s+(precis|puntual|efficien)|"
        r"come\s+(un\s+cinese|i\s+cinesi)\s+(che\s+)?copi|"
        r"come\s+(un\s+cinese|i\s+cinesi)\s+lavorano\s+tanto|"
        r"come\s+(gli?\s+american[io]|un\s+american[oa])\s+(esagera|semplific))",
        ViolationCategory.STEREOTYPE,
        ViolationSeverity.BLOCK,
        "Stereotipo nazionale.",
    ),
    # -------------------------------------------------------------------
    # TERAPIA IMPROVVISATA (Regola 6, N3)
    # -------------------------------------------------------------------
    (
        r"(?i)(non\s+devi\s+(sentirti\s+cos[\u00eci]|preoccuparti|avere\s+paura)|"
        r"tutto\s+andr[a\u00e0]'?\s+bene|"
        r"prova\s+a\s+rilassarti|"
        r"pensa\s+positivo|"
        r"sei\s+(forte|coraggios[oa]),?\s+ce\s+la\s+farai)",
        ViolationCategory.THERAPY_ATTEMPT,
        ViolationSeverity.BLOCK,
        "Tentativo di supporto psicologico improvvisato. Facilitare contatto "
        "con referente scolastico.",
    ),
    # -------------------------------------------------------------------
    # GAMIFICATION ANTI-PATTERNS (Regola 5, N3, F7.7)
    # From safeguarding-mvp-spec.md Section 6.2
    # -------------------------------------------------------------------
    (
        r"(?i)(sei\s+(al\s+)?(primo|secondo|terzo|ultimo)\s+(posto|in\s+classifica)|"
        r"classifica\s+(settimanale|giornaliera|mensile|della\s+classe)|"
        r"posizione\s+#?\d+\s+(su|di)\s+\d+|"
        r"top\s+\d+\s+(studenti?|della\s+classe))",
        ViolationCategory.STUDENT_COMPARISON,
        ViolationSeverity.BLOCK,
        "Pattern di ranking / classifica. Nessuna classifica tra studenti.",
    ),
    (
        r"(?i)(la\s+tua\s+serie\s+(positiva|di\s+vittorie)|"
        r"streak\s+di\s+\d+\s+giorni|"
        r"non\s+perdere\s+la\s+(tua\s+)?serie|"
        r"mantieni\s+(la\s+)?serie|"
        r"giorno\s+\d+\s+consecutivo)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Pattern di streak pressure. Nessuna pressione basata su serie consecutive.",
    ),
    (
        r"(?i)(tra\s+\d+\s+(minuti?|ore|secondi)|"
        r"countdown|conto\s+alla\s+rovescia|"
        r"timer\s+(attivo|in\s+corso)|"
        r"tempo\s+rimasto\s*:\s*\d+)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Pattern di countdown / timer. Nessun countdown per attivita' di apprendimento.",
    ),
    (
        r"(?i)(ricompensa\s+(misteriosa|segreta|casuale|a\s+sorpresa)|"
        r"premio\s+(misterios[oa]|segret[oa]|casuale|a\s+sorpresa)|"
        r"scopri\s+cosa\s+(hai\s+)?vinto|"
        r"apri\s+(il\s+)?forziere|"
        r"ruota\s+(della\s+)?fortuna)",
        ViolationCategory.FOMO_SCARCITY,
        ViolationSeverity.BLOCK,
        "Pattern di variable reward. Nessuna ricompensa a sorpresa o meccanica da slot machine.",
    ),
    # -------------------------------------------------------------------
    # CONTENUTO AGE-INAPPROPRIATE (Regola 3, F8.5)
    # -------------------------------------------------------------------
    (
        r"(?i)(contenut[oi]\s+(sessual|erot|pornograf)|"
        r"violenza\s+(grafica|esplicita|fisica)|"
        r"uso\s+di\s+(droga|droghe|sostanze\s+stupefacenti)|"
        r"suicid|autolesion)",
        ViolationCategory.AGE_INAPPROPRIATE,
        ViolationSeverity.BLOCK,
        "Contenuto non appropriato per fascia 13-19.",
    ),
]


def safeguarding_check(content: str) -> SafeguardingResult:
    """Run deterministic post-generation safeguarding check.

    Returns SafeguardingResult with passed=True if no BLOCK violations.
    WARN violations are recorded but do not block delivery.
    """
    violations: list[Violation] = []
    has_block = False

    for pattern, category, severity, description in BLOCKED_PATTERNS:
        for match in re.finditer(pattern, content):
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

    return SafeguardingResult(
        passed=not has_block,
        violations=violations,
        content=content if not has_block else None,
    )


# ---------------------------------------------------------------------------
# Wellbeing keyword detection (safeguarding-mvp-spec.md Section 4)
# ---------------------------------------------------------------------------
@dataclass
class WellbeingKeyword:
    phrase: str
    category: str  # frustration, hopelessness, isolation, self_harm_risk
    urgency: str  # low, medium, high, critical
    action: str  # log, alert_teacher, alert_referent


WELLBEING_KEYWORDS: list[WellbeingKeyword] = [
    # --- FRUSTRAZIONE ---
    WellbeingKeyword("non ce la faccio", "frustration", "medium", "alert_teacher"),
    WellbeingKeyword("non ci riesco", "frustration", "low", "log"),
    WellbeingKeyword("non capisco niente", "frustration", "low", "log"),
    WellbeingKeyword("e' troppo difficile", "frustration", "low", "log"),
    WellbeingKeyword("non sono capace", "frustration", "medium", "alert_teacher"),
    WellbeingKeyword("non sono portato", "frustration", "medium", "alert_teacher"),
    WellbeingKeyword("non sono abbastanza", "frustration", "medium", "alert_teacher"),
    WellbeingKeyword("mi viene da piangere", "frustration", "medium", "alert_teacher"),
    # --- DISPERAZIONE / RINUNCIA ---
    WellbeingKeyword("voglio smettere", "hopelessness", "high", "alert_referent"),
    WellbeingKeyword("voglio mollare", "hopelessness", "medium", "alert_teacher"),
    WellbeingKeyword("e' inutile", "hopelessness", "medium", "alert_teacher"),
    WellbeingKeyword(
        "tanto non cambiera' niente", "hopelessness", "high", "alert_referent"
    ),
    WellbeingKeyword("non servo a niente", "hopelessness", "high", "alert_referent"),
    WellbeingKeyword("non vale la pena", "hopelessness", "high", "alert_referent"),
    WellbeingKeyword("a che serve", "hopelessness", "medium", "alert_teacher"),
    WellbeingKeyword("tanto sono stupido", "hopelessness", "high", "alert_referent"),
    WellbeingKeyword("non ce la faro' mai", "hopelessness", "high", "alert_referent"),
    WellbeingKeyword(
        "non ha senso continuare", "hopelessness", "high", "alert_referent"
    ),
    # --- ISOLAMENTO ---
    WellbeingKeyword("mi sento solo", "isolation", "high", "alert_referent"),
    WellbeingKeyword("mi sento sola", "isolation", "high", "alert_referent"),
    WellbeingKeyword("nessuno mi capisce", "isolation", "high", "alert_referent"),
    WellbeingKeyword("nessuno mi aiuta", "isolation", "medium", "alert_teacher"),
    WellbeingKeyword("non ho amici", "isolation", "high", "alert_referent"),
    WellbeingKeyword("sono sempre da solo", "isolation", "high", "alert_referent"),
    # --- SEGNALI DI RISCHIO ---
    WellbeingKeyword("mi fa stare male", "self_harm_risk", "high", "alert_referent"),
    WellbeingKeyword(
        "non voglio piu' andare a scuola", "self_harm_risk", "high", "alert_referent"
    ),
    WellbeingKeyword(
        "mi faccio del male", "self_harm_risk", "critical", "alert_referent"
    ),
    WellbeingKeyword(
        "voglio farla finita", "self_harm_risk", "critical", "alert_referent"
    ),
    WellbeingKeyword(
        "non voglio piu' vivere", "self_harm_risk", "critical", "alert_referent"
    ),
    WellbeingKeyword(
        "mi voglio ammazzare", "self_harm_risk", "critical", "alert_referent"
    ),
    WellbeingKeyword("mi taglio", "self_harm_risk", "critical", "alert_referent"),
]

_URGENCY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def wellbeing_check(student_input: str) -> list[WellbeingKeyword]:
    """Scan student input for wellbeing signals.

    Returns matched keywords ordered by urgency (critical first).
    The system does NOT provide psychological support --
    it facilitates contact with the school referent.
    """
    normalised = (
        student_input.lower()
        .replace("\u2019", "'")
        .replace("\u00e8", "e'")
        .replace("\u00e0", "a'")
        .replace("\u00f2", "o'")
        .replace("\u00f9", "u'")
    )

    matches: list[WellbeingKeyword] = []
    for kw in WELLBEING_KEYWORDS:
        if kw.phrase in normalised:
            matches.append(kw)

    matches.sort(key=lambda m: _URGENCY_ORDER.get(m.urgency, 99))
    return matches
