"""Compose active-source integrity from preserved B43 and B51 evidence.

Compone la integridad de la source activa desde evidencia B43 y B51 preservada.
"""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
)
from app.services.pedagogical_active_candidate_source_resource_integrity_verification import (
    ActiveCandidateSourceResourceIntegrityVerification,
)


@dataclass(frozen=True)
class ActiveCandidateSourceIntegrityVerification:
    """Preserve positive admission and resource integrity for one B39 source.

    Conserva admission e integridad de recursos positivas para una source B39.
    """

    current_admission_gate_reevaluation: (
        ActiveCandidateSourceCurrentAdmissionGateReevaluation
    )
    resource_integrity_verification: (
        ActiveCandidateSourceResourceIntegrityVerification
    )


def verify_active_candidate_source_integrity(
    current_admission_gate_reevaluation: (
        ActiveCandidateSourceCurrentAdmissionGateReevaluation
    ),
    resource_integrity_verification: (
        ActiveCandidateSourceResourceIntegrityVerification
    ),
) -> ActiveCandidateSourceIntegrityVerification:
    """Compose B43 and B51 only when they preserve the same B39 object.

    Compone B43 y B51 solo cuando conservan exactamente el mismo objeto B39.
    """

    if not isinstance(
        current_admission_gate_reevaluation,
        ActiveCandidateSourceCurrentAdmissionGateReevaluation,
    ):
        raise ValueError(
            "current_admission_gate_reevaluation must be an "
            "ActiveCandidateSourceCurrentAdmissionGateReevaluation"
        )
    if not isinstance(
        resource_integrity_verification,
        ActiveCandidateSourceResourceIntegrityVerification,
    ):
        raise ValueError(
            "resource_integrity_verification must be an "
            "ActiveCandidateSourceResourceIntegrityVerification"
        )

    b43_candidate_integrity_verification = (
        current_admission_gate_reevaluation
        .admission_record_correspondence_verification
        .admission_record_acquisition
        .candidate_integrity_verification
    )
    b51_candidate_integrity_verification = (
        resource_integrity_verification
        .observed_resource_identity_collection
        .resource_acquisition
        .resource_binding_collection
        .expected_resource_coverage_verification
        .required_resource_inventory
        .candidate_integrity_verification
    )

    if b43_candidate_integrity_verification is not b51_candidate_integrity_verification:
        raise ValueError("active source integrity causal source mismatch")

    return ActiveCandidateSourceIntegrityVerification(
        current_admission_gate_reevaluation=(
            current_admission_gate_reevaluation
        ),
        resource_integrity_verification=resource_integrity_verification,
    )
