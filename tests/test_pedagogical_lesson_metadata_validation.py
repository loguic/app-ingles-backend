from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_lesson_metadata_validation import (
    validate_lesson_metadata_integrity,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate() -> PedagogicalUnitCandidate:
    """Build one valid candidate for lesson metadata tests.

    Construye un candidato válido para pruebas de metadatos.
    """
    return PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )


def test_valid_metadata_does_not_generate_findings():
    candidate = build_candidate()

    findings = validate_lesson_metadata_integrity(candidate)

    assert findings == []


def test_missing_optional_objective_is_allowed():
    candidate = build_candidate()

    findings = validate_lesson_metadata_integrity(candidate)

    assert candidate.candidate_unit.lessons[0].objective is None
    assert findings == []


def test_blank_objective_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["objective"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_lesson_metadata_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "lesson_metadata_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "objective" in findings[0].message.lower()


def test_blank_vocabulary_entry_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["vocabulary"] = ["   "]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_lesson_metadata_integrity(candidate)

    assert len(findings) == 1
    assert "vocabulary" in findings[0].message.lower()
    assert "index 0" in findings[0].message.lower()


def test_equivalent_vocabulary_entries_generate_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["vocabulary"] = [
        "Hello there",
        "  hello   THERE  ",
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_lesson_metadata_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "vocabulary" in findings[0].message.lower()
    assert "0, 1" in findings[0].message


def test_blank_grammar_entry_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["grammar"] = ["   "]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_lesson_metadata_integrity(candidate)

    assert len(findings) == 1
    assert "grammar" in findings[0].message.lower()
    assert "index 0" in findings[0].message.lower()


def test_equivalent_grammar_entries_generate_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["grammar"] = [
        "Verb to be",
        "  verb   TO be  ",
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_lesson_metadata_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "grammar" in findings[0].message.lower()
    assert "0, 1" in findings[0].message


def test_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = deepcopy(candidate.model_dump(mode="json"))

    validate_lesson_metadata_integrity(candidate)

    assert candidate.model_dump(mode="json") == before

def test_main_validator_rejects_blank_objective():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["objective"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    metadata_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "lesson_metadata_integrity"
    ]
    assert report.status == "failed"
    assert len(metadata_findings) == 1
    assert metadata_findings[0].reference_ids == ["a1-u1-l1"]

