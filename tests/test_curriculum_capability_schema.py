import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import (
    LessonCapabilityClaim,
    LessonCapabilityPlan,
    SkillPrerequisite,
)


def test_valid_lesson_capability_plan_is_accepted():
    """Accept claims and prerequisites owned by one lesson plan.

    Acepta claims y prerrequisitos pertenecientes a un plan de lección.
    """
    plan = LessonCapabilityPlan.model_validate(
        {
            "lesson_id": "a1-u1-l2",
            "claims": [
                {
                    "skill_id": "respond_to_personal_question",
                    "preparation_state": "PRACTICE_AVAILABLE",
                    "artifact_ids": ["a1-u1-l2-s3", "a1-u1-l2-c1"],
                }
            ],
            "prerequisites": [
                {
                    "required_skill_id": "understand_personal_question",
                    "required_state": "INSTRUCTION_AVAILABLE",
                    "before_stage_id": "a1-u1-l2-s3",
                    "reason": "The response stage requires prior instruction.",
                }
            ],
        }
    )

    assert plan.claims[0].preparation_state == "PRACTICE_AVAILABLE"
    assert plan.prerequisites[0].before_stage_id == "a1-u1-l2-s3"


@pytest.mark.parametrize(
    "state",
    [
        "EXPOSURE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "PRACTICE_AVAILABLE",
        "EVIDENCE_GATE_AVAILABLE",
    ],
)
def test_claim_accepts_each_curriculum_preparation_state(state):
    """Accept exactly each canonical curriculum preparation state.

    Acepta cada estado canónico de preparación curricular.
    """
    claim = LessonCapabilityClaim.model_validate(
        {
            "skill_id": "produce_contextual_response",
            "preparation_state": state,
            "artifact_ids": ["a1-u1-l1-s1"],
        }
    )

    assert claim.preparation_state == state


def test_claim_rejects_unknown_preparation_state():
    """Reject preparation states outside the curricular contract.

    Rechaza estados ajenos al contrato curricular.
    """
    with pytest.raises(ValidationError, match="literal_error"):
        LessonCapabilityClaim.model_validate(
            {
                "skill_id": "produce_contextual_response",
                "preparation_state": "MASTERED",
                "artifact_ids": ["a1-u1-l1-s1"],
            }
        )


@pytest.mark.parametrize("field", ["skill_id", "required_skill_id"])
def test_capability_contracts_reject_invalid_skill_ids(field):
    """Apply the existing Skill identifier pattern to both contracts.

    Aplica el patrón existente de Skill a ambos contratos.
    """
    if field == "skill_id":
        contract = LessonCapabilityClaim
        payload = {
            "skill_id": "Invalid-Skill",
            "preparation_state": "EXPOSURE_AVAILABLE",
            "artifact_ids": ["a1-u1-l1-s1"],
        }
    else:
        contract = SkillPrerequisite
        payload = {
            "required_skill_id": "Invalid-Skill",
            "required_state": "EXPOSURE_AVAILABLE",
            "reason": "Prior contextual presentation is required.",
        }

    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        contract.model_validate(payload)


@pytest.mark.parametrize(
    ("artifact_ids", "message"),
    [
        ([], "too_short"),
        (["a1-u1-l1-s1", "   "], "Claim artifact IDs cannot be blank"),
        (
            ["a1-u1-l1-s1", "a1-u1-l1-s1"],
            "Claim artifact IDs must be unique",
        ),
    ],
)
def test_claim_rejects_invalid_artifact_ids(artifact_ids, message):
    """Reject missing, blank or duplicate supporting artifacts.

    Rechaza artefactos justificativos ausentes, vacíos o duplicados.
    """
    with pytest.raises(ValidationError, match=message):
        LessonCapabilityClaim.model_validate(
            {
                "skill_id": "produce_contextual_response",
                "preparation_state": "EXPOSURE_AVAILABLE",
                "artifact_ids": artifact_ids,
            }
        )


@pytest.mark.parametrize("reason", ["", "   "])
def test_prerequisite_rejects_blank_reason(reason):
    """Reject an empty or whitespace-only prerequisite reason.

    Rechaza una razón de prerrequisito vacía o formada por espacios.
    """
    with pytest.raises(ValidationError, match="cannot be blank"):
        SkillPrerequisite.model_validate(
            {
                "required_skill_id": "understand_personal_question",
                "required_state": "PRACTICE_AVAILABLE",
                "reason": reason,
            }
        )


def test_prerequisite_allows_omitted_before_stage_id():
    """Allow lesson-entry prerequisites without a stage target.

    Permite prerrequisitos de entrada sin una etapa objetivo.
    """
    prerequisite = SkillPrerequisite.model_validate(
        {
            "required_skill_id": "understand_personal_question",
            "required_state": "PRACTICE_AVAILABLE",
            "reason": "The lesson consumes this prior preparation.",
        }
    )

    assert prerequisite.before_stage_id is None


def test_lesson_capability_plan_allows_empty_owned_collections():
    """Keep claims and prerequisites as explicit lesson-owned collections.

    Mantiene claims y prerrequisitos como colecciones propias de la lección.
    """
    plan = LessonCapabilityPlan.model_validate({"lesson_id": "a1-u1-l1"})

    assert plan.claims == []
    assert plan.prerequisites == []
