"""Derive a logical required-resource inventory from verified source evidence."""

from dataclasses import dataclass

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)


@dataclass(frozen=True)
class ActiveCandidateSourceRequiredResourceInventory:
    """Keep the stable logical resource inventory for one verified source."""

    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    )
    required_resource_ids: tuple[str, ...]


def build_active_candidate_source_required_resource_inventory(
    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    ),
) -> ActiveCandidateSourceRequiredResourceInventory:
    """Build a stable ordered union of declared required resource IDs."""

    if not isinstance(
        candidate_integrity_verification,
        ActiveCandidateSourceCandidateIntegrityVerification,
    ):
        raise ValueError(
            "candidate_integrity_verification must be an "
            "ActiveCandidateSourceCandidateIntegrityVerification"
        )

    resource_ids: list[str] = []
    seen_resource_ids: set[str] = set()

    for entry in candidate_integrity_verification.entries:
        candidate = PedagogicalUnitCandidate.model_validate_json(
            entry.candidate_bytes
        )
        for resource_id in candidate.required_resource_ids:
            if resource_id in seen_resource_ids:
                continue
            seen_resource_ids.add(resource_id)
            resource_ids.append(resource_id)

    return ActiveCandidateSourceRequiredResourceInventory(
        candidate_integrity_verification=candidate_integrity_verification,
        required_resource_ids=tuple(resource_ids),
    )
