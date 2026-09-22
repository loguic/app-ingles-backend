"""Add durable, append-only TTS human-review acceptance storage.

Revision ID: e6c42a9b1d70
Revises: d1842b7f3a91
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6c42a9b1d70"
down_revision: Union[str, Sequence[str], None] = "d1842b7f3a91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tts_human_review_acceptances",
        sa.Column("review_slot_id", sa.String(), nullable=False),
        sa.Column("review_slot_version", sa.String(), nullable=False),
        sa.Column("package_id", sa.String(), nullable=False),
        sa.Column("handoff_id", sa.String(), nullable=False),
        sa.Column("lock_transition_id", sa.String(), nullable=False),
        sa.Column("review_id", sa.String(), nullable=False),
        sa.Column("canonical_handoff", sa.LargeBinary(), nullable=False),
        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("review_slot_id"),
        sa.UniqueConstraint(
            "handoff_id",
            name="uq_tts_human_review_acceptances_handoff_id",
        ),
        sa.CheckConstraint(
            "review_slot_version = 'loguic-tts-public-review-slot/1.0'",
            name="ck_tts_human_review_acceptances_slot_version",
        ),
        sa.CheckConstraint(
            "length(canonical_handoff) > 0",
            name="ck_tts_human_review_acceptances_handoff_not_empty",
        ),
    )

    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION reject_tts_human_review_acceptance_mutation()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'TTS human review acceptances are append-only';
                RETURN NULL;
            END;
            $$
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_tts_human_review_acceptance_no_row_mutation
            BEFORE UPDATE OR DELETE ON tts_human_review_acceptances
            FOR EACH ROW
            EXECUTE FUNCTION reject_tts_human_review_acceptance_mutation()
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_tts_human_review_acceptance_no_truncate
            BEFORE TRUNCATE ON tts_human_review_acceptances
            FOR EACH STATEMENT
            EXECUTE FUNCTION reject_tts_human_review_acceptance_mutation()
            """
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "DROP TRIGGER trg_tts_human_review_acceptance_no_truncate "
            "ON tts_human_review_acceptances"
        )
        op.execute(
            "DROP TRIGGER trg_tts_human_review_acceptance_no_row_mutation "
            "ON tts_human_review_acceptances"
        )
        op.execute("DROP FUNCTION reject_tts_human_review_acceptance_mutation()")

    op.drop_table("tts_human_review_acceptances")
