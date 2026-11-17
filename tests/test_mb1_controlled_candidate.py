from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT
    / "content/candidates/a1-u2/pedagogical-unit-candidate-draft.json"
)
SKILL_ID = "mb1_ask_where_a_place_is_orally"
VISUAL_RESOURCE_ID = "visual.a1-u2-l1.station-restroom-help.v1"


def load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate_json(CANDIDATE_PATH.read_bytes())


def test_controlled_mb1_candidate_is_a_single_valid_draft():
    candidate = load_candidate()
    report = validate_pedagogical_candidate(candidate)

    assert candidate.validation_report == report
    assert report.status == "passed"
    assert candidate.candidate_unit.id == "a1-u2"
    assert len(candidate.candidate_unit.lessons) == 1
    assert candidate.pending_human_decisions
    assert any(
        "physical binding, manifest, acquisition, or activation" in decision
        for decision in candidate.pending_human_decisions
    )


def test_controlled_mb1_candidate_logically_binds_approved_visual_to_comprehension():
    candidate = load_candidate()
    lesson = candidate.candidate_unit.lessons[0]
    experience = lesson.experience

    assert experience is not None
    assert candidate.required_resource_ids == [VISUAL_RESOURCE_ID]
    assert len(experience.visual_contexts) == 1

    visual_context = experience.visual_contexts[0]
    assert visual_context.id == "a1-u2-l1-vc1"
    assert visual_context.resource_id == VISUAL_RESOURCE_ID
    assert visual_context.resource_type == "static_image"
    assert visual_context.stage_ids == ["a1-u2-l1-s1"]


def test_initial_comprehension_does_not_leak_the_correct_place_before_selection():
    lesson = load_candidate().candidate_unit.lessons[0]
    experience = lesson.experience
    conversations = {item.id: item for item in lesson.conversations}

    assert experience is not None
    comprehension_stage = next(
        stage for stage in experience.stages if stage.id == "a1-u2-l1-s1"
    )
    visual_context = experience.visual_contexts[0]
    initial_conversation = conversations["a1-u2-l1-c1"]
    pre_selection_text = " ".join(
        (
            lesson.title,
            lesson.objective,
            experience.mission.title,
            experience.mission.situation,
            experience.mission.observable_outcome,
            *experience.mission.success_criteria,
            comprehension_stage.instruction,
            visual_context.accessibility_label,
            initial_conversation.title,
            initial_conversation.context,
            *(turn.en for turn in initial_conversation.turns),
        )
    ).casefold()

    assert "toilet" not in pre_selection_text
    assert initial_conversation.turns[0].en == "Look at the station scene."


def test_controlled_mb1_candidate_keeps_the_approved_pedagogical_flow():
    lesson = load_candidate().candidate_unit.lessons[0]
    experience = lesson.experience

    assert experience is not None
    assert experience.contract_version == "3.0"
    assert experience.skill_ids == [SKILL_ID]
    assert [stage.id for stage in experience.stages] == [
        "a1-u2-l1-s1",
        "a1-u2-l1-s2",
        "a1-u2-l1-s3",
        "a1-u2-l1-s4",
        "a1-u2-l1-s5",
        "a1-u2-l1-s6",
        "a1-u2-l1-s7",
    ]
    assert [stage.type for stage in experience.stages] == [
        "comprehension",
        "language_support",
        "guided_production",
        "guided_production",
        "adaptive_feedback",
        "assisted_response",
        "evidence",
    ]

    evidence = {item.id: item for item in experience.evidence_definitions}
    assert evidence["a1-u2-l1-ev1"].measurement_mode == "binary"
    assert evidence["a1-u2-l1-ev1"].comprehension_exercise_id == (
        "a1-u2-l1-q1"
    )
    assert evidence["a1-u2-l1-ev4"].activity_id == "a1-u2-l1-c5"
    assert evidence["a1-u2-l1-ev4"].production_prompt_id == (
        "a1-u2-l1-c5-p1"
    )

    transfer_prompt = lesson.conversations[-1].turns[0].production_prompt
    assert transfer_prompt is not None
    assert transfer_prompt.production_function == "transfer"
    assert transfer_prompt.support_level == "none"
    assert transfer_prompt.visible_support == []


def test_controlled_mb1_candidate_requires_own_oral_attempts_with_less_support():
    lesson = load_candidate().candidate_unit.lessons[0]
    experience = lesson.experience
    conversations = {item.id: item for item in lesson.conversations}

    assert experience is not None
    assert conversations["a1-u2-l1-c1"].turns[0].en != (
        "Excuse me. Where is the toilet, please?"
    )

    initial_prompt = conversations["a1-u2-l1-c3"].turns[0].production_prompt
    retry_prompt = conversations["a1-u2-l1-c4"].turns[0].production_prompt
    transfer_prompt = conversations["a1-u2-l1-c5"].turns[0].production_prompt

    assert initial_prompt is not None
    assert retry_prompt is not None
    assert transfer_prompt is not None
    assert initial_prompt.accepted_modalities == ["voice"]
    assert retry_prompt.accepted_modalities == ["voice"]
    assert transfer_prompt.accepted_modalities == ["voice"]
    assert initial_prompt.support_level == "initial_word"
    assert retry_prompt.support_level == "none"
    assert retry_prompt.visible_support == []
    assert transfer_prompt.support_level == "none"
    assert transfer_prompt.visible_support == []
    assert experience.correction_policy is not None
    assert experience.correction_policy.max_guidance_items == 1
