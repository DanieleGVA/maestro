"""Pseudonymisation layer for LLM calls.

Non-negotiable: NO PII crosses to external LLMs.
- Student names, teacher names, school names replaced with pseudonyms.
- Native language: ALWAYS stripped, never sent to LLM (GDPR Art. 9).
- Mapping is session-scoped (in-memory only), destroyed after each call.
"""

import hashlib
from dataclasses import dataclass, field


@dataclass
class PseudonymMap:
    """Session-scoped mapping between PII and pseudonyms.

    Lives only in memory for the duration of a single LLM call.
    NEVER persisted to disk, database, or logs.
    """

    _forward: dict[str, str] = field(default_factory=dict)
    _reverse: dict[str, str] = field(default_factory=dict)

    def add(self, pii: str, pseudonym: str) -> None:
        self._forward[pii] = pseudonym
        self._reverse[pseudonym] = pii

    def pseudonymise(self, text: str) -> str:
        """Replace all known PII with pseudonyms in text."""
        result = text
        # Sort by length descending to avoid partial replacement
        for pii in sorted(self._forward.keys(), key=len, reverse=True):
            result = result.replace(pii, self._forward[pii])
        return result

    def depseudonymise(self, text: str) -> str:
        """Restore PII from pseudonyms in LLM response."""
        result = text
        for pseudonym in sorted(self._reverse.keys(), key=len, reverse=True):
            result = result.replace(pseudonym, self._reverse[pseudonym])
        return result

    def clear(self) -> None:
        """Destroy the mapping. Called after de-pseudonymisation."""
        self._forward.clear()
        self._reverse.clear()


def _hash8(value: str) -> str:
    """Generate 8-character hash for pseudonymisation."""
    return hashlib.sha256(value.encode()).hexdigest()[:8]


class PseudonymisationError(Exception):
    """Raised when PII is detected after pseudonymisation (fail-closed)."""


class Pseudonymizer:
    """Builds pseudonym maps and verifies PII removal.

    Per security-mvp-spec.md Section 6.2:
    - student_name -> STUDENTE_{hash8}
    - teacher_name -> DOCENTE_{hash8}
    - school_name  -> SCUOLA_PILOTA
    - class_name   -> CLASSE_A
    - email        -> [RIMOSSO]
    - native_language -> [RIMOSSO]  (Art. 9: NEVER sent to LLM)
    - registry_id  -> [RIMOSSO]
    - phone        -> [RIMOSSO]
    - birth_year   -> [RIMOSSO]
    """

    def build_map(
        self,
        *,
        student_name: str | None = None,
        student_surname: str | None = None,
        teacher_name: str | None = None,
        teacher_surname: str | None = None,
        school_name: str | None = None,
        class_name: str | None = None,
        email: str | None = None,
        native_language: str | None = None,
        birth_year: str | None = None,
        phone: str | None = None,
        registry_id: str | None = None,
    ) -> PseudonymMap:
        """Build a session-scoped pseudonym map from known PII values."""
        pmap = PseudonymMap()

        if student_name:
            full = (
                f"{student_name} {student_surname}"
                if student_surname
                else student_name
            )
            h = _hash8(full)
            pmap.add(full, f"STUDENTE_{h}")
            if student_surname:
                pmap.add(student_name, f"STUDENTE_{h}_NOME")
                pmap.add(student_surname, f"STUDENTE_{h}_COGNOME")

        if teacher_name:
            full = (
                f"{teacher_name} {teacher_surname}"
                if teacher_surname
                else teacher_name
            )
            h = _hash8(full)
            pmap.add(full, f"DOCENTE_{h}")
            if teacher_surname:
                pmap.add(teacher_name, f"DOCENTE_{h}_NOME")
                pmap.add(teacher_surname, f"DOCENTE_{h}_COGNOME")

        if school_name:
            pmap.add(school_name, "SCUOLA_PILOTA")

        if class_name:
            pmap.add(class_name, "CLASSE_A")

        # These are always stripped entirely, never sent in any form
        for value in (email, native_language, birth_year, phone, registry_id):
            if value:
                pmap.add(value, "[RIMOSSO]")

        return pmap

    def verify_no_pii_residual(
        self,
        text: str,
        *,
        known_pii: list[str] | None = None,
    ) -> bool:
        """Verify no known PII remains in pseudonymised text.

        Returns True if clean. Returns False if PII residual found.
        This is the fail-safe check before any external LLM call.
        """
        if not known_pii:
            return True
        text_lower = text.lower()
        for pii in known_pii:
            if pii and len(pii) >= 2 and pii.lower() in text_lower:
                return False
        return True

    def collect_known_pii(
        self,
        *,
        student_name: str | None = None,
        student_surname: str | None = None,
        teacher_name: str | None = None,
        teacher_surname: str | None = None,
        school_name: str | None = None,
        email: str | None = None,
        native_language: str | None = None,
        birth_year: str | None = None,
        phone: str | None = None,
        registry_id: str | None = None,
    ) -> list[str]:
        """Collect all known PII values for residual verification."""
        return [
            v
            for v in (
                student_name,
                student_surname,
                teacher_name,
                teacher_surname,
                school_name,
                email,
                native_language,
                birth_year,
                phone,
                registry_id,
            )
            if v and len(v) >= 2
        ]
