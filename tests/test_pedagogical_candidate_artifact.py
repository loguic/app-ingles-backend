import json
from pathlib import Path

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    PedagogicalUnitSpecification,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT
    / "content"
    / "candidates"
    / "a1-u1"
    / "pedagogical-unit-candidate-v2.json"
)
SPECIFICATION_PATH = (
    ROOT
    / "content"
    / "candidates"
    / "a1-u1"
    / "pedagogical-unit-specification-v2.json"
)


def load_candidate() -> PedagogicalUnitCandidate:
    """Load the isolated candidate artifact from disk.

    Carga desde disco el artefacto candidato aislado.
    """
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    )


def test_stored_candidate_matches_approved_specification():
    """Keep the candidate tied to the approved specification.

    Mantiene la candidata vinculada con la especificación aprobada.
    """
    candidate = load_candidate()
    specification = PedagogicalUnitSpecification.model_validate(
        json.loads(SPECIFICATION_PATH.read_text(encoding="utf-8"))
    )

    assert candidate.specification == specification


def test_stored_candidate_report_matches_current_validation():
    """Reject a stale or invented stored validation report.

    Rechaza un informe almacenado obsoleto o inventado.
    """
    candidate = load_candidate()
    recalculated = validate_pedagogical_candidate(candidate)

    assert candidate.validation_report == recalculated
    assert recalculated.status == "pending"
    assert len(recalculated.findings) == 1

    finding = recalculated.findings[0]
    assert finding.validator_id == "skill_coverage_status"
    assert finding.severity == "warning"
    assert finding.reference_ids == ["a1_introduce_yourself"]


def test_stored_candidate_remains_pending_human_approval():
    """Prevent lesson completion from being treated as Skill mastery.

    Impide tratar la finalización como dominio de la Skill.
    """
    candidate = load_candidate()
    coverage = candidate.skill_coverage[0]
    lesson = candidate.candidate_unit.lessons[0]

    assert coverage.status == "pending_approval"
    assert candidate.pending_human_decisions
    assert lesson.experience is not None
    assert lesson.experience.completion_policy.required_evidence_ids == [
        "a1-u1-l1-ev2",
        "a1-u1-l1-ev3",
    ]
