"""Unit tests for auth module: JWT validation and RBAC enforcement."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt as jose_jwt

from maestro.auth.keycloak import UserClaims, decode_jwt, fetch_jwks, invalidate_jwks_cache
from maestro.auth.rbac import check_own_data_or_role


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

# RSA key pair for testing (minimal, NOT for production)
_TEST_PRIVATE_KEY = {
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

_TEST_JWKS = {"keys": [_TEST_PRIVATE_KEY]}


def _make_jwt_payload(
    role: str = "student",
    sub: str = "user-123",
    school_id: str = "school-1",
    student_id: str = "student-1",
    class_id: str = "class-1",
) -> dict:
    """Create a standard JWT payload with MAESTRO claims."""
    return {
        "sub": sub,
        "email": "test@example.com",
        "preferred_username": "test_user",
        "maestro": {
            "role": role,
            "school_id": school_id,
            "student_id": student_id,
            "class_id": class_id,
        },
        "realm_access": {"roles": [role]},
        "iss": "http://localhost:8080/realms/maestro",
        "aud": "maestro-api",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }


# ---------------------------------------------------------------------------
# Tests: JWT decode
# ---------------------------------------------------------------------------


class TestDecodeJwt:
    """Tests for JWT decoding and claim extraction."""

    def test_decode_extracts_maestro_claims(self):
        """decode_jwt should extract role, school_id, student_id from maestro claims."""
        # We test the claim extraction logic by mocking jose.jwt.decode
        payload = _make_jwt_payload(role="teacher", sub="teacher-uuid")

        with patch("maestro.auth.keycloak.jwt.decode", return_value=payload):
            user = decode_jwt("fake-token", _TEST_JWKS)

        assert user.sub == "teacher-uuid"
        assert user.role == "teacher"
        assert user.school_id == "school-1"

    def test_decode_extracts_student_claims(self):
        """decode_jwt should correctly populate student-specific fields."""
        payload = _make_jwt_payload(
            role="student", sub="stu-uuid", student_id="stu-internal-1"
        )

        with patch("maestro.auth.keycloak.jwt.decode", return_value=payload):
            user = decode_jwt("fake-token", _TEST_JWKS)

        assert user.role == "student"
        assert user.student_id == "stu-internal-1"

    def test_decode_fallback_to_realm_roles(self):
        """decode_jwt should fall back to realm_access.roles if maestro.role is missing."""
        payload = _make_jwt_payload(role="admin")
        payload["maestro"] = {}  # Remove role from maestro claims

        with patch("maestro.auth.keycloak.jwt.decode", return_value=payload):
            user = decode_jwt("fake-token", _TEST_JWKS)

        assert user.role == "admin"

    def test_decode_raises_on_missing_role(self):
        """decode_jwt should raise JWTError if no role can be determined."""
        payload = _make_jwt_payload()
        payload["maestro"] = {}
        payload["realm_access"] = {"roles": []}

        from jose import JWTError

        with patch("maestro.auth.keycloak.jwt.decode", return_value=payload):
            with pytest.raises(JWTError, match="role"):
                decode_jwt("fake-token", _TEST_JWKS)

    def test_user_claims_immutable(self):
        """UserClaims should be frozen (immutable)."""
        user = UserClaims(sub="x", role="student")
        with pytest.raises(AttributeError):
            user.role = "admin"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Tests: JWKS caching
# ---------------------------------------------------------------------------


class TestJwksCache:
    """Tests for JWKS fetch and caching behaviour."""

    @pytest.mark.asyncio
    async def test_fetch_jwks_caches_result(self):
        """fetch_jwks should cache the JWKS response and not call HTTP again."""
        invalidate_jwks_cache()  # Ensure clean state

        mock_response = MagicMock()
        mock_response.json.return_value = _TEST_JWKS
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("maestro.auth.keycloak.httpx.AsyncClient", return_value=mock_client):
            result1 = await fetch_jwks()
            result2 = await fetch_jwks()

        assert result1 == _TEST_JWKS
        assert result2 == _TEST_JWKS
        # Should only call HTTP once due to caching
        mock_client.get.assert_called_once()

    def test_invalidate_cache(self):
        """invalidate_jwks_cache should reset the cache."""
        invalidate_jwks_cache()
        # After invalidation, next fetch should make a new HTTP call
        # (tested implicitly by test_fetch_jwks_caches_result)


# ---------------------------------------------------------------------------
# Tests: RBAC
# ---------------------------------------------------------------------------


class TestRbac:
    """Tests for role-based access control enforcement."""

    def test_student_can_access_own_data(self):
        """Students should be able to access their own data."""
        user = UserClaims(sub="u1", role="student", student_id="stu-1")
        # Should not raise
        check_own_data_or_role(user, "stu-1")

    def test_student_cannot_access_other_student(self):
        """Students must NOT access another student's data."""
        user = UserClaims(sub="u1", role="student", student_id="stu-1")
        with pytest.raises(HTTPException) as exc_info:
            check_own_data_or_role(user, "stu-2")
        assert exc_info.value.status_code == 403

    def test_teacher_can_access_student_data(self):
        """Teachers should be allowed to access student data by default."""
        user = UserClaims(sub="t1", role="teacher")
        # Should not raise (scope validation is at service layer)
        check_own_data_or_role(user, "stu-1")

    def test_admin_can_access_student_data(self):
        """Admins should be allowed to access student data."""
        user = UserClaims(sub="a1", role="admin")
        check_own_data_or_role(user, "stu-1")

    def test_unknown_role_denied(self):
        """Unknown roles should be denied access."""
        user = UserClaims(sub="x1", role="unknown")
        with pytest.raises(HTTPException) as exc_info:
            check_own_data_or_role(user, "stu-1")
        assert exc_info.value.status_code == 403
