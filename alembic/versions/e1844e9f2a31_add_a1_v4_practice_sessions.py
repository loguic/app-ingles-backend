"""Add isolated protected A1 v4 demo practice persistence.

Revision ID: e1844e9f2a31
Revises: e6c42a9b1d70
"""

from alembic import op
import sqlalchemy as sa


revision = "e1844e9f2a31"
down_revision = "e6c42a9b1d70"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "a1_v4_practice_sessions",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("declared_user_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "a1_v4_practice_audios",
        sa.Column("audio_reference", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["a1_v4_practice_sessions.session_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("audio_reference"),
    )
    op.create_index("ix_a1_v4_practice_audios_session_id", "a1_v4_practice_audios", ["session_id"])
    op.create_table(
        "a1_v4_practice_productions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("activity_id", sa.String(), nullable=False),
        sa.Column("audio_reference", sa.String(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("client_evaluation", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["a1_v4_practice_sessions.session_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "activity_id", name="uq_a1_v4_practice_activity"),
    )
    op.create_index("ix_a1_v4_practice_productions_session_id", "a1_v4_practice_productions", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_a1_v4_practice_productions_session_id", table_name="a1_v4_practice_productions")
    op.drop_table("a1_v4_practice_productions")
    op.drop_index("ix_a1_v4_practice_audios_session_id", table_name="a1_v4_practice_audios")
    op.drop_table("a1_v4_practice_audios")
    op.drop_table("a1_v4_practice_sessions")
