from dataclasses import FrozenInstanceError, fields

import pytest

from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    ActiveCandidateMembershipCollection,
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    ActiveCandidateSourceSnapshot,
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


def membership(
    unit_id: str,
    *,
    admission_id: str | None = None,
) -> ActiveCandidateMembership:
    return ActiveCandidateMembership(
        identity=CandidatePayloadIdentity(
            unit_id=unit_id,
            candidate_revision="revision-01",
            payload_schema_version="1.0",
            content_digest="sha256:" + "a" * 64,
        ),
        admission_id=admission_id or f"admission-{unit_id}",
    )


def collection(
    *memberships: ActiveCandidateMembership,
) -> ActiveCandidateMembershipCollection:
    return build_active_candidate_membership_collection(memberships)


def test_snapshot_has_exact_frozen_shape() -> None:
    snapshot = build_active_candidate_source_snapshot(
        collection(),
        snapshot_revision="snapshot-01",
    )

    assert isinstance(snapshot, ActiveCandidateSourceSnapshot)
    assert [field.name for field in fields(snapshot)] == [
        "snapshot_revision",
        "collection",
    ]

    with pytest.raises(FrozenInstanceError):
        snapshot.snapshot_revision = "snapshot-02"  # type: ignore[misc]


def test_snapshot_preserves_valid_revision_and_collection_by_identity() -> None:
    value = collection(membership("a1-u1"))

    snapshot = build_active_candidate_source_snapshot(
        value,
        snapshot_revision="  release-17  ",
    )

    assert snapshot.snapshot_revision == "  release-17  "
    assert snapshot.collection is value


@pytest.mark.parametrize("snapshot_revision", ["", "   ", 1])
def test_invalid_snapshot_revision_is_rejected(
    snapshot_revision: object,
) -> None:
    with pytest.raises(ValueError, match="snapshot_revision"):
        build_active_candidate_source_snapshot(
            collection(),
            snapshot_revision=snapshot_revision,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("invalid_collection", [None, ()])
def test_non_collection_is_rejected(invalid_collection: object) -> None:
    with pytest.raises(ValueError, match="collection"):
        build_active_candidate_source_snapshot(
            invalid_collection,  # type: ignore[arg-type]
            snapshot_revision="snapshot-01",
        )


def test_empty_collection_is_valid() -> None:
    value = collection()

    snapshot = build_active_candidate_source_snapshot(
        value,
        snapshot_revision="snapshot-empty",
    )

    assert snapshot.collection is value
    assert snapshot.collection.memberships == ()


def test_snapshot_inherits_collection_order_and_membership_identity() -> None:
    first = membership("unit-z")
    second = membership("unit-a")
    value = collection(first, second)

    snapshot = build_active_candidate_source_snapshot(
        value,
        snapshot_revision="snapshot-order",
    )

    assert snapshot.collection is value
    assert snapshot.collection.memberships == (first, second)
    assert snapshot.collection.memberships[0] is first
    assert snapshot.collection.memberships[1] is second


def test_same_revision_and_collection_are_structurally_equal() -> None:
    value = collection(membership("a1-u1"))

    first = build_active_candidate_source_snapshot(
        value,
        snapshot_revision="snapshot-01",
    )
    second = build_active_candidate_source_snapshot(
        value,
        snapshot_revision="snapshot-01",
    )

    assert first == second


def test_same_revision_with_different_collection_is_locally_valid() -> None:
    first = build_active_candidate_source_snapshot(
        collection(membership("a1-u1")),
        snapshot_revision="snapshot-01",
    )
    second = build_active_candidate_source_snapshot(
        collection(membership("a1-u2")),
        snapshot_revision="snapshot-01",
    )

    assert first != second
