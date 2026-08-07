"""Add direct-English production orientations.

Añade orientaciones para producciones de construcción directa.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c8e2f6b901"
down_revision: Union[str, Sequence[str], None] = "7d8e9f0a1b2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the immutable production-orientation table.

    Crea la tabla inmutable de orientación por producción.
    """
    op.create_table(
        "direct_english_construction_production_orientations",
        sa.Column("orientation_id", sa.String(), nullable=False),
        sa.Column("attempt_production_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("guidance_text", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("source_version", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(trim(orientation_id)) > 0",
            name="ck_direct_english_orientation_id_not_blank",
        ),
        sa.CheckConstraint(
            "priority IN ('relevance', 'direct_english_construction', "
            "'intelligibility', 'secondary_accuracy')",
            name="ck_direct_english_orientation_priority",
        ),
        sa.CheckConstraint(
            "source_type IN ('human', 'external')",
            name="ck_direct_english_orientation_source_type",
        ),
        sa.CheckConstraint(
            "length(trim(guidance_text)) > 0 "
            "AND length(guidance_text) <= 2000",
            name="ck_direct_english_orientation_guidance",
        ),
        sa.CheckConstraint(
            "length(trim(source_id)) > 0",
            name="ck_direct_english_orientation_source_id",
        ),
        sa.CheckConstraint(
            "(source_type = 'human' AND "
            "(source_version IS NULL OR length(trim(source_version)) > 0)) "
            "OR (source_type = 'external' AND source_version IS NOT NULL "
            "AND length(trim(source_version)) > 0)",
            name="ck_direct_english_orientation_source_version",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_production_id"],
            ["direct_english_construction_attempt_productions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("orientation_id"),
        sa.UniqueConstraint(
            "attempt_production_id",
            name="uq_direct_english_orientation_attempt_production",
        ),
    )


def downgrade() -> None:
    """Remove only the production-orientation table.

    Elimina únicamente la tabla de orientación por producción.
    """
    op.drop_table("direct_english_construction_production_orientations")
