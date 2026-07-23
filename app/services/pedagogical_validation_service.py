from app.services.pedagogical_content_limits_validation import (
    validate_content_limits,
)

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    SkillCoverage,
    SkillStage,
    ValidationFinding,
    ValidationReport,
)
from app.services.pedagogical_duplicate_validation import (
    validate_duplicate_exercise_options,
)


def _has_required_stage(
    coverage: SkillCoverage,
    stage: SkillStage,
) -> bool:
    """Return whether one coverage record contains the required stage.

    Indica si un registro de cobertura contiene la etapa requerida.
    """
    if stage == "introduce":
        return coverage.introduced_in_lesson_id is not None
    if stage == "practice":
        return bool(coverage.practice_activity_ids)
    if stage == "apply":
        return bool(coverage.application_activity_ids)
    if stage == "evaluate":
        return bool(coverage.evaluation_evidence_ids)
    if stage == "consolidate":
        return bool(coverage.consolidation_activity_ids)

    raise AssertionError(f"Unsupported Skill stage: {stage}")


def _collect_candidate_reference_ids(
    candidate: PedagogicalUnitCandidate,
) -> tuple[set[str], set[str], set[str], set[str]]:
    """Collect stable references available inside the candidate unit.

    Recopila las referencias estables disponibles en la unidad candidata.
    """
    lesson_ids = {
        lesson.id
        for lesson in candidate.candidate_unit.lessons
    }
    example_ids = {
        example.id
        for lesson in candidate.candidate_unit.lessons
        for example in lesson.examples
    }
    conversation_ids = {
        conversation.id
        for lesson in candidate.candidate_unit.lessons
        for conversation in lesson.conversations
    }
    exercise_ids = {
        exercise.id
        for lesson in candidate.candidate_unit.lessons
        for exercise in lesson.exercises
    }

    return lesson_ids, example_ids, conversation_ids, exercise_ids


def validate_internal_references(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Reject Skill coverage references absent from the candidate unit.

    Rechaza referencias de cobertura ausentes en la unidad candidata.
    """
    (
        lesson_ids,
        example_ids,
        conversation_ids,
        exercise_ids,
    ) = _collect_candidate_reference_ids(candidate)

    activity_ids = example_ids | conversation_ids | exercise_ids
    consolidation_ids = lesson_ids | activity_ids
    findings: list[ValidationFinding] = []

    for coverage in candidate.skill_coverage:
        reference_groups = [
            (
                "introduced_in_lesson_id",
                (
                    [coverage.introduced_in_lesson_id]
                    if coverage.introduced_in_lesson_id is not None
                    else []
                ),
                lesson_ids,
            ),
            (
                "practice_activity_ids",
                coverage.practice_activity_ids,
                activity_ids,
            ),
            (
                "application_activity_ids",
                coverage.application_activity_ids,
                conversation_ids,
            ),
            (
                "evaluation_evidence_ids",
                coverage.evaluation_evidence_ids,
                exercise_ids,
            ),
            (
                "consolidation_activity_ids",
                coverage.consolidation_activity_ids,
                consolidation_ids,
            ),
        ]

        for field_name, reference_ids, available_ids in reference_groups:
            for reference_id in reference_ids:
                if reference_id in available_ids:
                    continue

                findings.append(
                    ValidationFinding(
                        validator_id="internal_reference_integrity",
                        severity="error",
                        message=(
                            f"Skill {coverage.skill_id} references unknown "
                            f"{field_name}: {reference_id}."
                        ),
                        reference_ids=[
                            coverage.skill_id,
                            reference_id,
                        ],
                    )
                )

    return findings


def validate_evaluation_skill_links(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Require evaluation exercises to reference the evaluated Skill.

    Exige que los ejercicios de evaluación referencien el Skill evaluado.
    """
    exercises_by_id = {
        exercise.id: exercise
        for lesson in candidate.candidate_unit.lessons
        for exercise in lesson.exercises
    }
    findings: list[ValidationFinding] = []

    for coverage in candidate.skill_coverage:
        for evidence_id in coverage.evaluation_evidence_ids:
            exercise = exercises_by_id.get(evidence_id)

            # Unknown references are reported by the integrity validator.
            # Las referencias desconocidas se informan en el validador de integridad.
            if exercise is None:
                continue
            if coverage.skill_id in exercise.skill_ids:
                continue

            findings.append(
                ValidationFinding(
                    validator_id="evaluation_skill_link",
                    severity="error",
                    message=(
                        f"Evaluation evidence {evidence_id} does not "
                        f"reference Skill {coverage.skill_id}."
                    ),
                    reference_ids=[
                        coverage.skill_id,
                        evidence_id,
                    ],
                )
            )

    return findings


def validate_skill_coverage_status(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate the declared status of every Skill coverage record.

    Valida el estado declarado de cada registro de cobertura de Skill.
    """
    findings: list[ValidationFinding] = []

    for coverage in candidate.skill_coverage:
        if coverage.status == "complete":
            continue

        severity = (
            "error"
            if coverage.status == "incomplete"
            else "warning"
        )
        findings.append(
            ValidationFinding(
                validator_id="skill_coverage_status",
                severity=severity,
                message=(
                    f"Skill {coverage.skill_id} coverage status is "
                    f"{coverage.status}."
                ),
                reference_ids=[coverage.skill_id],
            )
        )

    return findings


def validate_skill_stage_coverage(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate mandatory stages for every declared Skill.

    Valida las etapas obligatorias de cada Skill declarado.
    """
    coverage_by_skill_id = {
        coverage.skill_id: coverage
        for coverage in candidate.skill_coverage
    }
    findings: list[ValidationFinding] = []

    for skill in candidate.specification.skills:
        coverage = coverage_by_skill_id[skill.id]

        for stage in skill.required_stages:
            if _has_required_stage(coverage, stage):
                continue

            findings.append(
                ValidationFinding(
                    validator_id="skill_stage_coverage",
                    severity="error",
                    message=(
                        f"Skill {skill.id} lacks required stage: {stage}."
                    ),
                    reference_ids=[skill.id],
                )
            )

    return findings


def _collect_referenced_audio_assets(
    candidate: PedagogicalUnitCandidate,
) -> set[str]:
    """Collect logical audio paths referenced by candidate content.

    Recopila las rutas lógicas de audio referenciadas por el candidato.
    """
    return {
        pronunciation.audio_asset
        for lesson in candidate.candidate_unit.lessons
        for pronunciation in [
            *[
                item
                for example in lesson.examples
                for item in example.pronunciations
            ],
            *[
                item
                for conversation in lesson.conversations
                for turn in conversation.turns
                for item in turn.pronunciations
            ],
            *[
                item
                for conversation in lesson.conversations
                for turn in conversation.turns
                for choice in turn.choices
                for item in choice.pronunciations
            ],
        ]
    }


def validate_required_resource_inventory(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate the logical inventory of referenced audio resources.

    Valida el inventario lógico de los recursos de audio referenciados.
    """
    findings: list[ValidationFinding] = []
    inventory = candidate.required_resource_ids

    if len(inventory) != len(set(inventory)):
        findings.append(
            ValidationFinding(
                validator_id="resource_inventory_unique",
                severity="error",
                message="Required resource IDs must be unique.",
                reference_ids=inventory,
            )
        )

    missing_ids = sorted(
        _collect_referenced_audio_assets(candidate) - set(inventory)
    )
    for resource_id in missing_ids:
        findings.append(
            ValidationFinding(
                validator_id="resource_inventory_complete",
                severity="error",
                message=(
                    f"Referenced audio resource is missing from the "
                    f"inventory: {resource_id}."
                ),
                reference_ids=[resource_id],
            )
        )

    return findings


def validate_pedagogical_candidate(
    candidate: PedagogicalUnitCandidate,
) -> ValidationReport:
    """Run the deterministic validators implemented for the candidate.

    Ejecuta los validadores deterministas implementados para el candidato.
    """
    findings = [
        *validate_skill_stage_coverage(candidate),
        *validate_internal_references(candidate),
        *validate_evaluation_skill_links(candidate),
        *validate_skill_coverage_status(candidate),
        *validate_required_resource_inventory(candidate),
        *validate_duplicate_exercise_options(candidate),
        *validate_content_limits(candidate),
    ]

    if any(finding.severity == "error" for finding in findings):
        status = "failed"
    elif any(finding.severity == "warning" for finding in findings):
        status = "pending"
    else:
        status = "passed"

    return ValidationReport(status=status, findings=findings)
