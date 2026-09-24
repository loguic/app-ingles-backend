"""Exercise the thin source-integrity operator only with synthetic inputs."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
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
OPERATOR_PATH = ROOT / "scripts/engineering/a1_source_integrity_operator.py"
SPEC = importlib.util.spec_from_file_location("a1_source_integrity_operator", OPERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


def _write_synthetic_source(tmp_path: Path) -> dict[str, object]:
    root = tmp_path / "repository"
    resource_root = root / "content/resources/a1-u1"
    (resource_root / "audio").mkdir(parents=True)
    (resource_root / "visual").mkdir()
    candidate_path = root / "candidate.json"
    admission_path = root / "admission.json"
    manifest_path = root / "manifest.json"
    expected_path = root / "expected.json"

    payload = json.loads(BASE_CANDIDATE_PATH.read_text(encoding="utf-8"))
    payload["pending_human_decisions"] = []
    payload["proposed_change_summary"] = ["Synthetic CLI fixture only."]
    candidate_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    candidate = PedagogicalUnitCandidate.model_validate(payload)
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
    manifest_path.write_bytes(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    )
    admission_path.write_bytes(
        serialize_candidate_admission_record_document(
            AdmissionRecord(
                admission_id=membership.admission_id,
                identity=identity,
                decision="admitted",
                reviewer_id="synthetic-reviewer",
                decided_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
            )
        )
    )

    resource_bytes = {
        resource_id: f"synthetic bytes for {resource_id}".encode()
        for resource_id in payload["required_resource_ids"]
    }
    bindings = tuple(
        (resource_id, f"audio/resource-{index}.bin")
        for index, resource_id in enumerate(resource_bytes, start=1)
    )
    for resource_id, relative_path in bindings:
        (resource_root / relative_path).write_bytes(resource_bytes[resource_id])
    (resource_root / "README.md").write_text(
        "\n".join(
            (
                "# Synthetic A1 bindings",
                "",
                "| resource_id | relative path |",
                "| --- | --- |",
                *(f"| {resource_id} | {relative_path} |" for resource_id, relative_path in bindings),
                "",
            )
        ),
        encoding="utf-8",
    )
    identities = build_expected_resource_identity_collection(
        tuple(
            derive_resource_physical_identity(bytes_, resource_id=resource_id)
            for resource_id, bytes_ in resource_bytes.items()
        )
    )
    document = build_expected_resource_identity_collection_document(
        source_snapshot_revision=snapshot.snapshot_revision,
        source_snapshot_manifest_digest="sha256:"
        + hashlib.sha256(
            serialize_active_candidate_source_snapshot_manifest(snapshot)
        ).hexdigest(),
        identities=identities,
    )
    expected_path.write_bytes(
        serialize_expected_resource_identity_collection_document(document)
    )
    return {
        "root": root,
        "manifest": manifest_path,
        "candidate": candidate_path,
        "admission": admission_path,
        "expected": expected_path,
        "resource": resource_root / bindings[0][1],
    }


def _arguments(source: dict[str, object], *extra: str) -> list[str]:
    return [
        "--manifest", str(source["manifest"]),
        "--candidate-unit-id", "a1-u1",
        "--candidate-path", str(source["candidate"]),
        "--admission-id", "synthetic-admission-1",
        "--admission-path", str(source["admission"]),
        "--expected-document", str(source["expected"]),
        "--repository-root", str(source["root"]),
        *extra,
    ]


def test_runs_once_with_explicit_synthetic_inputs_and_external_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _write_synthetic_source(tmp_path)
    calls: list[object] = []
    original = operator.run_active_candidate_source_integrity

    def run_once(manifest: Path, **kwargs: object):
        calls.append((manifest, kwargs))
        return original(manifest, **kwargs)

    monkeypatch.setattr(operator, "run_active_candidate_source_integrity", run_once)
    report = tmp_path / "operator-report.md"

    assert operator.main(_arguments(source, "--report", str(report))) == 0

    output = parse_qs(capsys.readouterr().out.strip())
    assert output == {
        "SOURCE_INTEGRITY_RUN": ["PASS"],
        "SOURCE_REVISION": ["synthetic-source-1"],
        "B43": ["PASS"],
        "RESOURCE_COUNT": ["18"],
        "B51": ["PASS"],
        "SAME_B39": ["PASS"],
        "B52_INVOKED": ["NO"],
        "CONTENT_TREE_CHANGED": ["NO"],
    }
    assert len(calls) == 1
    _, kwargs = calls[0]
    assert kwargs["candidate_bindings"][0].unit_id == "a1-u1"
    assert kwargs["candidate_bindings"][0].candidate_path == source["candidate"]
    assert kwargs["admission_record_bindings"][0].admission_id == "synthetic-admission-1"
    assert kwargs["admission_record_bindings"][0].document_path == source["admission"]
    assert kwargs["repository_root"] == source["root"]
    assert report.exists()
    assert "SOURCE_INTEGRITY_RUN=PASS" in report.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("flag", "value"),
    (
        ("--manifest", "relative-manifest.json"),
        ("--candidate-path", "relative-candidate.json"),
        ("--admission-path", "relative-admission.json"),
        ("--expected-document", "relative-expected.json"),
        ("--repository-root", "relative-root"),
    ),
)
def test_rejects_relative_paths_before_orchestrator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    flag: str,
    value: str,
) -> None:
    source = _write_synthetic_source(tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    args = _arguments(source)
    args[args.index(flag) + 1] = value

    assert operator.main(args) == 1
    assert calls == []
    assert "SOURCE_INTEGRITY_RUN=FAIL" in capsys.readouterr().err


def test_rejects_invalid_root_before_orchestrator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_synthetic_source(tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    args = _arguments(source)
    args[args.index("--repository-root") + 1] = str(tmp_path / "missing-root")

    assert operator.main(args) == 1
    assert calls == []


def test_propagates_synthetic_b51_mismatch_without_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _write_synthetic_source(tmp_path)
    Path(source["resource"]).write_bytes(b"changed")
    calls: list[object] = []
    original = operator.run_active_candidate_source_integrity

    def run_once(manifest: Path, **kwargs: object):
        calls.append(manifest)
        return original(manifest, **kwargs)

    monkeypatch.setattr(operator, "run_active_candidate_source_integrity", run_once)

    assert operator.main(_arguments(source)) == 1
    assert calls == [source["manifest"]]
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["SOURCE_INTEGRITY_RUN"] == ["FAIL"]
    assert output["ERROR_TYPE"] == ["ValueError"]
    assert "Resource integrity mismatch" in output["ERROR"][0]
    assert output["B52_INVOKED"] == ["NO"]


def test_missing_required_argument_does_not_invoke_orchestrator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_synthetic_source(tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    args = _arguments(source)
    index = args.index("--expected-document")
    del args[index : index + 2]

    with pytest.raises(SystemExit):
        operator.main(args)
    assert calls == []


def test_module_excludes_b52_activation_loader_runtime_and_git() -> None:
    source = inspect.getsource(operator)

    for forbidden_reference in (
        "verify_active_candidate_source_integrity",
        "from app.services.pedagogical_active_candidate_source_integrity_verification",
        "from app.services.content",
        "git ",
        "subprocess",
    ):
        assert forbidden_reference not in source
