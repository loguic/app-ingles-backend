"""Derive a traceable authoritative prerequisite validation report.

Deriva un reporte trazable de validación autoritativa de prerequisites.
"""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import ValidationReport
from app.services.pedagogical_authoritative_prerequisite_report_findings import (
    AuthoritativePrerequisiteReportFindingDerivation,
)


@dataclass(frozen=True)
class AuthoritativePrerequisiteValidationReport:
    """Bind the canonical finding derivation to its serializable report.

    Vincula la derivación canónica de findings con su reporte serializable.

    The finding derivation remains the source of status, findings, structured
    causes, and traceability. ValidationReport is presentation only.
    """

    finding_derivation: AuthoritativePrerequisiteReportFindingDerivation
    report: ValidationReport


def derive_authoritative_prerequisite_validation_report(
    finding_derivation: AuthoritativePrerequisiteReportFindingDerivation,
) -> AuthoritativePrerequisiteValidationReport:
    """Represent an already-classified validation without recalculating it.

    Representa una validación ya clasificada sin volver a calcularla.
    """
    status = finding_derivation.status_derivation.status
    findings = finding_derivation.findings
    has_error = any(finding.severity == "error" for finding in findings)
    has_warning = any(finding.severity == "warning" for finding in findings)

    if status == "failed" and not has_error:
        raise ValueError("failed status requires at least one error finding")
    if status == "pending" and (has_error or not has_warning):
        raise ValueError(
            "pending status requires at least one warning and no error findings"
        )
    if status == "passed" and (has_error or has_warning):
        raise ValueError(
            "passed status cannot contain error or warning findings"
        )

    report = ValidationReport(
        status=status,
        findings=list(findings),
    )
    return AuthoritativePrerequisiteValidationReport(
        finding_derivation=finding_derivation,
        report=report,
    )
