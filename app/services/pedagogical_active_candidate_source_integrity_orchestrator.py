"""Compose B38–B51 source-integrity evidence without composing B52."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateAdmissionRecordBinding,
    acquire_active_candidate_admission_records,
)
from app.services.pedagogical_active_candidate_admission_record_correspondence import (
    verify_active_candidate_admission_record_correspondence,
)
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
    reevaluate_active_candidate_current_admission_gates,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    verify_active_candidate_source_candidate_integrity,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
    acquire_active_candidate_source,
)
from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    verify_active_candidate_source_expected_resource_coverage,
)
from app.services.pedagogical_active_candidate_source_observed_resource_identity_collection import (
    derive_active_candidate_source_observed_resource_identities,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    build_active_candidate_source_required_resource_inventory,
)
from app.services.pedagogical_active_candidate_source_resource_acquisition import (
    acquire_active_candidate_source_resources,
)
from app.services.pedagogical_active_candidate_source_resource_integrity_verification import (
    ActiveCandidateSourceResourceIntegrityVerification,
    verify_active_candidate_source_resource_integrity,
)
from app.services.pedagogical_expected_resource_identity_collection_acquisition import (
    acquire_expected_resource_identity_collection,
)
from scripts.engineering.a1_resource_binding_adapter import (
    build_a1_resource_binding_collection,
)


@dataclass(frozen=True)
class ActiveCandidateSourceIntegrityOrchestration:
    """Keep separate B43 and B51 evidence for one shared B39 object."""

    current_admission_gate_reevaluation: (
        ActiveCandidateSourceCurrentAdmissionGateReevaluation
    )
    resource_integrity_verification: (
        ActiveCandidateSourceResourceIntegrityVerification
    )


def run_active_candidate_source_integrity(
    active_source_manifest_path: Path,
    *,
    candidate_bindings: Sequence[ActiveCandidateSourceBinding],
    admission_record_bindings: Sequence[ActiveCandidateAdmissionRecordBinding],
    expected_resource_identity_document_path: Path,
    repository_root: Path,
) -> ActiveCandidateSourceIntegrityOrchestration:
    """Run B38–B51 once, preserving one B39 and stopping before B52."""

    acquisition = acquire_active_candidate_source(
        active_source_manifest_path,
        candidate_bindings=candidate_bindings,
    )
    candidate_integrity_verification = (
        verify_active_candidate_source_candidate_integrity(acquisition)
    )

    admission_record_acquisition = acquire_active_candidate_admission_records(
        candidate_integrity_verification,
        admission_record_bindings=admission_record_bindings,
    )
    admission_record_correspondence = (
        verify_active_candidate_admission_record_correspondence(
            admission_record_acquisition
        )
    )
    current_admission_gate_reevaluation = (
        reevaluate_active_candidate_current_admission_gates(
            admission_record_correspondence
        )
    )

    expected_resource_identity_collection = (
        acquire_expected_resource_identity_collection(
            expected_resource_identity_document_path,
            candidate_integrity_verification=candidate_integrity_verification,
        )
    )
    required_resource_inventory = (
        build_active_candidate_source_required_resource_inventory(
            candidate_integrity_verification
        )
    )
    expected_resource_coverage = (
        verify_active_candidate_source_expected_resource_coverage(
            required_resource_inventory,
            expected_resource_identity_collection,
        )
    )
    resource_binding_collection = build_a1_resource_binding_collection(
        repository_root,
        expected_resource_coverage,
    )
    resource_acquisition = acquire_active_candidate_source_resources(
        resource_binding_collection
    )
    observed_resource_identity_collection = (
        derive_active_candidate_source_observed_resource_identities(
            resource_acquisition
        )
    )
    resource_integrity_verification = (
        verify_active_candidate_source_resource_integrity(
            observed_resource_identity_collection
        )
    )

    return ActiveCandidateSourceIntegrityOrchestration(
        current_admission_gate_reevaluation=current_admission_gate_reevaluation,
        resource_integrity_verification=resource_integrity_verification,
    )
