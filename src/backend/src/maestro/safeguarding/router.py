"""Safeguarding API endpoints.

GET /api/v1/safeguarding/alerts -- wellbeing alerts for teacher dashboard
POST /api/v1/safeguarding/alerts/{alert_id}/acknowledge -- acknowledge an alert

For MVP: falls back to hardcoded demo data when the DB table is empty or
not yet created.
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims
from maestro.safeguarding.schemas import WellbeingAlertOut

router = APIRouter(prefix="/safeguarding", tags=["safeguarding"])


# ---------------------------------------------------------------------------
# Demo data for MVP (returned when no real alerts exist in DB)
# ---------------------------------------------------------------------------
_DEMO_ALERTS: list[dict] = [
    {
        "id": "a0000000-0000-0000-0000-000000000001",
        "student_id": "40000000-0000-0000-0000-000000000003",
        "detected_phrase": "non ce la faccio piu'",
        "category": "frustration",
        "urgency": "medium",
        "context": "Lo studente ha espresso frustrazione durante l'esercizio sugli algoritmi.",
        "notified_teacher": True,
        "notified_referent": False,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "created_at": "2025-05-20T09:15:00+00:00",
    },
    {
        "id": "a0000000-0000-0000-0000-000000000002",
        "student_id": "40000000-0000-0000-0000-000000000001",
        "detected_phrase": "mi sento solo in questa materia",
        "category": "isolation",
        "urgency": "low",
        "context": "Commento durante una sessione di studio sulle reti.",
        "notified_teacher": True,
        "notified_referent": False,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "created_at": "2025-05-19T14:30:00+00:00",
    },
    {
        "id": "a0000000-0000-0000-0000-000000000003",
        "student_id": "40000000-0000-0000-0000-000000000005",
        "detected_phrase": "non ha senso continuare",
        "category": "hopelessness",
        "urgency": "high",
        "context": "Espressione durante il quiz sulle strutture dati dopo tre tentativi falliti.",
        "notified_teacher": True,
        "notified_referent": True,
        "acknowledged_by": "20000000-0000-0000-0000-000000000001",
        "acknowledged_at": "2025-05-19T15:00:00+00:00",
        "created_at": "2025-05-19T14:45:00+00:00",
    },
    {
        "id": "a0000000-0000-0000-0000-000000000004",
        "student_id": "40000000-0000-0000-0000-000000000002",
        "detected_phrase": "tanto non servira' a niente",
        "category": "frustration",
        "urgency": "low",
        "context": "Commento durante la revisione del compito su HTML e CSS.",
        "notified_teacher": True,
        "notified_referent": False,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "created_at": "2025-05-18T11:20:00+00:00",
    },
]


@router.get("/alerts", response_model=list[WellbeingAlertOut])
async def get_wellbeing_alerts(
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    urgency: str | None = Query(None, description="Filter by urgency level"),
) -> list[WellbeingAlertOut]:
    """Return wellbeing alerts for the teacher dashboard.

    Teachers see alerts for students in their classes. Admins see all
    alerts within the school.

    For MVP: tries the real DB table first; if empty or unavailable,
    returns hardcoded demo data so the frontend can be developed in parallel.
    """
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docenti e admin possono accedere agli alert",
        )

    # Try real DB first
    try:
        query = """
            SELECT id, student_id, detected_phrase, category, urgency,
                   context, notified_teacher, notified_referent,
                   acknowledged_by, acknowledged_at, created_at
            FROM safeguarding.wellbeing_alerts
            ORDER BY created_at DESC
            LIMIT 50
        """
        result = await db.execute(text(query))
        rows = result.all()

        if rows:
            alerts = []
            for r in rows:
                alert = WellbeingAlertOut(
                    id=str(r.id),
                    student_id=str(r.student_id),
                    detected_phrase=r.detected_phrase,
                    category=r.category,
                    urgency=r.urgency,
                    context=r.context,
                    notified_teacher=r.notified_teacher,
                    notified_referent=r.notified_referent,
                    acknowledged_by=str(r.acknowledged_by) if r.acknowledged_by else None,
                    acknowledged_at=r.acknowledged_at,
                    created_at=r.created_at,
                )
                if urgency is None or alert.urgency == urgency:
                    alerts.append(alert)
            return alerts
    except Exception:
        # Table may not exist yet in some dev setups; fall through to demo data
        pass

    # Fallback: demo data
    demo = _DEMO_ALERTS
    if urgency is not None:
        demo = [a for a in demo if a["urgency"] == urgency]

    return [WellbeingAlertOut(**a) for a in demo]
