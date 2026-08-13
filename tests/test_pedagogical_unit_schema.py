import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    PedagogicalUnitSpecification,
    SkillCoverage,
    SkillSpecification,
    ValidationReport,
)


def test_valid_skill_specification_is_accepted():
    """Accept one measurable Skill with stable stages.

    Acepta un Skill medible con etapas estables.
    """
    skill = SkillSpecification.model_validate(
        {
            "id": "a1_introduce_yourself",
            "description": "Introduce yourself using name and origin.",
            "required_stages": ["introduce", "practice", "evaluate"],
        }
    )

    assert skill.id == "a1_introduce_yourself"
    assert skill.required_stages[-1] == "evaluate"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {
                "id": "A1-invalid-skill",
                "description": "Invalid identifier.",
                "required_stages": ["practice"],
            },
            "string_pattern_mismatch",
        ),
        (
            {
                "id": "a1_empty_description",
                "description": "",
                "required_stages": ["practice"],
            },
            "string_too_short",
        ),
        (
            {
                "id": "a1_missing_stages",
                "description": "Skill without required coverage.",
                "required_stages": [],
            },
            "too_short",
        ),
        (
            {
                "id": "a1_unknown_stage",
                "description": "Skill with unsupported stage.",
                "required_stages": ["master"],
            },
            "literal_error",
        ),
    ],
)
def test_invalid_skill_specifications_are_rejected(payload, message):
    """Reject malformed or incomplete Skill contracts.

    Rechaza contratos de Skill incompletos o mal formados.
    """
    with pytest.raises(ValidationError, match=message):
        SkillSpecification.model_validate(payload)

def test_valid_skill_coverage_is_accepted():
    """Accept observable and traceable Skill coverage.

    Acepta una cobertura de Skill observable y trazable.
    """
    coverage = SkillCoverage.model_validate(
        {
            "skill_id": "a1_introduce_yourself",
            "introduced_in_lesson_id": "a1-u1-l1",
            "practice_activity_ids": ["a1-u1-l1-e1"],
            "application_activity_ids": ["a1-u1-l1-c1"],
            "evaluation_evidence_ids": ["a1-u1-l1-q1"],
            "consolidation_activity_ids": ["a1-u1-l2-c1"],
            "modalities": ["listening", "speaking", "pronunciation"],
            "status": "complete",
        }
    )

    assert coverage.skill_id == "a1_introduce_yourself"
    assert coverage.status == "complete"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("skill_id", "A1-invalid-skill", "string_pattern_mismatch"),
        ("modalities", ["conversation"], "literal_error"),
        ("status", "approved", "literal_error"),
    ],
)
def test_invalid_skill_coverage_values_are_rejected(field, value, message):
    """Reject unsupported coverage identifiers and values.

    Rechaza identificadores y valores de cobertura no permitidos.
    """
    payload = {
        "skill_id": "a1_introduce_yourself",
        "modalities": ["speaking"],
        "status": "incomplete",
    }
    payload[field] = value

    with pytest.raises(ValidationError, match=message):
        SkillCoverage.model_validate(payload)

def test_valid_pedagogical_unit_specification_is_accepted():
    """Accept one complete and approved unit specification.

    Acepta una especificación completa y aprobada de unidad.
    """
    specification = PedagogicalUnitSpecification.model_validate(
        {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Meeting people",
            "learner_outcome": "Introduce yourself in a short conversation.",
            "skills": [
                {
                    "id": "a1_introduce_yourself",
                    "description": "Introduce yourself using name and origin.",
                    "required_stages": ["introduce", "practice", "evaluate"],
                }
            ],
            "required_evidence": ["Complete a guided introduction."],
            "lesson_scope": ["Greetings and personal introductions."],
            "language_scope": ["My name is...", "I am from..."],
            "pronunciation_scope": ["Sentence stress in introductions."],
            "content_constraints": ["Use only A1 language."],
            "technical_constraints": ["Reuse current conversation contracts."],
            "acceptance_criteria": ["The learner completes the introduction."],
        }
    )

    assert specification.unit_id == "a1-u1"
    assert specification.skills[0].id == "a1_introduce_yourself"

def test_unit_id_must_match_cefr_level():
    """Reject a unit identifier that conflicts with its CEFR level.

    Rechaza un identificador de unidad incompatible con su nivel CEFR.
    """
    payload = {
        "unit_id": "a1-u1",
        "level": "A2",
        "title": "Invalid level",
        "learner_outcome": "Complete an observable task.",
        "skills": [
            {
                "id": "a1_introduce_yourself",
                "description": "Introduce yourself.",
                "required_stages": ["practice"],
            }
        ],
        "required_evidence": ["Observable evidence."],
        "lesson_scope": ["Controlled scope."],
        "language_scope": ["Controlled language."],
        "pronunciation_scope": ["Controlled pronunciation."],
        "content_constraints": ["Controlled content."],
        "technical_constraints": ["Reuse existing contracts."],
        "acceptance_criteria": ["Complete the task."],
    }

    with pytest.raises(ValidationError, match="unit_id prefix must match level"):
        PedagogicalUnitSpecification.model_validate(payload)

@pytest.mark.parametrize(
    "payload",
    [
        {"status": "passed", "findings": []},
        {
            "status": "failed",
            "findings": [
                {
                    "validator_id": "skill_coverage",
                    "severity": "error",
                    "message": "Required Skill coverage is incomplete.",
                }
            ],
        },
        {"status": "pending", "findings": []},
    ],
)
def test_coherent_validation_reports_are_accepted(payload):
    """Accept validation reports with coherent status and findings.

    Acepta informes con estado y hallazgos coherentes.
    """
    report = ValidationReport.model_validate(payload)

    assert report.status == payload["status"]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {
                "status": "passed",
                "findings": [
                    {
                        "validator_id": "skill_coverage",
                        "severity": "error",
                        "message": "Coverage failed.",
                    }
                ],
            },
            "passed validation reports cannot contain errors",
        ),
        (
            {
                "status": "failed",
                "findings": [
                    {
                        "validator_id": "content_limits",
                        "severity": "warning",
                        "message": "Review recommended.",
                    }
                ],
            },
            "failed validation reports require an error",
        ),
    ],
)
def test_incoherent_validation_reports_are_rejected(payload, message):
    """Reject contradictory validation reports.

    Rechaza informes de validación contradictorios.
    """
    with pytest.raises(ValidationError, match=message):
        ValidationReport.model_validate(payload)

def build_valid_candidate_payload() -> dict:
    """Return one valid isolated pedagogical unit candidate.

    Devuelve un paquete candidato pedagógico válido y aislado.
    """
    return {
        "specification": {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Meeting people",
            "learner_outcome": "Introduce yourself in a short conversation.",
            "skills": [
                {
                    "id": "a1_introduce_yourself",
                    "description": "Introduce yourself using name and origin.",
                    "required_stages": ["introduce", "practice", "evaluate"],
                }
            ],
            "required_evidence": ["Complete a guided introduction."],
            "lesson_scope": ["Greetings and personal introductions."],
            "language_scope": ["My name is...", "I am from..."],
            "pronunciation_scope": ["Sentence stress in introductions."],
            "content_constraints": ["Use only A1 language."],
            "technical_constraints": ["Reuse current conversation contracts."],
            "acceptance_criteria": ["The learner completes the introduction."],
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
                "modalities": ["listening", "speaking"],
                "status": "complete",
            }
        ],
        "validation_report": {
            "status": "passed",
            "findings": [],
        },
        "proposed_change_summary": [
            "Add the approved A1-U1 candidate after human review."
        ],
    }

def test_valid_pedagogical_unit_candidate_is_accepted():
    """Accept one coherent isolated candidate package.

    Acepta un paquete candidato aislado y coherente.
    """
    candidate = PedagogicalUnitCandidate.model_validate(
        build_valid_candidate_payload()
    )

    assert candidate.candidate_unit.id == candidate.specification.unit_id
    assert candidate.skill_coverage[0].status == "complete"
    assert candidate.validation_report.status == "passed"
    assert candidate.lesson_capability_plans == []
    assert candidate.model_dump()["lesson_capability_plans"] == []


def add_candidate_lesson(payload: dict, lesson_id: str) -> None:
    """Add one minimal lesson to a candidate payload.

    Añade una lección mínima al paquete de una candidata.
    """
    payload["candidate_unit"]["lessons"].append(
        {
            "id": lesson_id,
            "title": "Capability plan lesson",
        }
    )


def capability_plan(lesson_id: str) -> dict:
    """Return one valid capability plan payload.

    Devuelve un paquete válido de plan de capacidades.
    """
    return {
        "lesson_id": lesson_id,
        "claims": [
            {
                "skill_id": "a1_introduce_yourself",
                "preparation_state": "PRACTICE_AVAILABLE",
                "artifact_ids": [lesson_id + "-q1"],
            }
        ],
        "prerequisites": [
            {
                "required_skill_id": "a1_introduce_yourself",
                "required_state": "INSTRUCTION_AVAILABLE",
                "reason": "The practice requires prior instruction.",
            }
        ],
    }


def test_candidate_accepts_capability_plan_for_existing_lesson():
    """Accept one capability plan owned by an existing lesson.

    Acepta un plan de capacidades de una lección existente.
    """
    payload = build_valid_candidate_payload()
    add_candidate_lesson(payload, "a1-u1-l1")
    payload["lesson_capability_plans"] = [capability_plan("a1-u1-l1")]

    candidate = PedagogicalUnitCandidate.model_validate(payload)

    assert candidate.lesson_capability_plans[0].lesson_id == "a1-u1-l1"
    assert candidate.lesson_capability_plans[0].claims[0].skill_id == (
        "a1_introduce_yourself"
    )
    assert candidate.lesson_capability_plans[0].prerequisites[0].reason == (
        "The practice requires prior instruction."
    )


def test_candidate_accepts_distinct_capability_plan_lessons():
    """Accept distinct plans for distinct existing lessons.

    Acepta planes distintos para lecciones existentes distintas.
    """
    payload = build_valid_candidate_payload()
    add_candidate_lesson(payload, "a1-u1-l1")
    add_candidate_lesson(payload, "a1-u1-l2")
    payload["lesson_capability_plans"] = [
        capability_plan("a1-u1-l1"),
        capability_plan("a1-u1-l2"),
    ]

    candidate = PedagogicalUnitCandidate.model_validate(payload)

    assert [
        plan.lesson_id for plan in candidate.lesson_capability_plans
    ] == ["a1-u1-l1", "a1-u1-l2"]


def test_candidate_rejects_duplicate_capability_plan_lesson():
    """Reject two capability plans owned by the same lesson.

    Rechaza dos planes de capacidades de la misma lección.
    """
    payload = build_valid_candidate_payload()
    add_candidate_lesson(payload, "a1-u1-l1")
    payload["lesson_capability_plans"] = [
        capability_plan("a1-u1-l1"),
        capability_plan("a1-u1-l1"),
    ]

    with pytest.raises(
        ValidationError,
        match="Lesson capability plan lesson IDs must be unique",
    ):
        PedagogicalUnitCandidate.model_validate(payload)


def test_candidate_rejects_unknown_capability_plan_lesson():
    """Reject a capability plan owned by an unknown lesson.

    Rechaza un plan de capacidades de una lección desconocida.
    """
    payload = build_valid_candidate_payload()
    payload["lesson_capability_plans"] = [capability_plan("a1-u1-l9")]

    with pytest.raises(
        ValidationError,
        match="Lesson capability plans reference unknown lessons: a1-u1-l9",
    ):
        PedagogicalUnitCandidate.model_validate(payload)


def test_candidate_rejects_invalid_nested_capability_contract():
    """Preserve nested claim and prerequisite validation in candidates.

    Conserva la validación anidada de claims y prerrequisitos en candidatas.
    """
    payload = build_valid_candidate_payload()
    add_candidate_lesson(payload, "a1-u1-l1")
    plan = capability_plan("a1-u1-l1")
    plan["claims"][0]["artifact_ids"] = []
    plan["prerequisites"][0]["reason"] = "   "
    payload["lesson_capability_plans"] = [plan]

    with pytest.raises(ValidationError) as captured:
        PedagogicalUnitCandidate.model_validate(payload)

    errors = captured.value.errors()
    assert any(error["loc"][-1] == "artifact_ids" for error in errors)
    assert any(
        "Prerequisite reason cannot be blank" in error["msg"]
        for error in errors
    )

@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda payload: payload["candidate_unit"].update(id="a1-u2"),
            "candidate unit ID must match specification unit_id",
        ),
        (
            lambda payload: payload["skill_coverage"].append(
                payload["skill_coverage"][0].copy()
            ),
            "Skill coverage IDs must be unique",
        ),
        (
            lambda payload: payload["specification"]["skills"].append(
                {
                    "id": "a1_greetings_basic",
                    "description": "Use basic greetings appropriately.",
                    "required_stages": ["introduce", "practice", "evaluate"],
                }
            ),
            "Missing Skill coverage",
        ),
        (
            lambda payload: payload["skill_coverage"].append(
                {
                    "skill_id": "a1_unknown_skill",
                    "modalities": ["speaking"],
                    "status": "incomplete",
                }
            ),
            "Unknown Skill coverage",
        ),
    ],
)
def test_incoherent_pedagogical_unit_candidates_are_rejected(
    mutation,
    message,
):
    """Reject candidates that conflict with their specification.

    Rechaza candidatos incompatibles con su especificación.
    """
    payload = build_valid_candidate_payload()
    mutation(payload)

    with pytest.raises(ValidationError, match=message):
        PedagogicalUnitCandidate.model_validate(payload)
