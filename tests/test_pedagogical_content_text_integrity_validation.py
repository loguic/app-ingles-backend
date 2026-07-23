from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_content_text_integrity_validation import (
    validate_content_text_integrity,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate() -> PedagogicalUnitCandidate:
    """Build one valid candidate for text integrity tests.

    Construye un candidato válido para pruebas de integridad textual.
    """
    return PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )


def test_valid_content_text_does_not_generate_findings():
    candidate = build_candidate()

    findings = validate_content_text_integrity(candidate)

    assert findings == []


def test_blank_example_english_text_generates_finding():
    payload = build_candidate_payload()
    example = payload["candidate_unit"]["lessons"][0]["examples"][0]
    example["en"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-e1"]
    assert "english text" in findings[0].message.lower()


def test_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = deepcopy(candidate.model_dump(mode="json"))

    validate_content_text_integrity(candidate)

    assert candidate.model_dump(mode="json") == before

def test_blank_conversation_title_generates_finding():
    payload = build_candidate_payload()
    conversation = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]
    conversation["title"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-c1"]
    assert "title" in findings[0].message.lower()


def test_blank_turn_english_text_generates_finding():
    payload = build_candidate_payload()
    turn = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]["turns"][0]
    turn["en"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-c1-t1"]
    assert "english text" in findings[0].message.lower()

def test_blank_choice_english_text_generates_finding():
    payload = build_candidate_payload()
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["conversations"] = [
        {
            "id": "a1-u1-l1-c1",
            "title": "Choose a greeting",
            "mode": "branching",
            "start_turn_id": "a1-u1-l1-c1-t1",
            "turns": [
                {
                    "id": "a1-u1-l1-c1-t1",
                    "speaker": "learner",
                    "en": "Choose your response.",
                    "choices": [
                        {
                            "id": "a1-u1-l1-c1-choice-hello",
                            "en": "   ",
                        },
                        {
                            "id": "a1-u1-l1-c1-choice-goodbye",
                            "en": "Goodbye.",
                        },
                    ],
                }
            ],
        }
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == [
        "a1-u1-l1-c1-choice-hello"
    ]
    assert "english text" in findings[0].message.lower()

def test_blank_pronunciation_ipa_generates_finding():
    payload = build_candidate_payload()
    pronunciation = payload["candidate_unit"]["lessons"][0][
        "examples"
    ][0]["pronunciations"][0]
    pronunciation["ipa"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-e1"]
    assert "ipa" in findings[0].message.lower()


def test_blank_pronunciation_audio_asset_generates_finding():
    payload = build_candidate_payload()
    pronunciation = payload["candidate_unit"]["lessons"][0][
        "examples"
    ][0]["pronunciations"][0]
    pronunciation["audio_asset"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-e1"]
    assert "audio_asset" in findings[0].message.lower()

def test_duplicate_example_pronunciation_locale_generates_finding():
    payload = build_candidate_payload()
    example = payload["candidate_unit"]["lessons"][0]["examples"][0]
    example["pronunciations"].append(
        {
            "locale": "en-US",
            "ipa": "/second/",
            "audio_asset": "audio/example_second.wav",
        }
    )
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-e1"]
    assert "duplicate pronunciation locale" in findings[0].message.lower()
    assert "en-US" in findings[0].message


def test_duplicate_turn_pronunciation_locale_generates_finding():
    payload = build_candidate_payload()
    turn = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]["turns"][0]
    turn["pronunciations"].append(
        {
            "locale": "en-US",
            "ipa": "/second/",
            "audio_asset": "audio/turn_second.wav",
        }
    )
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-l1-c1-t1"]
    assert "duplicate pronunciation locale" in findings[0].message.lower()
    assert "en-US" in findings[0].message


def test_duplicate_choice_pronunciation_locale_generates_finding():
    payload = build_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["conversations"] = [
        {
            "id": "a1-u1-l1-c1",
            "title": "Choose a greeting",
            "mode": "branching",
            "start_turn_id": "a1-u1-l1-c1-t1",
            "turns": [
                {
                    "id": "a1-u1-l1-c1-t1",
                    "speaker": "learner",
                    "en": "Choose your response.",
                    "choices": [
                        {
                            "id": "a1-u1-l1-c1-choice-hello",
                            "en": "Hello.",
                            "pronunciations": [
                                {
                                    "locale": "en-US",
                                    "ipa": "/hello/",
                                    "audio_asset": "audio/choice_one.wav",
                                },
                                {
                                    "locale": "en-US",
                                    "ipa": "/hello second/",
                                    "audio_asset": "audio/choice_two.wav",
                                },
                            ],
                        },
                        {
                            "id": "a1-u1-l1-c1-choice-goodbye",
                            "en": "Goodbye.",
                        },
                    ],
                }
            ],
        }
    ]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_content_text_integrity(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_text_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == [
        "a1-u1-l1-c1-choice-hello"
    ]
    assert "duplicate pronunciation locale" in findings[0].message.lower()
    assert "en-US" in findings[0].message

def test_main_validator_rejects_blank_example_text():
    payload = build_candidate_payload()
    example = payload["candidate_unit"]["lessons"][0]["examples"][0]
    example["en"] = "   "
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    report = validate_pedagogical_candidate(candidate)

    text_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == "content_text_integrity"
    ]
    assert report.status == "failed"
    assert len(text_findings) == 1
    assert text_findings[0].reference_ids == ["a1-u1-l1-e1"]

