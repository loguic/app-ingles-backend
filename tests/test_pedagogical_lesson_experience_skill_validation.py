from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_lesson_experience_skill_validation import (
    validate_lesson_experience_skills,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_lesson_experience_schema import (
    build_experience_payload,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate(payload=None) -> PedagogicalUnitCandidate:
    """Build one candidate for LessonExperience Skill tests.

    Construye un candidato para pruebas de Skills de LessonExperience.
    """
    source = payload if payload is not None else build_candidate_payload()
    return PedagogicalUnitCandidate.model_validate(source)


def add_valid_experience(payload: dict) -> dict:
    """Attach one externally coherent LessonExperience.

    Añade una LessonExperience coherente con los recursos de la lección.
    """
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["experience"] = build_experience_payload()
    return payload


def test_legacy_candidate_without_experience_generates_no_findings():
    candidate = build_candidate()

    findings = validate_lesson_experience_skills(candidate)

    assert findings == []


def test_valid_experience_skills_generate_no_findings():
    payload = add_valid_experience(build_candidate_payload())
    candidate = build_candidate(payload)

    findings = validate_lesson_experience_skills(candidate)

    assert findings == []


def test_unknown_experience_skill_generates_finding():
    payload = add_valid_experience(build_candidate_payload())
    experience = payload["candidate_unit"]["lessons"][0]["experience"]
    experience["skill_ids"].append("a1_unknown_skill")
    candidate = build_candidate(payload)

    findings = validate_lesson_experience_skills(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "lesson_experience_skills"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == [
        "a1-u1-l1",
        "a1_unknown_skill",
    ]
    assert "unknown skill_id" in findings[0].message.lower()


def test_main_validator_rejects_unknown_experience_skill():
    payload = add_valid_experience(deepcopy(build_candidate_payload()))
    experience = payload["candidate_unit"]["lessons"][0]["experience"]
    experience["skill_ids"].append("a1_unknown_skill")
    candidate = build_candidate(payload)

    report = validate_pedagogical_candidate(candidate)
    findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "lesson_experience_skills"
    ]

    assert report.status == "failed"
    assert len(findings) == 1
