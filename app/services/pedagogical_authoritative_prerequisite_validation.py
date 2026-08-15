"""Translate authoritative curriculum prerequisite conclusions into findings.

Traduce conclusiones curriculares autoritativas de prerrequisitos a findings.
"""

from app.schemas.pedagogical_unit import ValidationFinding
from app.services.pedagogical_authoritative_prerequisite_conclusion import (
    CurriculumPrerequisiteAuthoritativeConclusionDerivation,
)


VALIDATOR_ID = "authoritative_prerequisite_preparation"


def validate_authoritative_prerequisite_conclusions(
    derivation: CurriculumPrerequisiteAuthoritativeConclusionDerivation,
) -> list[ValidationFinding]:
    """Translate only demonstrated negative curriculum conclusions.

    Traduce únicamente conclusiones curriculares negativas demostradas.
    """
    findings: list[ValidationFinding] = []

    for conclusion in derivation.conclusions:
        assessment = conclusion.assessment
        consumption = assessment.consumption
        prerequisite = consumption.prerequisite
        before_point = consumption.before_point

        findings.append(
            ValidationFinding(
                validator_id=VALIDATOR_ID,
                severity="error",
                message=(
                    f"Prerequisite Skill {prerequisite.required_skill_id} "
                    f"requires {prerequisite.required_state} before stage "
                    f"{before_point.stage_id} in lesson "
                    f"{before_point.lesson_id}, but the authoritative "
                    "curriculum prefix contains no valid known preparation "
                    "reaching that state."
                ),
                reference_ids=[
                    assessment.entry.position.unit_id,
                    before_point.lesson_id,
                    before_point.stage_id,
                    prerequisite.required_skill_id,
                    prerequisite.required_state,
                ],
            )
        )

    return findings
