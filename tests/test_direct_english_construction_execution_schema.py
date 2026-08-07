from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptFinalize,
    DirectEnglishConstructionAttemptStart,
    DirectEnglishConstructionOrientationCreate,
    DirectEnglishConstructionOrientationRecord,
    DirectEnglishConstructionProductionCapture,
    DirectEnglishConstructionRetryPreparation,
    DirectEnglishConstructionRetryPreparationRequest,
)


def submission_payload(function: str) -> dict:
    return {
        "user_id": "b180-user",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": f"a1-u1-l1-c-direct-{function}",
        "productions": [
            {
                "prompt_id": f"a1-u1-l1-p-{function}",
                "turn_id": f"a1-u1-l1-c-direct-{function}-t2",
                "modality": "voice",
                "audio_reference": f"audio/{function}.wav",
            }
        ],
    }


def capture_payload(function: str) -> dict:
    payload = {
        "production_function": function,
        "submission": submission_payload(function),
        "support_used": {
            "guided": "anchors",
            "expanded": "initial_word",
            "transfer": "none",
        }[function],
    }
    if function == "transfer":
        payload["transfer_variant_id"] = "transfer-v1"
    return payload


def test_start_requires_explicit_aware_timestamp():
    with pytest.raises(ValidationError, match="timezone information"):
        DirectEnglishConstructionAttemptStart(
            attempt_id="attempt-1",
            user_id="b180-user",
            level_id="A1",
            unit_id="a1-u1",
            lesson_id="a1-u1-l1",
            started_at=datetime(2026, 8, 7, 10, 0),
        )


def test_finalize_requires_exactly_three_unique_functions():
    payload = {
        "attempt_id": "attempt-1",
        "captures": [
            capture_payload("guided"),
            capture_payload("guided"),
            capture_payload("transfer"),
        ],
        "finalized_at": datetime.now(UTC),
    }
    with pytest.raises(ValidationError, match="functions must be unique"):
        DirectEnglishConstructionAttemptFinalize.model_validate(payload)


def test_finalize_accepts_input_in_any_order():
    command = DirectEnglishConstructionAttemptFinalize(
        attempt_id="attempt-1",
        captures=[
            DirectEnglishConstructionProductionCapture.model_validate(
                capture_payload("transfer")
            ),
            DirectEnglishConstructionProductionCapture.model_validate(
                capture_payload("guided")
            ),
            DirectEnglishConstructionProductionCapture.model_validate(
                capture_payload("expanded")
            ),
        ],
        finalized_at=datetime.now(UTC),
    )

    assert {item.production_function for item in command.captures} == {
        "guided",
        "expanded",
        "transfer",
    }


def test_transfer_capture_requires_variant_and_other_functions_forbid_it():
    missing = capture_payload("transfer")
    missing.pop("transfer_variant_id")
    with pytest.raises(ValidationError, match="requires transfer_variant_id"):
        DirectEnglishConstructionProductionCapture.model_validate(missing)

    crossed = capture_payload("guided")
    crossed["transfer_variant_id"] = "transfer-v1"
    with pytest.raises(ValidationError, match="Only transfer"):
        DirectEnglishConstructionProductionCapture.model_validate(crossed)


def test_capture_does_not_duplicate_modality_outside_production():
    fields = DirectEnglishConstructionProductionCapture.model_fields

    assert "modality" not in fields
    assert "modality_used" not in fields
    assert "requested_support" not in fields


def orientation_payload(**updates):
    payload = {
        "orientation_id": "orientation-1",
        "attempt_id": "attempt-1",
        "production_function": "guided",
        "priority": "relevance",
        "guidance_text": "Answer the question before adding detail.",
        "source_type": "human",
        "source_id": "teacher-1",
        "source_version": None,
        "created_at": datetime.now(UTC),
    }
    payload.update(updates)
    return payload


def test_orientation_accepts_human_and_versioned_external_sources():
    human = DirectEnglishConstructionOrientationCreate.model_validate(
        orientation_payload()
    )
    external = DirectEnglishConstructionOrientationCreate.model_validate(
        orientation_payload(
            source_type="external",
            source_id="review-system",
            source_version="1.0",
        )
    )

    assert human.source_version is None
    assert external.source_version == "1.0"


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"guidance_text": "   "}, "cannot be blank"),
        ({"guidance_text": "x" * 2001}, "at most 2000"),
        ({"priority": "automatic"}, "Input should be"),
        ({"source_type": "classifier"}, "Input should be"),
        ({"source_id": " "}, "cannot be blank"),
        (
            {"source_type": "external", "source_version": None},
            "requires source_version",
        ),
        (
            {"source_type": "external", "source_version": " "},
            "source_version cannot be blank",
        ),
        ({"created_at": datetime(2026, 8, 7, 10, 0)}, "timezone"),
    ],
)
def test_orientation_rejects_invalid_contract(updates, message):
    with pytest.raises(ValidationError, match=message):
        DirectEnglishConstructionOrientationCreate.model_validate(
            orientation_payload(**updates)
        )


@pytest.mark.parametrize("production_function", ["guided", "expanded", "transfer"])
def test_retry_preparation_request_accepts_each_function(production_function):
    request = DirectEnglishConstructionRetryPreparationRequest(
        previous_attempt_id="attempt-1",
        production_function=production_function,
    )

    assert request.production_function == production_function


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {"previous_attempt_id": " ", "production_function": "guided"},
            "cannot be blank",
        ),
        (
            {"previous_attempt_id": "attempt-1", "production_function": "other"},
            "Input should be",
        ),
    ],
)
def test_retry_preparation_request_rejects_invalid_identity(payload, message):
    with pytest.raises(ValidationError, match=message):
        DirectEnglishConstructionRetryPreparationRequest.model_validate(payload)


def retry_orientation_record():
    return DirectEnglishConstructionOrientationRecord(
        orientation_id="orientation-1",
        priority="direct_english_construction",
        guidance_text="Build from I plus a verb.",
        source_type="human",
        source_id="teacher-1",
        created_at=datetime.now(UTC),
    )


def test_retry_preparation_contract_requires_new_attempt_id():
    preparation = DirectEnglishConstructionRetryPreparation(
        previous_attempt_id="attempt-1",
        production_function="guided",
        orientation=retry_orientation_record(),
        conversation_id="conversation-guided",
        prompt_id="prompt-guided",
        previous_configured_support_level="anchors",
        previous_support_used="model",
        next_support_level="anchors",
    )

    assert preparation.requires_new_attempt_id is True
    assert preparation.transfer_selection_policy is None

    with pytest.raises(ValidationError, match="requires a new attempt_id"):
        DirectEnglishConstructionRetryPreparation.model_validate(
            preparation.model_dump() | {"requires_new_attempt_id": False}
        )


def test_transfer_retry_preparation_requires_coherent_metadata():
    payload = {
        "previous_attempt_id": "attempt-1",
        "production_function": "transfer",
        "orientation": retry_orientation_record(),
        "conversation_id": "conversation-transfer",
        "prompt_id": "prompt-transfer",
        "previous_configured_support_level": "none",
        "previous_support_used": "none",
        "next_support_level": "none",
        "transfer_bank_id": "bank-1",
        "previous_transfer_variant_id": "variant-1",
        "previous_transfer_prompt_snapshot": "What do you enjoy?",
        "transfer_selection_policy": "new_attempt_selector",
    }
    preparation = DirectEnglishConstructionRetryPreparation.model_validate(payload)

    assert preparation.transfer_selection_policy == "new_attempt_selector"

    for missing_field in (
        "transfer_bank_id",
        "previous_transfer_variant_id",
        "previous_transfer_prompt_snapshot",
        "transfer_selection_policy",
    ):
        invalid = payload | {missing_field: None}
        with pytest.raises(ValidationError, match="complete metadata"):
            DirectEnglishConstructionRetryPreparation.model_validate(invalid)
