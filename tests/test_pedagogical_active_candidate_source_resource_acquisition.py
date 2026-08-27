"""Tests for active candidate source resource acquisition v1."""

from dataclasses import FrozenInstanceError, fields
import inspect
import os
from pathlib import Path
from typing import Any, cast

import pytest

import app.services.pedagogical_active_candidate_source_resource_acquisition as acquisition_module
from app.services.pedagogical_active_candidate_source_resource_binding_collection import (
    ActiveCandidateSourceResourceBindingCollection,
    ResourceBinding,
)


def _binding(resource_id: str, resource_path: Path) -> ResourceBinding:
    return ResourceBinding(
        resource_id=resource_id,
        resource_path=resource_path,
    )


def _collection(
    *bindings: ResourceBinding,
) -> ActiveCandidateSourceResourceBindingCollection:
    return ActiveCandidateSourceResourceBindingCollection(
        expected_resource_coverage_verification=cast(Any, object()),
        bindings=bindings,
    )


def test_shapes_are_frozen_exact_and_preserve_b48_order_and_identity(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.resource"
    second_path = tmp_path / "second.resource"
    first_path.write_bytes(b"first\x00bytes")
    second_path.write_bytes(b"second bytes")
    first_binding = _binding("r2", first_path)
    second_binding = _binding("r1", second_path)
    collection = _collection(first_binding, second_binding)

    result = acquisition_module.acquire_active_candidate_source_resources(
        collection
    )

    assert [field.name for field in fields(acquisition_module.AcquiredResource)] == [
        "binding",
        "resource_bytes",
    ]
    assert [field.name for field in fields(result)] == [
        "resource_binding_collection",
        "entries",
    ]
    assert result.resource_binding_collection is collection
    assert [entry.binding for entry in result.entries] == [
        first_binding,
        second_binding,
    ]
    assert result.entries[0].binding is first_binding
    assert result.entries[1].binding is second_binding
    assert [entry.resource_bytes for entry in result.entries] == [
        b"first\x00bytes",
        b"second bytes",
    ]

    with pytest.raises(FrozenInstanceError):
        result.entries = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.entries[0].resource_bytes = b"changed"  # type: ignore[misc]


def test_rejects_non_b48_input_without_duck_typing() -> None:
    with pytest.raises(
        ValueError,
        match="ActiveCandidateSourceResourceBindingCollection",
    ):
        acquisition_module.acquire_active_candidate_source_resources(
            cast(ActiveCandidateSourceResourceBindingCollection, object())
        )


def test_empty_collection_performs_zero_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _collection()
    acquired_paths: list[Path] = []

    def track_read(resource_path: Path) -> bytes:
        acquired_paths.append(resource_path)
        return b"unexpected"

    monkeypatch.setattr(
        acquisition_module,
        "_read_regular_file_once",
        track_read,
    )

    result = acquisition_module.acquire_active_candidate_source_resources(
        collection
    )

    assert result.resource_binding_collection is collection
    assert result.entries == ()
    assert acquired_paths == []


def test_shared_path_is_acquired_once_and_reused_in_b48_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_path = Path("/declared/a.resource")
    second_path = Path("/declared/b.resource")
    bindings = (
        _binding("r1", first_path),
        _binding("r2", second_path),
        _binding("r3", first_path),
    )
    collection = _collection(*bindings)
    acquired_paths: list[Path] = []

    def track_read(resource_path: Path) -> bytes:
        acquired_paths.append(resource_path)
        return {
            first_path: b"shared bytes",
            second_path: b"other bytes",
        }[resource_path]

    monkeypatch.setattr(
        acquisition_module,
        "_read_regular_file_once",
        track_read,
    )

    result = acquisition_module.acquire_active_candidate_source_resources(
        collection
    )

    assert acquired_paths == [first_path, second_path]
    assert [entry.binding for entry in result.entries] == list(bindings)
    assert [entry.resource_bytes for entry in result.entries] == [
        b"shared bytes",
        b"other bytes",
        b"shared bytes",
    ]


def test_lexically_distinct_paths_are_acquired_separately(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    direct_path = tmp_path / "resource"
    traversing_path = tmp_path / "nested" / ".." / "resource"
    assert direct_path != traversing_path
    acquired_paths: list[Path] = []

    def track_read(resource_path: Path) -> bytes:
        acquired_paths.append(resource_path)
        return str(resource_path).encode()

    monkeypatch.setattr(
        acquisition_module,
        "_read_regular_file_once",
        track_read,
    )

    acquisition_module.acquire_active_candidate_source_resources(
        _collection(
            _binding("r1", direct_path),
            _binding("r2", traversing_path),
        )
    )

    assert acquired_paths == [direct_path, traversing_path]


def test_open_fstat_and_read_use_one_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resource_path = tmp_path / "resource.bin"
    resource_path.write_bytes(b"descriptor bytes")
    original_open = acquisition_module.os.open
    original_fstat = acquisition_module.os.fstat
    original_fdopen = acquisition_module.os.fdopen
    events: list[tuple[str, int]] = []
    captured_flags: list[int] = []

    def track_open(path: Path, flags: int) -> int:
        captured_flags.append(flags)
        resource_fd = original_open(path, flags)
        events.append(("open", resource_fd))
        return resource_fd

    def track_fstat(resource_fd: int):
        events.append(("fstat", resource_fd))
        return original_fstat(resource_fd)

    def track_fdopen(resource_fd: int, mode: str):
        events.append(("fdopen", resource_fd))
        return original_fdopen(resource_fd, mode)

    monkeypatch.setattr(acquisition_module.os, "open", track_open)
    monkeypatch.setattr(acquisition_module.os, "fstat", track_fstat)
    monkeypatch.setattr(acquisition_module.os, "fdopen", track_fdopen)

    result = acquisition_module._read_regular_file_once(resource_path)

    assert result == b"descriptor bytes"
    assert [name for name, _ in events] == ["open", "fstat", "fdopen"]
    assert len({resource_fd for _, resource_fd in events}) == 1
    assert captured_flags[0] & os.O_NOFOLLOW
    assert captured_flags[0] & os.O_NONBLOCK


def test_accepts_empty_regular_file(tmp_path: Path) -> None:
    resource_path = tmp_path / "empty.resource"
    resource_path.write_bytes(b"")

    result = acquisition_module.acquire_active_candidate_source_resources(
        _collection(_binding("empty", resource_path))
    )

    assert result.entries[0].resource_bytes == b""


def test_rejects_missing_directory_symlink_and_fifo_without_content_read(
    tmp_path: Path,
) -> None:
    regular_path = tmp_path / "regular.resource"
    regular_path.write_bytes(b"content")
    directory_path = tmp_path / "directory"
    directory_path.mkdir()
    symlink_path = tmp_path / "link.resource"
    symlink_path.symlink_to(regular_path)
    fifo_path = tmp_path / "resource.fifo"
    os.mkfifo(fifo_path)

    with pytest.raises(FileNotFoundError):
        acquisition_module._read_regular_file_once(tmp_path / "missing.resource")
    with pytest.raises(ValueError, match="regular file"):
        acquisition_module._read_regular_file_once(directory_path)
    with pytest.raises(OSError):
        acquisition_module._read_regular_file_once(symlink_path)
    with pytest.raises(ValueError, match="regular file"):
        acquisition_module._read_regular_file_once(fifo_path)


def test_failure_returns_no_partial_aggregate_and_stops_in_b48_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = tuple(Path(f"/declared/{index}.resource") for index in range(3))
    acquired_paths: list[Path] = []

    def fail_second(resource_path: Path) -> bytes:
        acquired_paths.append(resource_path)
        if resource_path == paths[1]:
            raise OSError("read failed")
        return b"bytes"

    monkeypatch.setattr(
        acquisition_module,
        "_read_regular_file_once",
        fail_second,
    )

    with pytest.raises(OSError, match="read failed"):
        acquisition_module.acquire_active_candidate_source_resources(
            _collection(
                *(
                    _binding(f"r{index}", resource_path)
                    for index, resource_path in enumerate(paths)
                )
            )
        )

    assert acquired_paths == [paths[0], paths[1]]


def test_preserved_bytes_remain_authoritative_after_path_changes(
    tmp_path: Path,
) -> None:
    resource_path = tmp_path / "resource.bin"
    resource_path.write_bytes(b"acquired bytes")

    result = acquisition_module.acquire_active_candidate_source_resources(
        _collection(_binding("r1", resource_path))
    )
    resource_path.write_bytes(b"later bytes")

    assert result.entries[0].resource_bytes == b"acquired bytes"


def test_module_has_no_revalidation_hashing_or_later_stage_dependencies() -> None:
    source = inspect.getsource(acquisition_module)

    for forbidden_reference in (
        ".resolve(",
        ".samefile(",
        ".exists(",
        ".is_file(",
        ".is_symlink(",
        ".read_bytes(",
        "hashlib",
        "ResourcePhysicalIdentity",
        "content_digest",
        "expected_resource_coverage_verification",
        "required_resource_ids",
    ):
        assert forbidden_reference not in source
