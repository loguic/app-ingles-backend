"""Verify exact expected-resource coverage for one active source inventory."""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    ActiveCandidateSourceRequiredResourceInventory,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    ExpectedResourceIdentityCollection,
)


@dataclass(frozen=True)
class ActiveCandidateSourceExpectedResourceCoverageVerification:
    """Represent exact expected-resource coverage for one source inventory."""

    required_resource_inventory: ActiveCandidateSourceRequiredResourceInventory
    expected_resource_identity_collection: ExpectedResourceIdentityCollection


def verify_active_candidate_source_expected_resource_coverage(
    required_resource_inventory: ActiveCandidateSourceRequiredResourceInventory,
    expected_resource_identity_collection: ExpectedResourceIdentityCollection,
) -> ActiveCandidateSourceExpectedResourceCoverageVerification:
    """Verify that required and expected resource ID domains are identical."""

    if not isinstance(
        required_resource_inventory,
        ActiveCandidateSourceRequiredResourceInventory,
    ):
        raise ValueError(
            "required_resource_inventory must be an "
            "ActiveCandidateSourceRequiredResourceInventory"
        )
    if not isinstance(
        expected_resource_identity_collection,
        ExpectedResourceIdentityCollection,
    ):
        raise ValueError(
            "expected_resource_identity_collection must be an "
            "ExpectedResourceIdentityCollection"
        )

    required_resource_ids = set(required_resource_inventory.required_resource_ids)
    expected_resource_ids = {
        identity.resource_id
        for identity in expected_resource_identity_collection.identities
    }
    if required_resource_ids != expected_resource_ids:
        missing_resource_ids = tuple(
            resource_id
            for resource_id in required_resource_inventory.required_resource_ids
            if resource_id not in expected_resource_ids
        )
        unexpected_resource_ids = tuple(
            identity.resource_id
            for identity in expected_resource_identity_collection.identities
            if identity.resource_id not in required_resource_ids
        )
        messages: list[str] = []
        if missing_resource_ids:
            messages.append(f"missing resource_ids: {missing_resource_ids}")
        if unexpected_resource_ids:
            messages.append(
                f"unexpected resource_ids: {unexpected_resource_ids}"
            )
        raise ValueError("expected resource coverage mismatch: " + "; ".join(messages))

    return ActiveCandidateSourceExpectedResourceCoverageVerification(
        required_resource_inventory=required_resource_inventory,
        expected_resource_identity_collection=(
            expected_resource_identity_collection
        ),
    )
