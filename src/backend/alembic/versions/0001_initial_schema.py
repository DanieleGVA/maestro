"""Initial schema — all MAESTRO tables.

Creates 4 PostgreSQL schemas (core, kmm, content, audit, kg) and all ORM
tables with indexes, check constraints, and audit-log immutability triggers.

Revision ID: 0001
Revises: None
Create Date: 2026-05-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 0. Create PostgreSQL extensions (idempotent)
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------
    # 1. Create schemas
    # ------------------------------------------------------------------
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS kmm")
    op.execute("CREATE SCHEMA IF NOT EXISTS content")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS kg")

    # ------------------------------------------------------------------
    # 2. CORE schema tables
    # ------------------------------------------------------------------

    # core.school
    op.create_table(
        "school",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="core",
    )

    # core.teacher
    op.create_table(
        "teacher",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.school.id"),
            nullable=False,
        ),
        sa.Column("keycloak_user_id", sa.String(255), unique=True, nullable=True),
        sa.Column("name_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("surname_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("email_encrypted", sa.LargeBinary, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="core",
    )

    # core.student
    op.create_table(
        "student",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.school.id"),
            nullable=False,
        ),
        sa.Column("keycloak_user_id", sa.String(255), unique=True, nullable=True),
        sa.Column("name_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("surname_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("email_encrypted", sa.LargeBinary, nullable=True),
        sa.Column("birth_year", sa.Integer, nullable=True),
        sa.Column("school_year", sa.Integer, nullable=False),
        sa.Column("school_registry_ref", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("native_language", sa.String(10), nullable=True),
        sa.Column("bilingualism_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("adaptation_profile", postgresql.JSONB, nullable=True),
        sa.Column("adaptation_profile_source", sa.String(50), nullable=True),
        sa.Column("tone_preference", sa.String(20), nullable=True),
        sa.Column("content_length_preference", sa.String(20), nullable=True),
        sa.Column("accessibility_prefs", postgresql.JSONB, nullable=True),
        sa.Column("consent_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspension_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'deleted')",
            name="ck_student_status",
        ),
        schema="core",
    )

    # core.course
    op.create_table(
        "course",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.school.id"),
            nullable=False,
        ),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.teacher.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("academic_year", sa.String(9), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="it"),
        sa.Column("kg_graph_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_course_status",
        ),
        schema="core",
    )

    # core.enrolment
    op.create_table(
        "enrolment",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.student.id"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.course.id"),
            nullable=False,
        ),
        sa.Column("academic_year", sa.String(9), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("student_id", "course_id", name="uq_enrolment_student_course"),
        sa.CheckConstraint(
            "status IN ('active', 'withdrawn')",
            name="ck_enrolment_status",
        ),
        schema="core",
    )

    # ------------------------------------------------------------------
    # 3. KMM schema tables
    # ------------------------------------------------------------------

    # kmm.student_node_state
    op.create_table(
        "student_node_state",
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.student.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("node_id", sa.Text, primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.course.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column(
            "current_state",
            sa.String(20),
            nullable=False,
            server_default="non_introdotto",
        ),
        sa.Column("previous_state", sa.String(20), nullable=True),
        sa.Column(
            "state_since",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("attempt_count", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("last_quiz_score", sa.SmallInteger, nullable=True),
        sa.Column("last_quiz_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_retention_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "retention_checks_passed", sa.SmallInteger, nullable=False, server_default="0"
        ),
        sa.Column("fsrs_stability", sa.Float, nullable=True),
        sa.Column("fsrs_difficulty", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "current_state IN ("
            "'non_introdotto', 'introdotto', 'lacuna', "
            "'in_recupero', 'da_consolidare', 'consolidato')",
            name="ck_sns_current_state",
        ),
        schema="kmm",
    )

    op.create_index(
        "idx_sns_student_course",
        "student_node_state",
        ["student_id", "course_id"],
        schema="kmm",
    )
    op.create_index(
        "idx_sns_course_state",
        "student_node_state",
        ["course_id", "current_state"],
        schema="kmm",
    )
    op.create_index(
        "idx_sns_next_retention",
        "student_node_state",
        ["next_retention_check"],
        schema="kmm",
        postgresql_where=sa.text("next_retention_check IS NOT NULL"),
    )

    # kmm.state_transition_log
    op.create_table(
        "state_transition_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.Text, nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_state", sa.String(20), nullable=False),
        sa.Column("new_state", sa.String(20), nullable=False),
        sa.Column("trigger_type", sa.String(30), nullable=False),
        sa.Column("triggered_by", sa.Text, nullable=True),
        sa.Column("trigger_ref", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("quiz_score", sa.SmallInteger, nullable=True),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("motivation", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "trigger_type IN ("
            "'verifica_errore', 'avvio_recupero', 'quiz_superato', "
            "'quiz_fallito', 'retention_check_ok', 'retention_check_fail', "
            "'regressione', 'override_docente', 'lezione_completata', "
            "'inizializzazione')",
            name="ck_stl_trigger_type",
        ),
        schema="kmm",
    )

    op.create_index(
        "idx_stl_student_node",
        "state_transition_log",
        ["student_id", "node_id", "course_id"],
        schema="kmm",
    )
    op.create_index(
        "idx_stl_course",
        "state_transition_log",
        ["course_id"],
        schema="kmm",
    )

    # kmm.retention_schedule
    op.create_table(
        "retention_schedule",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.student.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("node_id", sa.Text, nullable=False),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("core.course.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("check_number", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quiz_score", sa.SmallInteger, nullable=True),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("concept_difficulty_estimate", sa.Float, nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'notified', 'completed_pass', "
            "'completed_fail', 'cancelled')",
            name="ck_rs_status",
        ),
        schema="kmm",
    )

    op.create_index(
        "idx_rs_pending",
        "retention_schedule",
        ["scheduled_at"],
        schema="kmm",
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        "idx_rs_student",
        "retention_schedule",
        ["student_id", "node_id", "course_id"],
        schema="kmm",
    )

    # ------------------------------------------------------------------
    # 4. CONTENT schema tables
    # ------------------------------------------------------------------

    # content.generated_content
    op.create_table(
        "generated_content",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("student_pseudo_id", sa.String(100), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.Text, nullable=False, index=True),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content", postgresql.JSONB, nullable=False),
        sa.Column("model_id", sa.Text, nullable=False),
        sa.Column("prompt_template_id", sa.String(100), nullable=False),
        sa.Column("prompt_template_version", sa.Integer, nullable=False),
        sa.Column("prompt_hash", sa.Text, nullable=False),
        sa.Column("input_tokens", sa.Integer, nullable=False),
        sa.Column("output_tokens", sa.Integer, nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=False),
        sa.Column("sources_used", postgresql.JSONB, nullable=True),
        sa.Column("cache_hit", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("teacher_reviewed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("modified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "content_type IN ('recovery_document', 'remediation_path', 'quiz', "
            "'podcast_script', 'visual_diagram', 'quest_description')",
            name="ck_content_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'archived', 'blocked')",
            name="ck_content_status",
        ),
        schema="content",
    )

    # content.quiz
    op.create_table(
        "quiz",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_pseudo_id", sa.String(100), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.Text, nullable=False, index=True),
        sa.Column("purpose", sa.String(20), nullable=False),
        sa.Column("difficulty_level", sa.String(50), nullable=False),
        sa.Column("model_id", sa.Text, nullable=False),
        sa.Column("prompt_hash", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "purpose IN ('closure', 'retention')",
            name="ck_quiz_purpose",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'expired')",
            name="ck_quiz_status",
        ),
        schema="content",
    )

    # content.quiz_question
    op.create_table(
        "quiz_question",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "quiz_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content.quiz.id"),
            nullable=False,
        ),
        sa.Column("question_index", sa.Integer, nullable=False),
        sa.Column("question_type", sa.String(20), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSONB, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=False),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("bloom_level", sa.String(20), nullable=True),
        sa.Column("source_refs", postgresql.JSONB, nullable=True),
        sa.Column("from_teacher_bank", sa.Boolean, nullable=False, server_default="false"),
        sa.CheckConstraint(
            "question_type IN ('multiple_choice', 'true_false', 'fill_blank')",
            name="ck_question_type",
        ),
        schema="content",
    )

    # content.quiz_response
    op.create_table(
        "quiz_response",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "quiz_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content.quiz.id"),
            nullable=False,
        ),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answers", postgresql.JSONB, nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("total_questions", sa.Integer, nullable=False),
        sa.Column("correct_count", sa.Integer, nullable=False),
        sa.Column("total_time_ms", sa.Integer, nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="content",
    )

    # content.lesson_material
    op.create_table(
        "lesson_material",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("material_type", sa.String(20), nullable=False),
        sa.Column("file_format", sa.String(10), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("storage_key", sa.Text, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("processing_error", sa.Text, nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "material_type IN ('lesson', 'textbook', 'exercise', 'notes', "
            "'code_example', 'article', 'external_link')",
            name="ck_content_material_type",
        ),
        sa.CheckConstraint(
            "status IN ('uploaded', 'processing', 'transcribing', 'indexed', 'mapped', 'error')",
            name="ck_content_material_status",
        ),
        schema="content",
    )

    op.create_index(
        "idx_materials_course",
        "lesson_material",
        ["course_id"],
        schema="content",
    )
    op.create_index(
        "idx_materials_status",
        "lesson_material",
        ["status"],
        schema="content",
    )

    # content.lesson_chunk (uses pgvector)
    op.create_table(
        "lesson_chunk",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        # pgvector column: store as raw SQL type
        sa.Column("embedding", sa.Text, nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("material_id", "chunk_index", name="uq_content_chunk_mat_idx"),
        schema="content",
    )

    # Replace the text column with a proper vector(1536) column
    op.execute(
        "ALTER TABLE content.lesson_chunk "
        "ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)"
    )

    op.create_index(
        "idx_lesson_chunks_course",
        "lesson_chunk",
        ["course_id"],
        schema="content",
    )

    # ------------------------------------------------------------------
    # 5. KG schema tables
    # ------------------------------------------------------------------

    # kg.node
    op.create_table(
        "node",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_type", sa.String(10), nullable=False),
        sa.Column(
            "macro_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kg.node.id"),
            nullable=True,
        ),
        sa.Column("label_it", sa.Text, nullable=False),
        sa.Column("label_native", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("bloom_level", sa.String(20), nullable=True),
        sa.Column("school_year", sa.SmallInteger, nullable=False),
        sa.Column("school_level", sa.String(40), nullable=False),
        sa.Column("subject", sa.Text, nullable=False, server_default="informatica"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "course_id", "node_type", "label_it", name="uq_kg_node_course_type_label"
        ),
        sa.CheckConstraint(
            "(node_type = 'macro' AND macro_id IS NULL) OR "
            "(node_type = 'micro' AND macro_id IS NOT NULL)",
            name="ck_kg_node_macro_parent",
        ),
        sa.CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_node_type",
        ),
        sa.CheckConstraint(
            "difficulty IN ('base', 'intermedio', 'avanzato')",
            name="ck_kg_node_difficulty",
        ),
        sa.CheckConstraint(
            "bloom_level IS NULL OR bloom_level IN "
            "('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')",
            name="ck_kg_node_bloom",
        ),
        sa.CheckConstraint(
            "school_level IN ('secondaria_primo_grado', 'biennio_secondo_grado', "
            "'triennio_secondo_grado', 'post_diploma_its', 'formazione_professionale')",
            name="ck_kg_node_school_level",
        ),
        schema="kg",
    )

    op.create_index(
        "idx_kg_nodes_course",
        "node",
        ["course_id"],
        schema="kg",
        postgresql_where=sa.text("is_active"),
    )
    op.create_index(
        "idx_kg_nodes_macro",
        "node",
        ["macro_id"],
        schema="kg",
        postgresql_where=sa.text("node_type = 'micro'"),
    )

    # kg.edge
    op.create_table(
        "edge",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("edge_type", sa.String(20), nullable=False),
        sa.Column(
            "source_node_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kg.node.id"),
            nullable=False,
        ),
        sa.Column(
            "target_node_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kg.node.id"),
            nullable=False,
        ),
        sa.Column("strength", sa.String(20), nullable=True),
        sa.Column("relation_type", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "source_node_id", "target_node_id", "edge_type",
            name="uq_kg_edge_src_tgt_type",
        ),
        sa.CheckConstraint(
            "edge_type IN ('prerequisite', 'parent_of', 'related_to')",
            name="ck_kg_edge_type",
        ),
        sa.CheckConstraint(
            "strength IS NULL OR strength IN ('required', 'recommended')",
            name="ck_kg_edge_strength",
        ),
        sa.CheckConstraint(
            "source_node_id != target_node_id",
            name="ck_kg_edge_no_self",
        ),
        schema="kg",
    )

    op.create_index("idx_kg_edges_target", "edge", ["target_node_id"], schema="kg")
    op.create_index("idx_kg_edges_source", "edge", ["source_node_id"], schema="kg")
    op.create_index("idx_kg_edges_course", "edge", ["course_id"], schema="kg")

    # kg.node_embedding (uses pgvector)
    op.create_table(
        "node_embedding",
        sa.Column(
            "node_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kg.node.id"),
            primary_key=True,
        ),
        sa.Column("node_type", sa.String(10), nullable=False),
        sa.Column("embedding", sa.Text, nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_node_emb_type",
        ),
        schema="kg",
    )

    op.execute(
        "ALTER TABLE kg.node_embedding "
        "ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)"
    )

    # kg.concept_node_link
    op.create_table(
        "concept_node_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_type", sa.String(10), nullable=False),
        sa.Column("start_ms", sa.Integer, nullable=True),
        sa.Column("end_ms", sa.Integer, nullable=True),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auto_suggested", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "material_id", "chunk_id", "node_id",
            name="uq_kg_concept_link_mat_chunk_node",
        ),
        sa.CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_concept_link_type",
        ),
        schema="kg",
    )

    op.create_index("idx_concept_links_node", "concept_node_link", ["node_id"], schema="kg")
    op.create_index(
        "idx_concept_links_material", "concept_node_link", ["material_id"], schema="kg"
    )

    # kg.error_node_mapping
    op.create_table(
        "error_node_mapping",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=False),
        sa.Column("auto_confirmed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("teacher_confirmed", sa.Boolean, nullable=True),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "verification_id", "question_id", "student_id", "node_id",
            name="uq_kg_error_mapping",
        ),
        schema="kg",
    )

    op.create_index(
        "idx_error_mappings_student", "error_node_mapping", ["student_id"], schema="kg"
    )
    op.create_index(
        "idx_error_mappings_node", "error_node_mapping", ["node_id"], schema="kg"
    )
    op.create_index(
        "idx_error_mappings_verification",
        "error_node_mapping",
        ["verification_id"],
        schema="kg",
    )

    # kg.course_granularity_override
    op.create_table(
        "course_granularity_override",
        sa.Column("course_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_can_toggle_micro", sa.Boolean, nullable=False),
        sa.Column("overridden_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "overridden_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("reason", sa.Text, nullable=True),
        schema="kg",
    )

    # ------------------------------------------------------------------
    # 6. AUDIT schema tables
    # ------------------------------------------------------------------

    # audit.audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.Text, nullable=False),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Text, nullable=False),
        sa.Column("previous_value", postgresql.JSONB, nullable=True),
        sa.Column("new_value", postgresql.JSONB, nullable=True),
        sa.Column("ip_address_hash", sa.Text, nullable=True),
        sa.Column("user_agent_hash", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="audit",
    )

    # audit.llm_audit_log
    op.create_table(
        "llm_audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("agent_name", sa.Text, nullable=False),
        sa.Column("model_id", sa.Text, nullable=False),
        sa.Column("prompt_hash", sa.Text, nullable=False),
        sa.Column("input_tokens", sa.Integer, nullable=False),
        sa.Column("output_tokens", sa.Integer, nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=False),
        sa.Column("cache_hit", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="audit",
    )

    # audit.deletion_certificate
    op.create_table(
        "deletion_certificate",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id_hash", sa.Text, nullable=False),
        sa.Column("executed_by", sa.Text, nullable=False),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("tables_affected", postgresql.JSONB, nullable=False),
        sa.Column("rows_deleted", sa.Integer, nullable=False),
        sa.Column("rows_pseudonymised", sa.Integer, nullable=False),
        schema="audit",
    )

    # ------------------------------------------------------------------
    # 7. Audit immutability triggers (BEFORE UPDATE/DELETE -> raise)
    # ------------------------------------------------------------------

    # Create the reusable trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION audit.deny_modify()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Audit tables are immutable. UPDATE and DELETE are forbidden on %.%',
                TG_TABLE_SCHEMA, TG_TABLE_NAME;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql
    """)

    # Apply immutability triggers to all audit tables
    for table_name in ("audit_log", "llm_audit_log", "deletion_certificate"):
        op.execute(f"""
            CREATE TRIGGER trg_{table_name}_no_update
            BEFORE UPDATE ON audit.{table_name}
            FOR EACH ROW EXECUTE FUNCTION audit.deny_modify()
        """)
        op.execute(f"""
            CREATE TRIGGER trg_{table_name}_no_delete
            BEFORE DELETE ON audit.{table_name}
            FOR EACH ROW EXECUTE FUNCTION audit.deny_modify()
        """)

    # Apply immutability triggers to kmm.state_transition_log (append-only)
    op.execute("""
        CREATE TRIGGER trg_state_transition_log_no_update
        BEFORE UPDATE ON kmm.state_transition_log
        FOR EACH ROW EXECUTE FUNCTION audit.deny_modify()
    """)
    op.execute("""
        CREATE TRIGGER trg_state_transition_log_no_delete
        BEFORE DELETE ON kmm.state_transition_log
        FOR EACH ROW EXECUTE FUNCTION audit.deny_modify()
    """)

    # ------------------------------------------------------------------
    # 8. Auto-update updated_at trigger for mutable tables
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        CREATE TRIGGER trg_sns_updated_at
        BEFORE UPDATE ON kmm.student_node_state
        FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()
    """)

    op.execute("""
        CREATE TRIGGER trg_kg_node_updated_at
        BEFORE UPDATE ON kg.node
        FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()
    """)

    op.execute("""
        CREATE TRIGGER trg_lesson_material_updated_at
        BEFORE UPDATE ON content.lesson_material
        FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()
    """)


def downgrade() -> None:
    # ------------------------------------------------------------------
    # Drop triggers first
    # ------------------------------------------------------------------
    op.execute("DROP TRIGGER IF EXISTS trg_lesson_material_updated_at ON content.lesson_material")
    op.execute("DROP TRIGGER IF EXISTS trg_kg_node_updated_at ON kg.node")
    op.execute("DROP TRIGGER IF EXISTS trg_sns_updated_at ON kmm.student_node_state")
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at()")

    op.execute(
        "DROP TRIGGER IF EXISTS trg_state_transition_log_no_delete ON kmm.state_transition_log"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_state_transition_log_no_update ON kmm.state_transition_log"
    )

    for table_name in ("deletion_certificate", "llm_audit_log", "audit_log"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_no_delete ON audit.{table_name}")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_no_update ON audit.{table_name}")

    op.execute("DROP FUNCTION IF EXISTS audit.deny_modify()")

    # ------------------------------------------------------------------
    # Drop tables in reverse dependency order
    # ------------------------------------------------------------------

    # Audit
    op.drop_table("deletion_certificate", schema="audit")
    op.drop_table("llm_audit_log", schema="audit")
    op.drop_table("audit_log", schema="audit")

    # KG
    op.drop_table("course_granularity_override", schema="kg")
    op.drop_table("error_node_mapping", schema="kg")
    op.drop_table("concept_node_link", schema="kg")
    op.drop_table("node_embedding", schema="kg")
    op.drop_table("edge", schema="kg")
    op.drop_table("node", schema="kg")

    # Content
    op.drop_table("lesson_chunk", schema="content")
    op.drop_table("lesson_material", schema="content")
    op.drop_table("quiz_response", schema="content")
    op.drop_table("quiz_question", schema="content")
    op.drop_table("quiz", schema="content")
    op.drop_table("generated_content", schema="content")

    # KMM
    op.drop_table("retention_schedule", schema="kmm")
    op.drop_table("state_transition_log", schema="kmm")
    op.drop_table("student_node_state", schema="kmm")

    # Core
    op.drop_table("enrolment", schema="core")
    op.drop_table("course", schema="core")
    op.drop_table("student", schema="core")
    op.drop_table("teacher", schema="core")
    op.drop_table("school", schema="core")

    # Schemas
    op.execute("DROP SCHEMA IF EXISTS kg CASCADE")
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE")
    op.execute("DROP SCHEMA IF EXISTS content CASCADE")
    op.execute("DROP SCHEMA IF EXISTS kmm CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
