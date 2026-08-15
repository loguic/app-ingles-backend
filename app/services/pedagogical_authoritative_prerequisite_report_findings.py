"""Derive report findings from authoritative prerequisite validation state.

Deriva findings de reporte desde el estado autoritativo de prerequisites.
"""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import ValidationFinding
from app.services.pedagogical_authoritative_prerequisite_validation_status import (
    AuthoritativePrerequisiteValidationStatusDerivation,
)


CONTEXT_VALIDATOR_ID = "authoritative_prerequisite_context_integrity"
PROOF_VALIDATOR_ID = "authoritative_prerequisite_origin_integrity"
RESOLUTION_VALIDATOR_ID = "authoritative_prerequisite_resolution"
UNCERTAINTY_VALIDATOR_ID = "authoritative_prerequisite_uncertainty"


@dataclass(frozen=True)
class AuthoritativePrerequisiteReportFindingDerivation:
    """Preserve source status and its serializable report representation.

    Conserva el estado fuente y su representación serializable de reporte.

    Findings represent source derivations; they are not the canonical source of
    curriculum truth, causes, or validation status.
    """

    status_derivation: AuthoritativePrerequisiteValidationStatusDerivation
    findings: tuple[ValidationFinding, ...]


def _context_findings(status_derivation):
    context_derivation = status_derivation.orchestration.context_derivation
    if context_derivation.context is not None:
        return []

    if context_derivation.scope_errors:
        return [
            ValidationFinding(
                validator_id=CONTEXT_VALIDATOR_ID,
                severity="error",
                message=(
                    "Authoritative prerequisite context could not be derived: "
                    f"{error.cause}."
                ),
                reference_ids=[
                    error.target_level_code,
                    error.target_unit_id,
                ],
            )
            for error in context_derivation.scope_errors
        ]

    return [
        ValidationFinding(
            validator_id=CONTEXT_VALIDATOR_ID,
            severity="error",
            message=(
                "Authoritative prerequisite context could not be derived: "
                f"{error.cause}."
            ),
            reference_ids=(
                []
                if error.position is None
                else [error.position.level_code, error.position.unit_id]
            ),
        )
        for error in context_derivation.context_errors
    ]


def _proof_findings(status_derivation):
    orchestration = status_derivation.orchestration
    proof_derivation = orchestration.proof_derivation
    if proof_derivation is None or proof_derivation.result is not None:
        return []

    context = orchestration.context_derivation.context
    reference_ids = (
        []
        if context is None
        else [
            context.scope.target_position.level_code,
            context.scope.target_position.unit_id,
        ]
    )
    return [
        ValidationFinding(
            validator_id=PROOF_VALIDATOR_ID,
            severity="error",
            message=(
                "Authoritative curriculum prefix proof could not be "
                f"established: {error.cause}."
            ),
            reference_ids=list(reference_ids),
        )
        for error in proof_derivation.errors
    ]


def _consumption_findings(assessment_derivation):
    findings = []
    for resolution_error in assessment_derivation.consumption_errors:
        error = resolution_error.error
        references = [
            resolution_error.entry.position.unit_id,
            error.lesson_id,
        ]
        if error.before_stage_id is not None:
            references.append(error.before_stage_id)
        references.extend([error.required_skill_id, error.required_state])
        findings.append(
            ValidationFinding(
                validator_id=RESOLUTION_VALIDATOR_ID,
                severity="error",
                message=(
                    "Prerequisite consumption point for Skill "
                    f"{error.required_skill_id} in lesson {error.lesson_id} "
                    f"could not be resolved: {error.cause}."
                ),
                reference_ids=references,
            )
        )
    return findings


def _preparation_findings(assessment_derivation):
    findings = []
    for resolution_error in assessment_derivation.preparation_resolution_errors:
        consumption = resolution_error.consumption
        prerequisite = consumption.prerequisite
        before_point = consumption.before_point
        findings.append(
            ValidationFinding(
                validator_id=RESOLUTION_VALIDATOR_ID,
                severity="error",
                message=(
                    "Accumulated prerequisite preparation for Skill "
                    f"{prerequisite.required_skill_id} before stage "
                    f"{before_point.stage_id} could not be resolved: "
                    f"{resolution_error.error.cause}."
                ),
                reference_ids=[
                    resolution_error.entry.position.unit_id,
                    before_point.lesson_id,
                    before_point.stage_id,
                    prerequisite.required_skill_id,
                    prerequisite.required_state,
                ],
            )
        )
    return findings


def _uncertainty_findings(conclusion_derivation):
    findings = []
    for uncertainty in conclusion_derivation.uncertainties:
        assessment = uncertainty.assessment
        prerequisite = assessment.consumption.prerequisite
        before_point = assessment.consumption.before_point
        findings.append(
            ValidationFinding(
                validator_id=UNCERTAINTY_VALIDATOR_ID,
                severity="warning",
                message=(
                    "Prerequisite preparation for Skill "
                    f"{prerequisite.required_skill_id} before stage "
                    f"{before_point.stage_id} in lesson "
                    f"{before_point.lesson_id} could not be conclusively "
                    "determined because related claim precedence errors remain."
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


def derive_authoritative_prerequisite_report_findings(
    status_derivation: AuthoritativePrerequisiteValidationStatusDerivation,
) -> AuthoritativePrerequisiteReportFindingDerivation:
    """Represent already-derived source states without reclassifying them.

    Representa estados fuente ya derivados sin volver a clasificarlos.
    """
    orchestration = status_derivation.orchestration
    findings = _context_findings(status_derivation)
    findings.extend(_proof_findings(status_derivation))

    conclusion_derivation = orchestration.conclusion_derivation
    if conclusion_derivation is not None:
        assessment_derivation = conclusion_derivation.assessment_derivation
        findings.extend(_consumption_findings(assessment_derivation))
        findings.extend(_preparation_findings(assessment_derivation))

    findings.extend(orchestration.findings)

    if conclusion_derivation is not None:
        findings.extend(_uncertainty_findings(conclusion_derivation))

    return AuthoritativePrerequisiteReportFindingDerivation(
        status_derivation=status_derivation,
        findings=tuple(findings),
    )
