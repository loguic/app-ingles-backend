import json
from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_candidate() -> PedagogicalUnitCandidate:
    """Load the real pilot candidate. / Carga la candidata piloto real."""
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def test_valid_evaluation_plan_adds_no_integrity_finding():
    candidate = load_candidate()

    report = validate_pedagogical_candidate(candidate)

    evaluation_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "production_evaluation_integrity"
    ]

    assert evaluation_findings == []


def test_invalid_evaluation_plan_fails_normal_pipeline():
    candidate = load_candidate()
    candidate.evaluation_plans[0].criteria[
        0
    ].evidence_definition_id = "a1-u1-l1-ev999"

    report = validate_pedagogical_candidate(candidate)

    evaluation_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "production_evaluation_integrity"
    ]

    assert report.status == "failed"
    assert len(evaluation_findings) == 1
    assert "unknown evidence" in evaluation_findings[0].message
