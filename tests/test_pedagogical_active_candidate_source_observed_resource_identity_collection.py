"""Tests for observed physical identities from acquired resources v1."""

from dataclasses import FrozenInstanceError, fields
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import app.services.pedagogical_active_candidate_source_observed_resource_identity_collection as observed_module
from app.services.pedagogical_active_candidate_source_resource_acquisition import (
    AcquiredResource,
    ActiveCandidateSourceResourceAcquisition,
)
from app.services.pedagogical_active_candidate_source_resource_binding_collection import (
    ResourceBinding,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def _acquired(resource_id: str, resource_bytes: bytes, path: Path) -> AcquiredResource:
    return AcquiredResource(
        binding=ResourceBinding(
            resource_id=resource_id,
            resource_path=path,
        ),
        resource_bytes=resource_bytes,
    )


def _acquisition(
    *entries: AcquiredResource,
    resource_binding_collection: object | None = None,
) -> ActiveCandidateSourceResourceAcquisition:
    return ActiveCandidateSourceResourceAcquisition(
        resource_binding_collection=cast(
            Any,
            resource_binding_collection
            if resource_binding_collection is not None
            else object(),
        ),
        entries=entries,
    )


def test_public_shapes_and_api_are_frozen_and_exact() -> None:
    acquisition = _acquisition(
        _acquired("r1", b"bytes", Path("/declared/resource"))
    )

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert [
        field.name
        for field in fields(observed_module.ObservedResourcePhysicalIdentity)
    ] == ["acquired_resource", "physical_identity"]
    assert [field.name for field in fields(result)] == [
        "resource_acquisition",
        "entries",
    ]
    signature = inspect.signature(
        observed_module.derive_active_candidate_source_observed_resource_identities
    )
    assert list(signature.parameters) == ["resource_acquisition"]
    with pytest.raises(FrozenInstanceError):
        result.entries = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.entries[0].physical_identity = ResourcePhysicalIdentity(  # type: ignore[misc]
            resource_id="other",
            content_digest="sha256:other",
        )


def test_single_resource_uses_b44_digest_and_preserves_b49_objects() -> None:
    acquired_resource = _acquired(
        "  Audio/Á.WAV  ",
        b"abc",
        Path("/declared/resource"),
    )
    acquisition = _acquisition(acquired_resource)

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert result.resource_acquisition is acquisition
    assert result.entries[0].acquired_resource is acquired_resource
    assert result.entries[0].physical_identity.resource_id == "  Audio/Á.WAV  "
    assert result.entries[0].physical_identity.content_digest == (
        "sha256:"
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_empty_acquired_resource_bytes_have_the_b44_golden_digest() -> None:
    acquisition = _acquisition(
        _acquired("empty", b"", Path("/declared/empty"))
    )

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert result.entries[0].physical_identity == ResourcePhysicalIdentity(
        resource_id="empty",
        content_digest=(
            "sha256:"
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
    )


def test_multiple_resources_preserve_exact_order_and_identity() -> None:
    acquired_resources = (
        _acquired("r2", b"second", Path("/declared/second")),
        _acquired("r1", b"first", Path("/declared/first")),
        _acquired("r3", b"third", Path("/declared/third")),
    )
    acquisition = _acquisition(*acquired_resources)

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert tuple(entry.acquired_resource for entry in result.entries) == (
        acquired_resources
    )
    assert all(
        observed.acquired_resource is acquired
        for observed, acquired in zip(result.entries, acquired_resources)
    )
    assert [entry.physical_identity.resource_id for entry in result.entries] == [
        "r2",
        "r1",
        "r3",
    ]


def test_delegates_once_per_entry_with_exact_bytes_id_and_return_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acquired_resources = (
        _acquired(" Raw-ID ", b"\xff\x00raw", Path("/declared/a")),
        _acquired("r2", b"other", Path("/declared/b")),
    )
    acquisition = _acquisition(*acquired_resources)
    returned_identities = (
        ResourcePhysicalIdentity("first", "sha256:first"),
        ResourcePhysicalIdentity("second", "sha256:second"),
    )
    calls: list[tuple[bytes, str]] = []

    def derive(resource_bytes: bytes, *, resource_id: str) -> ResourcePhysicalIdentity:
        calls.append((resource_bytes, resource_id))
        return returned_identities[len(calls) - 1]

    monkeypatch.setattr(observed_module, "derive_resource_physical_identity", derive)

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert calls == [(b"\xff\x00raw", " Raw-ID "), (b"other", "r2")]
    assert calls[0][0] is acquired_resources[0].resource_bytes
    assert calls[1][0] is acquired_resources[1].resource_bytes
    assert result.entries[0].physical_identity is returned_identities[0]
    assert result.entries[1].physical_identity is returned_identities[1]


def test_same_path_and_bytes_with_different_ids_are_derived_separately(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shared_path = Path("/declared/shared")
    shared_bytes = b"shared bytes"
    acquisition = _acquisition(
        _acquired("r1", shared_bytes, shared_path),
        _acquired("r2", shared_bytes, shared_path),
    )
    calls: list[tuple[bytes, str]] = []
    original_derive = observed_module.derive_resource_physical_identity

    def track(resource_bytes: bytes, *, resource_id: str) -> ResourcePhysicalIdentity:
        calls.append((resource_bytes, resource_id))
        return original_derive(resource_bytes, resource_id=resource_id)

    monkeypatch.setattr(observed_module, "derive_resource_physical_identity", track)

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert calls == [(shared_bytes, "r1"), (shared_bytes, "r2")]
    assert len(result.entries) == 2
    assert [entry.physical_identity.resource_id for entry in result.entries] == [
        "r1",
        "r2",
    ]
    assert (
        result.entries[0].physical_identity.content_digest
        == result.entries[1].physical_identity.content_digest
    )
    assert (
        result.entries[0].physical_identity
        is not result.entries[1].physical_identity
    )


def test_empty_b49_is_positive_and_performs_zero_b44_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acquisition = _acquisition()
    calls: list[tuple[bytes, str]] = []

    def unexpected(resource_bytes: bytes, *, resource_id: str) -> ResourcePhysicalIdentity:
        calls.append((resource_bytes, resource_id))
        raise AssertionError("B44 must not be called")

    monkeypatch.setattr(
        observed_module,
        "derive_resource_physical_identity",
        unexpected,
    )

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    assert result.resource_acquisition is acquisition
    assert result.entries == ()
    assert calls == []


def test_rejects_non_b49_input_without_duck_typing() -> None:
    duck = SimpleNamespace(
        resource_binding_collection=object(),
        entries=(),
    )

    for invalid in (object(), duck, (), []):
        with pytest.raises(
            ValueError,
            match="ActiveCandidateSourceResourceAcquisition",
        ):
            observed_module.derive_active_candidate_source_observed_resource_identities(
                cast(ActiveCandidateSourceResourceAcquisition, invalid)
            )


def test_uses_preserved_bytes_after_original_path_changes(tmp_path: Path) -> None:
    resource_path = tmp_path / "resource.bin"
    resource_path.write_bytes(b"later filesystem bytes")
    acquired_resource = _acquired("r1", b"preserved bytes", resource_path)
    acquisition = _acquisition(acquired_resource)
    resource_path.unlink()

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    expected = observed_module.derive_resource_physical_identity(
        b"preserved bytes",
        resource_id="r1",
    )
    assert result.entries[0].physical_identity == expected


def test_transitive_expected_mismatch_is_ignored() -> None:
    expected_marker = SimpleNamespace(
        content_digest="sha256:deliberately-wrong",
    )
    transitive_b48 = SimpleNamespace(
        expected_resource_coverage_verification=SimpleNamespace(
            expected_resource_identity_collection=expected_marker
        )
    )
    acquisition = _acquisition(
        _acquired("r1", b"observed", Path("/declared/resource")),
        resource_binding_collection=transitive_b48,
    )

    result = observed_module.derive_active_candidate_source_observed_resource_identities(
        acquisition
    )

    expected_observed = observed_module.derive_resource_physical_identity(
        b"observed",
        resource_id="r1",
    )
    assert result.entries[0].physical_identity == expected_observed
    assert (
        result.entries[0].physical_identity.content_digest
        != expected_marker.content_digest
    )


def test_later_b44_failure_propagates_without_public_partial_aggregate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acquisition = _acquisition(
        _acquired("r1", b"first", Path("/declared/first")),
        _acquired("r2", b"second", Path("/declared/second")),
        _acquired("r3", b"third", Path("/declared/third")),
    )
    calls: list[str] = []
    observed_constructions: list[object] = []
    aggregate_constructions: list[object] = []

    def fail_second(
        resource_bytes: bytes,
        *,
        resource_id: str,
    ) -> ResourcePhysicalIdentity:
        calls.append(resource_id)
        if resource_id == "r2":
            raise TypeError("B44 failed")
        return ResourcePhysicalIdentity(resource_id, "sha256:derived")

    def track_aggregate(**kwargs: object) -> object:
        aggregate_constructions.append(kwargs)
        return object()

    def track_observed(**kwargs: object) -> object:
        observed_constructions.append(kwargs)
        return object()

    monkeypatch.setattr(
        observed_module,
        "derive_resource_physical_identity",
        fail_second,
    )
    monkeypatch.setattr(
        observed_module,
        "ActiveCandidateSourceObservedResourceIdentityCollection",
        track_aggregate,
    )
    monkeypatch.setattr(
        observed_module,
        "ObservedResourcePhysicalIdentity",
        track_observed,
    )

    with pytest.raises(TypeError, match="B44 failed"):
        observed_module.derive_active_candidate_source_observed_resource_identities(
            acquisition
        )

    assert calls == ["r1", "r2"]
    assert observed_constructions == []
    assert aggregate_constructions == []


def test_module_has_no_forbidden_boundary_dependencies_or_extra_results() -> None:
    source = inspect.getsource(observed_module)

    for forbidden_reference in (
        "hashlib",
        "ExpectedResourceIdentityCollection",
        "expected_resource",
        "content_digest",
        "Path",
        "open(",
        "read_bytes",
        "os.",
        "verified",
        "integrity",
        "status",
        "socket",
        "requests",
        "subprocess",
        "datetime",
        "time.",
        "random",
    ):
        assert forbidden_reference not in source

    result_fields = {
        field.name
        for result_type in (
            observed_module.ObservedResourcePhysicalIdentity,
            observed_module.ActiveCandidateSourceObservedResourceIdentityCollection,
        )
        for field in fields(result_type)
    }
    assert result_fields == {
        "acquired_resource",
        "physical_identity",
        "resource_acquisition",
        "entries",
    }
