"""Keycloak JWT validation and JWKS management.

Fetches public keys from Keycloak JWKS endpoint, validates JWT tokens,
and extracts MAESTRO-specific claims (role, school_id, class_id, student_id).
"""

import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from jose import JWTError, jwt

from maestro.config import settings

# Cache JWKS for 6 hours to avoid excessive HTTP calls to Keycloak
_JWKS_CACHE_TTL_SECONDS = 6 * 3600
_jwks_cache: dict[str, Any] | None = None
_jwks_cache_expires_at: float = 0.0


@dataclass(frozen=True)
class UserClaims:
    """Authenticated user claims extracted from Keycloak JWT."""

    sub: str
    role: str
    school_id: str | None = None
    student_id: str | None = None
    class_id: str | None = None
    email: str | None = None
    preferred_username: str | None = None


async def fetch_jwks() -> dict[str, Any]:
    """Fetch JWKS (JSON Web Key Set) from Keycloak, with in-memory caching."""
    global _jwks_cache, _jwks_cache_expires_at

    now = time.monotonic()
    if _jwks_cache is not None and now < _jwks_cache_expires_at:
        return _jwks_cache

    jwks_url = (
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
        "/protocol/openid-connect/certs"
    )
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_expires_at = now + _JWKS_CACHE_TTL_SECONDS
        return _jwks_cache


def decode_jwt(token: str, jwks: dict[str, Any]) -> UserClaims:
    """Decode and validate a Keycloak JWT, returning structured user claims.

    Raises jose.JWTError if the token is invalid, expired, or cannot be verified.
    """
    payload = jwt.decode(
        token,
        jwks,
        algorithms=[settings.jwt_algorithm],
        options={"verify_aud": False, "verify_iss": False},
    )

    maestro_claims = payload.get("maestro", {})

    role = maestro_claims.get("role")
    if not role:
        # Fallback: try realm_access.roles
        realm_roles = payload.get("realm_access", {}).get("roles", [])
        for candidate in ("admin", "teacher", "student"):
            if candidate in realm_roles:
                role = candidate
                break
    if not role:
        raise JWTError("Token mancante del claim 'role'")

    # Keycloak 26 may omit 'sub' in some token configurations; fall back to jti
    sub = payload.get("sub") or payload.get("jti") or ""

    return UserClaims(
        sub=sub,
        role=role,
        school_id=maestro_claims.get("school_id"),
        student_id=maestro_claims.get("student_id"),
        class_id=maestro_claims.get("class_id"),
        email=payload.get("email"),
        preferred_username=payload.get("preferred_username"),
    )


def invalidate_jwks_cache() -> None:
    """Force JWKS cache invalidation (e.g. after Keycloak key rotation)."""
    global _jwks_cache, _jwks_cache_expires_at
    _jwks_cache = None
    _jwks_cache_expires_at = 0.0
