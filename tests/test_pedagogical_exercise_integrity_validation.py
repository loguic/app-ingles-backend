from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_exercise_integrity_validation import (
    validate_exercise_integrity,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate() -> PedagogicalUnitCandidate:
    """Build one valid candidate for exercise integrity tests.

    Construye un candidato válido para pruebas de integridad de ejercicios.
    """
    return PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )


def test_valid_exercise_does_not_generate_findings():
    candidate = build_candidate()

    findings = validate_exercise_integrity(candidate)

    assert findings == []


def test_blank_prompt_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["prompt"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "prompt" in findings[0].message.lower()


def test_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = deepcopy(candidate.model_dump(mode="json"))

    validate_exercise_integrity(candidate)

    assert candidate.model_dump(mode="json") == before

def test_fewer_than_two_options_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = ["Hello, I am Ana."]
    exercise["answer_index"] = 0
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "at least 2 options" in findings[0].message.lower()


def test_blank_option_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["options"] = ["Hello, I am Ana.", "   "]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "option at index 1 is empty" in findings[0].message.lower()

def test_negative_answer_index_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["answer_index"] = -1
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "answer_index" in findings[0].message
    assert "-1" in findings[0].message


def test_answer_index_outside_options_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["answer_index"] = len(exercise["options"])
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "answer_index" in findings[0].message
    assert "outside the options range" in findings[0].message.lower()

def test_empty_skill_ids_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["skill_ids"] = []
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "at least one skill" in findings[0].message.lower()


def test_duplicate_skill_ids_generate_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["skill_ids"] = [
        "a1_introduce_yourself",
        "a1_introduce_yourself",
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "duplicate skill_id" in findings[0].message.lower()
    assert "a1_introduce_yourself" in findings[0].message


def test_unknown_skill_id_generates_finding():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["skill_ids"] = ["a1_unknown_skill"]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_exercise_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "exercise_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-q1"]
    assert "unknown skill_id" in findings[0].message.lower()
    assert "a1_unknown_skill" in findings[0].message

def test_main_validator_rejects_blank_exercise_prompt():
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    exercise["prompt"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    exercise_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "exercise_integrity"
    ]
    assert report.status == "failed"
    assert len(exercise_findings) == 1
    assert exercise_findings[0].reference_ids == ["a1-u1-l1-q1"]

