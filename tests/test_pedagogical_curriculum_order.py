import inspect

import pytest

from app.schemas.content import Level
from app.services import pedagogical_curriculum_order as subject


def test_public_cefr_order_is_the_exact_immutable_tuple():
    assert isinstance(subject.CEFR_LEVEL_ORDER, tuple)
    assert subject.CEFR_LEVEL_ORDER == (
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
    )

    with pytest.raises(TypeError):
        subject.CEFR_LEVEL_ORDER[0] = "changed"


@pytest.mark.parametrize(
    ("level", "expected_index"),
    [
        ("A1", 0),
        ("A2", 1),
        ("B1", 2),
        ("B2", 3),
        ("C1", 4),
        ("C2", 5),
    ],
)
def test_public_index_matches_the_canonical_order(level, expected_index):
    assert subject.cefr_level_index(level) == expected_index


@pytest.mark.parametrize("unknown", ["A0", "C3", "a1", "", "A1 "])
def test_unknown_level_is_rejected_without_fallback(unknown):
    with pytest.raises(ValueError):
        subject.cefr_level_index(unknown)


def test_index_function_uses_the_public_tuple(monkeypatch):
    replacement = ("C2", "C1", "B2", "B1", "A2", "A1")
    monkeypatch.setattr(subject, "CEFR_LEVEL_ORDER", replacement)

    assert subject.cefr_level_index("C2") == 0
    assert subject.cefr_level_index("A1") == 5


def test_level_code_uses_the_existing_string_contract():
    level = Level(code="A1", units=[])

    assert isinstance(level.code, str)
    assert subject.cefr_level_index(level.code) == 0


def test_module_has_no_parallel_order_or_mutable_mapping_cache():
    declared_sequences = [
        value
        for name, value in vars(subject).items()
        if not name.startswith("__") and isinstance(value, (tuple, list, dict))
    ]

    assert declared_sequences == [subject.CEFR_LEVEL_ORDER]
    assert not any(
        isinstance(value, (list, dict))
        for name, value in vars(subject).items()
        if not name.startswith("__")
    )


def test_module_contains_only_cefr_order_not_curriculum_context_or_ledger():
    source = inspect.getsource(subject)
    prohibited_public_names = {
        "OrderedCurriculumCandidateContext",
        "context_incomplete",
        "CurriculumCapabilityPreparationLedger",
        "ValidationFinding",
        "validator_id",
    }

    assert prohibited_public_names.isdisjoint(vars(subject))
    assert "skill_id" not in source
    assert "validation_report" not in source
    assert "filesystem" not in source
    assert "persist" not in source


def test_level_and_unit_ids_do_not_participate_in_the_api():
    signature = inspect.signature(subject.cefr_level_index)

    assert tuple(signature.parameters) == ("level",)
    assert "unit" not in inspect.getsource(subject.cefr_level_index)
