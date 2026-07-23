from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_duplicate_validation import (
    validate_duplicate_exercise_options,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate() -> PedagogicalUnitCandidate:
    """Build one valid candidate for isolated duplicate tests.

    Construye un candidato válido para pruebas aisladas de duplicados.
    """
    return PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )


def test_different_options_do_not_generate_findings():
    candidate = build_candidate()

    findings = validate_duplicate_exercise_options(candidate)

    assert findings == []


def test_exact_duplicate_generates_one_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = ["Hello, I am Ana.", "Hello, I am Ana."]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_duplicate_exercise_options(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "duplicate_exercise_options"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "indexes: 0, 1" in findings[0].message


def test_duplicate_ignores_letter_case():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = ["Hello, I am Ana.", "HELLO, I AM ANA."]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_duplicate_exercise_options(candidate)

    assert len(findings) == 1


def test_duplicate_ignores_additional_spaces():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = [
        "Hello, I am Ana.",
        "  Hello,   I am   Ana.  ",
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_duplicate_exercise_options(candidate)

    assert len(findings) == 1


def test_multiple_equivalent_options_generate_one_group_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = [
        "Hello, I am Ana.",
        "hello, i am ana.",
        "  HELLO,   I AM ANA. ",
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_duplicate_exercise_options(candidate)

    assert len(findings) == 1
    assert "indexes: 0, 1, 2" in findings[0].message


def test_equivalent_options_in_different_exercises_are_not_duplicates():
    payload = build_candidate_payload()
    first_exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    second_exercise = deepcopy(first_exercise)
    second_exercise["id"] = "a1-u1-l1-q2"
    first_exercise["options"] = ["Hello.", "Goodbye."]
    second_exercise["options"] = ["HELLO.", "Thank you."]
    payload["candidate_unit"]["lessons"][0]["exercises"].append(
        second_exercise
    )
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_duplicate_exercise_options(candidate)

    assert findings == []


def test_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = candidate.model_dump(mode="json")

    validate_duplicate_exercise_options(candidate)

    assert candidate.model_dump(mode="json") == before

def test_main_validator_rejects_duplicate_exercise_options():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = ["Hello.", "  HELLO.  "]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "failed"
    assert len(report.findings) == 1
    assert report.findings[0].validator_id == (
        "duplicate_exercise_options"
    )

