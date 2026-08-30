"""Add authoritative experience evidence runtime for B184.2.

Revision ID: 22c69d857dc6
Revises: d1841ea7f0c1
Create Date: 2026-08-30 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "22c69d857dc6"
down_revision: Union[str, Sequence[str], None] = "d1841ea7f0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_experience_binding(
    table_name: str,
    native_id: str,
    unique_name: str,
    foreign_key_name: str,
) -> None:
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(
            sa.Column("experience_attempt_id", sa.String(), nullable=True)
        )
        batch_op.create_foreign_key(
            foreign_key_name,
            "experience_attempts",
            ["experience_attempt_id"],
            ["attempt_id"],
        )
        batch_op.create_unique_constraint(
            unique_name,
            ["experience_attempt_id", native_id],
        )
        batch_op.create_index(
            "ix_" + table_name + "_experience_attempt_id",
            ["experience_attempt_id"],
            unique=False,
        )


def upgrade() -> None:
    _add_experience_binding(
        "conversation_attempts",
        "id",
        "uq_conversation_attempt_experience_source",
        "fk_conversation_attempt_experience",
    )
    _add_experience_binding(
        "conversation_production_submissions",
        "id",
        "uq_conversation_submission_experience_source",
        "fk_conversation_submission_experience",
    )
    _add_experience_binding(
        "direct_english_construction_attempts",
        "attempt_id",
        "uq_direct_english_experience_source",
        "fk_direct_english_experience",
    )

    op.create_table(
        "experience_comprehension_responses",
        sa.Column("response_id", sa.String(), nullable=False),
        sa.Column("experience_attempt_id", sa.String(), nullable=False),
        sa.Column("evidence_definition_id", sa.String(), nullable=False),
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("comprehension_exercise_id", sa.String(), nullable=False),
        sa.Column("selected_index", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("response_id"),
        sa.ForeignKeyConstraint(
            ["experience_attempt_id"],
            ["experience_attempts.attempt_id"],
            name="fk_comprehension_response_experience",
        ),
        sa.UniqueConstraint(
            "experience_attempt_id",
            "response_id",
            name="uq_comprehension_response_experience_source",
        ),
        sa.CheckConstraint(
            "selected_index >= 0",
            name="ck_comprehension_response_selected_index",
        ),
    )
    op.create_index(
        "ix_experience_comprehension_responses_experience_attempt_id",
        "experience_comprehension_responses",
        ["experience_attempt_id"],
    )

    op.create_table(
        "experience_evidence_states",
        sa.Column("experience_attempt_id", sa.String(), nullable=False),
        sa.Column("evidence_definition_id", sa.String(), nullable=False),
        sa.Column("evidence_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("comprehension_response_id", sa.String(), nullable=True),
        sa.Column(
            "conversation_production_submission_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column("conversation_attempt_id", sa.Integer(), nullable=True),
        sa.Column(
            "direct_english_construction_attempt_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column("accredited_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "experience_attempt_id",
            "evidence_definition_id",
        ),
        sa.ForeignKeyConstraint(
            ["experience_attempt_id"],
            ["experience_attempts.attempt_id"],
            name="fk_evidence_state_experience",
        ),
        sa.ForeignKeyConstraint(
            ["experience_attempt_id", "comprehension_response_id"],
            [
                "experience_comprehension_responses.experience_attempt_id",
                "experience_comprehension_responses.response_id",
            ],
            name="fk_evidence_state_comprehension_source",
        ),
        sa.ForeignKeyConstraint(
            [
                "experience_attempt_id",
                "conversation_production_submission_id",
            ],
            [
                "conversation_production_submissions.experience_attempt_id",
                "conversation_production_submissions.id",
            ],
            name="fk_evidence_state_submission_source",
        ),
        sa.ForeignKeyConstraint(
            ["experience_attempt_id", "conversation_attempt_id"],
            [
                "conversation_attempts.experience_attempt_id",
                "conversation_attempts.id",
            ],
            name="fk_evidence_state_conversation_source",
        ),
        sa.ForeignKeyConstraint(
            [
                "experience_attempt_id",
                "direct_english_construction_attempt_id",
            ],
            [
                "direct_english_construction_attempts.experience_attempt_id",
                "direct_english_construction_attempts.attempt_id",
            ],
            name="fk_evidence_state_direct_english_source",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'needs_review', 'satisfied')",
            name="ck_experience_evidence_state_status",
        ),
        sa.CheckConstraint(
            "evidence_type IN ('comprehension_result', 'contextual_response', "
            "'guided_production', 'conversation_completion')",
            name="ck_experience_evidence_state_type",
        ),
        sa.CheckConstraint(
            "source_type IN ('comprehension_response', "
            "'conversation_production_submission', 'conversation_attempt', "
            "'direct_english_construction_attempt')",
            name="ck_experience_evidence_source_type",
        ),
        sa.CheckConstraint(
            "(CASE WHEN comprehension_response_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN conversation_production_submission_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN conversation_attempt_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN direct_english_construction_attempt_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_experience_evidence_exactly_one_source",
        ),
        sa.CheckConstraint(
            "(source_type = 'comprehension_response' AND comprehension_response_id IS NOT NULL) OR "
            "(source_type = 'conversation_production_submission' AND conversation_production_submission_id IS NOT NULL) OR "
            "(source_type = 'conversation_attempt' AND conversation_attempt_id IS NOT NULL) OR "
            "(source_type = 'direct_english_construction_attempt' AND direct_english_construction_attempt_id IS NOT NULL)",
            name="ck_experience_evidence_source_reference",
        ),
        sa.CheckConstraint(
            "(evidence_type = 'comprehension_result' AND source_type = 'comprehension_response') OR "
            "(evidence_type = 'conversation_completion' AND source_type = 'conversation_attempt') OR "
            "(evidence_type = 'guided_production' AND source_type = 'direct_english_construction_attempt') OR "
            "(evidence_type = 'contextual_response' AND source_type IN "
            "('conversation_production_submission', 'direct_english_construction_attempt'))",
            name="ck_experience_evidence_source_compatibility",
        ),
    )


def _drop_experience_binding(
    table_name: str,
    unique_name: str,
    foreign_key_name: str,
) -> None:
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.drop_index(
            "ix_" + table_name + "_experience_attempt_id"
        )
        batch_op.drop_constraint(unique_name, type_="unique")
        batch_op.drop_constraint(foreign_key_name, type_="foreignkey")
        batch_op.drop_column("experience_attempt_id")


def downgrade() -> None:
    op.drop_table("experience_evidence_states")
    op.drop_index(
        "ix_experience_comprehension_responses_experience_attempt_id",
        table_name="experience_comprehension_responses",
    )
    op.drop_table("experience_comprehension_responses")
    _drop_experience_binding(
        "direct_english_construction_attempts",
        "uq_direct_english_experience_source",
        "fk_direct_english_experience",
    )
    _drop_experience_binding(
        "conversation_production_submissions",
        "uq_conversation_submission_experience_source",
        "fk_conversation_submission_experience",
    )
    _drop_experience_binding(
        "conversation_attempts",
        "uq_conversation_attempt_experience_source",
        "fk_conversation_attempt_experience",
    )
