"""Seed data for MAESTRO demo/dev environment.

Populates the database with a realistic Italian school scenario:
- 1 school (I.T.E.T. Pantanelli-Monnet, Brindisi)
- 1 teacher, 1 course (Informatica 5AI, 2024-2025)
- 5 students enrolled
- 10 KG nodes with prerequisite edges
- StudentNodeState entries for each student x node
- 5 sample quiz questions for "Database Relazionali"

Fully idempotent: checks for existing data before inserting.

Usage:
    python -m maestro.db.seed
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.db.engine import async_session_factory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Deterministic UUIDs for seed data (reproducible across runs)
# ---------------------------------------------------------------------------
SCHOOL_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
TEACHER_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
COURSE_ID = uuid.UUID("30000000-0000-0000-0000-000000000001")

STUDENT_IDS = [
    uuid.UUID(f"40000000-0000-0000-0000-00000000000{i}") for i in range(1, 6)
]

STUDENT_DATA = [
    {"name": "Luca", "surname": "Moretti", "email": "l.moretti@pantanelli.edu.it"},
    {"name": "Giulia", "surname": "Romano", "email": "g.romano@pantanelli.edu.it"},
    {"name": "Marco", "surname": "Colombo", "email": "m.colombo@pantanelli.edu.it"},
    {"name": "Sara", "surname": "Ricci", "email": "s.ricci@pantanelli.edu.it"},
    {"name": "Alessandro", "surname": "Ferraro", "email": "a.ferraro@pantanelli.edu.it"},
]

# 10 KG topics with deterministic IDs
KG_NODE_LABELS = [
    "Reti di Computer",
    "Protocollo TCP/IP",
    "HTML e CSS",
    "JavaScript Base",
    "Database Relazionali",
    "SQL",
    "Sicurezza Informatica",
    "Algoritmi",
    "Strutture Dati",
    "Programmazione OOP",
]

KG_NODE_IDS = [
    uuid.UUID(f"50000000-0000-0000-0000-00000000000{i}")
    for i in range(10)
]

# Prerequisite edges: (source_label, target_label) meaning source is prerequisite for target
PREREQUISITE_EDGES = [
    ("Reti di Computer", "Protocollo TCP/IP"),
    ("HTML e CSS", "JavaScript Base"),
    ("Database Relazionali", "SQL"),
    ("Algoritmi", "Strutture Dati"),
    ("Strutture Dati", "Programmazione OOP"),
    ("Algoritmi", "Programmazione OOP"),
    ("Reti di Computer", "Sicurezza Informatica"),
]

# Mastery state assignments for variety in heatmap
# Keys: (student_index, node_index) -> state
# Only overrides are listed; default is "non_introdotto"
STATE_OVERRIDES: dict[tuple[int, int], str] = {
    # Luca: strong in networking and databases
    (0, 0): "consolidato",     # Reti di Computer
    (0, 1): "da_consolidare",  # Protocollo TCP/IP
    (0, 4): "introdotto",      # Database Relazionali
    (0, 7): "introdotto",      # Algoritmi
    # Giulia: strong in web technologies
    (1, 2): "consolidato",     # HTML e CSS
    (1, 3): "da_consolidare",  # JavaScript Base
    (1, 7): "introdotto",      # Algoritmi
    (1, 8): "introdotto",      # Strutture Dati
    # Marco: has a gap in algorithms, recovering
    (2, 0): "introdotto",      # Reti di Computer
    (2, 7): "lacuna",          # Algoritmi
    (2, 8): "in_recupero",     # Strutture Dati
    # Sara: progressing well across the board
    (3, 0): "da_consolidare",  # Reti di Computer
    (3, 2): "da_consolidare",  # HTML e CSS
    (3, 4): "introdotto",      # Database Relazionali
    (3, 5): "introdotto",      # SQL
    (3, 7): "da_consolidare",  # Algoritmi
    # Alessandro: just started
    (4, 0): "introdotto",      # Reti di Computer
    (4, 7): "introdotto",      # Algoritmi
}

# Quiz data for "Database Relazionali" topic
QUIZ_ID = uuid.UUID("60000000-0000-0000-0000-000000000001")

QUIZ_QUESTIONS = [
    {
        "id": uuid.UUID("70000000-0000-0000-0000-000000000001"),
        "index": 0,
        "type": "multiple_choice",
        "text": "Quale delle seguenti e' una proprieta' ACID delle transazioni?",
        "options": {
            "A": "Atomicita'",
            "B": "Alleggerimento",
            "C": "Approssimazione",
            "D": "Allocazione",
        },
        "answer": "A",
        "explanation": "ACID sta per Atomicita', Consistenza, Isolamento, Durabilita'.",
        "bloom": "remember",
    },
    {
        "id": uuid.UUID("70000000-0000-0000-0000-000000000002"),
        "index": 1,
        "type": "true_false",
        "text": "Una chiave primaria puo' contenere valori NULL.",
        "options": {"A": "Vero", "B": "Falso"},
        "answer": "B",
        "explanation": "La chiave primaria deve essere univoca e NON NULL.",
        "bloom": "understand",
    },
    {
        "id": uuid.UUID("70000000-0000-0000-0000-000000000003"),
        "index": 2,
        "type": "multiple_choice",
        "text": "Quale tipo di relazione richiede una tabella ponte?",
        "options": {
            "A": "Uno a uno",
            "B": "Uno a molti",
            "C": "Molti a molti",
            "D": "Nessuna delle precedenti",
        },
        "answer": "C",
        "explanation": (
            "Le relazioni molti a molti richiedono una tabella ponte "
            "(junction table) per essere implementate nel modello relazionale."
        ),
        "bloom": "apply",
    },
    {
        "id": uuid.UUID("70000000-0000-0000-0000-000000000004"),
        "index": 3,
        "type": "multiple_choice",
        "text": "Cosa garantisce la normalizzazione di un database?",
        "options": {
            "A": "Maggiore velocita' delle query",
            "B": "Riduzione della ridondanza dei dati",
            "C": "Aumento dello spazio su disco",
            "D": "Eliminazione di tutte le tabelle",
        },
        "answer": "B",
        "explanation": (
            "La normalizzazione riduce la ridondanza dei dati e previene anomalie "
            "di inserimento, aggiornamento e cancellazione."
        ),
        "bloom": "understand",
    },
    {
        "id": uuid.UUID("70000000-0000-0000-0000-000000000005"),
        "index": 4,
        "type": "fill_blank",
        "text": "Il vincolo di _____ referenziale garantisce che ogni valore "
        "di chiave esterna corrisponda a una chiave primaria esistente.",
        "options": None,
        "answer": "integrita'",
        "explanation": (
            "Il vincolo di integrita' referenziale (FOREIGN KEY) assicura la "
            "coerenza tra le tabelle collegate."
        ),
        "bloom": "remember",
    },
]


def _encode_pii(value: str) -> bytes:
    """Encode PII field for storage.

    In dev mode we store plaintext as UTF-8 bytes.
    In production, this would use pgcrypto symmetric encryption.
    """
    return value.encode("utf-8")


async def _row_exists(session: AsyncSession, schema_table: str, id_value: uuid.UUID) -> bool:
    """Check whether a row with the given UUID id exists."""
    result = await session.execute(
        text(f"SELECT 1 FROM {schema_table} WHERE id = :id LIMIT 1"),
        {"id": id_value},
    )
    return result.scalar() is not None


async def _row_exists_composite(
    session: AsyncSession,
    schema_table: str,
    conditions: dict,
) -> bool:
    """Check whether a row matching the given conditions exists."""
    where_parts = [f"{col} = :{col}" for col in conditions]
    where_clause = " AND ".join(where_parts)
    result = await session.execute(
        text(f"SELECT 1 FROM {schema_table} WHERE {where_clause} LIMIT 1"),
        conditions,
    )
    return result.scalar() is not None


async def seed_demo_data(session: AsyncSession) -> None:
    """Populate the database with demo data. Idempotent."""

    now = datetime.now(timezone.utc)
    logger.info("Seeding demo data...")

    # ------------------------------------------------------------------
    # 1. School
    # ------------------------------------------------------------------
    if not await _row_exists(session, "core.school", SCHOOL_ID):
        await session.execute(
            text(
                "INSERT INTO core.school (id, name, code, address, created_at) "
                "VALUES (:id, :name, :code, :address, :created_at)"
            ),
            {
                "id": SCHOOL_ID,
                "name": "I.T.E.T. Pantanelli-Monnet",
                "code": "BRTF010008",
                "address": "Via Enrico Fermi, 1 - 72100 Brindisi (BR)",
                "created_at": now,
            },
        )
        logger.info("Seeded school: I.T.E.T. Pantanelli-Monnet")

    # ------------------------------------------------------------------
    # 2. Teacher
    # ------------------------------------------------------------------
    if not await _row_exists(session, "core.teacher", TEACHER_ID):
        await session.execute(
            text(
                "INSERT INTO core.teacher "
                "(id, school_id, name_encrypted, surname_encrypted, email_encrypted, "
                "status, created_at) "
                "VALUES (:id, :school_id, :name_enc, :surname_enc, :email_enc, "
                ":status, :created_at)"
            ),
            {
                "id": TEACHER_ID,
                "school_id": SCHOOL_ID,
                "name_enc": _encode_pii("Marco"),
                "surname_enc": _encode_pii("Rossi"),
                "email_enc": _encode_pii("m.rossi@pantanelli.edu.it"),
                "status": "active",
                "created_at": now,
            },
        )
        logger.info("Seeded teacher: Prof. Marco Rossi")

    # ------------------------------------------------------------------
    # 3. Course
    # ------------------------------------------------------------------
    if not await _row_exists(session, "core.course", COURSE_ID):
        await session.execute(
            text(
                "INSERT INTO core.course "
                "(id, school_id, teacher_id, name, academic_year, language, status, created_at) "
                "VALUES (:id, :school_id, :teacher_id, :name, :academic_year, "
                ":language, :status, :created_at)"
            ),
            {
                "id": COURSE_ID,
                "school_id": SCHOOL_ID,
                "teacher_id": TEACHER_ID,
                "name": "Informatica 5AI",
                "academic_year": "2024-2025",
                "language": "it",
                "status": "active",
                "created_at": now,
            },
        )
        logger.info("Seeded course: Informatica 5AI (2024-2025)")

    # ------------------------------------------------------------------
    # 4. Students
    # ------------------------------------------------------------------
    for i, (sid, data) in enumerate(zip(STUDENT_IDS, STUDENT_DATA)):
        if not await _row_exists(session, "core.student", sid):
            await session.execute(
                text(
                    "INSERT INTO core.student "
                    "(id, school_id, name_encrypted, surname_encrypted, email_encrypted, "
                    "school_year, status, created_at) "
                    "VALUES (:id, :school_id, :name_enc, :surname_enc, :email_enc, "
                    ":school_year, :status, :created_at)"
                ),
                {
                    "id": sid,
                    "school_id": SCHOOL_ID,
                    "name_enc": _encode_pii(data["name"]),
                    "surname_enc": _encode_pii(data["surname"]),
                    "email_enc": _encode_pii(data["email"]),
                    "school_year": 5,
                    "status": "active",
                    "created_at": now,
                },
            )
            logger.info("Seeded student: %s %s", data["name"], data["surname"])

    # ------------------------------------------------------------------
    # 5. Enrolments
    # ------------------------------------------------------------------
    for i, sid in enumerate(STUDENT_IDS):
        enrolment_id = uuid.UUID(f"80000000-0000-0000-0000-00000000000{i + 1}")
        if not await _row_exists(session, "core.enrolment", enrolment_id):
            await session.execute(
                text(
                    "INSERT INTO core.enrolment "
                    "(id, student_id, course_id, academic_year, status, enrolled_at) "
                    "VALUES (:id, :student_id, :course_id, :academic_year, :status, :enrolled_at)"
                ),
                {
                    "id": enrolment_id,
                    "student_id": sid,
                    "course_id": COURSE_ID,
                    "academic_year": "2024-2025",
                    "status": "active",
                    "enrolled_at": now,
                },
            )

    logger.info("Seeded %d enrolments", len(STUDENT_IDS))

    # ------------------------------------------------------------------
    # 6. KG Nodes
    # ------------------------------------------------------------------
    label_to_id = {}
    for nid, label in zip(KG_NODE_IDS, KG_NODE_LABELS):
        label_to_id[label] = nid
        if not await _row_exists(session, "kg.node", nid):
            await session.execute(
                text(
                    "INSERT INTO kg.node "
                    "(id, course_id, node_type, label_it, difficulty, bloom_level, "
                    "school_year, school_level, subject, sort_order, is_active, "
                    "created_by, created_at, updated_at) "
                    "VALUES (:id, :course_id, :node_type, :label_it, :difficulty, "
                    ":bloom_level, :school_year, :school_level, :subject, :sort_order, "
                    ":is_active, :created_by, :created_at, :updated_at)"
                ),
                {
                    "id": nid,
                    "course_id": COURSE_ID,
                    "node_type": "macro",
                    "label_it": label,
                    "difficulty": "base",
                    "bloom_level": "understand",
                    "school_year": 5,
                    "school_level": "triennio_secondo_grado",
                    "subject": "informatica",
                    "sort_order": KG_NODE_LABELS.index(label),
                    "is_active": True,
                    "created_by": TEACHER_ID,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            logger.info("Seeded KG node: %s", label)

    # ------------------------------------------------------------------
    # 7. KG Edges (prerequisite relationships)
    # ------------------------------------------------------------------
    for edge_idx, (src_label, tgt_label) in enumerate(PREREQUISITE_EDGES):
        edge_id = uuid.UUID(f"90000000-0000-0000-0000-00000000000{edge_idx + 1}")
        src_id = label_to_id[src_label]
        tgt_id = label_to_id[tgt_label]

        if not await _row_exists(session, "kg.edge", edge_id):
            await session.execute(
                text(
                    "INSERT INTO kg.edge "
                    "(id, course_id, edge_type, source_node_id, target_node_id, "
                    "strength, created_by, created_at) "
                    "VALUES (:id, :course_id, :edge_type, :source_node_id, "
                    ":target_node_id, :strength, :created_by, :created_at)"
                ),
                {
                    "id": edge_id,
                    "course_id": COURSE_ID,
                    "edge_type": "prerequisite",
                    "source_node_id": src_id,
                    "target_node_id": tgt_id,
                    "strength": "required",
                    "created_by": TEACHER_ID,
                    "created_at": now,
                },
            )
            logger.info("Seeded edge: %s -> %s", src_label, tgt_label)

    # ------------------------------------------------------------------
    # 8. StudentNodeState (mastery per student x node)
    # ------------------------------------------------------------------
    for si, sid in enumerate(STUDENT_IDS):
        for ni, nid in enumerate(KG_NODE_IDS):
            node_id_str = str(nid)
            exists = await _row_exists_composite(
                session,
                "kmm.student_node_state",
                {"student_id": sid, "node_id": node_id_str, "course_id": COURSE_ID},
            )
            if not exists:
                state = STATE_OVERRIDES.get((si, ni), "non_introdotto")
                await session.execute(
                    text(
                        "INSERT INTO kmm.student_node_state "
                        "(student_id, node_id, course_id, current_state, state_since, "
                        "attempt_count, retention_checks_passed, created_at, updated_at) "
                        "VALUES (:student_id, :node_id, :course_id, :current_state, "
                        ":state_since, :attempt_count, :retention_checks_passed, "
                        ":created_at, :updated_at)"
                    ),
                    {
                        "student_id": sid,
                        "node_id": node_id_str,
                        "course_id": COURSE_ID,
                        "current_state": state,
                        "state_since": now,
                        "attempt_count": 0 if state == "non_introdotto" else 1,
                        "retention_checks_passed": 0,
                        "created_at": now,
                        "updated_at": now,
                    },
                )

    logger.info("Seeded StudentNodeState for %d students x %d nodes", len(STUDENT_IDS), len(KG_NODE_IDS))

    # ------------------------------------------------------------------
    # 9. Sample quiz + questions for "Database Relazionali"
    # ------------------------------------------------------------------
    db_rel_node_id = label_to_id["Database Relazionali"]

    if not await _row_exists(session, "content.quiz", QUIZ_ID):
        await session.execute(
            text(
                "INSERT INTO content.quiz "
                "(id, request_id, student_pseudo_id, course_id, node_id, purpose, "
                "difficulty_level, model_id, prompt_hash, status, created_at) "
                "VALUES (:id, :request_id, :student_pseudo_id, :course_id, :node_id, "
                ":purpose, :difficulty_level, :model_id, :prompt_hash, :status, :created_at)"
            ),
            {
                "id": QUIZ_ID,
                "request_id": uuid.UUID("60000000-0000-0000-0000-000000000099"),
                "student_pseudo_id": "demo-pseudo-001",
                "course_id": COURSE_ID,
                "node_id": str(db_rel_node_id),
                "purpose": "closure",
                "difficulty_level": "base",
                "model_id": "seed-data",
                "prompt_hash": "seed-no-llm",
                "status": "active",
                "created_at": now,
            },
        )
        logger.info("Seeded quiz for Database Relazionali")

    for q in QUIZ_QUESTIONS:
        if not await _row_exists(session, "content.quiz_question", q["id"]):
            await session.execute(
                text(
                    "INSERT INTO content.quiz_question "
                    "(id, quiz_id, question_index, question_type, question_text, "
                    "options, correct_answer, explanation, bloom_level, from_teacher_bank) "
                    "VALUES (:id, :quiz_id, :question_index, :question_type, :question_text, "
                    ":options, :correct_answer, :explanation, :bloom_level, :from_teacher_bank)"
                ),
                {
                    "id": q["id"],
                    "quiz_id": QUIZ_ID,
                    "question_index": q["index"],
                    "question_type": q["type"],
                    "question_text": q["text"],
                    "options": (
                        json.dumps(q["options"]) if q["options"] else None
                    ),
                    "correct_answer": q["answer"],
                    "explanation": q["explanation"],
                    "bloom_level": q["bloom"],
                    "from_teacher_bank": False,
                },
            )

    logger.info("Seeded %d quiz questions", len(QUIZ_QUESTIONS))

    await session.commit()
    logger.info("Demo data seeding complete")


async def _async_main() -> None:
    """Run seeding as a standalone script."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    # Ensure the database is initialised before seeding
    from maestro.db.init_db import init_db

    await init_db()

    async with async_session_factory() as session:
        await seed_demo_data(session)


def main() -> None:
    """CLI entry point: python -m maestro.db.seed"""
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
