"""Add append-only reviews for B181 real productions."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b181c3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a4c8e2f6b901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "short_connected_exchange_production_reviews",
        sa.Column("review_id", sa.String(), nullable=False),
        sa.Column("production_id", sa.Integer(), nullable=False),
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
            name="ck_short_exchange_review_id_not_blank",
        ),
        sa.CheckConstraint(
            "dimension IN ('intention_understanding', "
            "'contingent_response')",
            name="ck_short_exchange_review_dimension",
        ),
        sa.CheckConstraint(
            "result IN ('positive', 'negative', 'pending')",
            name="ck_short_exchange_review_result",
        ),
        sa.CheckConstraint(
            "source_type IN ('human', 'external')",
            name="ck_short_exchange_review_source_type",
        ),
        sa.CheckConstraint(
            "length(trim(source_id)) > 0",
            name="ck_short_exchange_review_source_id",
        ),
        sa.CheckConstraint(
            "(source_type = 'human' AND "
            "(source_version IS NULL OR length(trim(source_version)) > 0)) "
            "OR (source_type = 'external' AND source_version IS NOT NULL "
            "AND length(trim(source_version)) > 0)",
            name="ck_short_exchange_review_source_version",
        ),
        sa.ForeignKeyConstraint(
            ["production_id"],
            ["learner_productions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("review_id"),
    )
    op.create_index(
        "ix_short_connected_exchange_production_reviews_production_id",
        "short_connected_exchange_production_reviews",
        ["production_id"],
        unique=False,
    )
    op.create_index(
        "ix_short_exchange_review_history",
        "short_connected_exchange_production_reviews",
        ["production_id", "dimension", "reviewed_at", "review_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_short_exchange_review_history",
        table_name="short_connected_exchange_production_reviews",
    )
    op.drop_index(
        "ix_short_connected_exchange_production_reviews_production_id",
        table_name="short_connected_exchange_production_reviews",
    )
    op.drop_table("short_connected_exchange_production_reviews")
