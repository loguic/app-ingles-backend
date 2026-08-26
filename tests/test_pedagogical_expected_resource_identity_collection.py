from dataclasses import FrozenInstanceError, fields
import inspect

import pytest

from app.services import pedagogical_expected_resource_identity_collection
from app.services.pedagogical_expected_resource_identity_collection import (
    ExpectedResourceIdentityCollection,
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def identity(
    resource_id: str,
    *,
    content_digest: str = "sha256:" + "a" * 64,
) -> ResourcePhysicalIdentity:
    return ResourcePhysicalIdentity(
        resource_id=resource_id,
        content_digest=content_digest,
    )


def test_collection_has_exact_frozen_shape() -> None:
    collection = build_expected_resource_identity_collection([])

    assert isinstance(collection, ExpectedResourceIdentityCollection)
    assert [field.name for field in fields(collection)] == ["identities"]
    assert isinstance(collection.identities, tuple)

    with pytest.raises(FrozenInstanceError):
        collection.identities = ()  # type: ignore[misc]


def test_empty_collection_is_valid() -> None:
    assert build_expected_resource_identity_collection([]).identities == ()


def test_tuple_input_is_valid() -> None:
    value = identity("resource-a")

    collection = build_expected_resource_identity_collection((value,))

    assert collection.identities == (value,)


def test_single_identity_is_preserved_by_identity() -> None:
    value = identity("audio/example.wav")

    collection = build_expected_resource_identity_collection([value])

    assert collection.identities == (value,)
    assert collection.identities[0] is value


def test_multiple_identities_preserve_input_order_without_sorting() -> None:
    first = identity("resource-z")
    second = identity("resource-a")
    third = identity("resource-m")

    collection = build_expected_resource_identity_collection(
        [first, second, third]
    )

    assert collection.identities == (first, second, third)


def test_collection_isolated_from_later_caller_list_mutation() -> None:
    first = identity("resource-a")
    second = identity("resource-b")
    values = [first]

    collection = build_expected_resource_identity_collection(values)
    values.append(second)

    assert collection.identities == (first,)


def test_duplicate_resource_id_with_same_digest_is_rejected() -> None:
    value = identity("resource-a")

    with pytest.raises(ValueError, match="resource-a"):
        build_expected_resource_identity_collection([value, value])


def test_duplicate_resource_id_with_different_digest_is_rejected() -> None:
    first = identity("resource-a", content_digest="digest-a")
    second = identity("resource-a", content_digest="digest-b")

    with pytest.raises(ValueError, match="resource-a"):
        build_expected_resource_identity_collection([first, second])


def test_different_resource_ids_may_share_a_digest() -> None:
    first = identity("resource-a", content_digest="shared")
    second = identity("resource-b", content_digest="shared")

    collection = build_expected_resource_identity_collection([first, second])

    assert collection.identities == (first, second)


def test_resource_ids_are_preserved_literally_and_compared_exactly() -> None:
    empty = identity("")
    whitespace = identity("  ")
    unicode_case = identity("  Áudio/FILE.WAV  ")
    case_variant = identity("  áudio/file.wav  ")

    collection = build_expected_resource_identity_collection(
        [empty, whitespace, unicode_case, case_variant]
    )

    assert collection.identities == (
        empty,
        whitespace,
        unicode_case,
        case_variant,
    )


def test_manual_identity_with_arbitrary_digest_is_declared_as_expected() -> None:
    value = ResourcePhysicalIdentity(
        resource_id="manual-resource",
        content_digest="anything",
    )

    collection = build_expected_resource_identity_collection([value])

    assert collection.identities == (value,)
    assert collection.identities[0] is value


@pytest.mark.parametrize(
    "invalid_identity",
    [None, {"resource_id": "resource-a"}, ("resource-a", "digest"), "resource-a"],
)
def test_entries_must_be_resource_physical_identities(
    invalid_identity: object,
) -> None:
    with pytest.raises(ValueError, match="ResourcePhysicalIdentity"):
        build_expected_resource_identity_collection(
            [invalid_identity]  # type: ignore[list-item]
        )


def test_resource_physical_identity_subclasses_are_rejected() -> None:
    class ResourcePhysicalIdentitySubclass(ResourcePhysicalIdentity):
        pass

    value = ResourcePhysicalIdentitySubclass(
        resource_id="resource-a",
        content_digest="digest-a",
    )

    with pytest.raises(ValueError, match="ResourcePhysicalIdentity"):
        build_expected_resource_identity_collection([value])  # type: ignore[list-item]


@pytest.mark.parametrize("invalid_identities", ["", "resource-a"])
def test_string_input_is_rejected(invalid_identities: str) -> None:
    with pytest.raises(ValueError, match="Sequence"):
        build_expected_resource_identity_collection(invalid_identities)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_identities",
    [
        {identity("resource-a")},
        (item for item in [identity("resource-a")]),
    ],
)
def test_input_must_be_a_sequence(invalid_identities: object) -> None:

    with pytest.raises(ValueError, match="Sequence"):
        build_expected_resource_identity_collection(invalid_identities)  # type: ignore[arg-type]


def test_module_has_no_resource_or_source_io_dependencies() -> None:
    source = inspect.getsource(pedagogical_expected_resource_identity_collection)

    for forbidden_reference in (
        "Path",
        "open(",
        "socket",
        "requests",
        "subprocess",
        "datetime",
        "time.",
        "random",
        "hashlib",
        "ActiveCandidate",
        "PedagogicalUnitCandidate",
        "AdmissionRecord",
        "required_resource_ids",
    ):
        assert forbidden_reference not in source
