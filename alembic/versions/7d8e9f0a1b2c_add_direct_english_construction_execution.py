"""Add direct-English construction execution records.

Añade registros de ejecución de construcción directa en inglés.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d8e9f0a1b2c"
down_revision: Union[str, Sequence[str], None] = "3c4f1a2b7d90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create attempt and production-link tables.

    Crea las tablas de intento y enlace con producciones.
    """
    op.create_table(
        "direct_english_construction_attempts",
        sa.Column("attempt_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("level_id", sa.String(), nullable=False),
        sa.Column("unit_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("transfer_bank_id", sa.String(), nullable=False),
        sa.Column("transfer_variant_id", sa.String(), nullable=False),
        sa.Column("transfer_prompt_snapshot", sa.Text(), nullable=False),
        sa.Column("selector_version", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "length(trim(attempt_id)) > 0",
            name="ck_direct_english_attempt_id_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(user_id)) > 0 "
            "AND length(trim(level_id)) > 0 "
            "AND length(trim(unit_id)) > 0 "
            "AND length(trim(lesson_id)) > 0",
            name="ck_direct_english_attempt_hierarchy_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(transfer_bank_id)) > 0 "
            "AND length(trim(transfer_variant_id)) > 0 "
            "AND length(trim(transfer_prompt_snapshot)) > 0 "
            "AND length(trim(selector_version)) > 0",
            name="ck_direct_english_attempt_selection_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('started', 'finalized')",
            name="ck_direct_english_attempt_status",
        ),
        sa.CheckConstraint(
            "(status = 'started' AND finalized_at IS NULL) OR "
            "(status = 'finalized' AND finalized_at IS NOT NULL)",
            name="ck_direct_english_attempt_finalization",
        ),
        sa.CheckConstraint(
            "finalized_at IS NULL OR finalized_at >= started_at",
            name="ck_direct_english_attempt_timeline",
        ),
        sa.PrimaryKeyConstraint("attempt_id"),
    )

    op.create_table(
        "direct_english_construction_attempt_productions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.String(), nullable=False),
        sa.Column("learner_production_id", sa.Integer(), nullable=False),
        sa.Column("production_function", sa.String(), nullable=False),
        sa.Column("evidence_id", sa.String(), nullable=False),
        sa.Column("configured_support_level", sa.String(), nullable=False),
        sa.Column("support_used", sa.String(), nullable=False),
        sa.CheckConstraint(
            "production_function IN ('guided', 'expanded', 'transfer')",
            name="ck_direct_english_attempt_production_function",
        ),
        sa.CheckConstraint(
            "configured_support_level IN "
            "('model', 'anchors', 'initial_word', 'none')",
            name="ck_direct_english_attempt_configured_support",
        ),
        sa.CheckConstraint(
            "support_used IN ('model', 'anchors', 'initial_word', 'none')",
            name="ck_direct_english_attempt_support_used",
        ),
        sa.CheckConstraint(
            "length(trim(evidence_id)) > 0",
            name="ck_direct_english_attempt_evidence_not_blank",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["direct_english_construction_attempts.attempt_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["learner_production_id"],
            ["learner_productions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "attempt_id",
            "production_function",
            name="uq_direct_english_attempt_function",
        ),
        sa.UniqueConstraint(
            "learner_production_id",
            name="uq_direct_english_attempt_learner_production",
        ),
    )
    op.create_index(
        "ix_direct_english_construction_attempt_productions_id",
        "direct_english_construction_attempt_productions",
        ["id"],
    )


def downgrade() -> None:
    """Remove execution tables in reverse dependency order.

    Elimina las tablas de ejecución en orden inverso de dependencia.
    """
    op.drop_index(
        "ix_direct_english_construction_attempt_productions_id",
        table_name="direct_english_construction_attempt_productions",
    )
    op.drop_table("direct_english_construction_attempt_productions")
    op.drop_table("direct_english_construction_attempts")
