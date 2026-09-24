"""Tests for read-only acquisition of source-bound expected identities."""

import hashlib
from pathlib import Path

import pytest

import app.services.pedagogical_expected_resource_identity_collection_acquisition as acquisition
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    verify_active_candidate_source_expected_resource_coverage,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    ActiveCandidateSourceRequiredResourceInventory,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_expected_resource_identity_collection_document import (
    build_expected_resource_identity_collection_document,
    serialize_expected_resource_identity_collection_document,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _b39(
    *,
    snapshot_revision: str = "source-r1",
) -> ActiveCandidateSourceCandidateIntegrityVerification:
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(()),
        snapshot_revision=snapshot_revision,
    )
    return ActiveCandidateSourceCandidateIntegrityVerification(snapshot=snapshot, entries=())


def _document_bytes(
    b39: ActiveCandidateSourceCandidateIntegrityVerification,
    identities: tuple[ResourcePhysicalIdentity, ...] = (
        ResourcePhysicalIdentity("resource-1", "sha256:" + "a" * 64),
    ),
) -> bytes:
    document = build_expected_resource_identity_collection_document(
        source_snapshot_revision=b39.snapshot.snapshot_revision,
        source_snapshot_manifest_digest=_digest(
            serialize_active_candidate_source_snapshot_manifest(b39.snapshot)
        ),
        identities=build_expected_resource_identity_collection(identities),
    )
    return serialize_expected_resource_identity_collection_document(document)


def test_acquires_canonical_document_once_and_returns_b45(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    b39 = _b39()
    path = tmp_path / "expected.json"
    expected_bytes = _document_bytes(
        b39,
        (
            ResourcePhysicalIdentity("  resource ", "sha256:" + "a" * 64),
            ResourcePhysicalIdentity("resource-2", "sha256:" + "a" * 64),
        ),
    )
    path.write_bytes(expected_bytes)
    reads: list[Path] = []
    original_read = acquisition._read_file_once

    def read_once(value: Path) -> bytes:
        reads.append(value)
        return original_read(value)

    monkeypatch.setattr(acquisition, "_read_file_once", read_once)
    result = acquisition.acquire_expected_resource_identity_collection(
        path, candidate_integrity_verification=b39
    )

    assert reads == [path]
    assert [item.resource_id for item in result.identities] == [
        "  resource ",
        "resource-2",
    ]
    assert result.identities[0].content_digest == "sha256:" + "a" * 64
    assert path.read_bytes() == expected_bytes


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        (b"\xef\xbb\xbf{}", "BOM"),
        (b"{", "valid JSON"),
        (
            b'{"document_schema_version":"1.0","document_schema_version":"1.0",'
            b'"source_snapshot_revision":"source-r1",'
            b'"source_snapshot_manifest_digest":"sha256:' + b"a" * 64 + b'",'
            b'"identities":[]}',
            "valid JSON",
        ),
        (
            b'{"document_schema_version":"2.0",'
            b'"source_snapshot_revision":"source-r1",'
            b'"source_snapshot_manifest_digest":"sha256:' + b"a" * 64 + b'",'
            b'"identities":[]}',
            "unsupported",
        ),
    ],
)
def test_rejects_bom_malformed_json_duplicate_keys_and_schema(
    payload: bytes,
    match: str,
    tmp_path: Path,
) -> None:
    path = tmp_path / "expected.json"
    path.write_bytes(payload)
    with pytest.raises(ValueError, match=match):
        acquisition.acquire_expected_resource_identity_collection(
            path, candidate_integrity_verification=_b39()
        )


def test_rejects_unknown_missing_invalid_and_noncanonical_documents(tmp_path: Path) -> None:
    b39 = _b39()
    canonical = _document_bytes(b39)
    variants = {
        "unknown": canonical.replace(b'"identities"', b'"unknown":true,"identities"'),
        "missing": canonical.replace(b',"identities":[{', b",\"removed\":[{"),
        "invalid-digest": canonical.replace(b"sha256:" + b"a" * 64, b"invalid"),
        "noncanonical": canonical[:-1] + b" \n",
    }
    for name, payload in variants.items():
        path = tmp_path / f"{name}.json"
        path.write_bytes(payload)
        with pytest.raises(ValueError):
            acquisition.acquire_expected_resource_identity_collection(
                path, candidate_integrity_verification=b39
            )


def test_rejects_duplicate_resource_ids_and_source_link_mismatches(tmp_path: Path) -> None:
    b39 = _b39()
    source_digest = _digest(
        serialize_active_candidate_source_snapshot_manifest(b39.snapshot)
    )
    duplicate = (
        b'{"document_schema_version":"1.0",'
        b'"source_snapshot_revision":"source-r1",'
        b'"source_snapshot_manifest_digest":"'
        + source_digest.encode("ascii")
        + b'","identities":['
        b'{"resource_id":"r1","content_digest":"sha256:'
        + b"a" * 64
        + b'"},{"resource_id":"r1","content_digest":"sha256:'
        + b"b" * 64
        + b'"}]}\n'
    )
    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_bytes(duplicate)
    with pytest.raises(ValueError, match="duplicate"):
        acquisition.acquire_expected_resource_identity_collection(
            duplicate_path, candidate_integrity_verification=b39
        )

    other_b39 = _b39(snapshot_revision="source-r2")
    path = tmp_path / "expected.json"
    path.write_bytes(_document_bytes(b39))
    with pytest.raises(ValueError, match="source revision mismatch"):
        acquisition.acquire_expected_resource_identity_collection(
            path, candidate_integrity_verification=other_b39
        )

    wrong_digest = _document_bytes(b39).replace(b"sha256:" + _digest(
        serialize_active_candidate_source_snapshot_manifest(b39.snapshot)
    ).removeprefix("sha256:").encode(), b"sha256:" + b"f" * 64)
    wrong_path = tmp_path / "wrong-digest.json"
    wrong_path.write_bytes(wrong_digest)
    with pytest.raises(ValueError, match="source manifest digest mismatch"):
        acquisition.acquire_expected_resource_identity_collection(
            wrong_path, candidate_integrity_verification=b39
        )


def test_rejects_missing_nonregular_symlink_and_invalid_b39(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="must exist"):
        acquisition.acquire_expected_resource_identity_collection(
            missing, candidate_integrity_verification=_b39()
        )
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="regular file"):
        acquisition.acquire_expected_resource_identity_collection(
            directory, candidate_integrity_verification=_b39()
        )
    path = tmp_path / "expected.json"
    path.write_bytes(_document_bytes(_b39()))
    symlink = tmp_path / "expected-link.json"
    symlink.symlink_to(path)
    with pytest.raises(ValueError, match="must not be a symlink"):
        acquisition.acquire_expected_resource_identity_collection(
            symlink, candidate_integrity_verification=_b39()
        )
    with pytest.raises(ValueError, match="candidate_integrity_verification"):
        acquisition.acquire_expected_resource_identity_collection(
            path, candidate_integrity_verification=object()  # type: ignore[arg-type]
        )


def test_acquired_b45_preserves_b47_missing_and_extra_behavior(tmp_path: Path) -> None:
    b39 = _b39()
    path = tmp_path / "expected.json"
    path.write_bytes(_document_bytes(b39, (ResourcePhysicalIdentity("r1", "sha256:" + "a" * 64),)))
    expected = acquisition.acquire_expected_resource_identity_collection(
        path, candidate_integrity_verification=b39
    )
    inventory = ActiveCandidateSourceRequiredResourceInventory(
        candidate_integrity_verification=b39,
        required_resource_ids=("r1", "r2"),
    )
    with pytest.raises(ValueError, match="missing resource_ids"):
        verify_active_candidate_source_expected_resource_coverage(inventory, expected)

    unexpected_path = tmp_path / "unexpected.json"
    unexpected_path.write_bytes(
        _document_bytes(
            b39,
            (
                ResourcePhysicalIdentity("r1", "sha256:" + "a" * 64),
                ResourcePhysicalIdentity("r3", "sha256:" + "b" * 64),
            ),
        )
    )
    unexpected = acquisition.acquire_expected_resource_identity_collection(
        unexpected_path, candidate_integrity_verification=b39
    )
    with pytest.raises(ValueError, match="unexpected resource_ids"):
        verify_active_candidate_source_expected_resource_coverage(
            ActiveCandidateSourceRequiredResourceInventory(
                candidate_integrity_verification=b39,
                required_resource_ids=("r1",),
            ),
            unexpected,
        )


def test_adapter_has_no_resource_or_b51_b52_dependencies() -> None:
    source = Path(acquisition.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "ResourceBinding",
        "acquire_active_candidate_source_resources",
        "derive_active_candidate_source_observed_resource_identities",
        "verify_active_candidate_source_resource_integrity",
        "verify_active_candidate_source_integrity",
        "resource_bytes",
    ):
        assert forbidden not in source
