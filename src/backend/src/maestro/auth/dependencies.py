"""FastAPI dependencies for authentication and database sessions."""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.keycloak import UserClaims, decode_jwt, fetch_jwks
from maestro.db.engine import async_session_factory

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UserClaims:
    """Validate the JWT bearer token and return the authenticated user claims.

    This is the primary authentication dependency used across all protected endpoints.
    """
    token = credentials.credentials
    try:
        jwks = await fetch_jwks()
        return decode_jwt(token, jwks)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Errore nella validazione del token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it after the request."""
    async with async_session_factory() as session:
        yield session
