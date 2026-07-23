import pytest

from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_identifier_validation import (
    validate_content_identifiers,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate(payload=None) -> PedagogicalUnitCandidate:
    """Build one candidate for isolated identifier tests.

    Construye un candidato para pruebas aisladas de identificadores.
    """
    source = payload if payload is not None else build_candidate_payload()
    return PedagogicalUnitCandidate.model_validate(source)


def test_valid_hierarchical_identifiers_pass_validation():
    candidate = build_candidate()

    findings = validate_content_identifiers(candidate)

    assert findings == []


def test_malformed_lesson_identifier_generates_finding():
    payload = deepcopy(build_candidate_payload())
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["id"] = "a1-u1-lesson-1"
    lesson["examples"][0]["id"] = "a1-u1-lesson-1-e1"
    lesson["conversations"][0]["id"] = "a1-u1-lesson-1-c1"
    lesson["conversations"][0]["turns"][0]["id"] = (
        "a1-u1-lesson-1-c1-t1"
    )
    lesson["exercises"][0]["id"] = "a1-u1-lesson-1-q1"
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_identifier_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-lesson-1"]
    assert "invalid lesson identifier" in findings[0].message


def test_duplicate_lesson_identifiers_generate_finding():
    payload = deepcopy(build_candidate_payload())
    payload["candidate_unit"]["lessons"][1]["id"] = "a1-u1-l1"
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "duplicate lesson identifier" in findings[0].message


def test_identifier_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = candidate.model_dump(mode="json")

    validate_content_identifiers(candidate)

    assert candidate.model_dump(mode="json") == before

@pytest.mark.parametrize(
    ("collection", "invalid_id", "content_type"),
    [
        ("examples", "a1-u1-l1-example-1", "example"),
        ("conversations", "a1-u1-l1-conversation-1", "conversation"),
        ("exercises", "a1-u1-l1-exercise-1", "exercise"),
    ],
)
def test_malformed_child_identifier_generates_finding(
    collection,
    invalid_id,
    content_type,
):
    payload = deepcopy(build_candidate_payload())
    element = payload["candidate_unit"]["lessons"][0][collection][0]
    element["id"] = invalid_id

    if collection == "conversations":
        element["turns"][0]["id"] = invalid_id + "-t1"

    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [invalid_id]
    assert f"invalid {content_type} identifier" in findings[0].message

@pytest.mark.parametrize(
    ("collection", "content_type"),
    [
        ("examples", "example"),
        ("conversations", "conversation"),
        ("exercises", "exercise"),
    ],
)
def test_duplicate_child_identifier_generates_finding(
    collection,
    content_type,
):
    payload = deepcopy(build_candidate_payload())
    elements = payload["candidate_unit"]["lessons"][0][collection]
    duplicate = deepcopy(elements[0])

    if collection == "conversations":
        duplicate["turns"][0]["id"] = (
            duplicate["id"] + "-t2"
        )

    elements.append(duplicate)
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [duplicate["id"]]
    assert f"duplicate {content_type} identifier" in findings[0].message

@pytest.mark.parametrize(
    ("element_type", "invalid_id"),
    [
        ("turn", "a1-u1-l1-c1-turn-1"),
        ("choice", "a1-u1-l1-c1-option-one"),
    ],
)
def test_malformed_conversation_element_identifier_generates_finding(
    element_type,
    invalid_id,
):
    payload = deepcopy(build_candidate_payload())
    conversation = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]

    if element_type == "turn":
        conversation["turns"][0]["id"] = invalid_id
    else:
        conversation["turns"][0]["choices"] = [
            {
                "id": invalid_id,
                "en": "Hello.",
            }
        ]

    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [invalid_id]
    assert f"invalid {element_type} identifier" in findings[0].message

def test_main_validator_rejects_invalid_content_identifier():
    payload = deepcopy(build_candidate_payload())
    payload["candidate_unit"]["lessons"][0]["examples"][0][
        "id"
    ] = "a1-u1-l1-example-1"
    candidate = build_candidate(payload)

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "failed"
    assert any(
        finding.validator_id == "content_identifier_integrity"
        for finding in report.findings
    )
