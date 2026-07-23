from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_unit_lesson_structure_validation import (
    validate_unit_lesson_structure,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate() -> PedagogicalUnitCandidate:
    """Build one valid candidate for structural integrity tests.

    Construye un candidato válido para pruebas de integridad estructural.
    """
    return PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )


def test_valid_unit_structure_does_not_generate_findings():
    candidate = build_candidate()

    findings = validate_unit_lesson_structure(candidate)

    assert findings == []


def test_blank_unit_title_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["title"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_unit_lesson_structure(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == (
        "unit_lesson_structure_integrity"
    )
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1"]
    assert "title" in findings[0].message.lower()


def test_unit_without_lessons_generates_direct_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"] = []
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_unit_lesson_structure(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == (
        "unit_lesson_structure_integrity"
    )
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1"]
    assert "at least one lesson" in findings[0].message.lower()


def test_blank_lesson_title_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["title"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_unit_lesson_structure(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == (
        "unit_lesson_structure_integrity"
    )
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "title" in findings[0].message.lower()


def test_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = deepcopy(candidate.model_dump(mode="json"))

    validate_unit_lesson_structure(candidate)

    assert candidate.model_dump(mode="json") == before


def test_main_validator_rejects_blank_lesson_title():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["title"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    structure_findings = [
        finding
        for finding in report.findings
        if finding.validator_id
        == "unit_lesson_structure_integrity"
    ]
    assert report.status == "failed"
    assert len(structure_findings) == 1
    assert structure_findings[0].reference_ids == ["a1-u1-l1"]
