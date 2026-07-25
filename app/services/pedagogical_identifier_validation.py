import re

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_content_identifiers(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate hierarchical and unique candidate content identifiers.

    Valida identificadores jerárquicos y únicos del contenido candidato.
    """
    findings: list[ValidationFinding] = []
    unit = candidate.candidate_unit
    lesson_pattern = re.compile(
        rf"^{re.escape(unit.id)}-l[1-9][0-9]*$"
    )
    seen_lesson_ids: set[str] = set()

    for lesson in unit.lessons:
        if lesson_pattern.fullmatch(lesson.id) is None:
            findings.append(
                ValidationFinding(
                    validator_id="content_identifier_integrity",
                    severity="error",
                    message=(
                        f"Candidate contains invalid lesson identifier: "
                        f"{lesson.id}."
                    ),
                    reference_ids=[lesson.id],
                )
            )

        if lesson.id in seen_lesson_ids:
            findings.append(
                ValidationFinding(
                    validator_id="content_identifier_integrity",
                    severity="error",
                    message=(
                        f"Candidate contains duplicate lesson identifier: "
                        f"{lesson.id}."
                    ),
                    reference_ids=[lesson.id],
                )
            )
        else:
            seen_lesson_ids.add(lesson.id)

    seen_child_ids: dict[str, set[str]] = {
        "example": set(),
        "conversation": set(),
        "exercise": set(),
    }

    for lesson in unit.lessons:
        child_identifier_rules = [
            ("example", lesson.examples, "e"),
            ("conversation", lesson.conversations, "c"),
            ("exercise", lesson.exercises, "q"),
        ]

        for content_type, elements, suffix in child_identifier_rules:
            pattern = re.compile(
                rf"^{re.escape(lesson.id)}-{suffix}[1-9][0-9]*$"
            )

            for element in elements:
                if pattern.fullmatch(element.id) is None:
                    findings.append(
                        ValidationFinding(
                            validator_id="content_identifier_integrity",
                            severity="error",
                            message=(
                                f"Candidate contains invalid {content_type} "
                                f"identifier: {element.id}."
                            ),
                            reference_ids=[element.id],
                        )
                    )

                if element.id in seen_child_ids[content_type]:
                    findings.append(
                        ValidationFinding(
                            validator_id="content_identifier_integrity",
                            severity="error",
                            message=(
                                f"Candidate contains duplicate "
                                f"{content_type} identifier: {element.id}."
                            ),
                            reference_ids=[element.id],
                        )
                    )
                else:
                    seen_child_ids[content_type].add(element.id)

    seen_production_prompt_ids: set[str] = set()

    for lesson in unit.lessons:
        for conversation in lesson.conversations:
            turn_pattern = re.compile(
                rf"^{re.escape(conversation.id)}-t[1-9][0-9]*$"
            )
            choice_pattern = re.compile(
                rf"^{re.escape(conversation.id)}-choice-"
                r"[a-z0-9]+(?:-[a-z0-9]+)*$"
            )
            production_prompt_pattern = re.compile(
                rf"^{re.escape(conversation.id)}-p[1-9][0-9]*$"
            )

            for turn in conversation.turns:
                if turn_pattern.fullmatch(turn.id) is None:
                    findings.append(
                        ValidationFinding(
                            validator_id=(
                                "content_identifier_integrity"
                            ),
                            severity="error",
                            message=(
                                "Candidate contains invalid turn "
                                f"identifier: {turn.id}."
                            ),
                            reference_ids=[turn.id],
                        )
                    )

                production_prompt = turn.production_prompt
                if production_prompt is not None:
                    prompt_id = production_prompt.id

                    if (
                        production_prompt_pattern.fullmatch(prompt_id)
                        is None
                    ):
                        findings.append(
                            ValidationFinding(
                                validator_id=(
                                    "content_identifier_integrity"
                                ),
                                severity="error",
                                message=(
                                    "Candidate contains invalid production "
                                    f"prompt identifier: {prompt_id}."
                                ),
                                reference_ids=[prompt_id],
                            )
                        )

                    if prompt_id in seen_production_prompt_ids:
                        findings.append(
                            ValidationFinding(
                                validator_id=(
                                    "content_identifier_integrity"
                                ),
                                severity="error",
                                message=(
                                    "Candidate contains duplicate production "
                                    f"prompt identifier: {prompt_id}."
                                ),
                                reference_ids=[prompt_id],
                            )
                        )
                    else:
                        seen_production_prompt_ids.add(prompt_id)

                for choice in turn.choices:
                    if choice_pattern.fullmatch(choice.id) is not None:
                        continue

                    findings.append(
                        ValidationFinding(
                            validator_id=(
                                "content_identifier_integrity"
                            ),
                            severity="error",
                            message=(
                                "Candidate contains invalid choice "
                                f"identifier: {choice.id}."
                            ),
                            reference_ids=[choice.id],
                        )
                    )


    # Validate hierarchical v2 identifiers across the complete unit.
    # Valida identificadores jerárquicos v2 en toda la unidad.
    seen_experience_ids: dict[str, set[str]] = {
        "mission": set(),
        "stage": set(),
        "language support": set(),
        "evidence": set(),
    }

    for lesson in unit.lessons:
        experience = lesson.experience
        if experience is None:
            continue

        experience_identifier_rules = [
            (
                "mission",
                [experience.mission],
                re.compile(
                    rf"^{re.escape(lesson.id)}-m[1-9][0-9]*$"
                ),
            ),
            (
                "stage",
                experience.stages,
                re.compile(
                    rf"^{re.escape(lesson.id)}-s[1-9][0-9]*$"
                ),
            ),
            (
                "language support",
                experience.language_support,
                re.compile(
                    rf"^{re.escape(lesson.id)}-ls[1-9][0-9]*$"
                ),
            ),
            (
                "evidence",
                experience.evidence_definitions,
                re.compile(
                    rf"^{re.escape(lesson.id)}-ev[1-9][0-9]*$"
                ),
            ),
        ]

        for content_type, elements, pattern in (
            experience_identifier_rules
        ):
            for element in elements:
                if pattern.fullmatch(element.id) is None:
                    findings.append(
                        ValidationFinding(
                            validator_id=(
                                "content_identifier_integrity"
                            ),
                            severity="error",
                            message=(
                                "Candidate contains invalid "
                                f"{content_type} identifier: "
                                f"{element.id}."
                            ),
                            reference_ids=[element.id],
                        )
                    )

                if element.id in seen_experience_ids[content_type]:
                    findings.append(
                        ValidationFinding(
                            validator_id=(
                                "content_identifier_integrity"
                            ),
                            severity="error",
                            message=(
                                "Candidate contains duplicate "
                                f"{content_type} identifier: "
                                f"{element.id}."
                            ),
                            reference_ids=[element.id],
                        )
                    )
                else:
                    seen_experience_ids[content_type].add(element.id)

    return findings
