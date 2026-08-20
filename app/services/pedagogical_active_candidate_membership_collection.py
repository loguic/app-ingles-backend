"""Collect active candidate memberships without publication concerns.

Agrupa membresías activas de candidatos sin responsabilidades de publicación.
"""

from dataclasses import dataclass
from typing import Sequence

from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)


@dataclass(frozen=True)
class ActiveCandidateMembershipCollection:
    """Represent one coherent collection of active candidate memberships.

    Representa una colección coherente de membresías activas de candidatos.
    """

    memberships: tuple[ActiveCandidateMembership, ...]


def build_active_candidate_membership_collection(
    memberships: Sequence[ActiveCandidateMembership],
) -> ActiveCandidateMembershipCollection:
    """Build an immutable collection with unique unit and admission identifiers.

    Construye una colección inmutable con unidades e identificadores de admission únicos.
    """

    collected_memberships = tuple(memberships)
    unit_ids: set[str] = set()
    admission_ids: set[str] = set()

    for membership in collected_memberships:
        unit_id = membership.identity.unit_id
        if unit_id in unit_ids:
            raise ValueError(
                f"duplicate active candidate membership unit_id: {unit_id}"
            )
        unit_ids.add(unit_id)

        admission_id = membership.admission_id
        if admission_id in admission_ids:
            raise ValueError(
                f"duplicate active candidate membership admission_id: {admission_id}"
            )
        admission_ids.add(admission_id)

    return ActiveCandidateMembershipCollection(
        memberships=collected_memberships,
    )
