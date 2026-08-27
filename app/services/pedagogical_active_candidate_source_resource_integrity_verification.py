"""Verify expected resource identities against observed B50 identities."""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_source_observed_resource_identity_collection import (
    ActiveCandidateSourceObservedResourceIdentityCollection,
)


@dataclass(frozen=True)
class ActiveCandidateSourceResourceIntegrityVerification:
    """Represent one source whose observed resource digests all match."""

    observed_resource_identity_collection: (
        ActiveCandidateSourceObservedResourceIdentityCollection
    )


def verify_active_candidate_source_resource_integrity(
    observed_resource_identity_collection: (
        ActiveCandidateSourceObservedResourceIdentityCollection
    ),
) -> ActiveCandidateSourceResourceIntegrityVerification:
    """Verify every B50 identity against its transitively expected digest."""

    if not isinstance(
        observed_resource_identity_collection,
        ActiveCandidateSourceObservedResourceIdentityCollection,
    ):
        raise ValueError(
            "observed_resource_identity_collection must be an "
            "ActiveCandidateSourceObservedResourceIdentityCollection"
        )

    expected_resource_identity_collection = (
        observed_resource_identity_collection.resource_acquisition
        .resource_binding_collection.expected_resource_coverage_verification
        .expected_resource_identity_collection
    )
    expected_identities_by_resource_id = {
        identity.resource_id: identity
        for identity in expected_resource_identity_collection.identities
    }
    mismatched_resource_ids: list[str] = []

    for observed_resource_identity in observed_resource_identity_collection.entries:
        observed_identity = observed_resource_identity.physical_identity
        try:
            expected_identity = expected_identities_by_resource_id[
                observed_identity.resource_id
            ]
        except KeyError as error:
            raise ValueError(
                "missing expected resource identity for observed resource_id: "
                + observed_identity.resource_id
            ) from error

        if expected_identity.content_digest != observed_identity.content_digest:
            mismatched_resource_ids.append(observed_identity.resource_id)

    if mismatched_resource_ids:
        raise ValueError(
            "Resource integrity mismatch for resource_ids: "
            + ", ".join(mismatched_resource_ids)
        )

    return ActiveCandidateSourceResourceIntegrityVerification(
        observed_resource_identity_collection=(
            observed_resource_identity_collection
        ),
    )
