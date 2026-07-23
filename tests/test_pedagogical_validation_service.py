from copy import deepcopy

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


def build_candidate_payload() -> dict:
    """Return one candidate with every required Skill stage covered.

    Devuelve un candidato con todas las etapas obligatorias cubiertas.
    """
    return {
        "specification": {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Meeting people",
            "learner_outcome": (
                "Introduce yourself in a short conversation."
            ),
            "skills": [
                {
                    "id": "a1_introduce_yourself",
                    "description": (
                        "Introduce yourself using name and origin."
                    ),
                    "required_stages": [
                        "introduce",
                        "practice",
                        "apply",
                        "evaluate",
                        "consolidate",
                    ],
                }
            ],
            "required_evidence": [
                "Complete a guided introduction."
            ],
            "lesson_scope": [
                "Greetings and personal introductions."
            ],
            "language_scope": ["My name is...", "I am from..."],
            "pronunciation_scope": [
                "Sentence stress in introductions."
            ],
            "content_constraints": ["Use only A1 language."],
            "technical_constraints": [
                "Reuse current conversation contracts."
            ],
            "acceptance_criteria": [
                "The learner completes the introduction."
            ],
        },
        "candidate_unit": {
            "id": "a1-u1",
            "title": "Meeting people",
            "lessons": [],
        },
        "skill_coverage": [
            {
                "skill_id": "a1_introduce_yourself",
                "introduced_in_lesson_id": "a1-u1-l1",
                "practice_activity_ids": ["a1-u1-l1-e1"],
                "application_activity_ids": ["a1-u1-l1-c1"],
                "evaluation_evidence_ids": ["a1-u1-l1-q1"],
                "consolidation_activity_ids": ["a1-u1-l2-c1"],
                "modalities": ["listening", "speaking"],
                "status": "complete",
            }
        ],
        "validation_report": {
            "status": "pending",
            "findings": [],
        },
        "proposed_change_summary": [
            "Add the candidate after human approval."
        ],
    }


def test_complete_required_skill_stages_pass_validation():
    """Pass when every required Skill stage has evidence.

    Aprueba cuando cada etapa obligatoria tiene evidencia.
    """
    candidate = PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "passed"
    assert report.findings == []


@pytest.mark.parametrize(
    ("field", "empty_value", "stage"),
    [
        ("introduced_in_lesson_id", None, "introduce"),
        ("practice_activity_ids", [], "practice"),
        ("application_activity_ids", [], "apply"),
        ("evaluation_evidence_ids", [], "evaluate"),
        ("consolidation_activity_ids", [], "consolidate"),
    ],
)
def test_missing_required_stage_fails_validation(
    field,
    empty_value,
    stage,
):
    """Fail reproducibly when one mandatory stage lacks evidence.

    Falla de forma reproducible si una etapa obligatoria no tiene evidencia.
    """
    payload = deepcopy(build_candidate_payload())
    payload["skill_coverage"][0][field] = empty_value
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "failed"
    assert len(report.findings) == 1

    finding = report.findings[0]
    assert finding.validator_id == "skill_stage_coverage"
    assert finding.severity == "error"
    assert finding.reference_ids == ["a1_introduce_yourself"]
    assert finding.message == (
        "Skill a1_introduce_yourself "
        f"lacks required stage: {stage}."
    )


def test_validation_recalculates_candidate_report():
    """Return a new report instead of trusting the stored candidate report.

    Devuelve un informe nuevo sin confiar en el informe almacenado.
    """
    candidate = PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )

    report = validate_pedagogical_candidate(candidate)

    assert candidate.validation_report.status == "pending"
    assert report.status == "passed"
    assert report is not candidate.validation_report
