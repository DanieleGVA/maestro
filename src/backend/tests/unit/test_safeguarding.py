"""Unit tests for safeguarding checks.

Tests BLOCKED_PATTERNS from safeguarding-mvp-spec.md and wellbeing keyword detection.
These tests are critical for minor safety -- every pattern MUST be verified.
"""

import pytest

from maestro.safeguarding.checker import (
    BLOCKED_PATTERNS,
    SYSTEM_PROMPT_SAFEGUARDING,
    ViolationCategory,
    ViolationSeverity,
    WellbeingKeyword,
    safeguarding_check,
    wellbeing_check,
)


class TestSafeguardingCheck:
    """Tests for the deterministic post-generation content check."""

    # ------------------------------------------------------------------
    # STUDENT COMPARISON (Regola 1)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Sei peggio dei compagni.",
            "Meglio della classe.",
            "Peggio della media.",
            "Peggio rispetto agli altri.",
            "Meglio dei tuoi compagni.",
        ],
    )
    def test_blocks_student_comparison_direct(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.STUDENT_COMPARISON for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "La maggior parte ha capito.",
            "Quasi tutti hanno passato.",
            "Tutti tranne te hanno capito.",
            "Solo tu non hai risposto.",
        ],
    )
    def test_blocks_student_comparison_implicit(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.STUDENT_COMPARISON for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "La media della classe e' 7.",
            "Punteggio medio del test.",
            "Classifica dei voti.",
            "Classifica di classe.",
            "Posizione in classifica.",
        ],
    )
    def test_blocks_class_statistics(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    @pytest.mark.parametrize(
        "text",
        [
            "Compared to other students, you are behind.",
            "Unlike most students, you failed.",
            "Most students understand this.",
        ],
    )
    def test_blocks_english_comparison(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    # ------------------------------------------------------------------
    # PUNITIVE TONE (Regola 2)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Sei scarso in programmazione.",
            "Sei incapace di capire.",
            "Sei un disastro.",
            "Sei un caso perso.",
            "Sei negato per la programmazione.",
            "Sei senza speranza.",
        ],
    )
    def test_blocks_punitive_judgement(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.PUNITIVE_TONE for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "Non sei capace di farlo.",
            "Non sarai mai in grado.",
            "Non sei portato per la materia.",
        ],
    )
    def test_blocks_negative_projection(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    @pytest.mark.parametrize(
        "text",
        [
            "Devi vergognarti!",
            "Che figuraccia!",
            "Che delusione!",
            "Dovresti vergognarti.",
            "Che vergogna.",
            "Pessimo risultato.",
        ],
    )
    def test_blocks_shame_language(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    def test_warns_hai_sbagliato(self) -> None:
        """'hai sbagliato' triggers WARN, not BLOCK."""
        result = safeguarding_check("Hai sbagliato questa parte.")
        assert result.passed  # WARN, not BLOCK
        assert any(
            v.severity == ViolationSeverity.WARN for v in result.violations
        )

    def test_allows_hai_sbagliato_a_scrivere(self) -> None:
        """'hai sbagliato a scrivere' is allowed (showing code errors)."""
        result = safeguarding_check("Hai sbagliato a scrivere il codice.")
        assert result.passed
        # Should not have any WARN about this specific phrase
        sbagliato_warnings = [
            v
            for v in result.violations
            if "hai sbagliato" in v.matched_text.lower()
        ]
        assert len(sbagliato_warnings) == 0

    def test_blocks_incredulity(self) -> None:
        result = safeguarding_check(
            "Come e' possibile che non capisci questo concetto?"
        )
        assert not result.passed

    def test_blocks_nonostante(self) -> None:
        result = safeguarding_check("Nonostante tutti gli aiuti, ancora non riesci.")
        assert not result.passed

    # ------------------------------------------------------------------
    # OFFENSIVE LANGUAGE (Regola 3)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Sei un cretino.",
            "Che idiota.",
            "Sei un imbecille.",
            "Deficiente!",
        ],
    )
    def test_blocks_italian_insults(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.OFFENSIVE_LANGUAGE for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "This is shit code.",
            "You're a loser.",
            "That's so dumb.",
        ],
    )
    def test_blocks_english_insults(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    # ------------------------------------------------------------------
    # FOMO / SCARCITY (Regola 5)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Ultima possibilita' per migliorare!",
            "Affrettati a completare!",
            "Il tempo sta scadendo!",
            "Fai in fretta!",
            "Non perdere l'occasione!",
        ],
    )
    def test_blocks_urgency_patterns(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.FOMO_SCARCITY for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "I tuoi compagni stanno avanzando!",
            "Gli altri sono avanti!",
            "I tuoi compagni hanno finito!",
        ],
    )
    def test_blocks_fomo_peer_progress(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    def test_blocks_scarcity_countdown(self) -> None:
        result = safeguarding_check("Solo 2 quest rimaste per oggi!")
        assert not result.passed

    # ------------------------------------------------------------------
    # GUILT TRIGGER
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Non studi da 5 giorni!",
            "Non entri da 3 settimane.",
            "Stai perdendo terreno!",
            "Stai restando indietro.",
        ],
    )
    def test_blocks_guilt_triggers(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.GUILT_TRIGGER for v in result.violations
        )

    # ------------------------------------------------------------------
    # RED FRAMING (Regola 4)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Il tuo risultato e' in rosso.",
            "Il tuo risultato \u00e8 rosso.",
            "Contrassegnato in rosso.",
            "Semaforo rosso per il tuo risultato.",
            "Sei in zona rossa.",
        ],
    )
    def test_blocks_red_framing(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.RED_FRAMING for v in result.violations
        )

    # ------------------------------------------------------------------
    # STEREOTYPES (Regola 9)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Al nord si lavora di piu'.",
            "Come un napoletano che si arrangia.",
            "Mentalita' del sud.",
        ],
    )
    def test_blocks_regional_stereotypes(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.STEREOTYPE for v in result.violations
        )

    @pytest.mark.parametrize(
        "text",
        [
            "Come una mamma in cucina.",
            "Non e' roba da ragazze.",
            "Lavoro da uomo.",
        ],
    )
    def test_blocks_gender_stereotypes(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    @pytest.mark.parametrize(
        "text",
        [
            "Come un tedesco preciso.",
            "Come i cinesi che copiano.",
        ],
    )
    def test_blocks_national_stereotypes(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed

    # ------------------------------------------------------------------
    # THERAPY ATTEMPT (Regola 6)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Non devi sentirti cosi.",
            "Tutto andra' bene.",
            "Prova a rilassarti.",
            "Pensa positivo!",
            "Sei forte, ce la farai!",
        ],
    )
    def test_blocks_therapy_attempts(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.THERAPY_ATTEMPT for v in result.violations
        )

    # ------------------------------------------------------------------
    # AGE-INAPPROPRIATE
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        "text",
        [
            "Contenuto sessuale non appropriato.",
            "Violenza esplicita nel testo.",
            "Uso di droghe nel codice.",
        ],
    )
    def test_blocks_age_inappropriate(self, text: str) -> None:
        result = safeguarding_check(text)
        assert not result.passed
        assert any(
            v.category == ViolationCategory.AGE_INAPPROPRIATE for v in result.violations
        )

    # ------------------------------------------------------------------
    # SAFE CONTENT
    # ------------------------------------------------------------------
    def test_allows_safe_content(self) -> None:
        safe_text = (
            "Questo concetto ha bisogno di un altro giro. "
            "Pensa a una variabile come a un'etichetta su un barattolo: "
            "il nome del barattolo non cambia, ma puoi mettere dentro cose diverse. "
            "Quando ti senti pronto, prova il quiz!"
        )
        result = safeguarding_check(safe_text)
        assert result.passed
        assert result.content == safe_text

    def test_allows_technical_content(self) -> None:
        """Technical IT content should not trigger false positives."""
        text = (
            "La funzione session_start() inizializza una sessione PHP. "
            "Il codice corretto chiama session_regenerate_id(true) per sicurezza. "
            "Ecco il codice [CORRETTO]: session_start(); session_regenerate_id(true);"
        )
        result = safeguarding_check(text)
        assert result.passed

    def test_allows_encouraging_tone(self) -> None:
        text = (
            "Non ci siamo ancora, ma ogni tentativo ti porta piu' vicino. "
            "Hai una nuova missione di recupero per Sessioni PHP. "
            "E' un percorso pensato apposta per te."
        )
        result = safeguarding_check(text)
        assert result.passed


class TestSafeguardingSystemPrompt:
    """Tests that the system prompt contains all 9 rules."""

    def test_system_prompt_contains_all_rules(self) -> None:
        for i in range(1, 10):
            assert f"{i}." in SYSTEM_PROMPT_SAFEGUARDING

    def test_system_prompt_mentions_key_concepts(self) -> None:
        assert "confrontare" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "punitivo" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "offensivo" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "rosso" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "fomo" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "psicologico" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "opportunita" in SYSTEM_PROMPT_SAFEGUARDING.lower() or "opportunit" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "tecnici" in SYSTEM_PROMPT_SAFEGUARDING.lower()
        assert "stereotip" in SYSTEM_PROMPT_SAFEGUARDING.lower()


class TestWellbeingCheck:
    """Tests for wellbeing keyword detection in student input."""

    def test_detects_frustration(self) -> None:
        matches = wellbeing_check("Non ce la faccio piu' con questo esercizio")
        assert len(matches) >= 1
        assert matches[0].category == "frustration"

    def test_detects_hopelessness(self) -> None:
        matches = wellbeing_check("Voglio smettere di studiare")
        assert len(matches) >= 1
        assert any(m.category == "hopelessness" for m in matches)

    def test_detects_isolation(self) -> None:
        matches = wellbeing_check("Mi sento solo, nessuno mi aiuta")
        assert len(matches) >= 1
        assert any(m.category == "isolation" for m in matches)

    def test_detects_self_harm_risk(self) -> None:
        matches = wellbeing_check("Mi faccio del male")
        assert len(matches) >= 1
        assert matches[0].category == "self_harm_risk"
        assert matches[0].urgency == "critical"

    def test_detects_critical_urgency_first(self) -> None:
        """Critical urgency keywords should be sorted first."""
        matches = wellbeing_check("Non ci riesco, voglio farla finita")
        assert len(matches) >= 2
        assert matches[0].urgency == "critical"

    def test_normalises_unicode_accents(self) -> None:
        """Unicode accented characters are normalised for matching."""
        matches = wellbeing_check("\u00c8 troppo difficile")
        assert len(matches) >= 1

    def test_normalises_unicode_apostrophes(self) -> None:
        matches = wellbeing_check("Non ce la faccio pi\u00f9")
        # "piu'" with unicode accent should still match "non ce la faccio"
        assert len(matches) >= 1

    def test_no_match_on_safe_input(self) -> None:
        matches = wellbeing_check("Ho capito il concetto, posso provare il quiz?")
        assert len(matches) == 0

    def test_no_match_on_empty_input(self) -> None:
        matches = wellbeing_check("")
        assert len(matches) == 0

    def test_multiple_matches_all_returned(self) -> None:
        text = "Non ci riesco, non sono capace, e' troppo difficile"
        matches = wellbeing_check(text)
        assert len(matches) >= 3

    def test_low_urgency_keywords_logged_not_alerted(self) -> None:
        matches = wellbeing_check("Non ci riesco")
        assert len(matches) >= 1
        low_matches = [m for m in matches if m.urgency == "low"]
        assert len(low_matches) >= 1
        assert low_matches[0].action == "log"
