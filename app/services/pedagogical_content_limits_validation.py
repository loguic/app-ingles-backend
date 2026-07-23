from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_content_limits(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate declared quantitative limits without changing content.

    Valida los límites cuantitativos declarados sin modificar contenido.
    """
    findings: list[ValidationFinding] = []
    limits = candidate.specification.content_limits
    unit = candidate.candidate_unit
    lesson_count = len(unit.lessons)

    if (
        limits.min_lessons is not None
        and lesson_count < limits.min_lessons
    ):
        findings.append(
            ValidationFinding(
                validator_id="content_limits",
                severity="error",
                message=(
                    f"Unit {unit.id} contains {lesson_count} lessons; "
                    f"minimum lessons is {limits.min_lessons}."
                ),
                reference_ids=[unit.id],
            )
        )

    if (
        limits.max_lessons is not None
        and lesson_count > limits.max_lessons
    ):
        findings.append(
            ValidationFinding(
                validator_id="content_limits",
                severity="error",
                message=(
                    f"Unit {unit.id} contains {lesson_count} lessons; "
                    f"maximum lessons is {limits.max_lessons}."
                ),
                reference_ids=[unit.id],
            )
        )

    lesson_limit_fields = [
        (
            "examples",
            "min_examples_per_lesson",
            "max_examples_per_lesson",
        ),
        (
            "conversations",
            "min_conversations_per_lesson",
            "max_conversations_per_lesson",
        ),
        (
            "exercises",
            "min_exercises_per_lesson",
            "max_exercises_per_lesson",
        ),
    ]

    for lesson in unit.lessons:
        for content_name, minimum_field, maximum_field in lesson_limit_fields:
            content_count = len(getattr(lesson, content_name))
            minimum = getattr(limits, minimum_field)
            maximum = getattr(limits, maximum_field)

            if minimum is not None and content_count < minimum:
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Lesson {lesson.id} contains {content_count} "
                            f"{content_name}; minimum {content_name} "
                            f"is {minimum}."
                        ),
                        reference_ids=[lesson.id],
                    )
                )

            if maximum is not None and content_count > maximum:
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Lesson {lesson.id} contains {content_count} "
                            f"{content_name}; maximum {content_name} "
                            f"is {maximum}."
                        ),
                        reference_ids=[lesson.id],
                    )
                )

    for lesson in unit.lessons:
        for exercise in lesson.exercises:
            option_count = len(exercise.options)

            if (
                limits.min_options_per_exercise is not None
                and option_count < limits.min_options_per_exercise
            ):
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains "
                            f"{option_count} options; minimum options "
                            f"is {limits.min_options_per_exercise}."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            if (
                limits.max_options_per_exercise is not None
                and option_count > limits.max_options_per_exercise
            ):
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains "
                            f"{option_count} options; maximum options "
                            f"is {limits.max_options_per_exercise}."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

        for conversation in lesson.conversations:
            turn_count = len(conversation.turns)

            if (
                limits.min_turns_per_conversation is not None
                and turn_count < limits.min_turns_per_conversation
            ):
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Conversation {conversation.id} contains "
                            f"{turn_count} turns; minimum turns "
                            f"is {limits.min_turns_per_conversation}."
                        ),
                        reference_ids=[conversation.id],
                    )
                )

            if (
                limits.max_turns_per_conversation is not None
                and turn_count > limits.max_turns_per_conversation
            ):
                findings.append(
                    ValidationFinding(
                        validator_id="content_limits",
                        severity="error",
                        message=(
                            f"Conversation {conversation.id} contains "
                            f"{turn_count} turns; maximum turns "
                            f"is {limits.max_turns_per_conversation}."
                        ),
                        reference_ids=[conversation.id],
                    )
                )

    return findings
