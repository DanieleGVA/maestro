"""RBAC enforcement for FastAPI endpoints.

Provides FastAPI dependencies for role-based access control following the
RBAC matrix defined in the security-mvp-spec.md (section 3.2).
"""

from fastapi import HTTPException, status

from maestro.auth.keycloak import UserClaims


def require_role(*allowed_roles: str):
    """Return a dependency that enforces role membership.

    Usage in a router::

        @router.get("/admin-only")
        async def admin_endpoint(user: UserClaims = Depends(require_role("admin"))):
            ...

    This is intentionally NOT a decorator but a dependency factory, which
    integrates cleanly with FastAPI's DI system.
    """
    from maestro.auth.dependencies import get_current_user
    from fastapi import Depends

    async def _check_role(user: UserClaims = Depends(get_current_user)) -> UserClaims:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso non autorizzato per il ruolo corrente",
            )
        return user

    return _check_role


def check_own_data_or_role(
    user: UserClaims,
    target_student_id: str,
    *,
    allowed_roles: tuple[str, ...] = ("teacher", "admin"),
) -> None:
    """Verify that the user can access data for the given student.

    - Students can only access their own data (student_id in JWT must match).
    - Teachers and admins are allowed by role (scope validation against
      class/school membership should be done at the service layer with a DB query).

    Raises HTTPException 403 if access is denied.
    """
    if user.role == "student":
        if user.student_id != target_student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato: puoi accedere solo ai tuoi dati",
            )
    elif user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso non autorizzato per il ruolo corrente",
        )
