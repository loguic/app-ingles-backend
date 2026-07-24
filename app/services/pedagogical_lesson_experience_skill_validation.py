from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_lesson_experience_skills(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate LessonExperience Skills against the approved specification.

    Valida las Skills de LessonExperience contra la especificación aprobada.
    """
    findings: list[ValidationFinding] = []
    declared_skill_ids = {
        skill.id
        for skill in candidate.specification.skills
    }

    for lesson in candidate.candidate_unit.lessons:
        if lesson.experience is None:
            continue

        for skill_id in lesson.experience.skill_ids:
            if skill_id in declared_skill_ids:
                continue

            findings.append(
                ValidationFinding(
                    validator_id="lesson_experience_skills",
                    severity="error",
                    message=(
                        f"LessonExperience in lesson {lesson.id} "
                        f"references unknown skill_id {skill_id}."
                    ),
                    reference_ids=[lesson.id, skill_id],
                )
            )

    return findings
