"""Add authoritative experience attempts for B184.1.

Revision ID: d1841ea7f0c1
Revises: b181c3e4f5a6
Create Date: 2026-08-28 13:44:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1841ea7f0c1"
down_revision: Union[str, Sequence[str], None] = "b181c3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "experience_attempts",
        sa.Column("attempt_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("level_id", sa.String(), nullable=False),
        sa.Column("unit_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("experience_contract_version", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('in_progress', 'completed')",
            name="ck_experience_attempt_status",
        ),
        sa.CheckConstraint(
            "(status = 'in_progress' AND completed_at IS NULL) OR "
            "(status = 'completed' AND completed_at IS NOT NULL)",
            name="ck_experience_attempt_completion",
        ),
        sa.CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_experience_attempt_timeline",
        ),
        sa.PrimaryKeyConstraint("attempt_id"),
    )
    op.create_index(
        "uq_experience_attempt_active_context",
        "experience_attempts",
        [
            "user_id",
            "level_id",
            "unit_id",
            "lesson_id",
            "experience_contract_version",
        ],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'"),
        sqlite_where=sa.text("status = 'in_progress'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_experience_attempt_active_context",
        table_name="experience_attempts",
    )
    op.drop_table("experience_attempts")
