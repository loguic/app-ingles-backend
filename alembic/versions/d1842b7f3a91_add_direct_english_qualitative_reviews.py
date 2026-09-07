"""Add append-only Direct-English qualitative reviews.

Revision ID: d1842b7f3a91
Revises: c1844e9f2a31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1842b7f3a91"
down_revision: Union[str, Sequence[str], None] = "c1844e9f2a31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Direct-English qualitative review history."""
    op.create_table(
        "direct_english_construction_production_reviews",
        sa.Column("review_id", sa.String(), nullable=False),
        sa.Column("attempt_production_id", sa.Integer(), nullable=False),
        sa.Column("dimension", sa.String(), nullable=False),
        sa.Column("result", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("source_version", sa.String(), nullable=True),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(review_id)) > 0",
            name="ck_direct_english_review_id_not_blank",
        ),
        sa.CheckConstraint(
            "dimension IN ('relevance', 'intelligibility')",
            name="ck_direct_english_review_dimension",
        ),
        sa.CheckConstraint(
            "result IN ('positive', 'negative', 'pending')",
            name="ck_direct_english_review_result",
        ),
        sa.CheckConstraint(
            "source_type IN ('human', 'external')",
            name="ck_direct_english_review_source_type",
        ),
        sa.CheckConstraint(
            "length(trim(source_id)) > 0",
            name="ck_direct_english_review_source_id",
        ),
        sa.CheckConstraint(
            "(source_type = 'human' AND "
            "(source_version IS NULL OR length(trim(source_version)) > 0)) "
            "OR (source_type = 'external' AND source_version IS NOT NULL "
            "AND length(trim(source_version)) > 0)",
            name="ck_direct_english_review_source_version",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_production_id"],
            ["direct_english_construction_attempt_productions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("review_id"),
    )
    op.create_index(
        "ix_direct_english_review_history",
        "direct_english_construction_production_reviews",
        ["attempt_production_id", "dimension", "reviewed_at", "review_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove only Direct-English qualitative review history."""
    op.drop_index(
        "ix_direct_english_review_history",
        table_name="direct_english_construction_production_reviews",
    )
    op.drop_table("direct_english_construction_production_reviews")
