"""Tests for expected-versus-observed resource integrity v1."""

from dataclasses import FrozenInstanceError, fields
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import app.services.pedagogical_active_candidate_source_resource_integrity_verification as integrity
from app.services.pedagogical_active_candidate_source_observed_resource_identity_collection import (
    ActiveCandidateSourceObservedResourceIdentityCollection,
    ObservedResourcePhysicalIdentity,
)
from app.services.pedagogical_active_candidate_source_resource_acquisition import (
    AcquiredResource,
    ActiveCandidateSourceResourceAcquisition,
)
from app.services.pedagogical_active_candidate_source_resource_binding_collection import (
    ResourceBinding,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def _identity(resource_id: str, content_digest: str) -> ResourcePhysicalIdentity:
    return ResourcePhysicalIdentity(
        resource_id=resource_id,
        content_digest=content_digest,
    )


def _observed_collection(
    expected_identities: tuple[ResourcePhysicalIdentity, ...],
    observed_identities: tuple[ResourcePhysicalIdentity, ...],
) -> ActiveCandidateSourceObservedResourceIdentityCollection:
    expected_resource_identity_collection = (
        build_expected_resource_identity_collection(expected_identities)
    )
    resource_binding_collection = SimpleNamespace(
        expected_resource_coverage_verification=SimpleNamespace(
            expected_resource_identity_collection=(
                expected_resource_identity_collection
            )
        )
    )
    acquired_resources = tuple(
        AcquiredResource(
            binding=ResourceBinding(
                resource_id=identity.resource_id,
                resource_path=Path(f"/declared/{index}"),
            ),
            resource_bytes=b"not used by B51",
        )
        for index, identity in enumerate(observed_identities)
    )
    acquisition = ActiveCandidateSourceResourceAcquisition(
        resource_binding_collection=cast(Any, resource_binding_collection),
        entries=acquired_resources,
    )
    return ActiveCandidateSourceObservedResourceIdentityCollection(
        resource_acquisition=acquisition,
        entries=tuple(
            ObservedResourcePhysicalIdentity(
                acquired_resource=acquired_resource,
                physical_identity=observed_identity,
            )
            for acquired_resource, observed_identity in zip(
                acquired_resources,
                observed_identities,
            )
        ),
    )


def test_public_shape_api_and_b50_identity_preservation() -> None:
    observed = _identity("r1", "sha256:one")
    collection = _observed_collection((observed,), (observed,))

    result = integrity.verify_active_candidate_source_resource_integrity(collection)

    assert [
        field.name
        for field in fields(
            integrity.ActiveCandidateSourceResourceIntegrityVerification
        )
    ] == ["observed_resource_identity_collection"]
    assert result.observed_resource_identity_collection is collection
    assert list(
        inspect.signature(
            integrity.verify_active_candidate_source_resource_integrity
        ).parameters
    ) == ["observed_resource_identity_collection"]
    with pytest.raises(FrozenInstanceError):
        result.observed_resource_identity_collection = collection  # type: ignore[misc]


def test_rejects_non_b50_input_without_duck_typing() -> None:
    duck = SimpleNamespace(resource_acquisition=object(), entries=())

    for invalid in (object(), duck, {}, (), []):
        with pytest.raises(
            ValueError,
            match="ActiveCandidateSourceObservedResourceIdentityCollection",
        ):
            integrity.verify_active_candidate_source_resource_integrity(
                cast(ActiveCandidateSourceObservedResourceIdentityCollection, invalid)
            )


def test_single_and_multiple_matching_identities_pass() -> None:
    single = _identity("r1", "sha256:one")
    single_collection = _observed_collection((single,), (single,))
    multiple = _observed_collection(
        (_identity("r1", "sha256:one"), _identity("r2", "sha256:two")),
        (single, _identity("r2", "sha256:two")),
    )

    single_result = integrity.verify_active_candidate_source_resource_integrity(
        single_collection
    )
    result = integrity.verify_active_candidate_source_resource_integrity(multiple)

    assert single_result.observed_resource_identity_collection is single_collection
    assert result.observed_resource_identity_collection is multiple


def test_expected_order_may_differ_from_observed_order() -> None:
    collection = _observed_collection(
        (_identity("r2", "sha256:two"), _identity("r1", "sha256:one")),
        (_identity("r1", "sha256:one"), _identity("r2", "sha256:two")),
    )

    result = integrity.verify_active_candidate_source_resource_integrity(collection)

    assert result.observed_resource_identity_collection is collection


def test_swapped_digests_fail_by_resource_id_not_positional_order() -> None:
    collection = _observed_collection(
        (_identity("r2", "sha256:two"), _identity("r1", "sha256:one")),
        (_identity("r1", "sha256:two"), _identity("r2", "sha256:one")),
    )

    with pytest.raises(
        ValueError,
        match=r"Resource integrity mismatch for resource_ids: r1, r2",
    ):
        integrity.verify_active_candidate_source_resource_integrity(collection)


def test_multiple_mismatches_report_b50_order_without_partial_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _observed_collection(
        (_identity("r1", "sha256:one"), _identity("r2", "sha256:two")),
        (_identity("r2", "sha256:wrong-two"), _identity("r1", "sha256:wrong-one")),
    )
    constructions: list[object] = []

    def track_result(**kwargs: object) -> object:
        constructions.append(kwargs)
        return object()

    monkeypatch.setattr(
        integrity,
        "ActiveCandidateSourceResourceIntegrityVerification",
        track_result,
    )

    with pytest.raises(
        ValueError,
        match=r"Resource integrity mismatch for resource_ids: r2, r1",
    ):
        integrity.verify_active_candidate_source_resource_integrity(collection)

    assert constructions == []


def test_empty_b50_is_positive_and_preserved_by_identity() -> None:
    collection = _observed_collection((), ())

    result = integrity.verify_active_candidate_source_resource_integrity(collection)

    assert result.observed_resource_identity_collection is collection


def test_same_digest_for_different_resource_ids_is_valid() -> None:
    collection = _observed_collection(
        (_identity("r1", "shared"), _identity("r2", "shared")),
        (_identity("r1", "shared"), _identity("r2", "shared")),
    )

    assert (
        integrity.verify_active_candidate_source_resource_integrity(collection)
        .observed_resource_identity_collection
        is collection
    )


def test_arbitrary_expected_digest_is_compared_literally() -> None:
    matching = _observed_collection(
        (_identity("  R ", "not-a-sha256-digest"),),
        (_identity("  R ", "not-a-sha256-digest"),),
    )
    mismatching = _observed_collection(
        (_identity("  R ", "not-a-sha256-digest"),),
        (_identity("  R ", "other"),),
    )

    assert (
        integrity.verify_active_candidate_source_resource_integrity(matching)
        .observed_resource_identity_collection
        is matching
    )
    with pytest.raises(
        ValueError,
        match=r"Resource integrity mismatch for resource_ids:   R ",
    ):
        integrity.verify_active_candidate_source_resource_integrity(mismatching)

    literal_id_mismatch = _observed_collection(
        (_identity("  R ", "not-a-sha256-digest"),),
        (_identity("R", "not-a-sha256-digest"),),
    )
    with pytest.raises(
        ValueError,
        match="missing expected resource identity for observed resource_id: R",
    ):
        integrity.verify_active_candidate_source_resource_integrity(
            literal_id_mismatch
        )


def test_missing_transitive_expected_identity_is_a_technical_contradiction() -> None:
    collection = _observed_collection(
        (_identity("r1", "sha256:one"),),
        (_identity("r2", "sha256:two"),),
    )

    with pytest.raises(
        ValueError,
        match="missing expected resource identity for observed resource_id: r2",
    ):
        integrity.verify_active_candidate_source_resource_integrity(collection)


def test_module_has_no_hash_filesystem_or_prior_verification_dependencies() -> None:
    source = inspect.getsource(integrity)

    for forbidden_reference in (
        "hashlib",
        "derive_resource_physical_identity",
        "resource_bytes",
        "Path",
        "open(",
        "read_bytes",
        "os.",
        "B39",
        "B43",
        "B47",
        "socket",
        "requests",
        "subprocess",
        "datetime",
        "time.",
        "random",
    ):
        assert forbidden_reference not in source
