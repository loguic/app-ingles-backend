from dataclasses import FrozenInstanceError, fields

import pytest

from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    ActiveCandidateMembershipCollection,
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


def membership(
    unit_id: str,
    *,
    candidate_revision: str = "revision-01",
    admission_id: str | None = None,
    digest_marker: str = "a",
) -> ActiveCandidateMembership:
    return ActiveCandidateMembership(
        identity=CandidatePayloadIdentity(
            unit_id=unit_id,
            candidate_revision=candidate_revision,
            payload_schema_version="1.0",
            content_digest="sha256:" + digest_marker * 64,
        ),
        admission_id=admission_id or f"admission-{unit_id}",
    )


def test_collection_has_exact_frozen_shape() -> None:
    collection = build_active_candidate_membership_collection([])

    assert [field.name for field in fields(collection)] == ["memberships"]

    with pytest.raises(FrozenInstanceError):
        collection.memberships = ()  # type: ignore[misc]


def test_empty_collection_is_valid() -> None:
    assert build_active_candidate_membership_collection([]).memberships == ()


def test_one_membership_is_preserved_by_identity() -> None:
    value = membership("a1-u1")

    collection = build_active_candidate_membership_collection([value])

    assert collection.memberships == (value,)
    assert collection.memberships[0] is value


def test_distinct_units_are_valid() -> None:
    first = membership("a1-u1")
    second = membership("a1-u2")

    collection = build_active_candidate_membership_collection([first, second])

    assert collection.memberships == (first, second)


def test_preserves_input_order_without_sorting() -> None:
    first = membership("unit-z")
    second = membership("unit-a")
    third = membership("unit-m")

    collection = build_active_candidate_membership_collection(
        [first, second, third]
    )

    assert collection.memberships == (first, second, third)


def test_isolates_collection_from_later_caller_list_mutation() -> None:
    first = membership("a1-u1")
    second = membership("a1-u2")
    values = [first]

    collection = build_active_candidate_membership_collection(values)
    values.append(second)

    assert collection.memberships == (first,)


def test_duplicate_unit_with_same_identity_is_rejected() -> None:
    value = membership("a1-u1")

    with pytest.raises(ValueError):
        build_active_candidate_membership_collection([value, value])


def test_duplicate_unit_with_different_revision_is_rejected() -> None:
    first = membership("a1-u1", candidate_revision="revision-01")
    second = membership(
        "a1-u1",
        candidate_revision="revision-02",
        admission_id="admission-a1-u1-revision-02",
        digest_marker="b",
    )

    with pytest.raises(ValueError):
        build_active_candidate_membership_collection([first, second])


def test_duplicate_unit_error_identifies_unit_id() -> None:
    first = membership("a1-u1")
    second = membership(
        "a1-u1",
        candidate_revision="revision-02",
        admission_id="admission-a1-u1-revision-02",
    )

    with pytest.raises(ValueError, match="a1-u1"):
        build_active_candidate_membership_collection([first, second])


def test_duplicate_admission_id_across_distinct_units_is_rejected() -> None:
    first = membership("a1-u1", admission_id="admission-shared")
    second = membership("a1-u2", admission_id="admission-shared")

    with pytest.raises(ValueError):
        build_active_candidate_membership_collection([first, second])


def test_duplicate_admission_error_identifies_admission_id() -> None:
    first = membership("a1-u1", admission_id="admission-shared")
    second = membership("a1-u2", admission_id="admission-shared")

    with pytest.raises(ValueError, match="admission-shared"):
        build_active_candidate_membership_collection([first, second])


def test_same_revision_string_across_distinct_units_is_valid() -> None:
    first = membership("a1-u1", candidate_revision="revision-shared")
    second = membership("a1-u2", candidate_revision="revision-shared")

    collection = build_active_candidate_membership_collection([first, second])

    assert collection.memberships == (first, second)
