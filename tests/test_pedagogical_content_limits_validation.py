import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_content_limits_validation import (
    validate_content_limits,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate_with_limits(**limits) -> PedagogicalUnitCandidate:
    """Build one valid candidate with declared quantitative limits.

    Construye un candidato válido con límites cuantitativos declarados.
    """
    payload = build_candidate_payload()
    payload["specification"]["content_limits"] = limits
    return PedagogicalUnitCandidate.model_validate(payload)


def test_candidate_without_declared_limits_passes_validation():
    candidate = build_candidate_with_limits()

    findings = validate_content_limits(candidate)

    assert findings == []


def test_minimum_lessons_generates_unit_finding():
    candidate = build_candidate_with_limits(min_lessons=3)

    findings = validate_content_limits(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_limits"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1"]
    assert "minimum lessons" in findings[0].message


def test_maximum_lessons_generates_unit_finding():
    candidate = build_candidate_with_limits(max_lessons=1)

    findings = validate_content_limits(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == ["a1-u1"]
    assert "maximum lessons" in findings[0].message


def test_content_limit_validation_does_not_modify_candidate():
    candidate = build_candidate_with_limits(min_lessons=3)
    before = candidate.model_dump(mode="json")

    validate_content_limits(candidate)

    assert candidate.model_dump(mode="json") == before

@pytest.mark.parametrize(
    ("limit_field", "limit_value", "reference_id", "message_fragment"),
    [
        ("min_examples_per_lesson", 1, "a1-u1-l2", "minimum examples"),
        ("max_examples_per_lesson", 0, "a1-u1-l1", "maximum examples"),
        (
            "min_conversations_per_lesson",
            1,
            "a1-u1-l2",
            "minimum conversations",
        ),
        (
            "max_conversations_per_lesson",
            0,
            "a1-u1-l1",
            "maximum conversations",
        ),
        ("min_exercises_per_lesson", 1, "a1-u1-l2", "minimum exercises"),
        ("max_exercises_per_lesson", 0, "a1-u1-l1", "maximum exercises"),
    ],
)
def test_lesson_content_limits_generate_findings(
    limit_field,
    limit_value,
    reference_id,
    message_fragment,
):
    candidate = build_candidate_with_limits(
        **{limit_field: limit_value}
    )

    findings = validate_content_limits(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [reference_id]
    assert message_fragment in findings[0].message

@pytest.mark.parametrize(
    ("limit_field", "limit_value", "reference_id", "message_fragment"),
    [
        (
            "min_options_per_exercise",
            3,
            "a1-u1-l1-q1",
            "minimum options",
        ),
        (
            "max_options_per_exercise",
            1,
            "a1-u1-l1-q1",
            "maximum options",
        ),
        (
            "min_turns_per_conversation",
            2,
            "a1-u1-l1-c1",
            "minimum turns",
        ),
        (
            "max_turns_per_conversation",
            0,
            "a1-u1-l1-c1",
            "maximum turns",
        ),
    ],
)
def test_activity_content_limits_generate_findings(
    limit_field,
    limit_value,
    reference_id,
    message_fragment,
):
    candidate = build_candidate_with_limits(
        **{limit_field: limit_value}
    )

    findings = validate_content_limits(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [reference_id]
    assert message_fragment in findings[0].message

def test_main_validator_rejects_content_limit_violation():
    candidate = build_candidate_with_limits(min_lessons=3)

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "failed"
    assert any(
        finding.validator_id == "content_limits"
        for finding in report.findings
    )

