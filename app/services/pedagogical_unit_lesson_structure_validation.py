from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_unit_lesson_structure(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate the basic structure of the unit and its lessons.

    Valida la estructura básica de la unidad y sus lecciones.
    """
    findings: list[ValidationFinding] = []
    unit = candidate.candidate_unit

    if not unit.title.strip():
        findings.append(
            ValidationFinding(
                validator_id="unit_lesson_structure_integrity",
                severity="error",
                message=f"Unit {unit.id} has an empty title.",
                reference_ids=[unit.id],
            )
        )

    if not unit.lessons:
        findings.append(
            ValidationFinding(
                validator_id="unit_lesson_structure_integrity",
                severity="error",
                message=(
                    f"Unit {unit.id} must contain at least one lesson."
                ),
                reference_ids=[unit.id],
            )
        )

    for lesson in unit.lessons:
        if lesson.title.strip():
            continue

        findings.append(
            ValidationFinding(
                validator_id="unit_lesson_structure_integrity",
                severity="error",
                message=f"Lesson {lesson.id} has an empty title.",
                reference_ids=[lesson.id],
            )
        )

    return findings
