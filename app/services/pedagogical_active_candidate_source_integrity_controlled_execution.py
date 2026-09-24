"""Run B38–B52 once while preserving the B39 object in memory."""

from collections.abc import Sequence
from pathlib import Path

from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateAdmissionRecordBinding,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
)
from app.services.pedagogical_active_candidate_source_integrity_orchestrator import (
    run_active_candidate_source_integrity,
)
from app.services.pedagogical_active_candidate_source_integrity_verification import (
    ActiveCandidateSourceIntegrityVerification,
    verify_active_candidate_source_integrity,
)


def run_active_candidate_source_integrity_controlled(
    active_source_manifest_path: Path,
    *,
    candidate_bindings: Sequence[ActiveCandidateSourceBinding],
    admission_record_bindings: Sequence[ActiveCandidateAdmissionRecordBinding],
    expected_resource_identity_document_path: Path,
    repository_root: Path,
) -> ActiveCandidateSourceIntegrityVerification:
    """Run B38–B51 once and immediately compose its B43 and B51 as B52."""

    orchestration = run_active_candidate_source_integrity(
        active_source_manifest_path,
        candidate_bindings=candidate_bindings,
        admission_record_bindings=admission_record_bindings,
        expected_resource_identity_document_path=(
            expected_resource_identity_document_path
        ),
        repository_root=repository_root,
    )
    return verify_active_candidate_source_integrity(
        orchestration.current_admission_gate_reevaluation,
        orchestration.resource_integrity_verification,
    )
