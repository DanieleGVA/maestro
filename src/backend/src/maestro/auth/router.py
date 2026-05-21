"""Auth endpoints: login proxy to Keycloak.

POST /api/v1/auth/login  -- Resource Owner Password Credentials grant
POST /api/v1/auth/refresh -- Token refresh (future use)

No PII is logged. Credentials are proxied to Keycloak and never stored.
"""

import logging

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from maestro.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Keycloak OIDC configuration
# ---------------------------------------------------------------------------
# The dashboard uses the public client "maestro-dashboard" for ROPC login.
# In production this should migrate to Authorization Code + PKCE, but for
# the MVP demo ROPC is acceptable (the frontend is teacher-facing only).
_KEYCLOAK_TOKEN_URL = (
    f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
    "/protocol/openid-connect/token"
)
_DASHBOARD_CLIENT_ID = "maestro-api"


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Credentials sent by the frontend login form."""

    username: str = Field(..., min_length=1, description="Keycloak username")
    password: str = Field(..., min_length=1, description="Keycloak password")


class LoginResponse(BaseModel):
    """Token pair returned to the frontend."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 0


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """Authenticate via Keycloak ROPC grant and return JWT tokens.

    Proxies credentials to Keycloak token endpoint. Credentials are never
    stored or logged.
    """
    form_data = {
        "grant_type": "password",
        "client_id": _DASHBOARD_CLIENT_ID,
        "username": body.username,
        "password": body.password,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(_KEYCLOAK_TOKEN_URL, data=form_data)
    except httpx.ConnectError:
        logger.error("Cannot connect to Keycloak at %s", _KEYCLOAK_TOKEN_URL)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servizio di autenticazione non raggiungibile",
        )
    except httpx.TimeoutException:
        logger.error("Keycloak timeout at %s", _KEYCLOAK_TOKEN_URL)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servizio di autenticazione non risponde",
        )

    if response.status_code == 401 or response.status_code == 400:
        # Keycloak returns 400 for invalid_grant (wrong password) and 401 for
        # other auth failures. Both mean "bad credentials" from the user's POV.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
        )

    if response.status_code >= 500:
        logger.error("Keycloak server error: %d", response.status_code)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Errore interno del servizio di autenticazione",
        )

    if response.status_code != 200:
        logger.warning("Unexpected Keycloak response: %d", response.status_code)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Risposta inattesa dal servizio di autenticazione",
        )

    data = response.json()

    return LoginResponse(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token", ""),
        token_type=data.get("token_type", "Bearer"),
        expires_in=data.get("expires_in", 0),
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(body: RefreshRequest) -> LoginResponse:
    """Refresh an expired access token using the refresh token."""
    form_data = {
        "grant_type": "refresh_token",
        "client_id": _DASHBOARD_CLIENT_ID,
        "refresh_token": body.refresh_token,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(_KEYCLOAK_TOKEN_URL, data=form_data)
    except (httpx.ConnectError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servizio di autenticazione non raggiungibile",
        )

    if response.status_code in (400, 401):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido o scaduto",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Errore nel rinnovo del token",
        )

    data = response.json()

    return LoginResponse(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token", ""),
        token_type=data.get("token_type", "Bearer"),
        expires_in=data.get("expires_in", 0),
    )
