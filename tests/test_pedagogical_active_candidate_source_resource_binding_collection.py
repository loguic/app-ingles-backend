from dataclasses import FrozenInstanceError, fields
import inspect
from pathlib import Path
from typing import cast

import pytest

import app.services.pedagogical_active_candidate_source_resource_binding_collection as bindings_module
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    ActiveCandidateSourceExpectedResourceCoverageVerification,
    verify_active_candidate_source_expected_resource_coverage,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    ActiveCandidateSourceRequiredResourceInventory,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def coverage_verification(
    *resource_ids: str,
) -> ActiveCandidateSourceExpectedResourceCoverageVerification:
    inventory = ActiveCandidateSourceRequiredResourceInventory(
        candidate_integrity_verification=cast(
            ActiveCandidateSourceCandidateIntegrityVerification,
            object(),
        ),
        required_resource_ids=resource_ids,
    )
    collection = build_expected_resource_identity_collection(
        [
            ResourcePhysicalIdentity(
                resource_id=resource_id,
                content_digest="manual",
            )
            for resource_id in resource_ids
        ]
    )
    return verify_active_candidate_source_expected_resource_coverage(
        inventory,
        collection,
    )


def binding(resource_id: str, path: str | None = None) -> bindings_module.ResourceBinding:
    return bindings_module.ResourceBinding(
        resource_id=resource_id,
        resource_path=Path(path or f"/declared/{resource_id or 'empty'}.resource"),
    )


def build(
    verification: ActiveCandidateSourceExpectedResourceCoverageVerification,
    resource_bindings: object,
) -> bindings_module.ActiveCandidateSourceResourceBindingCollection:
    return bindings_module.build_active_candidate_source_resource_binding_collection(
        verification,
        resource_bindings=resource_bindings,  # type: ignore[arg-type]
    )


def test_shape_is_frozen_and_preserves_coverage_and_binding_identity() -> None:
    verification = coverage_verification("r1")
    declared_binding = binding("r1")

    result = build(verification, [declared_binding])

    assert [field.name for field in fields(bindings_module.ResourceBinding)] == [
        "resource_id",
        "resource_path",
    ]
    assert [field.name for field in fields(result)] == [
        "expected_resource_coverage_verification",
        "bindings",
    ]
    assert result.expected_resource_coverage_verification is verification
    assert result.bindings == (declared_binding,)
    assert result.bindings[0] is declared_binding

    with pytest.raises(FrozenInstanceError):
        result.bindings = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        declared_binding.resource_id = "other"  # type: ignore[misc]


def test_result_uses_b46_representational_order_not_caller_order() -> None:
    verification = coverage_verification("r1", "r2")
    binding_r2 = binding("r2", "/declared/r2.resource")
    binding_r1 = binding("r1", "/declared/r1.resource")

    result = build(verification, (binding_r2, binding_r1))

    assert result.bindings == (binding_r1, binding_r2)
    assert result.bindings[0] is binding_r1
    assert result.bindings[1] is binding_r2


def test_empty_domain_and_empty_bindings_pass() -> None:
    result = build(coverage_verification(), [])

    assert result.bindings == ()


def test_rejects_invalid_coverage_verification_without_duck_typing() -> None:
    with pytest.raises(
        ValueError,
        match="ActiveCandidateSourceExpectedResourceCoverageVerification",
    ):
        build(cast(ActiveCandidateSourceExpectedResourceCoverageVerification, object()), [])


def test_resource_ids_are_preserved_and_compared_literally() -> None:
    resource_ids = ("", " ", "Áudio", "audio", "AUDIO")
    result = build(
        coverage_verification(*resource_ids),
        [binding(resource_id) for resource_id in reversed(resource_ids)],
    )

    assert [entry.resource_id for entry in result.bindings] == list(resource_ids)

    with pytest.raises(ValueError, match=r"missing resource_ids: \('audio',\)"):
        build(coverage_verification("audio"), [binding("AUDIO")])


def test_same_path_for_different_resource_ids_is_valid() -> None:
    shared_path = "/declared/shared.resource"

    result = build(
        coverage_verification("r1", "r2"),
        [binding("r1", shared_path), binding("r2", shared_path)],
    )

    assert result.bindings[0].resource_path == result.bindings[1].resource_path


@pytest.mark.parametrize(
    "declared_bindings",
    [
        [binding("r1", "/declared/a.resource"), binding("r1", "/declared/a.resource")],
        [binding("r1", "/declared/a.resource"), binding("r1", "/declared/b.resource")],
    ],
)
def test_duplicate_resource_id_fails_without_selecting_a_binding(
    declared_bindings: list[bindings_module.ResourceBinding],
) -> None:
    with pytest.raises(ValueError, match="duplicate"):
        build(coverage_verification("r1"), declared_bindings)


def test_missing_ids_are_reported_in_b46_order() -> None:
    with pytest.raises(
        ValueError,
        match=r"missing resource_ids: \('r3', 'r2'\)",
    ):
        build(
            coverage_verification("r3", "r1", "r2"),
            [binding("r1")],
        )


def test_unexpected_ids_are_reported_in_caller_order() -> None:
    with pytest.raises(
        ValueError,
        match=r"unexpected resource_ids: \('r4', 'r5'\)",
    ):
        build(
            coverage_verification("r1"),
            [binding("r4"), binding("r1"), binding("r5")],
        )


def test_combined_mismatch_reports_missing_and_unexpected_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            r"missing resource_ids: \('r2',\); "
            r"unexpected resource_ids: \('r3',\)"
        ),
    ):
        build(
            coverage_verification("r1", "r2"),
            [binding("r1"), binding("r3")],
        )


@pytest.mark.parametrize(
    ("verification", "declared_bindings", "message"),
    [
        (
            coverage_verification("r1"),
            [],
            r"missing resource_ids: \('r1',\)",
        ),
        (
            coverage_verification(),
            [binding("r1")],
            r"unexpected resource_ids: \('r1',\)",
        ),
    ],
)
def test_asymmetric_empty_domains_fail(
    verification: ActiveCandidateSourceExpectedResourceCoverageVerification,
    declared_bindings: list[bindings_module.ResourceBinding],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        build(verification, declared_bindings)


@pytest.mark.parametrize(
    "resource_bindings",
    ["", "r1", {binding("r1")}, (entry for entry in [binding("r1")])],
)
def test_rejects_non_sequence_resource_bindings(resource_bindings: object) -> None:
    with pytest.raises(ValueError, match="Sequence"):
        build(coverage_verification("r1"), resource_bindings)


class ResourceBindingSubclass(bindings_module.ResourceBinding):
    pass


@pytest.mark.parametrize(
    "declared_binding",
    [
        {"resource_id": "r1", "resource_path": Path("/declared/r1.resource")},
        ("r1", Path("/declared/r1.resource")),
        "r1",
        ResourceBindingSubclass("r1", Path("/declared/r1.resource")),
    ],
)
def test_rejects_non_exact_resource_binding_entries(declared_binding: object) -> None:
    with pytest.raises(ValueError, match="ResourceBinding"):
        build(coverage_verification("r1"), [declared_binding])


@pytest.mark.parametrize(
    "declared_binding, message",
    [
        (
            bindings_module.ResourceBinding(
                resource_id=cast(str, 1),
                resource_path=Path("/declared/r1.resource"),
            ),
            "resource_id",
        ),
        (
            bindings_module.ResourceBinding(
                resource_id="r1",
                resource_path=cast(Path, "/declared/r1.resource"),
            ),
            "resource_path must be a Path",
        ),
        (
            bindings_module.ResourceBinding(
                resource_id="r1",
                resource_path=Path("relative.resource"),
            ),
            "absolute",
        ),
    ],
)
def test_rejects_invalid_binding_fields(
    declared_binding: bindings_module.ResourceBinding,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        build(coverage_verification("r1"), [declared_binding])


def test_absolute_nonexistent_path_is_a_valid_declaration() -> None:
    declared_binding = binding("r1", "/definitely-not-present/r1.resource")

    result = build(coverage_verification("r1"), [declared_binding])

    assert result.bindings == (declared_binding,)


def test_materialization_isolated_from_caller_list_mutation() -> None:
    verification = coverage_verification("r1")
    bindings = [binding("r1")]

    result = build(verification, bindings)
    bindings.append(binding("other"))

    assert result.bindings == (bindings[0],)


def test_module_has_no_filesystem_or_later_stage_dependencies() -> None:
    source = inspect.getsource(bindings_module)

    for forbidden_reference in (
        ".resolve(",
        ".absolute(",
        ".expanduser(",
        ".exists(",
        ".is_file(",
        ".is_dir(",
        ".is_symlink(",
        ".stat(",
        ".open(",
        ".read_bytes(",
        "hashlib",
        "ResourcePhysicalIdentity",
        "PedagogicalUnitCandidate",
        "CandidatePayloadIdentity",
        "Admission",
        "B44",
    ):
        assert forbidden_reference not in source
