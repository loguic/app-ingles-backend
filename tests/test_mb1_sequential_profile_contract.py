"""MB1 opt-in profile is explicit; legacy 3.0 remains byte-compatible in dumps."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.content import LessonExperience


CANDIDATE = (
    Path(__file__).resolve().parents[1]
    / "content/candidates/a1-u2/pedagogical-unit-candidate-draft.json"
)


def candidate_experience_data():
    raw = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    return raw["candidate_unit"]["lessons"][0]["experience"]


def test_legacy_v3_has_no_profile_in_default_serialization():
    original = candidate_experience_data()
    lesson = LessonExperience.model_validate(original)
    assert lesson.direct_english_execution_profile is None
    assert "direct_english_execution_profile" not in original
    assert "direct_english_execution_profile" not in lesson.model_dump()
    assert "direct_english_execution_profile" not in lesson.model_dump(mode="json")


def test_sequential_profile_is_explicit_and_roundtrips():
    raw = candidate_experience_data()
    raw["direct_english_execution_profile"] = "stage_bound_evidence_v1"
    lesson = LessonExperience.model_validate(raw)
    assert lesson.direct_english_execution_profile == "stage_bound_evidence_v1"
    encoded = lesson.model_dump(mode="json")
    assert encoded["direct_english_execution_profile"] == "stage_bound_evidence_v1"
    assert LessonExperience.model_validate(encoded).direct_english_execution_profile == "stage_bound_evidence_v1"


@pytest.mark.parametrize(
    "change",
    [
        {"contract_version": "2.0"},
        {"pedagogical_method": "short_connected_exchange"},
    ],
)
def test_sequential_profile_rejects_wrong_contract_or_method(change):
    raw = candidate_experience_data()
    raw.update(change)
    raw["direct_english_execution_profile"] = "stage_bound_evidence_v1"
    with pytest.raises(ValidationError, match="Sequential Direct English profile requires"):
        LessonExperience.model_validate(raw)


def test_unknown_execution_profile_is_rejected():
    raw = candidate_experience_data()
    raw["direct_english_execution_profile"] = "unknown_profile"
    with pytest.raises(ValidationError):
        LessonExperience.model_validate(raw)
