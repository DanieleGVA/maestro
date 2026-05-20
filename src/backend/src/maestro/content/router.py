"""Content generation API router.

Endpoints:
  POST /api/v1/content/generate         -- generate content for node/student
  POST /api/v1/content/quiz/generate    -- generate quiz
  POST /api/v1/content/quiz/{id}/submit -- submit quiz answers
  GET  /api/v1/content/quiz/{id}        -- get quiz detail
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.content.cache import ContentCache
from maestro.content.quiz_engine import QuizEngine
from maestro.content.schemas import (
    ContentGenerateRequest,
    ContentOut,
    ContentMetadataOut,
    QuizGenerateRequest,
    QuizOut,
    QuizQuestionOut,
    QuizResultOut,
    QuizSubmitRequest,
)
from maestro.content.text_agent import TextAgent
from maestro.db.engine import get_db
from maestro.llm.gateway import LLMGateway

router = APIRouter(prefix="/api/v1/content", tags=["content"])

# Service singletons (wired at import time; in production use DI)
_gateway = LLMGateway()
_text_agent = TextAgent(_gateway)
_quiz_engine = QuizEngine(_gateway)
_cache = ContentCache()


@router.post("/generate")
async def generate_content(
    req: ContentGenerateRequest,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Generate personalised content for a student/node.

    Checks cache first; generates via Text Agent if not cached.
    """
    request_id = str(uuid.uuid4())
    node = req.target_nodes[0] if req.target_nodes else None
    if not node:
        raise HTTPException(status_code=422, detail="At least one target_node required")

    content_type = (
        "recovery_document" if req.request_type == "review_document" else "remediation_path"
    )

    # Check cache
    cached = await _cache.get(
        session,
        student_pseudo_id=req.student_pseudo_id,
        node_id=node.node_id,
        content_type=content_type,
    )
    if cached:
        return {
            "data": {
                "request_id": request_id,
                "content_type": content_type,
                "content": cached,
                "cache_hit": True,
            },
            "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
        }

    # Generate via Text Agent
    if req.request_type in ("review_document",):
        content = await _text_agent.generate_explanation(
            nodes=req.target_nodes,
            student_pseudo_id=req.student_pseudo_id,
            profile=req.content_profile,
            course_language="it",
            session=session,
        )
    else:
        content = await _text_agent.generate_recovery_mission(
            node=node,
            student_pseudo_id=req.student_pseudo_id,
            profile=req.content_profile,
            attempt_number=req.attempt_number,
            session=session,
        )

    # Cache the result (L1)
    if not content.get("fallback"):
        await _cache.set_l1(
            req.student_pseudo_id, node.node_id, content_type, content
        )

    return {
        "data": {
            "request_id": request_id,
            "content_type": content_type,
            "content": content,
            "cache_hit": False,
        },
        "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
    }


@router.post("/quiz/generate")
async def generate_quiz(
    req: QuizGenerateRequest,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a quiz for a concept node."""
    quiz_data = await _quiz_engine.generate_quiz(
        node_id=req.node_id,
        node_label=req.node_label,
        current_state=req.current_state,
        purpose=req.purpose,
        num_questions=req.num_questions,
        session=session,
    )

    request_id = str(uuid.uuid4())

    # Store quiz in DB
    quiz_id = str(uuid.uuid4())
    if not quiz_data.get("fallback"):
        prompt_hash = quiz_data.get("metadata", {}).get("prompt_hash", "")
        model_id = quiz_data.get("metadata", {}).get("model_id", "")

        await session.execute(
            text("""
                INSERT INTO content.quiz
                    (id, request_id, student_pseudo_id, course_id, node_id,
                     purpose, difficulty_level, model_id, prompt_hash)
                VALUES
                    (:id::uuid, :request_id::uuid, :pseudo_id, :course_id::uuid,
                     :node_id, :purpose, :difficulty, :model_id, :prompt_hash)
            """),
            {
                "id": quiz_id,
                "request_id": request_id,
                "pseudo_id": req.student_pseudo_id,
                "course_id": req.course_id,
                "node_id": req.node_id,
                "purpose": req.purpose,
                "difficulty": req.difficulty_level,
                "model_id": model_id,
                "prompt_hash": prompt_hash,
            },
        )

        # Store questions
        for idx, q in enumerate(quiz_data.get("questions", [])):
            await session.execute(
                text("""
                    INSERT INTO content.quiz_question
                        (id, quiz_id, question_index, question_type, question_text,
                         options, correct_answer, explanation, bloom_level, from_teacher_bank)
                    VALUES
                        (:id::uuid, :quiz_id::uuid, :idx, 'multiple_choice',
                         :question_text, :options::jsonb, :correct_answer,
                         :explanation, :bloom_level, false)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "quiz_id": quiz_id,
                    "idx": idx,
                    "question_text": q.get("question_text", ""),
                    "options": str(q.get("options", {})).replace("'", '"'),
                    "correct_answer": q.get("correct_answer", ""),
                    "explanation": q.get("explanation", ""),
                    "bloom_level": q.get("bloom_level", ""),
                },
            )

        await session.commit()

    return {
        "data": {
            "quiz_id": quiz_id,
            "node_id": req.node_id,
            "purpose": req.purpose,
            "questions": [
                {
                    "question_index": idx,
                    "question_text": q.get("question_text", ""),
                    "options": q.get("options", {}),
                }
                for idx, q in enumerate(quiz_data.get("questions", []))
            ],
            "fallback": quiz_data.get("fallback", False),
        },
        "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()},
    }


@router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    req: QuizSubmitRequest,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Submit quiz answers and get evaluation results."""
    # Fetch questions
    result = await session.execute(
        text("""
            SELECT id, question_index, correct_answer, question_text
            FROM content.quiz_question
            WHERE quiz_id = :quiz_id::uuid
            ORDER BY question_index
        """),
        {"quiz_id": quiz_id},
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Quiz non trovato")

    questions = [
        {
            "id": str(row[0]),
            "question_index": row[1],
            "correct_answer": row[2],
            "question_text": row[3],
        }
        for row in rows
    ]

    # Evaluate
    eval_result = _quiz_engine.evaluate_response(
        questions=questions,
        student_answers=req.answers,
    )

    # Store response
    response_id = str(uuid.uuid4())
    await session.execute(
        text("""
            INSERT INTO content.quiz_response
                (id, quiz_id, student_id, answers, score,
                 total_questions, correct_count, total_time_ms)
            VALUES
                (:id::uuid, :quiz_id::uuid, :student_id::uuid, :answers::jsonb,
                 :score, :total, :correct, :time_ms)
        """),
        {
            "id": response_id,
            "quiz_id": quiz_id,
            "student_id": req.student_id,
            "answers": str(req.answers).replace("'", '"'),
            "score": eval_result["score"],
            "total": eval_result["total_questions"],
            "correct": eval_result["correct_count"],
            "time_ms": req.total_time_ms,
        },
    )

    # Mark quiz as completed
    await session.execute(
        text("UPDATE content.quiz SET status = 'completed' WHERE id = :id::uuid"),
        {"id": quiz_id},
    )
    await session.commit()

    return {
        "data": {
            "quiz_id": quiz_id,
            "score": eval_result["score"],
            "total_questions": eval_result["total_questions"],
            "correct_count": eval_result["correct_count"],
            "per_question": eval_result["per_question"],
        },
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/quiz/{quiz_id}")
async def get_quiz(
    quiz_id: str,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Get quiz detail with questions (without correct answers for student view)."""
    result = await session.execute(
        text("""
            SELECT q.id, q.node_id, q.purpose, q.difficulty_level, q.status, q.created_at,
                   qq.id as qq_id, qq.question_index, qq.question_type,
                   qq.question_text, qq.options, qq.bloom_level
            FROM content.quiz q
            LEFT JOIN content.quiz_question qq ON qq.quiz_id = q.id
            WHERE q.id = :quiz_id::uuid
            ORDER BY qq.question_index
        """),
        {"quiz_id": quiz_id},
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Quiz non trovato")

    first = rows[0]
    questions = [
        {
            "id": str(row[6]),
            "question_index": row[7],
            "question_type": row[8],
            "question_text": row[9],
            "options": row[10],
            "bloom_level": row[11],
        }
        for row in rows
        if row[6] is not None
    ]

    return {
        "data": {
            "id": str(first[0]),
            "node_id": first[1],
            "purpose": first[2],
            "difficulty_level": first[3],
            "status": first[4],
            "questions": questions,
            "created_at": first[5].isoformat() if first[5] else None,
        },
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
