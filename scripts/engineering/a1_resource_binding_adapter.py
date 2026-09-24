"""Adapt the canonical A1-U1 relative map into the B48 binding input."""

from pathlib import Path, PurePosixPath

from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    ActiveCandidateSourceExpectedResourceCoverageVerification,
)
from app.services.pedagogical_active_candidate_source_resource_binding_collection import (
    ActiveCandidateSourceResourceBindingCollection,
    ResourceBinding,
    build_active_candidate_source_resource_binding_collection,
)
from scripts.engineering.a1_resource_asset_close import (
    RESOURCE_ROOT,
    ResourceBinding as A1RelativeResourceBinding,
    load_binding_map,
)


def build_a1_resource_binding_collection(
    repository_root: Path,
    expected_resource_coverage_verification: (
        ActiveCandidateSourceExpectedResourceCoverageVerification
    ),
) -> ActiveCandidateSourceResourceBindingCollection:
    """Resolve the canonical A1 map and delegate exact-domain checks to B48."""

    root = _validate_repository_root(repository_root)
    resource_root = _resolve_resource_root(root)
    relative_bindings = load_binding_map(root)
    resource_bindings = tuple(
        _resolve_binding(
            root=root,
            resource_root=resource_root,
            relative_binding=relative_binding,
        )
        for relative_binding in relative_bindings
    )
    return build_active_candidate_source_resource_binding_collection(
        expected_resource_coverage_verification,
        resource_bindings=resource_bindings,
    )


def _validate_repository_root(repository_root: Path) -> Path:
    if not isinstance(repository_root, Path):
        raise ValueError("repository_root must be a Path")
    if not repository_root.is_absolute():
        raise ValueError("repository_root must be absolute")
    if not repository_root.exists() or not repository_root.is_dir():
        raise ValueError("repository_root must be an existing directory")
    return repository_root.resolve(strict=True)


def _resolve_resource_root(repository_root: Path) -> Path:
    resource_root = (repository_root / RESOURCE_ROOT).resolve(strict=False)
    try:
        resource_root.relative_to(repository_root)
    except ValueError as error:
        raise ValueError("A1 resource root escapes repository_root") from error
    return resource_root


def _resolve_binding(
    *,
    root: Path,
    resource_root: Path,
    relative_binding: A1RelativeResourceBinding,
) -> ResourceBinding:
    if not isinstance(relative_binding, A1RelativeResourceBinding):
        raise ValueError("canonical A1 binding map contains an invalid binding")
    relative_path = relative_binding.relative_path
    if not isinstance(relative_path, PurePosixPath):
        raise ValueError("canonical A1 binding path must be a PurePosixPath")
    if (
        not relative_path.parts
        or relative_path.is_absolute()
        or ".." in relative_path.parts
        or relative_path.as_posix() != str(relative_path)
    ):
        raise ValueError("canonical A1 binding path must remain relative")

    resource_path = (resource_root / Path(*relative_path.parts)).resolve(
        strict=False
    )
    try:
        resource_path.relative_to(root)
        resource_path.relative_to(resource_root)
    except ValueError as error:
        raise ValueError("canonical A1 binding path escapes its authorized root") from error

    return ResourceBinding(
        resource_id=relative_binding.resource_id,
        resource_path=resource_path,
    )
