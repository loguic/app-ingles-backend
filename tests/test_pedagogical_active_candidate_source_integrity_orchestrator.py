"""Test synthetic B38–B51 orchestration with one shared B39."""

from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path

import pytest

import app.services.pedagogical_active_candidate_source_integrity_orchestrator as orchestrator
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateAdmissionRecordBinding,
)
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    serialize_candidate_admission_record_document,
)
from app.services.pedagogical_candidate_payload_identity import (
    derive_candidate_payload_identity,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_expected_resource_identity_collection_document import (
    build_expected_resource_identity_collection_document,
    serialize_expected_resource_identity_collection_document,
)
from app.services.pedagogical_resource_physical_identity import (
    derive_resource_physical_identity,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_CANDIDATE_PATH = (
    ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
)


def _resource_bytes() -> dict[str, bytes]:
    payload = json.loads(BASE_CANDIDATE_PATH.read_text(encoding="utf-8"))
    return {
        resource_id: f"synthetic bytes for {resource_id}".encode()
        for resource_id in payload["required_resource_ids"]
    }


def _write_synthetic_source(
    tmp_path: Path,
    *,
    decision: str = "admitted",
    expected_resource_ids: tuple[str, ...] | None = None,
) -> dict[str, object]:
    repository_root = tmp_path / "repository"
    resource_root = repository_root / "content/resources/a1-u1"
    (resource_root / "audio").mkdir(parents=True)
    (resource_root / "visual").mkdir()
    candidate_directory = repository_root / "candidates"
    candidate_directory.mkdir()
    admission_directory = repository_root / "admissions"
    admission_directory.mkdir()
    expected_directory = repository_root / "expected"
    expected_directory.mkdir()
    manifest_directory = repository_root / "active-source"
    manifest_directory.mkdir()

    candidate_payload = json.loads(BASE_CANDIDATE_PATH.read_text(encoding="utf-8"))
    candidate_payload["pending_human_decisions"] = []
    candidate_payload["proposed_change_summary"] = ["Synthetic fixture only."]
    candidate_path = candidate_directory / "candidate.json"
    candidate_path.write_text(
        json.dumps(candidate_payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    candidate = PedagogicalUnitCandidate.model_validate(candidate_payload)
    identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision="synthetic-candidate-v1",
    )
    membership = ActiveCandidateMembership(
        identity=identity,
        admission_id="synthetic-admission-1",
    )
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection((membership,)),
        snapshot_revision="synthetic-source-1",
    )
    manifest_path = manifest_directory / "source.json"
    manifest_path.write_bytes(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    )

    admission_path = admission_directory / "admission.json"
    admission_path.write_bytes(
        serialize_candidate_admission_record_document(
            AdmissionRecord(
                admission_id=membership.admission_id,
                identity=identity,
                decision=decision,  # type: ignore[arg-type]
                reviewer_id="synthetic-reviewer",
                decided_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
            )
        )
    )

    resource_bytes = _resource_bytes()
    relative_paths = tuple(
        (resource_id, f"audio/resource-{index}.bin")
        for index, resource_id in enumerate(resource_bytes, start=1)
    )
    for resource_id, relative_path in relative_paths:
        path = resource_root / relative_path
        path.write_bytes(resource_bytes[resource_id])
    (resource_root / "README.md").write_text(
        "\n".join(
            (
                "# Synthetic A1 bindings",
                "",
                "| resource_id | relative path |",
                "| --- | --- |",
                *(
                    f"| {resource_id} | {relative_path} |"
                    for resource_id, relative_path in relative_paths
                ),
                "",
            )
        ),
        encoding="utf-8",
    )

    selected_ids = expected_resource_ids or tuple(resource_bytes)
    identities = build_expected_resource_identity_collection(
        tuple(
            derive_resource_physical_identity(
                resource_bytes[resource_id],
                resource_id=resource_id,
            )
            for resource_id in selected_ids
        )
    )
    manifest_digest = "sha256:" + hashlib.sha256(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    ).hexdigest()
    document = build_expected_resource_identity_collection_document(
        source_snapshot_revision=snapshot.snapshot_revision,
        source_snapshot_manifest_digest=manifest_digest,
        identities=identities,
    )
    expected_path = expected_directory / "expected.json"
    expected_path.write_bytes(
        serialize_expected_resource_identity_collection_document(document)
    )

    return {
        "repository_root": repository_root,
        "manifest_path": manifest_path,
        "candidate_bindings": (
            ActiveCandidateSourceBinding(
                membership.identity.unit_id,
                candidate_path,
            ),
        ),
        "admission_record_bindings": (
            ActiveCandidateAdmissionRecordBinding(
                membership.admission_id,
                admission_path,
            ),
        ),
        "expected_path": expected_path,
        "resource_paths": tuple(
            resource_root / relative_path for _, relative_path in relative_paths
        ),
    }


def _run(source: dict[str, object]):
    return orchestrator.run_active_candidate_source_integrity(
        source["manifest_path"],  # type: ignore[arg-type]
        candidate_bindings=source["candidate_bindings"],  # type: ignore[arg-type]
        admission_record_bindings=source["admission_record_bindings"],  # type: ignore[arg-type]
        expected_resource_identity_document_path=source["expected_path"],  # type: ignore[arg-type]
        repository_root=source["repository_root"],  # type: ignore[arg-type]
    )


def _b43_b39(result: object):
    return (
        result.current_admission_gate_reevaluation
        .admission_record_correspondence_verification
        .admission_record_acquisition.candidate_integrity_verification
    )


def _b51_b39(result: object):
    return (
        result.resource_integrity_verification
        .observed_resource_identity_collection.resource_acquisition
        .resource_binding_collection.expected_resource_coverage_verification
        .required_resource_inventory.candidate_integrity_verification
    )


def test_runs_synthetic_b38_to_b51_with_one_b39_and_no_b52(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_synthetic_source(tmp_path)
    calls: list[str] = []
    original_b39 = orchestrator.verify_active_candidate_source_candidate_integrity
    original_b49 = orchestrator.acquire_active_candidate_source_resources
    original_b50 = orchestrator.derive_active_candidate_source_observed_resource_identities
    original_b51 = orchestrator.verify_active_candidate_source_resource_integrity

    def verify_b39_once(acquisition: object):
        calls.append("b39")
        return original_b39(acquisition)  # type: ignore[arg-type]

    def acquire_b49_once(bindings: object):
        calls.append("b49")
        return original_b49(bindings)  # type: ignore[arg-type]

    def derive_b50_once(acquisition: object):
        calls.append("b50")
        return original_b50(acquisition)  # type: ignore[arg-type]

    def verify_b51_once(observed: object):
        calls.append("b51")
        return original_b51(observed)  # type: ignore[arg-type]

    monkeypatch.setattr(
        orchestrator,
        "verify_active_candidate_source_candidate_integrity",
        verify_b39_once,
    )
    monkeypatch.setattr(
        orchestrator, "acquire_active_candidate_source_resources", acquire_b49_once
    )
    monkeypatch.setattr(
        orchestrator,
        "derive_active_candidate_source_observed_resource_identities",
        derive_b50_once,
    )
    monkeypatch.setattr(
        orchestrator,
        "verify_active_candidate_source_resource_integrity",
        verify_b51_once,
    )

    result = _run(source)

    assert calls == ["b39", "b49", "b50", "b51"]
    assert _b43_b39(result) is _b51_b39(result)
    assert len(result.current_admission_gate_reevaluation.entries) == 1
    assert len(result.resource_integrity_verification.observed_resource_identity_collection.entries) == len(_resource_bytes())


def test_expected_document_is_read_once_and_b49_is_sole_resource_reader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_synthetic_source(tmp_path)
    expected_reads: list[Path] = []
    resource_reads: list[Path] = []
    original_expected = orchestrator.acquire_expected_resource_identity_collection
    original_b49 = orchestrator.acquire_active_candidate_source_resources

    def expected_once(path: Path, **kwargs: object):
        expected_reads.append(path)
        return original_expected(path, **kwargs)

    def resource_once(bindings: object):
        result = original_b49(bindings)  # type: ignore[arg-type]
        resource_reads.extend(entry.binding.resource_path for entry in result.entries)
        return result

    monkeypatch.setattr(
        orchestrator, "acquire_expected_resource_identity_collection", expected_once
    )
    monkeypatch.setattr(
        orchestrator, "acquire_active_candidate_source_resources", resource_once
    )

    _run(source)

    assert expected_reads == [source["expected_path"]]
    assert resource_reads == list(source["resource_paths"])


@pytest.mark.parametrize(
    ("mutator", "match"),
    (
        (
            lambda source: source["resource_paths"][0].write_bytes(b"changed"),
            "Resource integrity mismatch",
        ),
        (
            lambda source: source["resource_paths"][0].unlink(),
            "No such file|cannot find",
        ),
    ),
)
def test_resource_failures_are_fail_fast_without_partial_result(
    tmp_path: Path,
    mutator: object,
    match: str,
) -> None:
    source = _write_synthetic_source(tmp_path)
    mutator(source)  # type: ignore[operator]

    with pytest.raises((OSError, ValueError), match=match):
        _run(source)


def test_b43_negative_and_b47_mismatch_fail_without_resource_acquisition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    negative = _write_synthetic_source(tmp_path / "negative", decision="rejected")
    mismatch = _write_synthetic_source(
        tmp_path / "mismatch",
        expected_resource_ids=(next(iter(_resource_bytes())),),
    )
    b49_calls: list[object] = []
    monkeypatch.setattr(
        orchestrator,
        "acquire_active_candidate_source_resources",
        lambda bindings: b49_calls.append(bindings),
    )

    with pytest.raises(ValueError, match="human_decision_admitted"):
        _run(negative)
    with pytest.raises(ValueError, match="expected resource coverage mismatch"):
        _run(mismatch)

    assert b49_calls == []


def test_module_has_no_b52_or_persistence_or_runtime_dependencies() -> None:
    source = inspect.getsource(orchestrator)

    for forbidden_reference in (
        "verify_active_candidate_source_integrity",
        "content_tree",
        "loader",
        "hashlib",
        "publish_",
        "open(",
        "write_",
    ):
        assert forbidden_reference not in source
