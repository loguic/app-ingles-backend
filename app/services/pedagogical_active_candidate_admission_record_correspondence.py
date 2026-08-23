"""Verify acquired admission record correspondence with active memberships.

Verifica la correspondencia de admission records adquiridos con memberships activas.
"""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateSourceAdmissionRecordAcquisition,
)


@dataclass(frozen=True)
class ActiveCandidateSourceAdmissionRecordCorrespondenceVerification:
    """Preserve B41 evidence after structural correspondence verification.

    Conserva evidencia B41 tras verificar correspondencia estructural.
    """

    admission_record_acquisition: ActiveCandidateSourceAdmissionRecordAcquisition


def verify_active_candidate_admission_record_correspondence(
    admission_record_acquisition: ActiveCandidateSourceAdmissionRecordAcquisition,
) -> ActiveCandidateSourceAdmissionRecordCorrespondenceVerification:
    """Verify every acquired record matches its already-associated membership.

    Verifica que cada record adquirido coincida con su membership ya asociada.
    """

    if not isinstance(
        admission_record_acquisition,
        ActiveCandidateSourceAdmissionRecordAcquisition,
    ):
        raise ValueError(
            "admission_record_acquisition must be an "
            "ActiveCandidateSourceAdmissionRecordAcquisition"
        )

    for entry in admission_record_acquisition.entries:
        if entry.admission_record.admission_id != entry.membership.admission_id:
            raise ValueError(
                "admission_id correspondence failure: expected "
                + entry.membership.admission_id
                + ", declared "
                + entry.admission_record.admission_id
            )
        if entry.admission_record.identity != entry.membership.identity:
            raise ValueError(
                "identity correspondence failure for unit_id: "
                + entry.membership.identity.unit_id
            )

    return ActiveCandidateSourceAdmissionRecordCorrespondenceVerification(
        admission_record_acquisition=admission_record_acquisition,
    )
