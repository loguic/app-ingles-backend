from dataclasses import FrozenInstanceError, fields
import inspect
from typing import cast

import pytest

import app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification as coverage
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    ActiveCandidateSourceRequiredResourceInventory,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    ExpectedResourceIdentityCollection,
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def required_inventory(
    *resource_ids: str,
) -> ActiveCandidateSourceRequiredResourceInventory:
    return ActiveCandidateSourceRequiredResourceInventory(
        candidate_integrity_verification=cast(
            ActiveCandidateSourceCandidateIntegrityVerification,
            object(),
        ),
        required_resource_ids=resource_ids,
    )


def expected_collection(
    *resource_ids: str,
    content_digest: str = "anything",
) -> ExpectedResourceIdentityCollection:
    return build_expected_resource_identity_collection(
        [
            ResourcePhysicalIdentity(
                resource_id=resource_id,
                content_digest=content_digest,
            )
            for resource_id in resource_ids
        ]
    )


def test_coverage_has_exact_frozen_shape_and_preserves_inputs() -> None:
    inventory = required_inventory("resource-a")
    collection = expected_collection("resource-a")

    result = coverage.verify_active_candidate_source_expected_resource_coverage(
        inventory,
        collection,
    )

    assert [field.name for field in fields(result)] == [
        "required_resource_inventory",
        "expected_resource_identity_collection",
    ]
    assert result.required_resource_inventory is inventory
    assert result.expected_resource_identity_collection is collection

    with pytest.raises(FrozenInstanceError):
        result.required_resource_inventory = inventory  # type: ignore[misc]


def test_multiple_resource_ids_pass_regardless_of_representational_order() -> None:
    inventory = required_inventory("r1", "r2", "r3")
    collection = expected_collection("r3", "r1", "r2")

    result = coverage.verify_active_candidate_source_expected_resource_coverage(
        inventory,
        collection,
    )

    assert result.required_resource_inventory is inventory
    assert result.expected_resource_identity_collection is collection


def test_empty_required_and_expected_domains_pass() -> None:
    result = coverage.verify_active_candidate_source_expected_resource_coverage(
        required_inventory(),
        expected_collection(),
    )

    assert isinstance(
        result,
        coverage.ActiveCandidateSourceExpectedResourceCoverageVerification,
    )


def test_resource_ids_are_compared_literally() -> None:
    resource_ids = ("", " ", "Áudio", "audio", "AUDIO")

    coverage.verify_active_candidate_source_expected_resource_coverage(
        required_inventory(*resource_ids),
        expected_collection(*resource_ids),
    )

    with pytest.raises(ValueError, match=r"missing resource_ids: \('Áudio',\)"):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            required_inventory("Áudio"),
            expected_collection("audio"),
        )


def test_arbitrary_and_shared_digests_do_not_affect_coverage() -> None:
    inventory = required_inventory("r1", "r2")
    collection = build_expected_resource_identity_collection(
        (
            ResourcePhysicalIdentity(resource_id="r1", content_digest="manual"),
            ResourcePhysicalIdentity(resource_id="r2", content_digest="manual"),
        )
    )

    result = coverage.verify_active_candidate_source_expected_resource_coverage(
        inventory,
        collection,
    )

    assert result.expected_resource_identity_collection is collection


def test_missing_ids_fail_in_required_inventory_order() -> None:
    with pytest.raises(
        ValueError,
        match=r"missing resource_ids: \('r3', 'r2'\)",
    ):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            required_inventory("r3", "r1", "r2"),
            expected_collection("r1"),
        )


def test_unexpected_ids_fail_in_expected_collection_order() -> None:
    with pytest.raises(
        ValueError,
        match=r"unexpected resource_ids: \('r4', 'r5'\)",
    ):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            required_inventory("r1"),
            expected_collection("r4", "r1", "r5"),
        )


def test_combined_mismatch_reports_missing_and_unexpected_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            r"missing resource_ids: \('r2',\); "
            r"unexpected resource_ids: \('r3',\)"
        ),
    ):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            required_inventory("r1", "r2"),
            expected_collection("r1", "r3"),
        )


@pytest.mark.parametrize(
    ("inventory", "collection", "message"),
    [
        (
            required_inventory("r1"),
            expected_collection(),
            r"missing resource_ids: \('r1',\)",
        ),
        (
            required_inventory(),
            expected_collection("r1"),
            r"unexpected resource_ids: \('r1',\)",
        ),
    ],
)
def test_asymmetric_empty_domains_fail(
    inventory: ActiveCandidateSourceRequiredResourceInventory,
    collection: ExpectedResourceIdentityCollection,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            inventory,
            collection,
        )


@pytest.mark.parametrize(
    ("inventory", "collection", "message"),
    [
        (
            object(),
            expected_collection("r1"),
            "ActiveCandidateSourceRequiredResourceInventory",
        ),
        (
            required_inventory("r1"),
            object(),
            "ExpectedResourceIdentityCollection",
        ),
    ],
)
def test_rejects_invalid_inputs_without_coercion(
    inventory: object,
    collection: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        coverage.verify_active_candidate_source_expected_resource_coverage(
            inventory,  # type: ignore[arg-type]
            collection,  # type: ignore[arg-type]
        )


def test_module_has_no_candidate_digest_or_io_dependencies() -> None:
    source = inspect.getsource(coverage)

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
        "PedagogicalUnitCandidate",
        "CandidatePayloadIdentity",
        "Admission",
        "ResourcePhysicalIdentity",
    ):
        assert forbidden_reference not in source
