"""Add persistent conversational diagnostic records.

Añade registros persistentes del diagnóstico conversacional.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3c4f1a2b7d90"
down_revision: Union[str, Sequence[str], None] = "f81a78f8c1c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create diagnostic tables in dependency order.

    Crea las tablas diagnósticas en orden de dependencia.
    """
    with op.batch_alter_table("learner_productions") as batch_op:
        batch_op.create_unique_constraint(
            "uq_learner_production_id_prompt",
            ["id", "prompt_id"],
        )
    with op.batch_alter_table("production_evaluation_results") as batch_op:
        batch_op.create_unique_constraint(
            "uq_evaluation_result_id_production",
            ["id", "production_id"],
        )

    op.create_table(
        "conversational_diagnostic_sessions",
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("age_profile", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("age_profile IN ('6-8', '9-12', '13-17', 'adult')", name="ck_diagnostic_session_age_profile"),
        sa.CheckConstraint("status IN ('in_progress', 'provisional', 'completed', 'cancelled')", name="ck_diagnostic_session_status"),
        sa.CheckConstraint("(status = 'in_progress' AND completed_at IS NULL) OR (status <> 'in_progress' AND completed_at IS NOT NULL)", name="ck_diagnostic_session_completion"),
        sa.CheckConstraint("completed_at IS NULL OR completed_at >= started_at", name="ck_diagnostic_session_timeline"),
        sa.PrimaryKeyConstraint("diagnostic_session_id"),
    )
    op.create_index("ix_conversational_diagnostic_sessions_user_id", "conversational_diagnostic_sessions", ["user_id"])

    op.create_table(
        "conversational_diagnostic_contexts",
        sa.Column("context_id", sa.String(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("usual_languages", sa.JSON(), nullable=False),
        sa.Column("previous_english_contact", sa.Text(), nullable=False),
        sa.Column("general_interests", sa.JSON(), nullable=False),
        sa.Column("learning_goals", sa.JSON(), nullable=False),
        sa.Column("autonomy_level", sa.String(), nullable=False),
        sa.Column("responsible_adult_present", sa.Boolean(), nullable=True),
        sa.Column("audio_authorized", sa.Boolean(), nullable=False),
        sa.CheckConstraint("autonomy_level IN ('supported', 'developing', 'independent')", name="ck_diagnostic_context_autonomy"),
        sa.ForeignKeyConstraint(["diagnostic_session_id"], ["conversational_diagnostic_sessions.diagnostic_session_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("context_id"),
        sa.UniqueConstraint("diagnostic_session_id", name="uq_diagnostic_context_session"),
        sa.UniqueConstraint("diagnostic_session_id", "context_id", name="uq_diagnostic_context_session_context"),
    )

    op.create_table(
        "conversational_diagnostic_activities",
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("context_id", sa.String(), nullable=False),
        sa.Column("prompt_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("communicative_intention", sa.Text(), nullable=False),
        sa.Column("modality", sa.String(), nullable=False),
        sa.Column("expected_evidence_type", sa.String(), nullable=False),
        sa.Column("available_supports", sa.JSON(), nullable=False),
        sa.Column("transfer_variant_id", sa.String(), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.CheckConstraint("sequence_order > 0", name="ck_diagnostic_activity_order"),
        sa.CheckConstraint("stage IN ('adaptation', 'listening_comprehension', 'initial_response', 'guided_construction', 'connected_exchange', 'transfer', 'context_selection')", name="ck_diagnostic_activity_stage"),
        sa.CheckConstraint("modality IN ('listening', 'text', 'voice', 'selection')", name="ck_diagnostic_activity_modality"),
        sa.CheckConstraint("expected_evidence_type IN ('comprehension', 'spontaneous_production', 'supported_production', 'connected_exchange', 'transfer', 'motivating_context')", name="ck_diagnostic_activity_evidence_type"),
        sa.CheckConstraint("(stage = 'transfer' AND transfer_variant_id IS NOT NULL) OR (stage <> 'transfer' AND transfer_variant_id IS NULL)", name="ck_diagnostic_activity_transfer"),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "context_id"], ["conversational_diagnostic_contexts.diagnostic_session_id", "conversational_diagnostic_contexts.context_id"], name="fk_diagnostic_activity_session_context", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("activity_id"),
        sa.UniqueConstraint("diagnostic_session_id", "activity_id", name="uq_diagnostic_activity_session_activity"),
        sa.UniqueConstraint("diagnostic_session_id", "activity_id", "prompt_id", name="uq_diagnostic_activity_session_activity_prompt"),
        sa.UniqueConstraint("diagnostic_session_id", "sequence_order", name="uq_diagnostic_activity_session_order"),
    )

    op.create_table(
        "conversational_diagnostic_activity_productions",
        sa.Column("production_id", sa.Integer(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("prompt_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "activity_id", "prompt_id"], ["conversational_diagnostic_activities.diagnostic_session_id", "conversational_diagnostic_activities.activity_id", "conversational_diagnostic_activities.prompt_id"], name="fk_activity_production_session_activity_prompt", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_id", "prompt_id"], ["learner_productions.id", "learner_productions.prompt_id"], name="fk_activity_production_production_prompt", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("production_id"),
        sa.UniqueConstraint("diagnostic_session_id", "activity_id", "production_id", name="uq_activity_production_trace"),
    )

    op.create_table(
        "conversational_diagnostic_support_usages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("production_id", sa.Integer(), nullable=False),
        sa.Column("support_type", sa.String(), nullable=False),
        sa.Column("support_level", sa.String(), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("provided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("withdrawn_afterward", sa.Boolean(), nullable=False),
        sa.CheckConstraint("sequence_order > 0", name="ck_diagnostic_support_order"),
        sa.CheckConstraint("support_type IN ('none', 'visual', 'repetition', 'keyword', 'pattern', 'example', 'translation')", name="ck_diagnostic_support_type"),
        sa.CheckConstraint("support_level IN ('none', 'minimal', 'moderate', 'full')", name="ck_diagnostic_support_level"),
        sa.CheckConstraint("(support_type = 'none' AND support_level = 'none' AND withdrawn_afterward = false) OR (support_type <> 'none' AND support_level <> 'none')", name="ck_diagnostic_support_coherence"),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "activity_id", "production_id"], ["conversational_diagnostic_activity_productions.diagnostic_session_id", "conversational_diagnostic_activity_productions.activity_id", "conversational_diagnostic_activity_productions.production_id"], name="fk_diagnostic_support_activity_production", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_id", "production_id", "sequence_order", name="uq_diagnostic_support_activity_production_order"),
    )

    op.create_table(
        "conversational_diagnostic_observations",
        sa.Column("observation_id", sa.String(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("production_id", sa.Integer(), nullable=True),
        sa.Column("dimension", sa.String(), nullable=False),
        sa.Column("evidence_role", sa.String(), nullable=False),
        sa.Column("context_reference", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("support_level", sa.String(), nullable=False),
        sa.Column("observer_id", sa.String(), nullable=False),
        sa.Column("observer_version", sa.String(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("(evidence_role = 'context_relevance' AND dimension = 'motivating_context' AND context_reference IS NOT NULL) OR (evidence_role <> 'context_relevance' AND dimension <> 'motivating_context' AND context_reference IS NULL)", name="ck_diagnostic_observation_context"),
        sa.CheckConstraint("dimension IN ('listening_comprehension', 'response_initiation', 'direct_english_construction', 'oral_production', 'continuity', 'linguistic_retrieval', 'intelligibility', 'support_need', 'transfer', 'motivating_context')", name="ck_diagnostic_observation_dimension"),
        sa.CheckConstraint("evidence_role IN ('strength', 'development_need', 'priority_blockage', 'context_relevance')", name="ck_diagnostic_observation_evidence_role"),
        sa.CheckConstraint("support_level IN ('none', 'minimal', 'moderate', 'full')", name="ck_diagnostic_observation_support_level"),
        sa.CheckConstraint("dimension NOT IN ('response_initiation', 'direct_english_construction', 'oral_production', 'continuity', 'linguistic_retrieval', 'intelligibility', 'support_need', 'transfer') OR production_id IS NOT NULL", name="ck_diagnostic_observation_required_production"),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "activity_id", "production_id"], ["conversational_diagnostic_activity_productions.diagnostic_session_id", "conversational_diagnostic_activity_productions.activity_id", "conversational_diagnostic_activity_productions.production_id"], name="fk_diagnostic_observation_activity_production", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "activity_id"], ["conversational_diagnostic_activities.diagnostic_session_id", "conversational_diagnostic_activities.activity_id"], name="fk_diagnostic_observation_session_activity", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("observation_id"),
        sa.UniqueConstraint("diagnostic_session_id", "observation_id", name="uq_diagnostic_observation_session_observation"),
        sa.UniqueConstraint("diagnostic_session_id", "observation_id", "production_id", name="uq_diagnostic_observation_session_observation_production"),
    )

    op.create_table(
        "conversational_diagnostic_observation_evaluations",
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("observation_id", sa.String(), nullable=False),
        sa.Column("evaluation_result_id", sa.Integer(), nullable=False),
        sa.Column("production_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "observation_id", "production_id"], ["conversational_diagnostic_observations.diagnostic_session_id", "conversational_diagnostic_observations.observation_id", "conversational_diagnostic_observations.production_id"], name="fk_observation_evaluation_observation_production", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluation_result_id", "production_id"], ["production_evaluation_results.id", "production_evaluation_results.production_id"], name="fk_observation_evaluation_result_production", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("diagnostic_session_id", "observation_id", "evaluation_result_id"),
    )

    op.create_table(
        "initial_conversational_profiles",
        sa.Column("profile_id", sa.String(), nullable=False),
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("priority_blockage", sa.Text(), nullable=False),
        sa.Column("target_capacity", sa.Text(), nullable=False),
        sa.Column("recommended_support_level", sa.String(), nullable=False),
        sa.Column("relevant_contexts", sa.JSON(), nullable=False),
        sa.Column("recommended_method", sa.String(), nullable=False),
        sa.Column("first_lesson_id", sa.String(), nullable=False),
        sa.Column("review_criterion", sa.Text(), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("generator_id", sa.String(), nullable=False),
        sa.Column("generator_version", sa.String(), nullable=False),
        sa.CheckConstraint("status IN ('provisional', 'confirmed')", name="ck_initial_profile_status"),
        sa.CheckConstraint("recommended_support_level IN ('none', 'minimal', 'moderate', 'full')", name="ck_initial_profile_support_level"),
        sa.CheckConstraint("recommended_method = 'direct-english-construction'", name="ck_initial_profile_method"),
        sa.ForeignKeyConstraint(["diagnostic_session_id"], ["conversational_diagnostic_sessions.diagnostic_session_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.UniqueConstraint("diagnostic_session_id", "profile_id", name="uq_initial_profile_session_profile"),
    )

    op.create_table(
        "initial_conversational_profile_evidences",
        sa.Column("diagnostic_session_id", sa.String(), nullable=False),
        sa.Column("profile_id", sa.String(), nullable=False),
        sa.Column("observation_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "observation_id"], ["conversational_diagnostic_observations.diagnostic_session_id", "conversational_diagnostic_observations.observation_id"], name="fk_profile_evidence_session_observation", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["diagnostic_session_id", "profile_id"], ["initial_conversational_profiles.diagnostic_session_id", "initial_conversational_profiles.profile_id"], name="fk_profile_evidence_session_profile", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("diagnostic_session_id", "profile_id", "observation_id"),
    )


def downgrade() -> None:
    """Remove diagnostic tables in reverse dependency order.

    Elimina las tablas diagnósticas en orden inverso de dependencia.
    """
    op.drop_table("initial_conversational_profile_evidences")
    op.drop_table("initial_conversational_profiles")
    op.drop_table("conversational_diagnostic_observation_evaluations")
    op.drop_table("conversational_diagnostic_observations")
    op.drop_table("conversational_diagnostic_support_usages")
    op.drop_table("conversational_diagnostic_activity_productions")
    op.drop_table("conversational_diagnostic_activities")
    op.drop_table("conversational_diagnostic_contexts")
    op.drop_index("ix_conversational_diagnostic_sessions_user_id", table_name="conversational_diagnostic_sessions")
    op.drop_table("conversational_diagnostic_sessions")
    with op.batch_alter_table("production_evaluation_results") as batch_op:
        batch_op.drop_constraint(
            "uq_evaluation_result_id_production",
            type_="unique",
        )
    with op.batch_alter_table("learner_productions") as batch_op:
        batch_op.drop_constraint(
            "uq_learner_production_id_prompt",
            type_="unique",
        )
