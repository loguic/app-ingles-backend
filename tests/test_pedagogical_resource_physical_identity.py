from dataclasses import FrozenInstanceError, fields
import inspect
import re

import pytest

from app.services import pedagogical_resource_physical_identity
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
    derive_resource_physical_identity,
)


def test_identity_contract_is_frozen_exact_and_does_not_store_bytes() -> None:
    result = derive_resource_physical_identity(
        b"resource bytes",
        resource_id="audio/example.wav",
    )

    assert [field.name for field in fields(result)] == [
        "resource_id",
        "content_digest",
    ]
    assert result.resource_id == "audio/example.wav"
    assert not hasattr(result, "resource_bytes")
    with pytest.raises(FrozenInstanceError):
        result.resource_id = "audio/other.wav"  # type: ignore[misc]


def test_digest_is_raw_bytes_sha256_golden_and_deterministic() -> None:
    resource_bytes = b"abc"

    result = derive_resource_physical_identity(
        resource_bytes,
        resource_id="audio/example.wav",
    )

    assert result == derive_resource_physical_identity(
        resource_bytes,
        resource_id="audio/example.wav",
    )
    assert result.content_digest == (
        "sha256:"
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", result.content_digest)


def test_changing_one_raw_byte_changes_digest() -> None:
    first = derive_resource_physical_identity(
        b"audio-data-1",
        resource_id="audio/example.wav",
    )
    changed = derive_resource_physical_identity(
        b"audio-data-2",
        resource_id="audio/example.wav",
    )

    assert first.content_digest != changed.content_digest


def test_empty_bytes_are_physically_identifiable() -> None:
    result = derive_resource_physical_identity(b"", resource_id="")

    assert result.resource_id == ""
    assert result.content_digest == (
        "sha256:"
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_resource_id_is_literal_and_outside_the_hash_preimage() -> None:
    resource_bytes = b"same resource bytes"
    first = derive_resource_physical_identity(
        resource_bytes,
        resource_id="  Audio/Á.WAV  ",
    )
    second = derive_resource_physical_identity(
        resource_bytes,
        resource_id="audio/other.wav",
    )

    assert first.resource_id == "  Audio/Á.WAV  "
    assert first.content_digest == second.content_digest
    assert first != second


@pytest.mark.parametrize(
    "invalid_resource_bytes",
    [bytearray(b"bytes"), memoryview(b"bytes"), "bytes", 1, None],
)
def test_resource_bytes_must_be_exactly_bytes(invalid_resource_bytes: object) -> None:
    with pytest.raises(TypeError, match="resource_bytes must be bytes"):
        derive_resource_physical_identity(
            invalid_resource_bytes,  # type: ignore[arg-type]
            resource_id="audio/example.wav",
        )


@pytest.mark.parametrize("invalid_resource_id", [b"resource", 1, None])
def test_resource_id_must_be_str(invalid_resource_id: object) -> None:
    with pytest.raises(TypeError, match="resource_id must be str"):
        derive_resource_physical_identity(
            b"bytes",
            resource_id=invalid_resource_id,  # type: ignore[arg-type]
        )


def test_derivation_hashes_the_exact_raw_bytes_without_transformation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resource_bytes = b"\xff\x00Cafe\xcc\x81\n"
    captured_inputs: list[bytes] = []
    original_sha256 = pedagogical_resource_physical_identity.hashlib.sha256

    def capture_sha256(value: bytes) -> object:
        captured_inputs.append(value)
        return original_sha256(value)

    monkeypatch.setattr(
        pedagogical_resource_physical_identity.hashlib,
        "sha256",
        capture_sha256,
    )

    derive_resource_physical_identity(
        resource_bytes,
        resource_id="audio/raw.bin",
    )

    assert captured_inputs == [resource_bytes]


def test_module_has_no_filesystem_network_clock_or_random_dependencies() -> None:
    source = inspect.getsource(pedagogical_resource_physical_identity)

    for forbidden_reference in (
        "Path",
        "open(",
        "socket",
        "requests",
        "subprocess",
        "datetime",
        "time.",
        "random",
        "json",
    ):
        assert forbidden_reference not in source
