"""Verify deterministic admission gates for one candidate and decision record."""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationReport,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_payload_identity import (
    PAYLOAD_SCHEMA_VERSION,
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


@dataclass(frozen=True)
class AdmissionGateVerification:
    """Preserve the evidence derived while verifying admission gates.

    Conserva la evidencia derivada al verificar las puertas de admission.
    """

    derived_identity: CandidatePayloadIdentity
    admission_record: AdmissionRecord
    local_validation_report: ValidationReport
    identity_matches: bool
    local_validation_passed: bool
    pending_human_decisions_clear: bool
    human_decision_admitted: bool

    @property
    def verified(self) -> bool:
        """Return whether every contractual admission gate is satisfied."""
        return (
            self.identity_matches
            and self.local_validation_passed
            and self.pending_human_decisions_clear
            and self.human_decision_admitted
        )


def verify_candidate_admission(
    candidate: PedagogicalUnitCandidate,
    admission_record: AdmissionRecord,
) -> AdmissionGateVerification:
    """Purely verify all admission gates for one typed candidate.

    Verifica de forma pura todas las puertas de admission de una candidata.
    """
    if (
        admission_record.identity.payload_schema_version
        != PAYLOAD_SCHEMA_VERSION
    ):
        raise ValueError("unsupported payload schema version")

    derived_identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision=admission_record.identity.candidate_revision,
    )
    local_validation_report = validate_pedagogical_candidate(candidate)

    return AdmissionGateVerification(
        derived_identity=derived_identity,
        admission_record=admission_record,
        local_validation_report=local_validation_report,
        identity_matches=derived_identity == admission_record.identity,
        local_validation_passed=(
            local_validation_report.status == "passed"
        ),
        pending_human_decisions_clear=(
            candidate.pending_human_decisions == []
        ),
        human_decision_admitted=(
            admission_record.decision == "admitted"
        ),
    )
