from pathlib import Path

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint

from app.db.models import (
    DirectEnglishConstructionAttempt,
    DirectEnglishConstructionAttemptProduction,
)


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic"
    / "versions"
    / "7d8e9f0a1b2c_add_direct_english_construction_execution.py"
)


def constraint_names(table, constraint_type):
    return {
        item.name
        for item in table.constraints
        if isinstance(item, constraint_type)
    }


def test_attempt_model_contains_only_execution_identity_and_snapshot():
    table = DirectEnglishConstructionAttempt.__table__

    assert table.name == "direct_english_construction_attempts"
    assert set(table.columns) == {
        table.c.attempt_id,
        table.c.user_id,
        table.c.level_id,
        table.c.unit_id,
        table.c.lesson_id,
        table.c.transfer_bank_id,
        table.c.transfer_variant_id,
        table.c.transfer_prompt_snapshot,
        table.c.selector_version,
        table.c.status,
        table.c.started_at,
        table.c.finalized_at,
    }
    assert {"progress", "mastery", "score", "correct"}.isdisjoint(
        table.columns.keys()
    )
    assert "ck_direct_english_attempt_status" in constraint_names(
        table, CheckConstraint
    )
    assert "ck_direct_english_attempt_finalization" in constraint_names(
        table, CheckConstraint
    )
    assert "ck_direct_english_attempt_timeline" in constraint_names(
        table, CheckConstraint
    )


def test_attempt_production_has_required_relational_integrity():
    table = DirectEnglishConstructionAttemptProduction.__table__

    assert table.name == "direct_english_construction_attempt_productions"
    assert "modality" not in table.columns
    assert "completion_requirements_met" not in table.columns
    assert constraint_names(table, UniqueConstraint) >= {
        "uq_direct_english_attempt_function",
        "uq_direct_english_attempt_learner_production",
    }
    targets = {
        element.target_fullname
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for element in constraint.elements
    }
    assert targets == {
        "direct_english_construction_attempts.attempt_id",
        "learner_productions.id",
    }


def test_migration_is_linear_static_and_reversible():
    source = MIGRATION.read_text(encoding="utf-8")

    assert 'revision: str = "7d8e9f0a1b2c"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "3c4f1a2b7d90"' in source
    assert source.count("op.create_table(") == 2
    assert source.count("op.drop_table(") == 2
    assert source.index(
        'op.drop_table("direct_english_construction_attempt_productions")'
    ) < source.index('op.drop_table("direct_english_construction_attempts")')
    assert "completion_requirements_met" not in source
