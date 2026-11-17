"""Fail-closed content validation for opt-in MB1 stage-bound evidence."""

import json
from pathlib import Path

import pytest

from app.schemas.content import Lesson
from app.services.direct_english_construction_content_validation import (
    validate_direct_english_construction_lesson,
)


CANDIDATE = (
    Path(__file__).resolve().parents[1]
    / "content/candidates/a1-u2/pedagogical-unit-candidate-draft.json"
)


def lesson_with_profile():
    raw = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    lesson = Lesson.model_validate(raw["candidate_unit"]["lessons"][0])
    lesson.experience.direct_english_execution_profile = "stage_bound_evidence_v1"
    return lesson


def test_mb1_stage_bound_candidate_passes_structural_validation():
    validate_direct_english_construction_lesson(lesson_with_profile())


def test_unmarked_mb1_still_fails_historical_v3_validation():
    lesson = lesson_with_profile()
    lesson.experience.direct_english_execution_profile = None
    with pytest.raises(ValueError, match="exactly four canonical evidence"):
        validate_direct_english_construction_lesson(lesson)


@pytest.mark.parametrize("mutation, message", [
    ("wrong_evidence_type", "evidence types"),
    ("wrong_evidence_stage", "exact stages"),
    ("wrong_evidence_prompt", "exact prompt"),
    ("wrong_evidence_function", "exact prompt"),
    ("missing_qualitative_review", "qualitative review"),
    ("text_as_oral_evidence", "text accreditation"),
    ("retry_with_cue", "no answer cues"),
    ("transfer_with_cue", "no answer cues"),
    ("wrong_transfer_context", "context must differ"),
    ("unbound_capture", "unbound production"),
    ("feedback_activity", "separately recorded event"),
    ("wrong_practice", "remain scaffolded"),
    ("missing_question", "question and scene"),
    ("wrong_stage_order", "seven ordered stages"),
    ("bad_guidance_limit", "bounded guidance policy"),
    ("missing_required_evidence", "ordered mandatory evidence"),
])
def test_stage_bound_profile_rejects_contract_violations(mutation, message):
    lesson = lesson_with_profile()
    exp = lesson.experience
    convs = {c.id: c for c in lesson.conversations}
    evidence = exp.evidence_definitions
    if mutation == "wrong_evidence_type":
        evidence[2].evidence_type = "conversation_completion"
    elif mutation == "wrong_evidence_stage":
        evidence[2].stage_id = exp.stages[3].id
    elif mutation == "wrong_evidence_prompt":
        evidence[2].production_prompt_id = "invalid"
    elif mutation == "wrong_evidence_function":
        convs["a1-u2-l1-c4"].turns[0].production_prompt.production_function = "guided"
    elif mutation == "missing_qualitative_review":
        evidence[1].external_review_requirements = []
    elif mutation == "text_as_oral_evidence":
        convs["a1-u2-l1-c3"].turns[0].production_prompt.accepted_modalities = ["voice", "text"]
    elif mutation == "retry_with_cue":
        convs["a1-u2-l1-c4"].turns[0].production_prompt.visible_support = ["Where"]
    elif mutation == "transfer_with_cue":
        convs["a1-u2-l1-c5"].turns[0].production_prompt.visible_support = ["exit"]
    elif mutation == "wrong_transfer_context":
        convs["a1-u2-l1-c5"].context = convs["a1-u2-l1-c3"].context
    elif mutation == "unbound_capture":
        convs["a1-u2-l1-c1"].turns[0].production_prompt = (
            convs["a1-u2-l1-c3"].turns[0].production_prompt.model_copy(deep=True)
        )
        convs["a1-u2-l1-c1"].turns[0].production_prompt.id = "extra-id"
    elif mutation == "feedback_activity":
        exp.stages[4].activity_ids.append("a1-u2-l1-c2")
    elif mutation == "wrong_practice":
        convs["a1-u2-l1-c2"].turns[0].production_prompt.support_level = "none"
    elif mutation == "missing_question":
        evidence[0].comprehension_exercise_id = "nonexistent"
    elif mutation == "wrong_stage_order":
        exp.stages[3].type = "applied_conversation"
    elif mutation == "bad_guidance_limit":
        exp.correction_policy.max_guidance_items = 2
    elif mutation == "missing_required_evidence":
        exp.completion_policy.required_evidence_ids.pop()
    else:
        raise AssertionError("unexpected test mutation")
    with pytest.raises(ValueError, match=message):
        validate_direct_english_construction_lesson(lesson)
