"""Add the server-selected evidence binding to Direct-English attempts.

Revision ID: c1844e9f2a31
Revises: 22c69d857dc6
Create Date: 2026-09-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1844e9f2a31"
down_revision: Union[str, Sequence[str], None] = "22c69d857dc6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Persist the v3 Direct-English evidence purpose without rewriting v2."""
    op.add_column(
        "direct_english_construction_attempts",
        sa.Column("evidence_definition_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Remove the v3 Direct-English evidence purpose."""
    op.drop_column(
        "direct_english_construction_attempts",
        "evidence_definition_id",
    )
