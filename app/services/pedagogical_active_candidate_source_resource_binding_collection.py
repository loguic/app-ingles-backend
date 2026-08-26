"""Build exact local resource bindings for one covered active source."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    ActiveCandidateSourceExpectedResourceCoverageVerification,
)


@dataclass(frozen=True)
class ResourceBinding:
    """Declare one local absolute path for one logical resource identifier."""

    resource_id: str
    resource_path: Path


@dataclass(frozen=True)
class ActiveCandidateSourceResourceBindingCollection:
    """Keep exact declared resource bindings for one covered active source."""

    expected_resource_coverage_verification: (
        ActiveCandidateSourceExpectedResourceCoverageVerification
    )
    bindings: tuple[ResourceBinding, ...]


def build_active_candidate_source_resource_binding_collection(
    expected_resource_coverage_verification: (
        ActiveCandidateSourceExpectedResourceCoverageVerification
    ),
    *,
    resource_bindings: Sequence[ResourceBinding],
) -> ActiveCandidateSourceResourceBindingCollection:
    """Build exact, ordered, in-memory bindings for a covered resource domain."""

    if not isinstance(
        expected_resource_coverage_verification,
        ActiveCandidateSourceExpectedResourceCoverageVerification,
    ):
        raise ValueError(
            "expected_resource_coverage_verification must be an "
            "ActiveCandidateSourceExpectedResourceCoverageVerification"
        )
    if not isinstance(resource_bindings, Sequence) or isinstance(
        resource_bindings,
        str,
    ):
        raise ValueError("resource_bindings must be a Sequence")

    collected_bindings = tuple(resource_bindings)
    bindings_by_resource_id: dict[str, ResourceBinding] = {}

    for binding in collected_bindings:
        if type(binding) is not ResourceBinding:
            raise ValueError("resource_bindings must contain ResourceBinding values")
        if type(binding.resource_id) is not str:
            raise ValueError("resource binding resource_id must be a string")
        if not isinstance(binding.resource_path, Path):
            raise ValueError("resource binding resource_path must be a Path")
        if not binding.resource_path.is_absolute():
            raise ValueError("resource binding resource_path must be absolute")
        if binding.resource_id in bindings_by_resource_id:
            raise ValueError(
                "duplicate active candidate source resource binding resource_id: "
                + binding.resource_id
            )
        bindings_by_resource_id[binding.resource_id] = binding

    required_resource_ids = (
        expected_resource_coverage_verification.required_resource_inventory.required_resource_ids
    )
    required_resource_id_set = set(required_resource_ids)
    missing_resource_ids = tuple(
        resource_id
        for resource_id in required_resource_ids
        if resource_id not in bindings_by_resource_id
    )
    unexpected_resource_ids = tuple(
        binding.resource_id
        for binding in collected_bindings
        if binding.resource_id not in required_resource_id_set
    )
    if missing_resource_ids or unexpected_resource_ids:
        messages: list[str] = []
        if missing_resource_ids:
            messages.append(f"missing resource_ids: {missing_resource_ids}")
        if unexpected_resource_ids:
            messages.append(
                f"unexpected resource_ids: {unexpected_resource_ids}"
            )
        raise ValueError("resource binding domain mismatch: " + "; ".join(messages))

    return ActiveCandidateSourceResourceBindingCollection(
        expected_resource_coverage_verification=(
            expected_resource_coverage_verification
        ),
        bindings=tuple(
            bindings_by_resource_id[resource_id]
            for resource_id in required_resource_ids
        ),
    )
