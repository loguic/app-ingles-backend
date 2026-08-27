"""Derive observed physical identities from acquired resource evidence."""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_source_resource_acquisition import (
    AcquiredResource,
    ActiveCandidateSourceResourceAcquisition,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
    derive_resource_physical_identity,
)


@dataclass(frozen=True)
class ObservedResourcePhysicalIdentity:
    """Associate one preserved acquired resource with its derived identity."""

    acquired_resource: AcquiredResource
    physical_identity: ResourcePhysicalIdentity


@dataclass(frozen=True)
class ActiveCandidateSourceObservedResourceIdentityCollection:
    """Keep observed identities in the exact B49 acquisition order."""

    resource_acquisition: ActiveCandidateSourceResourceAcquisition
    entries: tuple[ObservedResourcePhysicalIdentity, ...]


def derive_active_candidate_source_observed_resource_identities(
    resource_acquisition: ActiveCandidateSourceResourceAcquisition,
) -> ActiveCandidateSourceObservedResourceIdentityCollection:
    """Derive one B44 identity for every acquired B49 resource."""

    if not isinstance(
        resource_acquisition,
        ActiveCandidateSourceResourceAcquisition,
    ):
        raise ValueError(
            "resource_acquisition must be an "
            "ActiveCandidateSourceResourceAcquisition"
        )

    derived_entries: list[tuple[AcquiredResource, ResourcePhysicalIdentity]] = []
    for acquired_resource in resource_acquisition.entries:
        physical_identity = derive_resource_physical_identity(
            acquired_resource.resource_bytes,
            resource_id=acquired_resource.binding.resource_id,
        )
        derived_entries.append((acquired_resource, physical_identity))

    entries = tuple(
        ObservedResourcePhysicalIdentity(
            acquired_resource=acquired_resource,
            physical_identity=physical_identity,
        )
        for acquired_resource, physical_identity in derived_entries
    )

    return ActiveCandidateSourceObservedResourceIdentityCollection(
        resource_acquisition=resource_acquisition,
        entries=entries,
    )
