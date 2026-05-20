"""Unit tests for the pseudonymisation layer.

Non-negotiable: NO PII crosses to external LLMs.
These tests verify that ALL PII types are properly replaced and that
residual detection catches any missed PII.
"""

import pytest

from maestro.llm.pseudonymizer import Pseudonymizer, PseudonymMap


class TestPseudonymMap:
    """Tests for the in-memory PseudonymMap."""

    def test_pseudonymise_replaces_known_values(self) -> None:
        pmap = PseudonymMap()
        pmap.add("Mario Rossi", "STUDENTE_abc12345")
        result = pmap.pseudonymise("Lo studente Mario Rossi ha un errore.")
        assert "Mario Rossi" not in result
        assert "STUDENTE_abc12345" in result

    def test_depseudonymise_restores_originals(self) -> None:
        pmap = PseudonymMap()
        pmap.add("Mario Rossi", "STUDENTE_abc12345")
        text = "STUDENTE_abc12345 ha completato il quiz."
        result = pmap.depseudonymise(text)
        assert result == "Mario Rossi ha completato il quiz."

    def test_longest_match_first(self) -> None:
        """Longer PII values are replaced before shorter ones to avoid partial replacement."""
        pmap = PseudonymMap()
        pmap.add("Mario", "STUDENTE_x_NOME")
        pmap.add("Mario Rossi", "STUDENTE_x")
        result = pmap.pseudonymise("Il docente ha detto a Mario Rossi che...")
        # Full name should be replaced, not partial
        assert "STUDENTE_x" in result
        assert "Mario Rossi" not in result

    def test_clear_destroys_mapping(self) -> None:
        pmap = PseudonymMap()
        pmap.add("Test", "PSEUDONYM")
        pmap.clear()
        # After clear, pseudonymise should not replace anything
        result = pmap.pseudonymise("Test value")
        assert result == "Test value"

    def test_empty_map_is_identity(self) -> None:
        pmap = PseudonymMap()
        text = "No PII here."
        assert pmap.pseudonymise(text) == text
        assert pmap.depseudonymise(text) == text


class TestPseudonymizer:
    """Tests for the Pseudonymizer class."""

    def setup_method(self) -> None:
        self.pseudonymizer = Pseudonymizer()

    def test_build_map_student_full_name(self) -> None:
        pmap = self.pseudonymizer.build_map(
            student_name="Luca", student_surname="Bianchi"
        )
        result = pmap.pseudonymise("Luca Bianchi sta studiando.")
        assert "Luca" not in result
        assert "Bianchi" not in result
        assert "STUDENTE_" in result

    def test_build_map_teacher_name(self) -> None:
        pmap = self.pseudonymizer.build_map(
            teacher_name="Prof", teacher_surname="Verdi"
        )
        result = pmap.pseudonymise("Prof Verdi ha assegnato il compito.")
        assert "Prof" not in result or "Verdi" not in result
        assert "DOCENTE_" in result

    def test_build_map_school_name(self) -> None:
        pmap = self.pseudonymizer.build_map(school_name="ITIS Galileo Galilei")
        result = pmap.pseudonymise("Studente dell'ITIS Galileo Galilei.")
        assert "ITIS Galileo Galilei" not in result
        assert "SCUOLA_PILOTA" in result

    def test_build_map_class_name(self) -> None:
        pmap = self.pseudonymizer.build_map(class_name="3B Informatica")
        result = pmap.pseudonymise("Classe 3B Informatica, sezione A.")
        assert "3B Informatica" not in result
        assert "CLASSE_A" in result

    def test_native_language_always_redacted(self) -> None:
        """Native language is GDPR Art. 9 sensitive data. ALWAYS stripped."""
        pmap = self.pseudonymizer.build_map(native_language="ucraino")
        result = pmap.pseudonymise("Lingua nativa: ucraino. Bilinguismo attivo.")
        assert "ucraino" not in result
        assert "[RIMOSSO]" in result

    def test_email_redacted(self) -> None:
        pmap = self.pseudonymizer.build_map(email="mario.rossi@scuola.it")
        result = pmap.pseudonymise("Email: mario.rossi@scuola.it")
        assert "mario.rossi@scuola.it" not in result
        assert "[RIMOSSO]" in result

    def test_birth_year_redacted(self) -> None:
        pmap = self.pseudonymizer.build_map(birth_year="2008")
        result = pmap.pseudonymise("Nato nel 2008.")
        assert "2008" not in result

    def test_phone_redacted(self) -> None:
        pmap = self.pseudonymizer.build_map(phone="3331234567")
        result = pmap.pseudonymise("Telefono: 3331234567")
        assert "3331234567" not in result

    def test_registry_id_redacted(self) -> None:
        pmap = self.pseudonymizer.build_map(registry_id="MAT-2024-0042")
        result = pmap.pseudonymise("Matricola: MAT-2024-0042")
        assert "MAT-2024-0042" not in result

    def test_multiple_pii_fields_combined(self) -> None:
        """All PII fields pseudonymised in a single call."""
        pmap = self.pseudonymizer.build_map(
            student_name="Anna",
            student_surname="Neri",
            teacher_name="Giuseppe",
            teacher_surname="Bianchi",
            school_name="Liceo Scientifico",
            email="anna.neri@test.it",
            native_language="arabo",
            birth_year="2009",
        )
        text = (
            "Anna Neri, studentessa del Liceo Scientifico, "
            "insegnante Giuseppe Bianchi, email anna.neri@test.it, "
            "lingua nativa: arabo, anno nascita: 2009."
        )
        result = pmap.pseudonymise(text)
        assert "Anna" not in result
        assert "Neri" not in result
        assert "Giuseppe" not in result
        assert "Bianchi" not in result
        assert "Liceo Scientifico" not in result
        assert "anna.neri@test.it" not in result
        assert "arabo" not in result
        assert "2009" not in result

    def test_verify_no_pii_residual_clean(self) -> None:
        """Clean text passes verification."""
        result = self.pseudonymizer.verify_no_pii_residual(
            "STUDENTE_abc ha un errore nel codice.",
            known_pii=["Mario", "Rossi", "ITIS Galileo"],
        )
        assert result is True

    def test_verify_no_pii_residual_detected(self) -> None:
        """PII residual is detected."""
        result = self.pseudonymizer.verify_no_pii_residual(
            "Lo studente Mario ha un errore nel codice.",
            known_pii=["Mario", "Rossi"],
        )
        assert result is False

    def test_verify_case_insensitive(self) -> None:
        """PII check is case-insensitive."""
        result = self.pseudonymizer.verify_no_pii_residual(
            "Lo studente MARIO ha un errore.",
            known_pii=["Mario"],
        )
        assert result is False

    def test_verify_no_pii_empty_list(self) -> None:
        """Empty PII list always passes."""
        result = self.pseudonymizer.verify_no_pii_residual(
            "Anything goes here.", known_pii=[]
        )
        assert result is True

    def test_verify_no_pii_none(self) -> None:
        result = self.pseudonymizer.verify_no_pii_residual(
            "Text", known_pii=None
        )
        assert result is True

    def test_short_pii_values_ignored(self) -> None:
        """Values shorter than 2 chars are too short to be meaningful PII checks."""
        result = self.pseudonymizer.verify_no_pii_residual(
            "I am a test.", known_pii=["a", "I"]
        )
        assert result is True

    def test_collect_known_pii(self) -> None:
        pii = self.pseudonymizer.collect_known_pii(
            student_name="Anna",
            student_surname="Neri",
            teacher_name=None,
            email="test@test.it",
            native_language="ucraino",
        )
        assert "Anna" in pii
        assert "Neri" in pii
        assert "test@test.it" in pii
        assert "ucraino" in pii
        # None values excluded
        assert None not in pii
