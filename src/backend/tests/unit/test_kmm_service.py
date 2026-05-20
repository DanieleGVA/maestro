"""Unit tests for KMM service layer (kmm/service.py).

Tests high-level quiz result processing and teacher override logic.
All DB operations mocked.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.kmm.models import MasteryState, TriggerType
from maestro.kmm.state_machine import IllegalTransitionError


class TestProcessQuizResult:
    """Test the process_quiz_result service function."""

    @pytest.mark.asyncio
    async def test_score_ge_80_from_in_recupero_targets_da_consolidare(self) -> None:
        from maestro.kmm.service import process_quiz_result

        mock_sns = MagicMock()
        mock_sns.current_state = "in_recupero"

        with (
            patch(
                "maestro.kmm.service.get_student_state",
                new_callable=AsyncMock,
                return_value=mock_sns,
            ),
            patch(
                "maestro.kmm.service.execute_transition",
                new_callable=AsyncMock,
            ) as mock_exec,
        ):
            session = AsyncMock()
            await process_quiz_result(
                session, "stu-1", "node-1", "course-1", score=85
            )

            ctx = mock_exec.call_args[0][5]
            assert mock_exec.call_args[0][4] == "da_consolidare"
            assert ctx.trigger_type == TriggerType.quiz_superato.value
            assert ctx.quiz_score == 85

    @pytest.mark.asyncio
    async def test_score_lt_50_targets_lacuna(self) -> None:
        from maestro.kmm.service import process_quiz_result

        mock_sns = MagicMock()
        mock_sns.current_state = "in_recupero"

        with (
            patch(
                "maestro.kmm.service.get_student_state",
                new_callable=AsyncMock,
                return_value=mock_sns,
            ),
            patch(
                "maestro.kmm.service.execute_transition",
                new_callable=AsyncMock,
            ) as mock_exec,
        ):
            session = AsyncMock()
            await process_quiz_result(
                session, "stu-1", "node-1", "course-1", score=30
            )

            assert mock_exec.call_args[0][4] == "lacuna"

    @pytest.mark.asyncio
    async def test_score_50_79_stays_in_current_state(self) -> None:
        from maestro.kmm.service import process_quiz_result

        mock_sns = MagicMock()
        mock_sns.current_state = "in_recupero"

        with (
            patch(
                "maestro.kmm.service.get_student_state",
                new_callable=AsyncMock,
                return_value=mock_sns,
            ),
            patch(
                "maestro.kmm.service.execute_transition",
                new_callable=AsyncMock,
            ) as mock_exec,
        ):
            session = AsyncMock()
            await process_quiz_result(
                session, "stu-1", "node-1", "course-1", score=65
            )

            assert mock_exec.call_args[0][4] == "in_recupero"

    @pytest.mark.asyncio
    async def test_score_ge_80_from_da_consolidare_targets_consolidato(self) -> None:
        """Retention check: 80+ from da_consolidare -> consolidato."""
        from maestro.kmm.service import process_quiz_result

        mock_sns = MagicMock()
        mock_sns.current_state = "da_consolidare"

        with (
            patch(
                "maestro.kmm.service.get_student_state",
                new_callable=AsyncMock,
                return_value=mock_sns,
            ),
            patch(
                "maestro.kmm.service.execute_transition",
                new_callable=AsyncMock,
            ) as mock_exec,
        ):
            session = AsyncMock()
            await process_quiz_result(
                session, "stu-1", "node-1", "course-1", score=90
            )

            assert mock_exec.call_args[0][4] == "consolidato"

    @pytest.mark.asyncio
    async def test_no_state_record_raises(self) -> None:
        from maestro.kmm.service import process_quiz_result
        from maestro.kmm.state_machine import StateNotFoundError

        with patch(
            "maestro.kmm.service.get_student_state",
            new_callable=AsyncMock,
            return_value=None,
        ):
            session = AsyncMock()
            with pytest.raises(StateNotFoundError):
                await process_quiz_result(
                    session, "stu-1", "node-1", "course-1", score=80
                )


class TestProcessRetentionCheck:
    @pytest.mark.asyncio
    async def test_pass_targets_consolidato(self) -> None:
        from maestro.kmm.service import process_retention_check

        with patch(
            "maestro.kmm.service.execute_transition",
            new_callable=AsyncMock,
        ) as mock_exec:
            session = AsyncMock()
            await process_retention_check(
                session, "stu-1", "node-1", "course-1", passed=True
            )

            assert mock_exec.call_args[0][4] == "consolidato"

    @pytest.mark.asyncio
    async def test_fail_targets_lacuna(self) -> None:
        from maestro.kmm.service import process_retention_check

        with patch(
            "maestro.kmm.service.execute_transition",
            new_callable=AsyncMock,
        ) as mock_exec:
            session = AsyncMock()
            await process_retention_check(
                session, "stu-1", "node-1", "course-1", passed=False
            )

            assert mock_exec.call_args[0][4] == "lacuna"


class TestTeacherOverride:
    @pytest.mark.asyncio
    async def test_short_motivation_raises(self) -> None:
        from maestro.kmm.service import teacher_override

        session = AsyncMock()
        with pytest.raises(IllegalTransitionError, match="motivation"):
            await teacher_override(
                session,
                teacher_id="t1",
                student_id="s1",
                node_id="n1",
                course_id="c1",
                target_state="consolidato",
                motivation="troppo corta",
            )

    @pytest.mark.asyncio
    async def test_valid_override_calls_execute(self) -> None:
        from maestro.kmm.service import teacher_override

        with patch(
            "maestro.kmm.service.execute_transition",
            new_callable=AsyncMock,
        ) as mock_exec:
            session = AsyncMock()
            await teacher_override(
                session,
                teacher_id="t1",
                student_id="s1",
                node_id="n1",
                course_id="c1",
                target_state="consolidato",
                motivation="Lo studente ha dimostrato competenza in classe durante la presentazione",
            )

            ctx = mock_exec.call_args[0][5]
            assert ctx.trigger_type == TriggerType.override_docente.value
            assert ctx.triggered_by == "t1"
