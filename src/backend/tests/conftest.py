"""Shared pytest fixtures for the MAESTRO backend test suite.

Provides mock DB sessions, mock Redis, mock LLM clients, and sample data
so ALL tests run without external services.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Sample UUIDs (deterministic for reproducibility)
# ---------------------------------------------------------------------------
STUDENT_UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEACHER_UUID = uuid.UUID("00000000-0000-0000-0000-000000000002")
ADMIN_UUID = uuid.UUID("00000000-0000-0000-0000-000000000003")
SCHOOL_UUID = uuid.UUID("00000000-0000-0000-0000-000000000010")
COURSE_UUID = uuid.UUID("00000000-0000-0000-0000-000000000020")
CLASS_UUID = uuid.UUID("00000000-0000-0000-0000-000000000030")
NODE_UUID = uuid.UUID("00000000-0000-0000-0000-000000000100")


# ---------------------------------------------------------------------------
# Mock DB session
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock AsyncSession with common operations stubbed."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.get = AsyncMock(return_value=None)
    return session


# ---------------------------------------------------------------------------
# Mock Redis
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_redis() -> AsyncMock:
    """Create a mock Redis client."""
    r = AsyncMock()
    r.get = AsyncMock(return_value=None)
    r.setex = AsyncMock()
    r.delete = AsyncMock()
    r.ping = AsyncMock(return_value=True)
    return r


# ---------------------------------------------------------------------------
# Mock LLM clients
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_llm_response() -> MagicMock:
    """Create a mock RawLLMResponse."""
    from maestro.llm.clients import RawLLMResponse

    return RawLLMResponse(
        content='{"blocks": [], "summary": "Test content"}',
        model_id="test-model",
        input_tokens=100,
        output_tokens=50,
        latency_ms=200,
    )


@pytest.fixture
def mock_anthropic_client(mock_llm_response: MagicMock) -> AsyncMock:
    """Create a mock AnthropicClient."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value=mock_llm_response)
    return client


@pytest.fixture
def mock_openai_client(mock_llm_response: MagicMock) -> AsyncMock:
    """Create a mock OpenAIClient."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value=mock_llm_response)
    return client


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def student_claims():
    """Create UserClaims for a student."""
    from maestro.auth.keycloak import UserClaims

    return UserClaims(
        sub=str(STUDENT_UUID),
        role="student",
        school_id=str(SCHOOL_UUID),
        student_id=str(STUDENT_UUID),
        class_id=str(CLASS_UUID),
        email="studente@scuola.it",
    )


@pytest.fixture
def teacher_claims():
    """Create UserClaims for a teacher."""
    from maestro.auth.keycloak import UserClaims

    return UserClaims(
        sub=str(TEACHER_UUID),
        role="teacher",
        school_id=str(SCHOOL_UUID),
        class_id=str(CLASS_UUID),
    )


@pytest.fixture
def admin_claims():
    """Create UserClaims for an admin."""
    from maestro.auth.keycloak import UserClaims

    return UserClaims(
        sub=str(ADMIN_UUID),
        role="admin",
        school_id=str(SCHOOL_UUID),
    )


# ---------------------------------------------------------------------------
# Sample student data
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_student_context() -> dict[str, Any]:
    """Sample student context with PII for pseudonymisation tests."""
    return {
        "name": "Luca",
        "surname": "Rossi",
        "teacher_name": "Marco",
        "teacher_surname": "Bianchi",
        "school_name": "ITIS Galileo Galilei",
        "class_name": "3B Informatica",
        "email": "luca.rossi@scuola.it",
        "native_language": "ucraino",
        "birth_year": "2009",
        "phone": "3331234567",
        "registry_id": "MAT-2024-0042",
    }


# ---------------------------------------------------------------------------
# Sample KG / content fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_target_nodes():
    """Sample target nodes for content generation."""
    from maestro.content.schemas import TargetNode

    return [
        TargetNode(
            node_id="micro-session-fixation",
            node_type="micro",
            current_state="lacuna",
            label_it="Session Fixation",
            error_description="Confusione tra session fixation e session hijacking",
        ),
        TargetNode(
            node_id="micro-sql-injection",
            node_type="micro",
            current_state="in_recupero",
            label_it="SQL Injection",
            error_description="Mancata sanitizzazione input utente",
        ),
    ]


@pytest.fixture
def sample_content_profile():
    """Sample content adaptation profile."""
    from maestro.content.schemas import ContentAdaptationProfile

    return ContentAdaptationProfile(
        visuale=0.3,
        audio=0.1,
        pratico=0.2,
        lettura=0.3,
        dialogo=0.1,
        tone="confidenziale",
        length="approfondimento",
    )


# ---------------------------------------------------------------------------
# Sample orchestrator state
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_state() -> dict[str, Any]:
    """Minimal MaestroState for orchestrator tests."""
    return {
        "request_id": str(uuid.uuid4()),
        "request_type": "gap_closure",
        "student_pseudo_id": "STUDENTE_abc12345",
        "student_internal_id": str(STUDENT_UUID),
        "course_id": str(COURSE_UUID),
        "active_consents": ["a", "b", "c"],
        "target_node_ids": ["micro-session-fixation"],
        "content_profile": {
            "visuale": 0.3,
            "audio": 0.1,
            "pratico": 0.2,
            "lettura": 0.3,
            "dialogo": 0.1,
            "tone": "confidenziale",
            "length": "approfondimento",
        },
        "agent_trace": [],
        "errors": [],
    }


# ---------------------------------------------------------------------------
# JWKS fixture for auth tests
# ---------------------------------------------------------------------------
MOCK_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "test-key-1",
            "use": "sig",
            "n": (
                "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtV"
                "T86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64t"
                "Z_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2"
                "QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91Ck"
                "uCxD_T5FZzOg3dS6JQ_8-cNp8bSF5OPvGFZ9fk85NJn-2Yz-q7D98Lcphng"
                "Q-X2_FRs4n4eFT0N94C0X68FPSzgGqyA1tp7jn-_GM7X9S-TbkvEi1j3l"
            ),
            "e": "AQAB",
        }
    ]
}
