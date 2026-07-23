from app.schemas.content import Pronunciation
from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def _validate_pronunciations(
    owner_label: str,
    owner_id: str,
    pronunciations: list[Pronunciation],
) -> list[ValidationFinding]:
    """Validate required pronunciation fields.

    Valida los campos obligatorios de pronunciación.
    """
    findings: list[ValidationFinding] = []
    seen_locales: set[str] = set()
    duplicate_locales: set[str] = set()

    for pronunciation in pronunciations:
        if pronunciation.locale in seen_locales:
            duplicate_locales.add(pronunciation.locale)
        seen_locales.add(pronunciation.locale)

        if not pronunciation.ipa.strip():
            findings.append(
                ValidationFinding(
                    validator_id="content_text_integrity",
                    severity="error",
                    message=(
                        f"{owner_label} {owner_id} has empty pronunciation IPA."
                    ),
                    reference_ids=[owner_id],
                )
            )

        if not pronunciation.audio_asset.strip():
            findings.append(
                ValidationFinding(
                    validator_id="content_text_integrity",
                    severity="error",
                    message=(
                        f"{owner_label} {owner_id} has empty "
                        "pronunciation audio_asset."
                    ),
                    reference_ids=[owner_id],
                )
            )

    for locale in sorted(duplicate_locales):
        findings.append(
            ValidationFinding(
                validator_id="content_text_integrity",
                severity="error",
                message=(
                    f"{owner_label} {owner_id} contains duplicate "
                    f"pronunciation locale {locale}."
                ),
                reference_ids=[owner_id],
            )
        )

    return findings


def validate_content_text_integrity(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate deterministic text integrity rules.

    Valida reglas deterministas de integridad textual.
    """
    findings: list[ValidationFinding] = []

    for lesson in candidate.candidate_unit.lessons:
        for example in lesson.examples:
            findings.extend(
                _validate_pronunciations(
                    "Example", example.id, example.pronunciations
                )
            )

            if example.en.strip():
                continue

            findings.append(
                ValidationFinding(
                    validator_id="content_text_integrity",
                    severity="error",
                    message=(
                        f"Example {example.id} has empty English text."
                    ),
                    reference_ids=[example.id],
                )
            )


        for conversation in lesson.conversations:
            if not conversation.title.strip():
                findings.append(
                    ValidationFinding(
                        validator_id="content_text_integrity",
                        severity="error",
                        message=(
                            f"Conversation {conversation.id} has an empty title."
                        ),
                        reference_ids=[conversation.id],
                    )
                )

            for turn in conversation.turns:
                findings.extend(
                    _validate_pronunciations(
                        "Turn", turn.id, turn.pronunciations
                    )
                )

                if not turn.en.strip():
                    findings.append(
                        ValidationFinding(
                            validator_id="content_text_integrity",
                            severity="error",
                            message=(
                                f"Turn {turn.id} has empty English text."
                            ),
                            reference_ids=[turn.id],
                        )
                    )

                for choice in turn.choices:
                    findings.extend(
                        _validate_pronunciations(
                            "Choice", choice.id, choice.pronunciations
                        )
                    )

                    if choice.en.strip():
                        continue

                    findings.append(
                        ValidationFinding(
                            validator_id="content_text_integrity",
                            severity="error",
                            message=(
                                f"Choice {choice.id} has empty English text."
                            ),
                            reference_ids=[choice.id],
                        )
                    )

    return findings
