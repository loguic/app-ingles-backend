"""Derive the physical identity of one raw resource byte sequence."""

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class ResourcePhysicalIdentity:
    """Identify caller-associated raw resource bytes without storing them."""

    resource_id: str
    content_digest: str


def derive_resource_physical_identity(
    resource_bytes: bytes,
    *,
    resource_id: str,
) -> ResourcePhysicalIdentity:
    """Derive one deterministic SHA-256 identity from exact raw bytes."""

    if type(resource_bytes) is not bytes:
        raise TypeError("resource_bytes must be bytes")
    if type(resource_id) is not str:
        raise TypeError("resource_id must be str")

    return ResourcePhysicalIdentity(
        resource_id=resource_id,
        content_digest="sha256:" + hashlib.sha256(resource_bytes).hexdigest(),
    )
