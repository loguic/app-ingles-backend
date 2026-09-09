from app.schemas.content import ExerciseVisualOption
from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def normalize_candidate_text(value: str) -> str:
    """Normalize candidate text for exact deterministic comparison.

    Normaliza texto candidato para una comparación exacta determinista.
    """
    return " ".join(value.casefold().split())


def normalize_visual_accessibility_label(value: str) -> str:
    """Normalize a visual option label without semantic interpretation.

    Normaliza una etiqueta visual sin interpretación semántica.
    """
    return value.strip().casefold()


def validate_duplicate_exercise_options(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Reject equivalent options inside one multiple-choice exercise.

    Rechaza opciones equivalentes dentro de un ejercicio de selección.
    """
    findings: list[ValidationFinding] = []

    for lesson in candidate.candidate_unit.lessons:
        for exercise in lesson.exercises:
            if not exercise.options or isinstance(exercise.options[0], str):
                option_indexes: dict[str, list[int]] = {}

                for index, option in enumerate(exercise.options):
                    assert isinstance(option, str)
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
                                "equivalent options at indexes: "
                                + ", ".join(
                                    str(index) for index in indexes
                                )
                                + "."
                            ),
                            reference_ids=[exercise.id],
                        )
                    )
                continue

            resource_indexes: dict[str, list[int]] = {}
            accessibility_label_indexes: dict[str, list[int]] = {}

            for index, option in enumerate(exercise.options):
                assert isinstance(option, ExerciseVisualOption)
                resource_indexes.setdefault(option.resource_id, []).append(index)
                normalized_label = normalize_visual_accessibility_label(
                    option.accessibility_label
                )
                accessibility_label_indexes.setdefault(
                    normalized_label, []
                ).append(index)

            for indexes in resource_indexes.values():
                if len(indexes) < 2:
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="duplicate_exercise_options",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains duplicate "
                            "visual resource_ids at indexes: "
                            + ", ".join(str(index) for index in indexes)
                            + "."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

            for indexes in accessibility_label_indexes.values():
                if len(indexes) < 2:
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="duplicate_exercise_options",
                        severity="error",
                        message=(
                            f"Exercise {exercise.id} contains equivalent "
                            "visual accessibility labels at indexes: "
                            + ", ".join(str(index) for index in indexes)
                            + "."
                        ),
                        reference_ids=[exercise.id],
                    )
                )

    return findings
