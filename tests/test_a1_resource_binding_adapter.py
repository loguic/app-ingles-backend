"""Test adaptation of the canonical A1 map into the existing B48 boundary."""

import inspect
from pathlib import Path, PurePosixPath

import pytest

from app.services.pedagogical_active_candidate_integrity_verification import (
    verify_active_candidate_source_candidate_integrity,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
    acquire_active_candidate_source,
)
from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    ActiveCandidateSourceExpectedResourceCoverageVerification,
    verify_active_candidate_source_expected_resource_coverage,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    ActiveCandidateSourceRequiredResourceInventory,
    build_active_candidate_source_required_resource_inventory,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_expected_resource_identity_collection_acquisition import (
    acquire_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)
from scripts.engineering import a1_resource_binding_adapter as adapter
from scripts.engineering.a1_resource_asset_close import ResourceBinding as RelativeBinding


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "content/active-source/active-candidate-source-002.json"
CANDIDATE_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
EXPECTED_DOCUMENT_PATH = (
    ROOT / "content/expected-resource-identities/active-candidate-source-002.json"
)


def _coverage(*resource_ids: str) -> ActiveCandidateSourceExpectedResourceCoverageVerification:
    inventory = ActiveCandidateSourceRequiredResourceInventory(
        candidate_integrity_verification=object(),
        required_resource_ids=resource_ids,
    )
    expected = build_expected_resource_identity_collection(
        tuple(
            ResourcePhysicalIdentity(
                resource_id=resource_id,
                content_digest="sha256:" + "a" * 64,
            )
            for resource_id in resource_ids
        )
    )
    return verify_active_candidate_source_expected_resource_coverage(inventory, expected)


def _relative_binding(resource_id: str, relative_path: str) -> RelativeBinding:
    return RelativeBinding(resource_id, PurePosixPath(relative_path))


def _real_a1_coverage() -> ActiveCandidateSourceExpectedResourceCoverageVerification:
    acquisition = acquire_active_candidate_source(
        SOURCE_PATH,
        candidate_bindings=(ActiveCandidateSourceBinding("a1-u1", CANDIDATE_PATH),),
    )
    b39 = verify_active_candidate_source_candidate_integrity(acquisition)
    expected = acquire_expected_resource_identity_collection(
        EXPECTED_DOCUMENT_PATH,
        candidate_integrity_verification=b39,
    )
    return verify_active_candidate_source_expected_resource_coverage(
        build_active_candidate_source_required_resource_inventory(b39),
        expected,
    )


def test_real_a1_map_returns_exact_ordered_absolute_b48_bindings() -> None:
    coverage = _real_a1_coverage()

    result = adapter.build_a1_resource_binding_collection(ROOT, coverage)

    required_ids = coverage.required_resource_inventory.required_resource_ids
    assert result.expected_resource_coverage_verification is coverage
    assert len(result.bindings) == 18
    assert tuple(binding.resource_id for binding in result.bindings) == required_ids
    assert all(binding.resource_path.is_absolute() for binding in result.bindings)
    assert all(binding.resource_path.is_relative_to(ROOT) for binding in result.bindings)
    assert all(
        binding.resource_path.is_relative_to(ROOT / "content/resources/a1-u1")
        for binding in result.bindings
    )


def test_rejects_relative_missing_and_non_directory_roots(
    tmp_path: Path,
) -> None:
    coverage = _coverage("r1")
    with pytest.raises(ValueError, match="repository_root must be absolute"):
        adapter.build_a1_resource_binding_collection(Path("relative"), coverage)
    with pytest.raises(ValueError, match="existing directory"):
        adapter.build_a1_resource_binding_collection(tmp_path / "missing", coverage)
    file_root = tmp_path / "file"
    file_root.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="existing directory"):
        adapter.build_a1_resource_binding_collection(file_root, coverage)


@pytest.mark.parametrize(
    ("relative_path", "message"),
    (
        ("/etc/passwd", "remain relative"),
        ("../../etc/passwd", "remain relative"),
        ("../outside.wav", "remain relative"),
    ),
)
def test_rejects_absolute_traversal_and_resource_root_escape(
    monkeypatch: pytest.MonkeyPatch,
    relative_path: str,
    message: str,
) -> None:
    monkeypatch.setattr(
        adapter,
        "load_binding_map",
        lambda root: (_relative_binding("r1", relative_path),),
    )

    with pytest.raises(ValueError, match=message):
        adapter.build_a1_resource_binding_collection(ROOT, _coverage("r1"))


@pytest.mark.parametrize(
    ("bindings", "message"),
    (
        ((), "missing resource_ids"),
        ((_relative_binding("extra", "audio/extra.wav"),), "missing resource_ids"),
        (
            (
                _relative_binding("r1", "audio/one.wav"),
                _relative_binding("r1", "audio/two.wav"),
            ),
            "duplicate active candidate source resource binding resource_id",
        ),
    ),
)
def test_delegates_missing_extra_and_duplicate_id_rejection_to_b48(
    monkeypatch: pytest.MonkeyPatch,
    bindings: tuple[RelativeBinding, ...],
    message: str,
) -> None:
    monkeypatch.setattr(adapter, "load_binding_map", lambda root: bindings)

    with pytest.raises(ValueError, match=message):
        adapter.build_a1_resource_binding_collection(ROOT, _coverage("r1"))


def test_preserves_literal_ids_and_b47_order_without_resource_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        adapter,
        "load_binding_map",
        lambda root: (
            _relative_binding(" Áudio ", "visual/second.png"),
            _relative_binding("audio", "audio/first.wav"),
        ),
    )

    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("adapter must not open resource files")

    monkeypatch.setattr(Path, "open", fail_open)
    result = adapter.build_a1_resource_binding_collection(
        ROOT,
        _coverage("audio", " Áudio "),
    )

    assert tuple(binding.resource_id for binding in result.bindings) == (
        "audio",
        " Áudio ",
    )
    assert tuple(path.resource_path.name for path in result.bindings) == (
        "first.wav",
        "second.png",
    )


def test_module_stops_at_b48_without_resource_or_later_stage_dependencies() -> None:
    source = inspect.getsource(adapter)

    for forbidden_reference in (
        "hashlib",
        "read_bytes",
        ".open(",
        "acquire_active_candidate_source_resources",
        "derive_active_candidate_source_observed_resource_identities",
        "verify_active_candidate_source_resource_integrity",
        "verify_active_candidate_source_integrity",
    ):
        assert forbidden_reference not in source
