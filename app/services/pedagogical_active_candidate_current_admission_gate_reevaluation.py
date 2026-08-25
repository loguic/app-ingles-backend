"""Reevaluate current admission gates from preserved active-source evidence."""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    AcquiredActiveCandidateAdmissionRecordEntry,
)
from app.services.pedagogical_active_candidate_admission_record_correspondence import (
    ActiveCandidateSourceAdmissionRecordCorrespondenceVerification,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    CandidatePayloadIntegrityVerification,
)
from app.services.pedagogical_candidate_admission_verification import (
    AdmissionGateVerification,
    verify_candidate_admission,
)


@dataclass(frozen=True)
class ActiveCandidateCurrentAdmissionGateReevaluationEntry:
    """Keep one current gate reevaluation linked to its preserved evidence."""

    candidate_integrity_verification: CandidatePayloadIntegrityVerification
    acquired_admission_record_entry: AcquiredActiveCandidateAdmissionRecordEntry
    admission_gate_verification: AdmissionGateVerification


@dataclass(frozen=True)
class ActiveCandidateSourceCurrentAdmissionGateReevaluation:
    """Represent one source whose current admission gates all verify."""

    admission_record_correspondence_verification: (
        ActiveCandidateSourceAdmissionRecordCorrespondenceVerification
    )
    entries: tuple[ActiveCandidateCurrentAdmissionGateReevaluationEntry, ...]


def reevaluate_active_candidate_current_admission_gates(
    admission_record_correspondence_verification: (
        ActiveCandidateSourceAdmissionRecordCorrespondenceVerification
    ),
) -> ActiveCandidateSourceCurrentAdmissionGateReevaluation:
    """Reevaluate every current admission gate from preserved B39/B41 evidence."""

    if not isinstance(
        admission_record_correspondence_verification,
        ActiveCandidateSourceAdmissionRecordCorrespondenceVerification,
    ):
        raise ValueError(
            "admission_record_correspondence_verification must be an "
            "ActiveCandidateSourceAdmissionRecordCorrespondenceVerification"
        )

    admission_record_acquisition = (
        admission_record_correspondence_verification.admission_record_acquisition
    )
    candidate_integrity_entries = (
        admission_record_acquisition.candidate_integrity_verification.entries
    )
    acquired_admission_record_entries = admission_record_acquisition.entries

    if len(candidate_integrity_entries) != len(acquired_admission_record_entries):
        raise ValueError("candidate and admission record entry alignment failure")

    entries: list[ActiveCandidateCurrentAdmissionGateReevaluationEntry] = []
    for (
        candidate_integrity_entry,
        acquired_admission_record_entry,
    ) in zip(
        candidate_integrity_entries,
        acquired_admission_record_entries,
        strict=True,
    ):
        if (
            candidate_integrity_entry.membership
            != acquired_admission_record_entry.membership
        ):
            raise ValueError(
                "candidate and admission record membership alignment failure"
            )

        reconstructed_candidate = PedagogicalUnitCandidate.model_validate_json(
            candidate_integrity_entry.candidate_bytes
        )
        admission_gate_verification = verify_candidate_admission(
            reconstructed_candidate,
            acquired_admission_record_entry.admission_record,
        )

        if not admission_gate_verification.identity_matches:
            raise ValueError("current admission gate identity contradiction")

        failed_gates = _failed_normal_gates(admission_gate_verification)
        if failed_gates:
            raise ValueError(
                "current admission gates not verified: "
                + ", ".join(failed_gates)
            )

        entries.append(
            ActiveCandidateCurrentAdmissionGateReevaluationEntry(
                candidate_integrity_verification=candidate_integrity_entry,
                acquired_admission_record_entry=acquired_admission_record_entry,
                admission_gate_verification=admission_gate_verification,
            )
        )

    return ActiveCandidateSourceCurrentAdmissionGateReevaluation(
        admission_record_correspondence_verification=(
            admission_record_correspondence_verification
        ),
        entries=tuple(entries),
    )


def _failed_normal_gates(
    admission_gate_verification: AdmissionGateVerification,
) -> tuple[str, ...]:
    failed_gates: list[str] = []
    if not admission_gate_verification.local_validation_passed:
        failed_gates.append("local_validation_passed")
    if not admission_gate_verification.pending_human_decisions_clear:
        failed_gates.append("pending_human_decisions_clear")
    if not admission_gate_verification.human_decision_admitted:
        failed_gates.append("human_decision_admitted")
    return tuple(failed_gates)
