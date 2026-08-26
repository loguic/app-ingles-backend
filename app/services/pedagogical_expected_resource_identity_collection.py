"""Collect caller-declared expected resource identities."""

from collections.abc import Sequence
from dataclasses import dataclass

from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


@dataclass(frozen=True)
class ExpectedResourceIdentityCollection:
    """Represent one ordered declaration of expected resource identities."""

    identities: tuple[ResourcePhysicalIdentity, ...]


def build_expected_resource_identity_collection(
    identities: Sequence[ResourcePhysicalIdentity],
) -> ExpectedResourceIdentityCollection:
    """Build an immutable collection with unique resource identifiers."""

    if not isinstance(identities, Sequence) or isinstance(identities, str):
        raise ValueError("identities must be a Sequence")

    collected_identities = tuple(identities)
    resource_ids: set[str] = set()

    for identity in collected_identities:
        if type(identity) is not ResourcePhysicalIdentity:
            raise ValueError(
                "identities must contain ResourcePhysicalIdentity values"
            )

        if identity.resource_id in resource_ids:
            raise ValueError(
                "duplicate expected resource identity resource_id: "
                f"{identity.resource_id}"
            )
        resource_ids.add(identity.resource_id)

    return ExpectedResourceIdentityCollection(
        identities=collected_identities,
    )
