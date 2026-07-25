import pytest

from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_identifier_validation import (
    validate_content_identifiers,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def build_candidate(payload=None) -> PedagogicalUnitCandidate:
    """Build one candidate for isolated identifier tests.

    Construye un candidato para pruebas aisladas de identificadores.
    """
    source = payload if payload is not None else build_candidate_payload()
    return PedagogicalUnitCandidate.model_validate(source)


def test_valid_hierarchical_identifiers_pass_validation():
    candidate = build_candidate()

    findings = validate_content_identifiers(candidate)

    assert findings == []


def test_malformed_lesson_identifier_generates_finding():
    payload = deepcopy(build_candidate_payload())
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["id"] = "a1-u1-lesson-1"
    lesson["examples"][0]["id"] = "a1-u1-lesson-1-e1"
    lesson["conversations"][0]["id"] = "a1-u1-lesson-1-c1"
    lesson["conversations"][0]["turns"][0]["id"] = (
        "a1-u1-lesson-1-c1-t1"
    )
    lesson["exercises"][0]["id"] = "a1-u1-lesson-1-q1"
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_identifier_integrity"
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == ["a1-u1-lesson-1"]
    assert "invalid lesson identifier" in findings[0].message


def test_duplicate_lesson_identifiers_generate_finding():
    payload = deepcopy(build_candidate_payload())
    payload["candidate_unit"]["lessons"][1]["id"] = "a1-u1-l1"
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == ["a1-u1-l1"]
    assert "duplicate lesson identifier" in findings[0].message


def test_identifier_validation_does_not_modify_candidate():
    candidate = build_candidate()
    before = candidate.model_dump(mode="json")

    validate_content_identifiers(candidate)

    assert candidate.model_dump(mode="json") == before

@pytest.mark.parametrize(
    ("collection", "invalid_id", "content_type"),
    [
        ("examples", "a1-u1-l1-example-1", "example"),
        ("conversations", "a1-u1-l1-conversation-1", "conversation"),
        ("exercises", "a1-u1-l1-exercise-1", "exercise"),
    ],
)
def test_malformed_child_identifier_generates_finding(
    collection,
    invalid_id,
    content_type,
):
    payload = deepcopy(build_candidate_payload())
    element = payload["candidate_unit"]["lessons"][0][collection][0]
    element["id"] = invalid_id

    if collection == "conversations":
        element["turns"][0]["id"] = invalid_id + "-t1"

    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [invalid_id]
    assert f"invalid {content_type} identifier" in findings[0].message

@pytest.mark.parametrize(
    ("collection", "content_type"),
    [
        ("examples", "example"),
        ("conversations", "conversation"),
        ("exercises", "exercise"),
    ],
)
def test_duplicate_child_identifier_generates_finding(
    collection,
    content_type,
):
    payload = deepcopy(build_candidate_payload())
    elements = payload["candidate_unit"]["lessons"][0][collection]
    duplicate = deepcopy(elements[0])

    if collection == "conversations":
        duplicate["turns"][0]["id"] = (
            duplicate["id"] + "-t2"
        )

    elements.append(duplicate)
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [duplicate["id"]]
    assert f"duplicate {content_type} identifier" in findings[0].message

@pytest.mark.parametrize(
    ("element_type", "invalid_id"),
    [
        ("turn", "a1-u1-l1-c1-turn-1"),
        ("choice", "a1-u1-l1-c1-option-one"),
    ],
)
def test_malformed_conversation_element_identifier_generates_finding(
    element_type,
    invalid_id,
):
    payload = deepcopy(build_candidate_payload())
    conversation = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]

    if element_type == "turn":
        conversation["turns"][0]["id"] = invalid_id
    else:
        conversation["turns"][0]["choices"] = [
            {
                "id": invalid_id,
                "en": "Hello.",
            }
        ]

    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].reference_ids == [invalid_id]
    assert f"invalid {element_type} identifier" in findings[0].message

def test_main_validator_rejects_invalid_content_identifier():
    payload = deepcopy(build_candidate_payload())
    payload["candidate_unit"]["lessons"][0]["examples"][0][
        "id"
    ] = "a1-u1-l1-example-1"
    candidate = build_candidate(payload)

    report = validate_pedagogical_candidate(candidate)

    assert report.status == "failed"
    assert any(
        finding.validator_id == "content_identifier_integrity"
        for finding in report.findings
    )

def _build_minimal_experience(lesson_id: str) -> dict:
    """Build one valid minimal v2 experience for identifier tests.

    Construye una experiencia v2 mínima válida para probar identificadores.
    """
    stage_id = lesson_id + "-s1"
    evidence_id = lesson_id + "-ev1"
    activity_id = lesson_id + "-gp1"

    return {
        "contract_version": "2.0",
        "mission": {
            "id": lesson_id + "-m1",
            "title": "Introduce yourself",
            "situation": "Meet someone for the first time.",
            "observable_outcome": "State your name and origin.",
            "success_criteria": [
                "The learner gives a name.",
                "The learner gives an origin.",
            ],
        },
        "skill_ids": ["a1_introduce_yourself"],
        "stages": [
            {
                "id": stage_id,
                "type": "guided_production",
                "instruction": "Produce a short introduction.",
                "activity_ids": [activity_id],
                "mode": "required",
                "completion_condition": "evidence_recorded",
            }
        ],
        "language_support": [
            {
                "id": lesson_id + "-ls1",
                "type": "reference_expression",
                "en": "I am Ana. I am from Spain.",
                "stage_ids": [stage_id],
            }
        ],
        "evidence_definitions": [
            {
                "id": evidence_id,
                "skill_ids": ["a1_introduce_yourself"],
                "stage_id": stage_id,
                "activity_id": activity_id,
                "evidence_type": "guided_production",
                "measurement_mode": "completion",
                "required": True,
            }
        ],
        "completion_policy": {
            "practiced_stage_ids": [stage_id],
            "required_evidence_ids": [evidence_id],
            "reinforcement_on_failure": True,
            "allow_retry": True,
        },
    }


@pytest.mark.parametrize(
    ("element_type", "invalid_id", "message"),
    [
        (
            "mission",
            "a1-u1-l1-mission-1",
            "invalid mission identifier",
        ),
        (
            "stage",
            "a1-u1-l1-stage-1",
            "invalid stage identifier",
        ),
        (
            "support",
            "a1-u1-l1-support-1",
            "invalid language support identifier",
        ),
        (
            "evidence",
            "a1-u1-l1-evidence-1",
            "invalid evidence identifier",
        ),
    ],
)
def test_malformed_lesson_experience_identifier_generates_finding(
    element_type,
    invalid_id,
    message,
):
    payload = deepcopy(build_candidate_payload())
    experience = _build_minimal_experience("a1-u1-l1")

    if element_type == "mission":
        experience["mission"]["id"] = invalid_id
    elif element_type == "stage":
        experience["stages"][0]["id"] = invalid_id
        experience["language_support"][0]["stage_ids"] = [invalid_id]
        experience["evidence_definitions"][0]["stage_id"] = invalid_id
        experience["completion_policy"]["practiced_stage_ids"] = [
            invalid_id
        ]
    elif element_type == "support":
        experience["language_support"][0]["id"] = invalid_id
    else:
        experience["evidence_definitions"][0]["id"] = invalid_id
        experience["completion_policy"]["required_evidence_ids"] = [
            invalid_id
        ]

    payload["candidate_unit"]["lessons"][0]["experience"] = experience
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == "content_identifier_integrity"
    assert findings[0].reference_ids == [invalid_id]
    assert message in findings[0].message


@pytest.mark.parametrize(
    ("element_type", "message"),
    [
        ("mission", "duplicate mission identifier"),
        ("stage", "duplicate stage identifier"),
        ("support", "duplicate language support identifier"),
        ("evidence", "duplicate evidence identifier"),
    ],
)
def test_duplicate_lesson_experience_identifier_across_lessons(
    element_type,
    message,
):
    payload = deepcopy(build_candidate_payload())
    first = _build_minimal_experience("a1-u1-l1")
    second = _build_minimal_experience("a1-u1-l2")

    if element_type == "mission":
        second["mission"]["id"] = first["mission"]["id"]
    elif element_type == "stage":
        duplicate_id = first["stages"][0]["id"]
        second["stages"][0]["id"] = duplicate_id
        second["language_support"][0]["stage_ids"] = [duplicate_id]
        second["evidence_definitions"][0]["stage_id"] = duplicate_id
        second["completion_policy"]["practiced_stage_ids"] = [
            duplicate_id
        ]
    elif element_type == "support":
        second["language_support"][0]["id"] = (
            first["language_support"][0]["id"]
        )
    else:
        duplicate_id = first["evidence_definitions"][0]["id"]
        second["evidence_definitions"][0]["id"] = duplicate_id
        second["completion_policy"]["required_evidence_ids"] = [
            duplicate_id
        ]

    payload["candidate_unit"]["lessons"][0]["experience"] = first
    payload["candidate_unit"]["lessons"][1]["experience"] = second
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert any(message in finding.message for finding in findings)

def _add_production_prompt(
    conversation: dict,
    prompt_id: str,
) -> None:
    """Add one learner production prompt for identifier tests.

    Añade un prompt de producción para probar identificadores.
    """
    conversation["turns"].append(
        {
            "id": conversation["id"] + "-t2",
            "speaker": "learner",
            "en": "Respond personally.",
            "production_prompt": {
                "id": prompt_id,
                "accepted_modalities": ["text"],
                "required": True,
            },
        }
    )


def test_malformed_production_prompt_identifier_generates_finding():
    payload = deepcopy(build_candidate_payload())
    conversation = payload["candidate_unit"]["lessons"][0][
        "conversations"
    ][0]
    invalid_id = conversation["id"] + "-prompt-1"
    _add_production_prompt(conversation, invalid_id)
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    matching = [
        finding
        for finding in findings
        if "invalid production prompt identifier" in finding.message
    ]
    assert len(matching) == 1
    assert matching[0].validator_id == "content_identifier_integrity"
    assert matching[0].severity == "error"
    assert matching[0].reference_ids == [invalid_id]


def test_duplicate_production_prompt_identifier_across_unit_generates_finding():
    payload = deepcopy(build_candidate_payload())
    first_lesson = payload["candidate_unit"]["lessons"][0]
    second_lesson = payload["candidate_unit"]["lessons"][1]
    first_conversation = first_lesson["conversations"][0]

    second_conversation = {
        "id": second_lesson["id"] + "-c1",
        "title": "Second production conversation",
        "mode": "guided",
        "turns": [
            {
                "id": second_lesson["id"] + "-c1-t1",
                "speaker": "partner",
                "en": "Respond.",
            }
        ],
    }
    second_lesson["conversations"] = [second_conversation]

    duplicate_id = first_conversation["id"] + "-p1"
    _add_production_prompt(first_conversation, duplicate_id)
    _add_production_prompt(second_conversation, duplicate_id)
    candidate = build_candidate(payload)

    findings = validate_content_identifiers(candidate)

    assert any(
        "duplicate production prompt identifier" in finding.message
        and finding.reference_ids == [duplicate_id]
        for finding in findings
    )
