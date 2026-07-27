"""Baseline of the schema that existed before B131.

Baseline del esquema existente antes de B131.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1fe71209621"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the historical application schema.

    Crea el esquema histórico de la aplicación.
    """
    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("level_id", sa.String(), nullable=False),
        sa.Column("unit_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("selected_index", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "id",
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "exercise_id",
    ):
        op.create_index(
            f"ix_user_progress_{column}",
            "user_progress",
            [column],
        )

    op.create_table(
        "conversation_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("level_id", sa.String(), nullable=False),
        sa.Column("unit_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("visited_turn_ids", sa.JSON(), nullable=False),
        sa.Column("selected_choice_ids", sa.JSON(), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "id",
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "conversation_id",
    ):
        op.create_index(
            f"ix_conversation_attempts_{column}",
            "conversation_attempts",
            [column],
        )

    op.create_table(
        "conversation_production_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("level_id", sa.String(), nullable=False),
        sa.Column("unit_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "id",
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "conversation_id",
    ):
        op.create_index(
            f"ix_conversation_production_submissions_{column}",
            "conversation_production_submissions",
            [column],
        )

    op.create_table(
        "learner_productions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("prompt_id", sa.String(), nullable=False),
        sa.Column("turn_id", sa.String(), nullable=False),
        sa.Column("modality", sa.String(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("audio_reference", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["conversation_production_submissions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "submission_id",
            "prompt_id",
            name="uq_learner_production_submission_prompt",
        ),
    )
    for column in (
        "id",
        "submission_id",
        "prompt_id",
        "turn_id",
    ):
        op.create_index(
            f"ix_learner_productions_{column}",
            "learner_productions",
            [column],
        )


def downgrade() -> None:
    """Remove the historical schema in reverse dependency order.

    Elimina el esquema histórico en orden inverso de dependencias.
    """
    op.drop_table("learner_productions")
    op.drop_table("conversation_production_submissions")
    op.drop_table("conversation_attempts")
    op.drop_table("user_progress")
