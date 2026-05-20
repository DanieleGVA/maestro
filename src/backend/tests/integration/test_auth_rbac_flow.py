"""Integration tests for Auth + RBAC flow.

Tests that JWT validation, role extraction, and RBAC enforcement work
together correctly across different user types.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from maestro.auth.keycloak import UserClaims
from maestro.auth.rbac import check_own_data_or_role, require_role


class TestRBACWithUserClaims:
    """Test RBAC enforcement with different user roles."""

    def test_student_accesses_own_data(self) -> None:
        """Students should be able to access their own data."""
        user = UserClaims(sub="stu-1", role="student", student_id="stu-1")
        # Should not raise
        check_own_data_or_role(user, "stu-1")

    def test_student_cannot_access_other_data(self) -> None:
        """Students should NOT be able to access another student's data."""
        user = UserClaims(sub="stu-1", role="student", student_id="stu-1")
        with pytest.raises(HTTPException) as exc_info:
            check_own_data_or_role(user, "stu-2")
        assert exc_info.value.status_code == 403

    def test_teacher_accesses_any_student(self) -> None:
        """Teachers should access any student's data (by role)."""
        user = UserClaims(sub="teacher-1", role="teacher")
        # Should not raise for any student ID
        check_own_data_or_role(user, "stu-1")
        check_own_data_or_role(user, "stu-999")

    def test_admin_accesses_any_student(self) -> None:
        """Admins should access any student's data."""
        user = UserClaims(sub="admin-1", role="admin")
        check_own_data_or_role(user, "stu-1")

    def test_unknown_role_denied(self) -> None:
        """Unknown roles should be denied."""
        user = UserClaims(sub="guest-1", role="guest")
        with pytest.raises(HTTPException) as exc_info:
            check_own_data_or_role(user, "stu-1")
        assert exc_info.value.status_code == 403


class TestJWTClaimsExtraction:
    """Test UserClaims structure and role handling."""

    def test_student_claims_complete(self) -> None:
        user = UserClaims(
            sub="sub-1",
            role="student",
            school_id="school-1",
            student_id="stu-1",
            class_id="class-1",
            email="student@scuola.it",
        )
        assert user.sub == "sub-1"
        assert user.role == "student"
        assert user.student_id == "stu-1"

    def test_teacher_claims_no_student_id(self) -> None:
        user = UserClaims(sub="sub-2", role="teacher")
        assert user.student_id is None
        assert user.class_id is None

    def test_claims_are_frozen(self) -> None:
        """UserClaims should be immutable (frozen dataclass)."""
        user = UserClaims(sub="sub-1", role="student")
        with pytest.raises(AttributeError):
            user.role = "admin"  # type: ignore[misc]


class TestCustomAllowedRoles:
    """Test check_own_data_or_role with custom allowed_roles."""

    def test_custom_roles_restrict_access(self) -> None:
        """Only admin should be allowed when allowed_roles=('admin',)."""
        teacher = UserClaims(sub="t-1", role="teacher")
        with pytest.raises(HTTPException):
            check_own_data_or_role(teacher, "stu-1", allowed_roles=("admin",))

    def test_custom_roles_grant_access(self) -> None:
        """Teacher should be allowed when explicitly in allowed_roles."""
        teacher = UserClaims(sub="t-1", role="teacher")
        check_own_data_or_role(teacher, "stu-1", allowed_roles=("teacher",))
