"""Classify authoritative prerequisite validation resolution status.

Clasifica el estado de resolución de la validación autoritativa de prerrequisitos.
"""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import ValidationStatus
from app.services.pedagogical_authoritative_prerequisite_orchestration import (
    AuthoritativePrerequisiteValidationDerivation,
)


@dataclass(frozen=True)
class AuthoritativePrerequisiteValidationStatusDerivation:
    """Bind one authoritative validation orchestration to its status.

    Vincula una orquestación de validación autoritativa con su estado.
    """

    orchestration: AuthoritativePrerequisiteValidationDerivation
    status: ValidationStatus


def derive_authoritative_prerequisite_validation_status(
    orchestration: AuthoritativePrerequisiteValidationDerivation,
) -> AuthoritativePrerequisiteValidationStatusDerivation:
    """Classify resolution without recalculating curricular derivations.

    Clasifica la resolución sin recalcular derivaciones curriculares.
    """
    context = orchestration.context_derivation.context
    if context is None:
        status: ValidationStatus = "failed"
    elif (
        orchestration.proof_derivation is None
        or orchestration.proof_derivation.result is None
    ):
        status = "failed"
    elif orchestration.conclusion_derivation is None:
        status = "failed"
    else:
        assessment_derivation = (
            orchestration.conclusion_derivation.assessment_derivation
        )
        has_derivation_errors = bool(
            assessment_derivation.consumption_errors
            or assessment_derivation.preparation_resolution_errors
        )
        has_error_findings = any(
            finding.severity == "error"
            for finding in orchestration.findings
        )
        if has_derivation_errors or has_error_findings:
            status = "failed"
        elif orchestration.conclusion_derivation.uncertainties:
            status = "pending"
        else:
            status = "passed"

    return AuthoritativePrerequisiteValidationStatusDerivation(
        orchestration=orchestration,
        status=status,
    )
