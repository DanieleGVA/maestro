"""Unit tests for the KMM state machine (state_machine.py).

Tests ALL legal transitions and verifies that illegal transitions are rejected.
Pure logic tests -- no database required.
"""

import pytest

from maestro.kmm.models import MasteryState, TriggerType
from maestro.kmm.state_machine import (
    LEGAL_TRANSITIONS,
    STATE_ORDER,
    IllegalTransitionError,
    TransitionContext,
    validate_transition,
)


# ---------------------------------------------------------------------------
# State ordering tests (ADR-005 Conflict 3)
# ---------------------------------------------------------------------------


class TestStateOrder:
    def test_canonical_ordering(self) -> None:
        """lacuna(0) < in_recupero(1) < non_introdotto(2) < introdotto(3) < da_consolidare(4) < consolidato(5)."""
        assert STATE_ORDER["lacuna"] == 0
        assert STATE_ORDER["in_recupero"] == 1
        assert STATE_ORDER["non_introdotto"] == 2
        assert STATE_ORDER["introdotto"] == 3
        assert STATE_ORDER["da_consolidare"] == 4
        assert STATE_ORDER["consolidato"] == 5

    def test_all_states_present(self) -> None:
        for state in MasteryState:
            assert state.value in STATE_ORDER

    def test_lacuna_is_worst(self) -> None:
        worst = min(STATE_ORDER, key=STATE_ORDER.get)  # type: ignore[arg-type]
        assert worst == "lacuna"

    def test_consolidato_is_best(self) -> None:
        best = max(STATE_ORDER, key=STATE_ORDER.get)  # type: ignore[arg-type]
        assert best == "consolidato"


# ---------------------------------------------------------------------------
# Legal transition validation
# ---------------------------------------------------------------------------


class TestLegalTransitions:
    """Test every legal transition defined in LEGAL_TRANSITIONS."""

    def test_non_introdotto_to_introdotto(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.lezione_completata.value)
        assert validate_transition("non_introdotto", "introdotto", ctx.trigger_type, ctx)

    def test_introdotto_to_lacuna(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.verifica_errore.value)
        assert validate_transition("introdotto", "lacuna", ctx.trigger_type, ctx)

    def test_lacuna_to_in_recupero(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.avvio_recupero.value)
        assert validate_transition("lacuna", "in_recupero", ctx.trigger_type, ctx)

    def test_in_recupero_to_da_consolidare_quiz_pass(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_superato.value, quiz_score=85
        )
        assert validate_transition(
            "in_recupero", "da_consolidare", ctx.trigger_type, ctx
        )

    def test_in_recupero_to_in_recupero_quiz_retry(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_fallito.value, quiz_score=65
        )
        assert validate_transition(
            "in_recupero", "in_recupero", ctx.trigger_type, ctx
        )

    def test_in_recupero_to_lacuna_quiz_fail(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_fallito.value, quiz_score=30
        )
        assert validate_transition("in_recupero", "lacuna", ctx.trigger_type, ctx)

    def test_da_consolidare_to_consolidato_retention_pass(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.retention_check_ok.value)
        assert validate_transition(
            "da_consolidare", "consolidato", ctx.trigger_type, ctx
        )

    def test_da_consolidare_to_da_consolidare_retention_pass_partial(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.retention_check_ok.value)
        assert validate_transition(
            "da_consolidare", "da_consolidare", ctx.trigger_type, ctx
        )

    def test_da_consolidare_to_lacuna_retention_fail(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.retention_check_fail.value)
        assert validate_transition(
            "da_consolidare", "lacuna", ctx.trigger_type, ctx
        )

    def test_consolidato_to_lacuna_regression(self) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.regressione.value)
        assert validate_transition("consolidato", "lacuna", ctx.trigger_type, ctx)


# ---------------------------------------------------------------------------
# Illegal transition tests
# ---------------------------------------------------------------------------


class TestIllegalTransitions:
    """Verify that all illegal transitions are properly rejected."""

    @pytest.mark.parametrize(
        "current,target",
        [
            ("non_introdotto", "lacuna"),
            ("non_introdotto", "in_recupero"),
            ("non_introdotto", "da_consolidare"),
            ("non_introdotto", "consolidato"),
            ("introdotto", "introdotto"),
            ("introdotto", "non_introdotto"),
            ("introdotto", "in_recupero"),
            ("introdotto", "da_consolidare"),
            ("introdotto", "consolidato"),
            ("lacuna", "non_introdotto"),
            ("lacuna", "introdotto"),
            ("lacuna", "da_consolidare"),
            ("lacuna", "consolidato"),
            ("lacuna", "lacuna"),
            ("in_recupero", "non_introdotto"),
            ("in_recupero", "introdotto"),
            ("in_recupero", "consolidato"),
            ("da_consolidare", "non_introdotto"),
            ("da_consolidare", "introdotto"),
            ("da_consolidare", "in_recupero"),
            ("consolidato", "non_introdotto"),
            ("consolidato", "introdotto"),
            ("consolidato", "in_recupero"),
            ("consolidato", "da_consolidare"),
            ("consolidato", "consolidato"),
        ],
    )
    def test_illegal_transition_raises(self, current: str, target: str) -> None:
        ctx = TransitionContext(trigger_type=TriggerType.avvio_recupero.value)
        with pytest.raises(IllegalTransitionError):
            validate_transition(current, target, ctx.trigger_type, ctx)


# ---------------------------------------------------------------------------
# Quiz score validation
# ---------------------------------------------------------------------------


class TestQuizScoreValidation:
    def test_quiz_superato_requires_score_ge_80(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_superato.value, quiz_score=75
        )
        with pytest.raises(IllegalTransitionError, match="score >= 80"):
            validate_transition(
                "in_recupero", "da_consolidare", ctx.trigger_type, ctx
            )

    def test_quiz_superato_none_score_raises(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_superato.value, quiz_score=None
        )
        with pytest.raises(IllegalTransitionError, match="score >= 80"):
            validate_transition(
                "in_recupero", "da_consolidare", ctx.trigger_type, ctx
            )

    def test_quiz_superato_score_80_passes(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_superato.value, quiz_score=80
        )
        assert validate_transition(
            "in_recupero", "da_consolidare", ctx.trigger_type, ctx
        )

    def test_quiz_superato_score_100_passes(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_superato.value, quiz_score=100
        )
        assert validate_transition(
            "in_recupero", "da_consolidare", ctx.trigger_type, ctx
        )

    def test_quiz_fallito_with_score_80_raises(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.quiz_fallito.value, quiz_score=80
        )
        with pytest.raises(IllegalTransitionError, match="score < 80"):
            validate_transition(
                "in_recupero", "in_recupero", ctx.trigger_type, ctx
            )


# ---------------------------------------------------------------------------
# Override docente
# ---------------------------------------------------------------------------


class TestOverrideDocente:
    def test_override_bypasses_legal_transitions(self) -> None:
        """Override can go from any state to any state."""
        ctx = TransitionContext(
            trigger_type=TriggerType.override_docente.value,
            triggered_by="teacher-uuid",
            motivation="Lo studente ha dimostrato competenza in classe",
        )
        # non_introdotto -> consolidato is normally illegal
        assert validate_transition(
            "non_introdotto", "consolidato", ctx.trigger_type, ctx
        )

    def test_override_requires_motivation(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.override_docente.value,
            triggered_by="teacher-uuid",
            motivation=None,
        )
        with pytest.raises(IllegalTransitionError, match="motivation"):
            validate_transition(
                "non_introdotto", "consolidato", ctx.trigger_type, ctx
            )

    def test_override_motivation_too_short(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.override_docente.value,
            triggered_by="teacher-uuid",
            motivation="troppo corta",
        )
        with pytest.raises(IllegalTransitionError, match="motivation"):
            validate_transition(
                "non_introdotto", "consolidato", ctx.trigger_type, ctx
            )

    def test_override_motivation_exactly_20_chars(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.override_docente.value,
            triggered_by="teacher-uuid",
            motivation="a" * 20,
        )
        assert validate_transition(
            "non_introdotto", "consolidato", ctx.trigger_type, ctx
        )

    def test_override_whitespace_motivation_fails(self) -> None:
        ctx = TransitionContext(
            trigger_type=TriggerType.override_docente.value,
            triggered_by="teacher-uuid",
            motivation="   " * 10,  # 30 chars but all whitespace
        )
        with pytest.raises(IllegalTransitionError, match="motivation"):
            validate_transition(
                "non_introdotto", "consolidato", ctx.trigger_type, ctx
            )


# ---------------------------------------------------------------------------
# LEGAL_TRANSITIONS completeness
# ---------------------------------------------------------------------------


class TestTransitionTableCompleteness:
    def test_all_states_have_entries(self) -> None:
        """Every state in MasteryState must be a key in LEGAL_TRANSITIONS."""
        for state in MasteryState:
            assert state.value in LEGAL_TRANSITIONS, (
                f"{state.value} missing from LEGAL_TRANSITIONS"
            )

    def test_all_target_states_are_valid(self) -> None:
        """Every target state in the transitions must be a valid MasteryState."""
        valid = {s.value for s in MasteryState}
        for source, targets in LEGAL_TRANSITIONS.items():
            for t in targets:
                assert t in valid, f"Invalid target {t} from {source}"
