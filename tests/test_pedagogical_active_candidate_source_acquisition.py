from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path

import pytest

from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    AcquiredActiveCandidateSourceEntry,
    ActiveCandidateSourceAcquisition,
    ActiveCandidateSourceBinding,
    acquire_active_candidate_source,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_FIXTURE_PATH = (
    ROOT
    / "content"
    / "candidates"
    / "a1-u1"
    / "pedagogical-unit-candidate-v2.json"
)


def _candidate_bytes() -> bytes:
    return CANDIDATE_FIXTURE_PATH.read_bytes()


def _snapshot(
    unit_ids: tuple[str, ...] = ("a1-u1",),
    *,
    payload_schema_version: str = "1.0",
    snapshot_revision: str = "source-r1",
):
    memberships = tuple(
        ActiveCandidateMembership(
            identity=CandidatePayloadIdentity(
                unit_id=unit_id,
                candidate_revision=f"candidate-r{index}",
                payload_schema_version=payload_schema_version,
                content_digest="sha256:" + f"{index:064x}",
            ),
            admission_id=f"admission-{index}",
        )
        for index, unit_id in enumerate(unit_ids, start=1)
    )
    return build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(memberships),
        snapshot_revision=snapshot_revision,
    )


def _write_manifest(tmp_path: Path, snapshot) -> Path:
    manifest_path = tmp_path / "active-manifest.json"
    manifest_path.write_bytes(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    )
    return manifest_path


def _write_candidate(tmp_path: Path, name: str, raw_bytes: bytes | None = None) -> Path:
    candidate_path = tmp_path / name
    candidate_path.write_bytes(raw_bytes or _candidate_bytes())
    return candidate_path


def _bindings(snapshot, candidate_paths: tuple[Path, ...]):
    return tuple(
        ActiveCandidateSourceBinding(
            unit_id=membership.identity.unit_id,
            candidate_path=candidate_path,
        )
        for membership, candidate_path in zip(
            snapshot.collection.memberships,
            candidate_paths,
            strict=True,
        )
    )


def test_acquires_unverified_entries_in_manifest_order_and_preserves_bytes(
    tmp_path: Path,
):
    snapshot = _snapshot(("a1-u2", "a1-u1"))
    manifest_path = _write_manifest(tmp_path, snapshot)
    first_path = _write_candidate(tmp_path, "candidate-first.json")
    second_path = _write_candidate(tmp_path, "candidate-second.json")
    bindings = _bindings(snapshot, (first_path, second_path))

    acquisition = acquire_active_candidate_source(
        manifest_path,
        candidate_bindings=tuple(reversed(bindings)),
    )

    assert acquisition.snapshot == snapshot
    assert [entry.membership for entry in acquisition.entries] == list(
        snapshot.collection.memberships
    )
    assert [entry.candidate_path for entry in acquisition.entries] == [
        first_path,
        second_path,
    ]
    assert [entry.candidate_bytes for entry in acquisition.entries] == [
        _candidate_bytes(),
        _candidate_bytes(),
    ]
    assert all(entry.candidate.specification.unit_id == "a1-u1" for entry in acquisition.entries)


def test_accepts_empty_manifest_with_empty_bindings(tmp_path: Path):
    snapshot = _snapshot(())
    manifest_path = _write_manifest(tmp_path, snapshot)

    acquisition = acquire_active_candidate_source(
        manifest_path,
        candidate_bindings=(),
    )

    assert acquisition.snapshot == snapshot
    assert acquisition.entries == ()


def test_result_shapes_are_frozen_and_do_not_claim_deep_candidate_immutability(
    tmp_path: Path,
):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    candidate_path = _write_candidate(tmp_path, "candidate.json")

    acquisition = acquire_active_candidate_source(
        manifest_path,
        candidate_bindings=_bindings(snapshot, (candidate_path,)),
    )

    assert [field.name for field in fields(ActiveCandidateSourceBinding)] == [
        "unit_id",
        "candidate_path",
    ]
    assert [field.name for field in fields(AcquiredActiveCandidateSourceEntry)] == [
        "membership",
        "candidate_path",
        "candidate_bytes",
        "candidate",
    ]
    assert [field.name for field in fields(ActiveCandidateSourceAcquisition)] == [
        "snapshot",
        "entries",
    ]
    with pytest.raises(FrozenInstanceError):
        acquisition.entries = ()

    original_bytes = acquisition.entries[0].candidate_bytes
    acquisition.entries[0].candidate.proposed_change_summary.append("mutable")

    assert acquisition.entries[0].candidate_bytes == original_bytes


def test_rejects_manifest_that_is_not_byte_conformant(tmp_path: Path):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    manifest_path.write_bytes(
        serialize_active_candidate_source_snapshot_manifest(snapshot).rstrip(b"\n")
    )
    candidate_path = _write_candidate(tmp_path, "candidate.json")

    with pytest.raises(ValueError, match="byte-conformant"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=_bindings(snapshot, (candidate_path,)),
        )


def test_rejects_duplicate_manifest_json_key(tmp_path: Path):
    manifest_path = tmp_path / "active-manifest.json"
    manifest_path.write_bytes(
        b'{"manifest_schema_version":"1.0",'
        b'"manifest_schema_version":"1.0",'
        b'"snapshot_revision":"source-r1","memberships":[]}\n'
    )

    with pytest.raises(ValueError, match="valid JSON"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())


def test_rejects_manifest_invalid_utf8_bom_and_malformed_json(tmp_path: Path):
    manifest_path = tmp_path / "active-manifest.json"
    raw_values = (
        (b"\xff", "valid UTF-8"),
        (b"\xef\xbb\xbf{}", "BOM"),
        (b'{"manifest_schema_version":"1.0"', "valid JSON"),
    )

    for raw_bytes, message in raw_values:
        manifest_path.write_bytes(raw_bytes)
        with pytest.raises(ValueError, match=message):
            acquire_active_candidate_source(manifest_path, candidate_bindings=())


def test_rejects_manifest_unsupported_schema_and_invalid_shapes(tmp_path: Path):
    snapshot = _snapshot()
    document = json.loads(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    )
    manifest_path = tmp_path / "active-manifest.json"

    unsupported_schema = {**document, "manifest_schema_version": "2.0"}
    manifest_path.write_text(json.dumps(unsupported_schema), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())

    with_unknown_field = {**document, "unexpected": "value"}
    manifest_path.write_text(json.dumps(with_unknown_field), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())

    without_memberships = {
        key: value
        for key, value in document.items()
        if key != "memberships"
    }
    manifest_path.write_text(json.dumps(without_memberships), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())

    wrong_memberships_type = {**document, "memberships": {}}
    manifest_path.write_text(json.dumps(wrong_memberships_type), encoding="utf-8")
    with pytest.raises(ValueError, match="array"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())


def test_rejects_byte_nonconformant_manifest_key_order_whitespace_and_unicode(
    tmp_path: Path,
):
    snapshot = _snapshot((), snapshot_revision="source-é")
    document = json.loads(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    )
    manifest_path = tmp_path / "active-manifest.json"
    key_order_changed = {
        "snapshot_revision": document["snapshot_revision"],
        "manifest_schema_version": document["manifest_schema_version"],
        "memberships": document["memberships"],
    }
    raw_values = (
        json.dumps(
            key_order_changed,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n",
        json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
        json.dumps(
            document,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n",
    )

    for raw_bytes in raw_values:
        manifest_path.write_bytes(raw_bytes)
        with pytest.raises(ValueError, match="byte-conformant"):
            acquire_active_candidate_source(manifest_path, candidate_bindings=())


def test_rejects_missing_duplicate_and_unexpected_bindings(tmp_path: Path):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    candidate_path = _write_candidate(tmp_path, "candidate.json")
    binding = _bindings(snapshot, (candidate_path,))[0]

    with pytest.raises(ValueError, match="missing"):
        acquire_active_candidate_source(manifest_path, candidate_bindings=())
    with pytest.raises(ValueError, match="duplicate"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=(binding, binding),
        )
    with pytest.raises(ValueError, match="unexpected"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=(
                ActiveCandidateSourceBinding(
                    unit_id="a1-u2",
                    candidate_path=candidate_path,
                ),
            ),
        )


def test_rejects_relative_missing_directory_and_symlink_paths(tmp_path: Path):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    candidate_path = _write_candidate(tmp_path, "candidate.json")
    binding = _bindings(snapshot, (candidate_path,))[0]

    with pytest.raises(ValueError, match="manifest_path must be absolute"):
        acquire_active_candidate_source(
            Path("active-manifest.json"),
            candidate_bindings=(binding,),
        )
    with pytest.raises(ValueError, match="candidate_path must exist"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=(
                ActiveCandidateSourceBinding(
                    unit_id=binding.unit_id,
                    candidate_path=tmp_path / "missing.json",
                ),
            ),
        )
    with pytest.raises(ValueError, match="candidate_path must be a regular file"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=(
                ActiveCandidateSourceBinding(
                    unit_id=binding.unit_id,
                    candidate_path=tmp_path,
                ),
            ),
        )

    symlink_path = tmp_path / "candidate-symlink.json"
    symlink_path.symlink_to(candidate_path)
    with pytest.raises(ValueError, match="candidate_path must not be a symlink"):
        acquire_active_candidate_source(
            manifest_path,
            candidate_bindings=(
                ActiveCandidateSourceBinding(
                    unit_id=binding.unit_id,
                    candidate_path=symlink_path,
                ),
            ),
        )


def test_rejects_invalid_utf8_bom_and_duplicate_candidate_json(
    tmp_path: Path,
):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    raw_values = (
        b"\xff",
        b"\xef\xbb\xbf{}",
        b'{"candidate_unit":{},"candidate_unit":{}}',
    )

    for index, raw_bytes in enumerate(raw_values):
        candidate_path = _write_candidate(
            tmp_path,
            f"invalid-{index}.json",
            raw_bytes,
        )
        with pytest.raises(ValueError, match="valid UTF-8|BOM|valid JSON"):
            acquire_active_candidate_source(
                manifest_path,
                candidate_bindings=_bindings(snapshot, (candidate_path,)),
            )


def test_rejects_malformed_and_model_invalid_candidate_json(tmp_path: Path):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    raw_values = (b'{"candidate_unit":', b"{}")

    for index, raw_bytes in enumerate(raw_values):
        candidate_path = _write_candidate(
            tmp_path,
            f"candidate-invalid-{index}.json",
            raw_bytes,
        )
        with pytest.raises(ValueError):
            acquire_active_candidate_source(
                manifest_path,
                candidate_bindings=_bindings(snapshot, (candidate_path,)),
            )


def test_allows_noncanonical_candidate_bytes_and_unsupported_payload_schema(
    tmp_path: Path,
):
    snapshot = _snapshot(payload_schema_version="99.0")
    manifest_path = _write_manifest(tmp_path, snapshot)
    noncanonical_candidate_bytes = json.dumps(
        json.loads(_candidate_bytes().decode("utf-8")),
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    candidate_path = _write_candidate(
        tmp_path,
        "candidate-noncanonical.json",
        noncanonical_candidate_bytes,
    )

    acquisition = acquire_active_candidate_source(
        manifest_path,
        candidate_bindings=_bindings(snapshot, (candidate_path,)),
    )

    assert acquisition.snapshot == snapshot
    assert acquisition.entries[0].candidate_bytes == noncanonical_candidate_bytes


def test_opens_manifest_and_candidate_once_each(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    snapshot = _snapshot()
    manifest_path = _write_manifest(tmp_path, snapshot)
    candidate_path = _write_candidate(tmp_path, "candidate.json")
    original_open = Path.open
    opened_paths: list[Path] = []

    def track_open(path: Path, *args, **kwargs):
        if path in {manifest_path, candidate_path}:
            opened_paths.append(path)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", track_open)

    acquire_active_candidate_source(
        manifest_path,
        candidate_bindings=_bindings(snapshot, (candidate_path,)),
    )

    assert opened_paths == [manifest_path, candidate_path]
