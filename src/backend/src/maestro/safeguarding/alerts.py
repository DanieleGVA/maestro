"""Wellbeing alert management.

Creates alerts when student input triggers wellbeing keywords.
MVP: alerts are stored in DB; teacher dashboard reads them.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.common.audit import log_audit_event
from maestro.safeguarding.checker import WellbeingKeyword


async def create_wellbeing_alert(
    session: AsyncSession,
    *,
    student_id: str,
    teacher_id: str | None,
    trigger_text: str,
    matched_keywords: list[WellbeingKeyword],
    context: str | None = None,
) -> str:
    """Create a wellbeing alert and notify the teacher.

    Args:
        session: DB session.
        student_id: Internal student UUID.
        teacher_id: Teacher UUID (for notification).
        trigger_text: The student input that triggered the alert.
        matched_keywords: Keywords that matched (sorted by urgency).
        context: Last few messages for context.

    Returns:
        The alert UUID.
    """
    if not matched_keywords:
        return ""

    # Use the highest-urgency keyword
    primary = matched_keywords[0]
    alert_id = str(uuid.uuid4())

    notify_teacher = primary.urgency in ("medium", "high", "critical")
    notify_referent = primary.urgency in ("high", "critical")

    await session.execute(
        text("""
            INSERT INTO safeguarding.wellbeing_alerts
                (id, student_id, teacher_id, detected_phrase, category,
                 urgency, context, notified_teacher, notified_referent)
            VALUES
                (:id::uuid, :student_id::uuid, :teacher_id::uuid, :detected_phrase,
                 :category, :urgency, :context, :notified_teacher, :notified_referent)
        """),
        {
            "id": alert_id,
            "student_id": student_id,
            "teacher_id": teacher_id,
            "detected_phrase": primary.phrase,
            "category": primary.category,
            "urgency": primary.urgency,
            "context": context,
            "notified_teacher": notify_teacher,
            "notified_referent": notify_referent,
        },
    )

    # Create notification for teacher if needed (MVP: DB flag)
    if notify_teacher and teacher_id:
        urgency_label = "URGENTE - " if primary.urgency == "critical" else ""
        await session.execute(
            text("""
                INSERT INTO core.notification
                    (id, recipient_id, recipient_type, type, title, body, status)
                VALUES
                    (:id::uuid, :recipient_id::uuid, 'teacher', 'wellbeing_alert',
                     :title, :body, 'unread')
            """),
            {
                "id": str(uuid.uuid4()),
                "recipient_id": teacher_id,
                "title": f"{urgency_label}Segnale di benessere rilevato",
                "body": (
                    f"Categoria: {primary.category}. "
                    f"Urgenza: {primary.urgency}. "
                    f"Si prega di verificare lo stato d'animo dello studente."
                ),
            },
        )

    # Audit log
    await log_audit_event(
        session,
        actor_id="system",
        actor_type="system",
        action="wellbeing.alert",
        entity_type="student",
        entity_id=student_id,
        new_value={
            "alert_id": alert_id,
            "category": primary.category,
            "urgency": primary.urgency,
            "notified_teacher": notify_teacher,
            "notified_referent": notify_referent,
        },
    )

    return alert_id
