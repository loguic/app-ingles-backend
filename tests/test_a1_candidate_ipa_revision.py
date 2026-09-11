import json
from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_candidate_payload_identity import (
    derive_candidate_payload_identity,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
V3_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json"
V4_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
V3_FILE_SHA256 = "1e674bc6d4058f58ec7c6b21252c7aa26b3974e058db5e64aa6e4b4802b6894f"
EXPECTED_V4_DIGEST = (
    "sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d"
)


def _document(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate(path: Path) -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(_document(path))


def _scalar_differences(
    left: object,
    right: object,
    path: tuple[object, ...] = (),
) -> list[tuple[tuple[object, ...], object, object]]:
    if type(left) is not type(right):
        return [(path, left, right)]
    if isinstance(left, dict):
        differences: list[tuple[tuple[object, ...], object, object]] = []
        assert isinstance(right, dict)
        for key in left.keys() | right.keys():
            if key not in left or key not in right:
                differences.append((path + (key,), left.get(key), right.get(key)))
            else:
                differences.extend(
                    _scalar_differences(left[key], right[key], path + (key,))
                )
        return differences
    if isinstance(left, list):
        assert isinstance(right, list)
        if len(left) != len(right):
            return [(path + ("length",), len(left), len(right))]
        differences = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(
                _scalar_differences(
                    left_item,
                    right_item,
                    path + (index,),
                )
            )
        return differences
    return [] if left == right else [(path, left, right)]


def _canonical_document(document: dict[str, object]) -> dict[str, object]:
    return {
        key: document[key]
        for key in (
            "specification",
            "candidate_unit",
            "evaluation_plans",
            "feedback_plans",
            "lesson_capability_plans",
            "skill_coverage",
            "required_resource_ids",
        )
    }


def _language_support(candidate: PedagogicalUnitCandidate):
    experience = candidate.candidate_unit.lessons[0].experience
    assert experience is not None
    return experience.language_support


def _focal_word_expression_ipa_matches(
    candidate: PedagogicalUnitCandidate,
    *,
    word_index: int,
    expression_index: int,
    locale: str,
) -> bool:
    """Check one known A1-U1 word/expression alignment without a global gate."""
    support = _language_support(candidate)
    word = support[word_index]
    expression = support[expression_index]
    word_tokens = word.en.strip().casefold().rstrip(".,!?;:").split()
    expression_tokens = [
        token.rstrip(".,!?;:")
        for token in expression.en.strip().casefold().split()
    ]
    assert len(word_tokens) == 1
    positions = [
        index
        for index, token in enumerate(expression_tokens)
        if token == word_tokens[0]
    ]
    assert len(positions) == 1

    word_pronunciations = {
        pronunciation.locale: pronunciation
        for pronunciation in word.pronunciations
    }
    expression_pronunciations = {
        pronunciation.locale: pronunciation
        for pronunciation in expression.pronunciations
    }
    word_ipa_tokens = word_pronunciations[locale].ipa.strip("/").split()
    expression_ipa_tokens = (
        expression_pronunciations[locale].ipa.strip("/").split()
    )
    assert len(word_ipa_tokens) == 1
    assert len(expression_ipa_tokens) == len(expression_tokens)
    return word_ipa_tokens[0] == expression_ipa_tokens[positions[0]]


def test_v3_is_byte_identical_and_v4_has_one_canonical_ipa_delta() -> None:
    import hashlib

    assert hashlib.sha256(V3_PATH.read_bytes()).hexdigest() == V3_FILE_SHA256
    v3_document = _document(V3_PATH)
    v4_document = _document(V4_PATH)

    assert _scalar_differences(
        _canonical_document(v3_document),
        _canonical_document(v4_document),
    ) == [
        (
            (
                "candidate_unit",
                "lessons",
                0,
                "experience",
                "language_support",
                4,
                "pronunciations",
                0,
                "ipa",
            ),
            "/hɛlp/",
            "/help/",
        )
    ]
    assert v4_document["proposed_change_summary"][0].startswith(
        "Identify this isolated proposal externally as candidate_revision "
        "a1-u1-candidate-v4;"
    )


def test_v4_identity_and_approved_help_references_are_exact() -> None:
    v3 = _candidate(V3_PATH)
    v4 = _candidate(V4_PATH)
    support = _language_support(v4)

    assert support[4].pronunciations[0].locale == "en-GB"
    assert support[4].pronunciations[0].ipa == "/help/"
    assert support[4].pronunciations[0].audio_asset == (
        "audio.a1-u1-l1.help.en-gb.v1"
    )
    assert support[4].pronunciations[1].locale == "en-US"
    assert support[4].pronunciations[1].ipa == "/hɛlp/"
    assert support[5].pronunciations[0].locale == "en-GB"
    assert support[5].pronunciations[0].ipa == "/aɪ niːd help/"
    assert v4.specification == v3.specification
    assert v4.required_resource_ids == v3.required_resource_ids
    assert validate_pedagogical_candidate(v4).status == "passed"
    assert derive_candidate_payload_identity(
        v4,
        candidate_revision="a1-u1-candidate-v4",
    ).content_digest == EXPECTED_V4_DIGEST


def test_v4_focal_word_expression_ipa_consistency() -> None:
    v3 = _candidate(V3_PATH)
    v4 = _candidate(V4_PATH)

    assert not _focal_word_expression_ipa_matches(
        v3,
        word_index=4,
        expression_index=5,
        locale="en-GB",
    )
    for word_index, expression_index, locale in (
        (0, 1, "en-GB"),
        (0, 1, "en-US"),
        (2, 3, "en-GB"),
        (4, 5, "en-GB"),
    ):
        assert _focal_word_expression_ipa_matches(
            v4,
            word_index=word_index,
            expression_index=expression_index,
            locale=locale,
        )
