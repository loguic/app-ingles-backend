from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_exercise_integrity(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate deterministic integrity rules for exercises.

    Valida reglas deterministas de integridad para los ejercicios.
    """
    findings: list[ValidationFinding] = []
    declared_skill_ids = {
        skill.id for skill in candidate.specification.skills
    }

    for lesson in candidate.candidate_unit.lessons:
        for exercise in lesson.exercises:
            if not exercise.prompt.strip():
                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} has an empty prompt."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            if len(exercise.options) < 2:
                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} must contain "
                            "at least 2 options."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            for index, option in enumerate(exercise.options):
                if option.strip():
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} option at index "
                            f"{index} is empty."
                        ),
                        reference_ids=[exercise.id],
                    )
                )


            if not 0 <= exercise.answer_index < len(exercise.options):
                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} answer_index "
                            f"{exercise.answer_index} is outside "
                            "the options range."
                        ),
                        reference_ids=[exercise.id],
                    )
                )


            if not exercise.skill_ids:
                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} must reference "
                            "at least one Skill."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            seen_skill_ids: set[str] = set()
            duplicate_skill_ids: set[str] = set()

            for skill_id in exercise.skill_ids:
                if skill_id in seen_skill_ids:
                    duplicate_skill_ids.add(skill_id)
                seen_skill_ids.add(skill_id)

            for skill_id in sorted(duplicate_skill_ids):
                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains duplicate "
                            f"skill_id {skill_id}."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            for skill_id in exercise.skill_ids:
                if skill_id in declared_skill_ids:
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="exercise_integrity",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} references unknown "
                            f"skill_id {skill_id}."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

    return findings
