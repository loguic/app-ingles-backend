"""Build one eligible runtime projection from one positive in-memory B52."""

import hashlib

from app.schemas.content import ContentTreeResponse, Level
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_resource_integrity_verification import (
    ActiveCandidateSourceResourceIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    ActiveCandidateSourceSnapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_runtime_activation_documents import (
    RuntimeContentProjectionDocumentV1,
    build_runtime_content_projection_document,
)
from app.services.pedagogical_active_candidate_source_integrity_verification import (
    ActiveCandidateSourceIntegrityVerification,
)


def build_eligible_runtime_content_projection(
    active_source_integrity: ActiveCandidateSourceIntegrityVerification,
) -> RuntimeContentProjectionDocumentV1:
    """Build one unpublishable projection from the sole eligible B52 source."""

    if not isinstance(
        active_source_integrity,
        ActiveCandidateSourceIntegrityVerification,
    ):
        raise ValueError(
            "active_source_integrity must be an "
            "ActiveCandidateSourceIntegrityVerification"
        )

    b43 = active_source_integrity.current_admission_gate_reevaluation
    b51 = active_source_integrity.resource_integrity_verification
    if not isinstance(b43, ActiveCandidateSourceCurrentAdmissionGateReevaluation):
        raise ValueError("active source integrity current admission evidence is invalid")
    if not isinstance(b51, ActiveCandidateSourceResourceIntegrityVerification):
        raise ValueError("active source integrity resource evidence is invalid")

    b43_candidate_integrity = (
        b43.admission_record_correspondence_verification
        .admission_record_acquisition
        .candidate_integrity_verification
    )
    b51_candidate_integrity = (
        b51.observed_resource_identity_collection
        .resource_acquisition
        .resource_binding_collection
        .expected_resource_coverage_verification
        .required_resource_inventory
        .candidate_integrity_verification
    )
    if b43_candidate_integrity is not b51_candidate_integrity:
        raise ValueError("active source integrity causal source mismatch")
    if not isinstance(
        b43_candidate_integrity,
        ActiveCandidateSourceCandidateIntegrityVerification,
    ):
        raise ValueError("active source integrity candidate evidence is invalid")

    snapshot = b43_candidate_integrity.snapshot
    if not isinstance(snapshot, ActiveCandidateSourceSnapshot):
        raise ValueError("active source integrity snapshot is invalid")
    memberships = snapshot.collection.memberships
    entries = b43_candidate_integrity.entries
    if len(memberships) != 1 or len(entries) != 1:
        raise ValueError("runtime projection v1 requires exactly one active candidate")

    entry = entries[0]
    membership = memberships[0]
    if entry.membership != membership:
        raise ValueError("runtime projection candidate membership mismatch")

    try:
        candidate = PedagogicalUnitCandidate.model_validate_json(entry.candidate_bytes)
    except (TypeError, ValueError) as error:
        raise ValueError("runtime projection candidate bytes are invalid") from error
    if candidate.candidate_unit.id != membership.identity.unit_id:
        raise ValueError("runtime projection candidate unit does not match membership")

    content_tree = ContentTreeResponse(
        levels=[
            Level(
                code=candidate.specification.level,
                units=[candidate.candidate_unit],
            )
        ]
    )
    manifest_digest = "sha256:" + hashlib.sha256(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    ).hexdigest()
    return build_runtime_content_projection_document(
        source_snapshot_revision=snapshot.snapshot_revision,
        source_snapshot_manifest_digest=manifest_digest,
        content_tree=content_tree,
    )
