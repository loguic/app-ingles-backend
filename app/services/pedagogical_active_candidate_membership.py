"""Active candidate membership declaration service.

Servicio de declaración de membresía activa de candidatos.
"""

from dataclasses import dataclass

from app.services.pedagogical_candidate_admission_verification import (
    AdmissionGateVerification,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


@dataclass(frozen=True)
class ActiveCandidateMembership:
    """Represent one explicitly declared active candidate revision.

    Representa una revisión exacta de candidato declarada explícitamente activa.
    """

    identity: CandidatePayloadIdentity
    admission_id: str


def declare_active_candidate_membership(
    admission_verification: AdmissionGateVerification,
) -> ActiveCandidateMembership:
    """Declare active membership from already verified admission evidence.

    Declara membresía activa a partir de evidencia de admisión ya verificada.
    """

    if not admission_verification.verified:
        raise ValueError(
            "Active candidate membership requires verified admission gates."
        )

    return ActiveCandidateMembership(
        identity=admission_verification.derived_identity,
        admission_id=admission_verification.admission_record.admission_id,
    )