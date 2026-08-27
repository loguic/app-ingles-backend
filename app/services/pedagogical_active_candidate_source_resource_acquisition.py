"""Acquire exact local resource bytes for one bound active candidate source."""

from dataclasses import dataclass
import os
from pathlib import Path
import stat

from app.services.pedagogical_active_candidate_source_resource_binding_collection import (
    ActiveCandidateSourceResourceBindingCollection,
    ResourceBinding,
)


@dataclass(frozen=True)
class AcquiredResource:
    """Preserve one original binding and its acquired raw bytes."""

    binding: ResourceBinding
    resource_bytes: bytes


@dataclass(frozen=True)
class ActiveCandidateSourceResourceAcquisition:
    """Keep acquired resource evidence in the original B48 order."""

    resource_binding_collection: ActiveCandidateSourceResourceBindingCollection
    entries: tuple[AcquiredResource, ...]


def acquire_active_candidate_source_resources(
    resource_binding_collection: ActiveCandidateSourceResourceBindingCollection,
) -> ActiveCandidateSourceResourceAcquisition:
    """Acquire each distinct declared Path once without integrity verification."""

    if not isinstance(
        resource_binding_collection,
        ActiveCandidateSourceResourceBindingCollection,
    ):
        raise ValueError(
            "resource_binding_collection must be an "
            "ActiveCandidateSourceResourceBindingCollection"
        )

    resource_bytes_by_path: dict[Path, bytes] = {}
    entries: list[AcquiredResource] = []

    for binding in resource_binding_collection.bindings:
        resource_path = binding.resource_path
        if resource_path not in resource_bytes_by_path:
            resource_bytes_by_path[resource_path] = _read_regular_file_once(
                resource_path
            )
        entries.append(
            AcquiredResource(
                binding=binding,
                resource_bytes=resource_bytes_by_path[resource_path],
            )
        )

    return ActiveCandidateSourceResourceAcquisition(
        resource_binding_collection=resource_binding_collection,
        entries=tuple(entries),
    )


def _read_regular_file_once(resource_path: Path) -> bytes:
    """Open, validate, and fully read one regular file from one descriptor."""

    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    resource_fd = os.open(resource_path, flags)
    try:
        descriptor_status = os.fstat(resource_fd)
        if not stat.S_ISREG(descriptor_status.st_mode):
            raise ValueError(
                "resource_path must reference a regular file: "
                + str(resource_path)
            )

        with os.fdopen(resource_fd, "rb") as resource_file:
            resource_fd = -1
            return resource_file.read()
    finally:
        if resource_fd != -1:
            os.close(resource_fd)
