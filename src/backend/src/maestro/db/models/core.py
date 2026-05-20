"""ORM models for the 'core' schema: Student, Teacher, School, Course, Enrolment."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class School(Base):
    """School entity (core.school)."""

    __tablename__ = "school"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), unique=True)
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    teachers: Mapped[list["Teacher"]] = relationship(back_populates="school")
    students: Mapped[list["Student"]] = relationship(back_populates="school")
    courses: Mapped[list["Course"]] = relationship(back_populates="school")


class Teacher(Base):
    """Teacher entity (core.teacher). PII fields are encrypted at rest via pgcrypto."""

    __tablename__ = "teacher"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.school.id"), nullable=False
    )
    keycloak_user_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    surname_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    school: Mapped["School"] = relationship(back_populates="teachers")
    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")


class Student(Base):
    """Student entity (core.student). All students are minors (13-19).

    PII fields (name, surname, email) are encrypted at rest with pgcrypto.
    The application never reads raw PII in bulk queries.
    """

    __tablename__ = "student"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'deleted')",
            name="ck_student_status",
        ),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.school.id"), nullable=False
    )
    keycloak_user_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    surname_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    birth_year: Mapped[int | None] = mapped_column(Integer)
    school_year: Mapped[int] = mapped_column(Integer, nullable=False)
    school_registry_ref: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    native_language: Mapped[str | None] = mapped_column(String(10))
    bilingualism_active: Mapped[bool] = mapped_column(Boolean, default=False)
    adaptation_profile: Mapped[dict | None] = mapped_column(JSONB)
    adaptation_profile_source: Mapped[str | None] = mapped_column(String(50))
    tone_preference: Mapped[str | None] = mapped_column(String(20))
    content_length_preference: Mapped[str | None] = mapped_column(String(20))
    accessibility_prefs: Mapped[dict | None] = mapped_column(JSONB)
    consent_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suspension_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    school: Mapped["School"] = relationship(back_populates="students")
    enrolments: Mapped[list["Enrolment"]] = relationship(back_populates="student")


class Course(Base):
    """Course definition (core.course)."""

    __tablename__ = "course"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_course_status",
        ),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.school.id"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.teacher.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(9), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="it", nullable=False)
    kg_graph_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    school: Mapped["School"] = relationship(back_populates="courses")
    teacher: Mapped["Teacher"] = relationship(back_populates="courses")
    enrolments: Mapped[list["Enrolment"]] = relationship(back_populates="course")


class Enrolment(Base):
    """Student-Course enrolment (core.enrolment)."""

    __tablename__ = "enrolment"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrolment_student_course"),
        CheckConstraint(
            "status IN ('active', 'withdrawn')",
            name="ck_enrolment_status",
        ),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.student.id"), nullable=False
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.course.id"), nullable=False
    )
    academic_year: Mapped[str] = mapped_column(String(9), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="enrolments")
    course: Mapped["Course"] = relationship(back_populates="enrolments")
