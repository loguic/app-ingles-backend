from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)
from app.services.pedagogical_duplicate_validation import (
    normalize_candidate_text,
)


def _validate_metadata_entries(
    lesson_id: str,
    field_name: str,
    values: list[str],
) -> list[ValidationFinding]:
    """Validate nonblank and unique lesson metadata entries.

    Valida entradas no vacías y únicas de metadatos de lección.
    """
    findings: list[ValidationFinding] = []
    normalized_indexes: dict[str, list[int]] = {}

    for index, value in enumerate(values):
        normalized = normalize_candidate_text(value)

        if not normalized:
            findings.append(
                ValidationFinding(
                    validator_id="lesson_metadata_integrity",
                    severity="error",
                    message=(
                        f"Lesson {lesson_id} contains an empty "
                        f"{field_name} entry at index {index}."
                    ),
                    reference_ids=[lesson_id],
                )
            )
            continue

        normalized_indexes.setdefault(normalized, []).append(index)

    for indexes in normalized_indexes.values():
        if len(indexes) < 2:
            continue

        findings.append(
            ValidationFinding(
                validator_id="lesson_metadata_integrity",
                severity="error",
                message=(
                    f"Lesson {lesson_id} contains equivalent "
                    f"{field_name} entries at indexes: "
                    + ", ".join(str(index) for index in indexes)
                    + "."
                ),
                reference_ids=[lesson_id],
            )
        )

    return findings


def validate_lesson_metadata_integrity(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate deterministic lesson metadata integrity rules.

    Valida reglas deterministas de integridad de metadatos de lección.
    """
    findings: list[ValidationFinding] = []

    for lesson in candidate.candidate_unit.lessons:
        if (
            lesson.objective is not None
            and not lesson.objective.strip()
        ):
            findings.append(
                ValidationFinding(
                    validator_id="lesson_metadata_integrity",
                    severity="error",
                    message=f"Lesson {lesson.id} has an empty objective.",
                    reference_ids=[lesson.id],
                )
            )

        findings.extend(
            _validate_metadata_entries(
                lesson.id,
                "vocabulary",
                lesson.vocabulary,
            )
        )
        findings.extend(
            _validate_metadata_entries(
                lesson.id,
                "grammar",
                lesson.grammar,
            )
        )

    return findings
