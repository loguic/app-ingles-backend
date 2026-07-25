import pytest
from pydantic import ValidationError

from app.schemas.conversation_production import (
    ConversationProductionSubmission,
    LearnerProductionItem,
)


def build_text_production() -> dict:
    # Build one captured written response.
    # Construye una respuesta escrita capturada.
    return {
        "prompt_id": "a1-u1-l1-c3-p1",
        "turn_id": "a1-u1-l1-c3-t2",
        "modality": "text",
        "response_text": "My name is Ana.",
    }


def test_text_production_records_content_without_claiming_correctness():
    # Store what the learner wrote, not an evaluation.
    # Guarda lo escrito por el estudiante, no una evaluación.
    item = LearnerProductionItem.model_validate(build_text_production())

    assert item.prompt_id == "a1-u1-l1-c3-p1"
    assert item.turn_id == "a1-u1-l1-c3-t2"
    assert item.modality == "text"
    assert item.response_text == "My name is Ana."
    assert item.audio_reference is None


def test_voice_production_records_only_a_controlled_audio_reference():
    # Store a recording reference without claiming pronunciation accuracy.
    # Guarda una referencia de grabación sin afirmar precisión fonética.
    item = LearnerProductionItem.model_validate(
        {
            "prompt_id": "a1-u1-l1-c3-p2",
            "turn_id": "a1-u1-l1-c3-t4",
            "modality": "voice",
            "audio_reference": "recordings/session-1/origin.wav",
        }
    )

    assert item.modality == "voice"
    assert item.audio_reference == "recordings/session-1/origin.wav"
    assert item.response_text is None


@pytest.mark.parametrize("response_text", [None, "", "   "])
def test_text_modality_requires_non_blank_text(response_text):
    # Reject empty written production.
    # Rechaza producción escrita vacía.
    payload = build_text_production()
    payload["response_text"] = response_text

    with pytest.raises(
        ValidationError,
        match="Text production requires non-blank response_text",
    ):
        LearnerProductionItem.model_validate(payload)


@pytest.mark.parametrize("audio_reference", [None, "", "   "])
def test_voice_modality_requires_non_blank_audio_reference(audio_reference):
    # Reject voice production without a usable reference.
    # Rechaza producción oral sin una referencia utilizable.
    payload = {
        "prompt_id": "a1-u1-l1-c3-p2",
        "turn_id": "a1-u1-l1-c3-t4",
        "modality": "voice",
        "audio_reference": audio_reference,
    }

    with pytest.raises(
        ValidationError,
        match="Voice production requires non-blank audio_reference",
    ):
        LearnerProductionItem.model_validate(payload)


def test_one_production_item_cannot_mix_text_and_voice():
    # Keep each captured item tied to one modality.
    # Mantiene cada elemento capturado asociado a una modalidad.
    payload = build_text_production()
    payload["audio_reference"] = "recordings/session-1/name.wav"

    with pytest.raises(
        ValidationError,
        match="Text production cannot define audio_reference",
    ):
        LearnerProductionItem.model_validate(payload)

def build_submission() -> dict:
    # Build one complete collection of captured productions.
    # Construye una colección completa de producciones capturadas.
    return {
        "user_id": "learner-1",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c3",
        "productions": [
            build_text_production(),
            {
                "prompt_id": "a1-u1-l1-c3-p2",
                "turn_id": "a1-u1-l1-c3-t4",
                "modality": "voice",
                "audio_reference": "recordings/session-1/origin.wav",
            },
        ],
    }


def test_submission_groups_productions_without_evaluating_them():
    # Group captured outputs under one conversation and learner.
    # Agrupa las producciones bajo una conversación y un estudiante.
    submission = ConversationProductionSubmission.model_validate(
        build_submission()
    )

    assert submission.user_id == "learner-1"
    assert submission.conversation_id == "a1-u1-l1-c3"
    assert len(submission.productions) == 2
    assert submission.productions[0].response_text == "My name is Ana."
    assert submission.productions[1].audio_reference.endswith("origin.wav")


def test_submission_requires_at_least_one_production():
    # Reject an empty submission that contains no observable production.
    # Rechaza un envío vacío sin producción observable.
    payload = build_submission()
    payload["productions"] = []

    with pytest.raises(ValidationError):
        ConversationProductionSubmission.model_validate(payload)


def test_submission_rejects_duplicate_prompt_ids():
    # Keep one captured result per production prompt in one submission.
    # Mantiene un resultado capturado por prompt dentro del envío.
    payload = build_submission()
    payload["productions"].append(build_text_production())

    with pytest.raises(
        ValidationError,
        match="production prompt IDs must be unique",
    ):
        ConversationProductionSubmission.model_validate(payload)
