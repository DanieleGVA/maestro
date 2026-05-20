"""Integration tests for the pseudonymisation pipeline.

Verifies end-to-end that PII is stripped before LLM calls and restored after.
This is a non-negotiable safety path: NO PII crosses to external LLMs.
"""

from __future__ import annotations

import pytest

from maestro.llm.pseudonymizer import PseudonymMap, Pseudonymizer


class TestFullPseudonymisationRoundTrip:
    """Test the complete pseudonymise -> send -> depseudonymise flow."""

    def test_student_name_round_trip(self) -> None:
        """Student name should be stripped before LLM and restored after."""
        p = Pseudonymizer()
        pmap = p.build_map(
            student_name="Maria", student_surname="Bianchi"
        )

        original = "Maria Bianchi ha un errore nel codice di session management."
        pseudonymised = pmap.pseudonymise(original)

        # No PII in pseudonymised text
        assert "Maria" not in pseudonymised
        assert "Bianchi" not in pseudonymised
        assert "STUDENTE_" in pseudonymised

        # Simulate LLM response using pseudonyms
        llm_response = pseudonymised.replace("errore", "problema identificato")

        # Restore PII
        restored = pmap.depseudonymise(llm_response)
        assert "Maria Bianchi" in restored or ("Maria" in restored and "Bianchi" in restored)

    def test_native_language_never_exposed(self) -> None:
        """Native language (GDPR Art. 9) must NEVER appear in pseudonymised text."""
        p = Pseudonymizer()
        pmap = p.build_map(native_language="ucraino")

        text = "Lo studente parla ucraino come lingua madre."
        result = pmap.pseudonymise(text)

        assert "ucraino" not in result
        assert "[RIMOSSO]" in result

    def test_all_pii_types_stripped(self) -> None:
        """All PII types should be replaced in a single operation."""
        p = Pseudonymizer()
        pmap = p.build_map(
            student_name="Luca",
            student_surname="Rossi",
            teacher_name="Marco",
            teacher_surname="Verdi",
            school_name="ITIS Galileo",
            class_name="3B Info",
            email="luca@scuola.it",
            native_language="arabo",
            birth_year="2009",
            phone="3331234567",
            registry_id="MAT-001",
        )

        text = (
            "Luca Rossi della 3B Info all'ITIS Galileo, "
            "docente Marco Verdi, email luca@scuola.it, "
            "lingua arabo, nato 2009, tel 3331234567, matricola MAT-001."
        )
        result = pmap.pseudonymise(text)

        for pii in ["Luca", "Rossi", "Marco", "Verdi", "ITIS Galileo",
                     "3B Info", "luca@scuola.it", "arabo", "2009",
                     "3331234567", "MAT-001"]:
            assert pii not in result, f"PII '{pii}' still present after pseudonymisation"

    def test_pii_verification_catches_residual(self) -> None:
        """If pseudonymisation fails, verification should catch it."""
        p = Pseudonymizer()
        # Build map but don't actually pseudonymise
        known_pii = p.collect_known_pii(
            student_name="Mario",
            student_surname="Rossi",
        )

        # Text still contains PII
        text = "Lo studente Mario Rossi ha completato il quiz."
        result = p.verify_no_pii_residual(text, known_pii=known_pii)
        assert result is False

    def test_clean_text_passes_verification(self) -> None:
        """Properly pseudonymised text should pass verification."""
        p = Pseudonymizer()
        pmap = p.build_map(student_name="Anna", student_surname="Neri")
        known_pii = p.collect_known_pii(student_name="Anna", student_surname="Neri")

        text = "Anna Neri ha un errore."
        clean = pmap.pseudonymise(text)

        assert p.verify_no_pii_residual(clean, known_pii=known_pii) is True

    def test_clear_destroys_mapping_irreversibly(self) -> None:
        """After clear(), depseudonymise should not restore originals."""
        p = Pseudonymizer()
        pmap = p.build_map(student_name="Test", student_surname="User")

        text = pmap.pseudonymise("Test User ha studiato.")
        pmap.clear()

        # After clear, the mapping is gone
        restored = pmap.depseudonymise(text)
        assert "Test User" not in restored
