"""Represent logical active candidate source snapshots.

Representa snapshots lógicos de la source activa de candidatos.
"""

from dataclasses import dataclass

from app.services.pedagogical_active_candidate_membership_collection import (
    ActiveCandidateMembershipCollection,
)


@dataclass(frozen=True)
class ActiveCandidateSourceSnapshot:
    """Represent one immutable, revision-identified active source state.

    Representa un estado inmutable de source activa identificado por revisión.
    """

    snapshot_revision: str
    collection: ActiveCandidateMembershipCollection


def build_active_candidate_source_snapshot(
    collection: ActiveCandidateMembershipCollection,
    *,
    snapshot_revision: str,
) -> ActiveCandidateSourceSnapshot:
    """Build one logical active source snapshot from a conforming collection.

    Construye un snapshot lógico de source activa desde una collection conforme.
    """

    if not isinstance(snapshot_revision, str) or not snapshot_revision.strip():
        raise ValueError("snapshot_revision must be a non-blank string")
    if not isinstance(collection, ActiveCandidateMembershipCollection):
        raise ValueError(
            "collection must be an ActiveCandidateMembershipCollection"
        )

    return ActiveCandidateSourceSnapshot(
        snapshot_revision=snapshot_revision,
        collection=collection,
    )
