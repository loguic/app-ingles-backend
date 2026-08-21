"""Tests for active candidate source snapshot manifest publication."""

from pathlib import Path

from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    MANIFEST_SCHEMA_VERSION,
    publish_active_candidate_source_snapshot_manifest,
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)
import app.services.pedagogical_active_candidate_source_snapshot_manifest as manifest_module


def _membership(
    unit_id: str,
    *,
    candidate_revision: str = "candidate-r1",
    admission_id: str | None = None,
) -> ActiveCandidateMembership:
    return ActiveCandidateMembership(
        identity=CandidatePayloadIdentity(
            unit_id=unit_id,
            candidate_revision=candidate_revision,
            payload_schema_version="1.0",
            content_digest=f"sha256:{unit_id}",
        ),
        admission_id=admission_id or f"admission-{unit_id}",
    )


def _snapshot(
    snapshot_revision: str = "source-r1",
    *memberships: ActiveCandidateMembership,
):
    return build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(memberships),
        snapshot_revision=snapshot_revision,
    )


def test_serialization_has_exact_v1_shape_and_deterministic_bytes() -> None:
    snapshot = _snapshot(
        " source-r1 ",
        _membership("U2", candidate_revision="candidate-r2"),
        _membership("U1", candidate_revision="candidata-ñ"),
    )

    expected = (
        b'{"manifest_schema_version":"1.0","snapshot_revision":" source-r1 ",'
        b'"memberships":[{"identity":{"unit_id":"U2",'
        b'"candidate_revision":"candidate-r2","payload_schema_version":"1.0",'
        b'"content_digest":"sha256:U2"},"admission_id":"admission-U2"},'
        b'{"identity":{"unit_id":"U1","candidate_revision":"candidata-'
        b"\xc3\xb1\",\"payload_schema_version\":\"1.0\",\"content_digest\":\"sha256:U1\"},"
        b'"admission_id":"admission-U1"}]}\n'
    )

    assert MANIFEST_SCHEMA_VERSION == "1.0"
    assert serialize_active_candidate_source_snapshot_manifest(snapshot) == expected
    assert serialize_active_candidate_source_snapshot_manifest(snapshot) == expected


def test_empty_collection_serializes_as_an_empty_memberships_array() -> None:
    snapshot = _snapshot()

    assert serialize_active_candidate_source_snapshot_manifest(snapshot) == (
        b'{"manifest_schema_version":"1.0","snapshot_revision":"source-r1",'
        b'"memberships":[]}\n'
    )


def test_publish_creates_and_replaces_the_complete_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "active-manifest.json"
    first_snapshot = _snapshot("source-r1", _membership("U1"))
    second_snapshot = _snapshot("source-r2", _membership("U2"))

    publish_active_candidate_source_snapshot_manifest(
        first_snapshot,
        manifest_path=manifest_path,
    )
    assert manifest_path.read_bytes() == serialize_active_candidate_source_snapshot_manifest(
        first_snapshot
    )

    with manifest_path.open("rb") as first_descriptor:
        publish_active_candidate_source_snapshot_manifest(
            second_snapshot,
            manifest_path=manifest_path,
        )
        assert first_descriptor.read() == serialize_active_candidate_source_snapshot_manifest(
            first_snapshot
        )

    assert manifest_path.read_bytes() == serialize_active_candidate_source_snapshot_manifest(
        second_snapshot
    )


def test_publish_rejects_invalid_manifest_paths(tmp_path: Path) -> None:
    snapshot = _snapshot()
    target_directory = tmp_path / "directory-target"
    target_directory.mkdir()
    target_symlink = tmp_path / "symlink-target"
    target_symlink.symlink_to(tmp_path / "missing-target")
    parent_file = tmp_path / "parent-file"
    parent_file.write_text("not a directory", encoding="utf-8")

    for path in (
        Path("relative-manifest.json"),
        tmp_path / "missing-parent" / "manifest.json",
        parent_file / "manifest.json",
        target_directory,
        target_symlink,
    ):
        try:
            publish_active_candidate_source_snapshot_manifest(
                snapshot,
                manifest_path=path,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected invalid manifest path: {path}")


def test_replace_failure_keeps_previous_manifest_and_cleans_unpublished_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest_path = tmp_path / "active-manifest.json"
    first_snapshot = _snapshot("source-r1", _membership("U1"))
    publish_active_candidate_source_snapshot_manifest(
        first_snapshot,
        manifest_path=manifest_path,
    )
    original_bytes = manifest_path.read_bytes()

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(manifest_module.os, "replace", fail_replace)

    try:
        publish_active_candidate_source_snapshot_manifest(
            _snapshot("source-r2", _membership("U2")),
            manifest_path=manifest_path,
        )
    except OSError as error:
        assert str(error) == "replace failed"
    else:
        raise AssertionError("expected replace failure")

    assert manifest_path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".active-manifest.json.*.tmp")) == []


def test_file_fsync_failure_keeps_previous_manifest_and_cleans_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest_path = tmp_path / "active-manifest.json"
    first_snapshot = _snapshot("source-r1", _membership("U1"))
    publish_active_candidate_source_snapshot_manifest(
        first_snapshot,
        manifest_path=manifest_path,
    )
    original_bytes = manifest_path.read_bytes()

    def fail_file_fsync(descriptor: int) -> None:
        raise OSError("temporary file sync failed")

    def unexpected_replace(source: Path, target: Path) -> None:
        raise AssertionError("os.replace must not run after file fsync failure")

    monkeypatch.setattr(manifest_module.os, "fsync", fail_file_fsync)
    monkeypatch.setattr(manifest_module.os, "replace", unexpected_replace)

    try:
        publish_active_candidate_source_snapshot_manifest(
            _snapshot("source-r2", _membership("U2")),
            manifest_path=manifest_path,
        )
    except OSError as error:
        assert str(error) == "temporary file sync failed"
    else:
        raise AssertionError("expected temporary file fsync failure")

    assert manifest_path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".active-manifest.json.*.tmp")) == []


def test_cleanup_failure_does_not_mask_pre_replace_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest_path = tmp_path / "active-manifest.json"
    first_snapshot = _snapshot("source-r1", _membership("U1"))
    publish_active_candidate_source_snapshot_manifest(
        first_snapshot,
        manifest_path=manifest_path,
    )
    original_bytes = manifest_path.read_bytes()

    def fail_file_fsync(descriptor: int) -> None:
        raise OSError("temporary file sync failed")

    def fail_cleanup(path: Path) -> None:
        raise OSError("cleanup failed")

    monkeypatch.setattr(manifest_module.os, "fsync", fail_file_fsync)
    monkeypatch.setattr(manifest_module.Path, "unlink", fail_cleanup)

    try:
        publish_active_candidate_source_snapshot_manifest(
            _snapshot("source-r2", _membership("U2")),
            manifest_path=manifest_path,
        )
    except OSError as error:
        assert str(error) == "temporary file sync failed"
    else:
        raise AssertionError("expected temporary file fsync failure")

    assert manifest_path.read_bytes() == original_bytes


def test_directory_fsync_failure_reports_visible_but_unconfirmed_durability(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest_path = tmp_path / "active-manifest.json"
    snapshot = _snapshot("source-r1", _membership("U1"))

    def fail_directory_fsync(directory: Path) -> None:
        raise OSError("directory sync failed")

    monkeypatch.setattr(manifest_module, "_fsync_directory", fail_directory_fsync)

    try:
        publish_active_candidate_source_snapshot_manifest(
            snapshot,
            manifest_path=manifest_path,
        )
    except OSError as error:
        assert "visible but durable directory sync failed" in str(error)
    else:
        raise AssertionError("expected directory fsync failure")

    assert manifest_path.read_bytes() == serialize_active_candidate_source_snapshot_manifest(
        snapshot
    )
