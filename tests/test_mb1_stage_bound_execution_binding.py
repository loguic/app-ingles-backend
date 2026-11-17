"""Gate 2.03: explicit source binding, never automatic MB1 progression.

Gate 2.03: vinculo explicito; nunca avance MB1 automatico.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.services.direct_english_construction_execution_service as service
from app.schemas.content import Lesson
from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptStart,
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


@pytest.mark.parametrize(
    "evidence_id, function, conversation_id, support",
    [
        ("a1-u2-l1-ev2", "guided", "a1-u2-l1-c3", "initial_word"),
        ("a1-u2-l1-ev3", "expanded", "a1-u2-l1-c4", "none"),
        ("a1-u2-l1-ev4", "transfer", "a1-u2-l1-c5", "none"),
    ],
)
def test_stage_bound_binds_only_declared_oral_source(
    evidence_id, function, conversation_id, support,
):
    entries = service._execution_entries(lesson_with_profile(), evidence_id)
    assert list(entries) == [function]
    conversation, _turn, prompt, evidence = entries[function]
    assert evidence.id == evidence_id
    assert conversation.id == conversation_id
    assert prompt.id == evidence.production_prompt_id
    assert prompt.support_level == support


@pytest.mark.parametrize(
    "invalid_id",
    [None, "", "a1-u2-l1-ev1", "a1-u2-l1-c2", "a1-u1-l1-ev2"],
)
def test_stage_bound_rejects_implicit_or_wrong_source(invalid_id):
    with pytest.raises(service.DirectEnglishConstructionInvariantError):
        service._execution_entries(lesson_with_profile(), invalid_id)


def test_preparatory_capture_never_accredited_as_direct_oral_evidence():
    lesson = lesson_with_profile()
    all_entries = [
        service._execution_entries(lesson, item.id)
        for item in lesson.experience.evidence_definitions[1:]
    ]
    assert "a1-u2-l1-c2" not in {
        entry[0].id for group in all_entries for entry in group.values()
    }


def test_structurally_invalid_stage_bound_lesson_is_not_resolved():
    lesson = lesson_with_profile()
    lesson.experience.evidence_definitions[2].production_prompt_id = "unbound"
    with pytest.raises(
        service.DirectEnglishConstructionInvariantError,
        match="Stage-bound lesson content is invalid",
    ):
        service._execution_entries(lesson, "a1-u2-l1-ev3")


def test_opt_in_does_not_erase_legacy_v3_mapping():
    lesson = lesson_with_profile()
    assert service._uses_stage_bound_evidence_mapping(lesson)
    assert not service._uses_single_evidence_mapping(lesson)
    lesson.experience.direct_english_execution_profile = None
    assert not service._uses_stage_bound_evidence_mapping(lesson)
    assert service._uses_single_evidence_mapping(lesson)


def test_historical_three_capture_start_rejects_stage_bound_before_db(monkeypatch):
    lesson = lesson_with_profile()
    monkeypatch.setattr(service, "_resolve_lesson", lambda *args: lesson)
    command = DirectEnglishConstructionAttemptStart(
        attempt_id="isolated-1", user_id="u", level_id="A1",
        unit_id="a1-u2", lesson_id="a1-u2-l1",
        started_at=datetime(2026, 11, 15, tzinfo=UTC),
        experience_attempt_id="experience-1",
    )
    with pytest.raises(
        service.DirectEnglishConstructionInvariantError,
        match="single-capture execution is not yet enabled",
    ):
        service.start_direct_english_construction_attempt(command, db=None)


def test_stage_bound_transfer_selector_is_stable_for_explicit_evidence():
    lesson = lesson_with_profile()
    first = service.select_direct_english_transfer_variant(
        lesson, "attempt-transfer-1", "a1-u2-l1-ev4"
    )
    assert first == service.select_direct_english_transfer_variant(
        lesson, "attempt-transfer-1", "a1-u2-l1-ev4"
    )
    assert first[0] == "a1-u2-l1-c5-nearby-station"
    assert first[1].id == "a1-u2-l1-c5-tv1"


def test_stage_bound_transfer_selector_cannot_use_initial_evidence():
    with pytest.raises(
        service.DirectEnglishConstructionInvariantError,
        match="transfer prompt",
    ):
        service.select_direct_english_transfer_variant(
            lesson_with_profile(), "attempt-initial-1", "a1-u2-l1-ev2"
        )
