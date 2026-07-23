from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    SkillCoverage,
    SkillStage,
    ValidationFinding,
    ValidationReport,
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


def validate_pedagogical_candidate(
    candidate: PedagogicalUnitCandidate,
) -> ValidationReport:
    """Run the deterministic validators implemented for the candidate.

    Ejecuta los validadores deterministas implementados para el candidato.
    """
    findings = validate_skill_stage_coverage(candidate)
    status = "failed" if findings else "passed"

    return ValidationReport(status=status, findings=findings)
