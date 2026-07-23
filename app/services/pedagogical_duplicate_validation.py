from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def normalize_candidate_text(value: str) -> str:
    """Normalize candidate text for exact deterministic comparison.

    Normaliza texto candidato para una comparación exacta determinista.
    """
    return " ".join(value.casefold().split())


def validate_duplicate_exercise_options(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Reject equivalent options inside one multiple-choice exercise.

    Rechaza opciones equivalentes dentro de un ejercicio de selección.
    """
    findings: list[ValidationFinding] = []

    for lesson in candidate.candidate_unit.lessons:
        for exercise in lesson.exercises:
            option_indexes: dict[str, list[int]] = {}

            for index, option in enumerate(exercise.options):
                normalized = normalize_candidate_text(option)
                option_indexes.setdefault(normalized, []).append(index)

            for indexes in option_indexes.values():
                if len(indexes) < 2:
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="duplicate_exercise_options",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains "
                            f"equivalent options at indexes: "
                            + ", ".join(str(index) for index in indexes)
                            + "."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

    return findings
