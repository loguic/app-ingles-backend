"""Validate the durable A1 v4 expected-resource declaration as data."""

import hashlib
from pathlib import Path

from app.services.pedagogical_active_candidate_integrity_verification import (
    verify_active_candidate_source_candidate_integrity,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
    acquire_active_candidate_source,
)
from app.services.pedagogical_active_candidate_source_expected_resource_coverage_verification import (
    verify_active_candidate_source_expected_resource_coverage,
)
from app.services.pedagogical_active_candidate_source_required_resource_inventory import (
    build_active_candidate_source_required_resource_inventory,
)
from app.services.pedagogical_expected_resource_identity_collection_acquisition import (
    acquire_expected_resource_identity_collection,
)
from app.services.pedagogical_expected_resource_identity_collection_document import (
    build_expected_resource_identity_collection_document,
    serialize_expected_resource_identity_collection_document,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from scripts.engineering.a1_resource_asset_close import (
    RESOURCE_ROOT,
    load_binding_map,
    validate_binding_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "content/active-source/active-candidate-source-002.json"
CANDIDATE_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
DOCUMENT_PATH = (
    ROOT / "content/expected-resource-identities/active-candidate-source-002.json"
)


def test_a1_v4_expected_resource_identity_document_is_source_bound_and_complete() -> None:
    source = acquire_active_candidate_source(
        SOURCE_PATH,
        candidate_bindings=(
            ActiveCandidateSourceBinding("a1-u1", CANDIDATE_PATH),
        ),
    )
    b39 = verify_active_candidate_source_candidate_integrity(source)
    inventory = build_active_candidate_source_required_resource_inventory(b39)

    assert DOCUMENT_PATH.exists()
    assert DOCUMENT_PATH.is_file()
    assert not DOCUMENT_PATH.is_symlink()
    expected = acquire_expected_resource_identity_collection(
        DOCUMENT_PATH,
        candidate_integrity_verification=b39,
    )
    coverage = verify_active_candidate_source_expected_resource_coverage(
        inventory,
        expected,
    )

    assert b39.snapshot.snapshot_revision == "active-candidate-source-002"
    assert len(inventory.required_resource_ids) == 18
    assert len(expected.identities) == 18
    assert tuple(item.resource_id for item in expected.identities) == (
        inventory.required_resource_ids
    )
    assert coverage.expected_resource_identity_collection is expected

    manifest_digest = "sha256:" + hashlib.sha256(
        serialize_active_candidate_source_snapshot_manifest(b39.snapshot)
    ).hexdigest()
    document = build_expected_resource_identity_collection_document(
        source_snapshot_revision=b39.snapshot.snapshot_revision,
        source_snapshot_manifest_digest=manifest_digest,
        identities=expected,
    )
    assert serialize_expected_resource_identity_collection_document(document) == (
        DOCUMENT_PATH.read_bytes()
    )

    bindings = load_binding_map(ROOT)
    validate_binding_inventory(ROOT, bindings)
    binding_by_id = {binding.resource_id: binding for binding in bindings}
    assert tuple(binding_by_id) == inventory.required_resource_ids

    approved_asset_state = next(
        line
        for line in (ROOT / "docs/estado-operativo.md").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.startswith("A1 ASSET STATE:")
    )
    for identity in expected.identities:
        binding = binding_by_id[identity.resource_id]
        asset_path = ROOT / RESOURCE_ROOT / binding.relative_path
        assert asset_path.is_file()
        assert not asset_path.is_symlink()
        digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
        assert identity.content_digest == "sha256:" + digest
        assert identity.resource_id in approved_asset_state
        assert digest in approved_asset_state
