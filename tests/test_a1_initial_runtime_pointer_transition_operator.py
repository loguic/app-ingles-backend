"""Temporary-only coverage for initial A1 runtime-pointer creation."""

from __future__ import annotations

import hashlib
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from app.schemas.content import ContentTreeResponse
from app.services import pedagogical_runtime_activation_documents as documents


ROOT = Path(__file__).resolve().parents[1]
OPERATOR_PATH = ROOT / "scripts/engineering/a1_initial_runtime_pointer_transition_operator.py"
SPEC = importlib.util.spec_from_file_location("a1_initial_runtime_pointer", OPERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


def _path(root: Path, family: str, revision: str) -> Path:
    digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    return root / "content" / family / f"sha256-{digest}.json"


def _source(tmp_path: Path):
    root = tmp_path / "repository"
    (root / "content/runtime-activations").mkdir(parents=True)
    (root / "content/runtime-projections").mkdir()
    projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="source-001",
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=ContentTreeResponse(levels=[]),
    )
    record = documents.build_runtime_activation_record_document(
        activation_revision="activation-001",
        projection_document=projection,
        previous_activation_revision=None,
    )
    projection_path = _path(root, "runtime-projections", projection.source_snapshot_revision)
    record_path = _path(root, "runtime-activations", record.activation_revision)
    documents.publish_runtime_content_projection_document(projection, document_path=projection_path)
    documents.publish_runtime_activation_record_document(record, document_path=record_path)
    return root, projection, record, projection_path, record_path


def _arguments(root: Path, projection_path: Path, record_path: Path) -> list[str]:
    return [
        "--repository-root", str(root),
        "--activation-revision", "activation-001",
        "--activation-record-document", str(record_path),
        "--projection-document", str(projection_path),
    ]


def test_initial_create_is_atomic_no_replace_and_existing_replace_publisher_still_works(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / "runtime-active.json"
    first = documents.build_active_runtime_pointer_document(
        activation_record=documents.build_runtime_activation_record_document(
            activation_revision="first",
            projection_document=documents.build_runtime_content_projection_document(
                source_snapshot_revision="source", source_snapshot_manifest_digest="sha256:" + "a" * 64,
                content_tree=ContentTreeResponse(levels=[]),
            ),
            previous_activation_revision=None,
        )
    )
    documents.create_initial_active_runtime_pointer_document(first, document_path=pointer_path)
    with pytest.raises(ValueError, match="must be absent"):
        documents.create_initial_active_runtime_pointer_document(first, document_path=pointer_path)
    assert pointer_path.read_bytes() == documents.serialize_active_runtime_pointer_document(first)
    documents.publish_active_runtime_pointer_document(first, document_path=pointer_path)
    assert pointer_path.read_bytes() == documents.serialize_active_runtime_pointer_document(first)


def test_two_concurrent_initial_creations_allow_exactly_one(tmp_path: Path) -> None:
    pointer_path = tmp_path / "runtime-active.json"
    projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="source", source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=ContentTreeResponse(levels=[]),
    )
    pointers = [
        documents.build_active_runtime_pointer_document(
            activation_record=documents.build_runtime_activation_record_document(
                activation_revision=f"activation-{index}", projection_document=projection,
                previous_activation_revision=None,
            )
        )
        for index in range(2)
    ]

    def create(pointer):
        try:
            documents.create_initial_active_runtime_pointer_document(pointer, document_path=pointer_path)
            return "created"
        except ValueError:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(create, pointers))
    assert sorted(outcomes) == ["created", "rejected"]
    assert pointer_path.read_bytes() in {
        documents.serialize_active_runtime_pointer_document(pointer)
        for pointer in pointers
    }


def test_operator_first_transition_reacquires_full_chain(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, projection, record, projection_path, record_path = _source(tmp_path)
    assert operator.main(_arguments(root, projection_path, record_path)) == 0
    chain = documents.acquire_active_runtime_document_chain(root)
    assert chain.projection_document == projection
    assert chain.activation_record_document == record
    output = parse_qs(capsys.readouterr().out.strip())
    assert output["INITIAL_POINTER_TRANSITION"] == ["PASS"]
    assert output["PUBLICATION_STATE"] == ["CONFIRMED"]
    assert output["OBSERVATION"] == ["VISIBLE_VERIFIED"]


@pytest.mark.parametrize("kind", ("regular", "symlink", "broken_symlink"))
def test_operator_rejects_any_preexisting_pointer(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    pointer_path = root / "content/runtime-active.json"
    if kind == "regular":
        pointer_path.write_bytes(b"existing")
    elif kind == "symlink":
        target = root / "target.json"
        target.write_bytes(b"target")
        pointer_path.symlink_to(target)
    else:
        pointer_path.symlink_to(root / "missing.json")
    assert operator.main(_arguments(root, projection_path, record_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["PUBLICATION_STATE"] == ["PRECONDITION_FAILURE"]
    assert pointer_path.exists() or pointer_path.is_symlink()


def test_operator_rejects_missing_or_incompatible_documents(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    record_path.unlink()
    assert operator.main(_arguments(root, projection_path, record_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["PUBLICATION_STATE"] == ["PRECONDITION_FAILURE"]
    assert not (root / "content/runtime-active.json").exists()


def test_operator_rejects_individually_canonical_incompatible_record_and_projection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    incompatible_projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="source-incompatible",
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=ContentTreeResponse(levels=[]),
    )
    incompatible_record = documents.build_runtime_activation_record_document(
        activation_revision="activation-001",
        projection_document=incompatible_projection,
        previous_activation_revision=None,
    )
    record_path.unlink()
    documents.publish_runtime_activation_record_document(
        incompatible_record,
        document_path=record_path,
    )

    assert operator.main(_arguments(root, projection_path, record_path)) == 1

    output = parse_qs(capsys.readouterr().err.strip())
    assert output["PUBLICATION_STATE"] == ["PRECONDITION_FAILURE"]
    assert "source revision mismatch" in output["ERROR"][0]
    assert not (root / "content/runtime-active.json").exists()


def test_operator_reports_pre_visibility_failure_without_retry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    calls = 0

    def fail_before(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise OSError("write failed")

    monkeypatch.setattr(operator, "create_initial_active_runtime_pointer_document", fail_before)
    assert operator.main(_arguments(root, projection_path, record_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert calls == 1
    assert output["PUBLICATION_STATE"] == ["PRE_VISIBILITY_FAILURE"]
    assert output["OBSERVATION"] == ["ABSENT"]


def test_operator_observes_visible_durability_failure_without_rollback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    monkeypatch.setattr(
        documents,
        "_fsync_directory",
        lambda directory: (_ for _ in ()).throw(OSError("fsync failed")),
    )
    assert operator.main(_arguments(root, projection_path, record_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["PUBLICATION_STATE"] == ["VISIBLE_DURABILITY_INCOMPLETE"]
    assert output["OBSERVATION"] == ["VISIBLE_VERIFIED"]
    assert (root / "content/runtime-active.json").exists()


def test_operator_reports_visible_verification_failure_without_rollback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _, projection_path, record_path = _source(tmp_path)
    monkeypatch.setattr(operator, "_observation", lambda *args, **kwargs: "VISIBLE_UNVERIFIED")
    assert operator.main(_arguments(root, projection_path, record_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["PUBLICATION_STATE"] == ["VISIBLE_VERIFICATION_FAILURE"]
    assert output["OBSERVATION"] == ["VISIBLE_UNVERIFIED"]
    assert (root / "content/runtime-active.json").exists()


def test_competing_create_immediately_before_link_is_rejected_without_overwrite(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pointer_path = tmp_path / "runtime-active.json"
    pointer = documents.build_active_runtime_pointer_document(
        activation_record=documents.build_runtime_activation_record_document(
            activation_revision="activation", projection_document=documents.build_runtime_content_projection_document(
                source_snapshot_revision="source", source_snapshot_manifest_digest="sha256:" + "a" * 64,
                content_tree=ContentTreeResponse(levels=[]),
            ), previous_activation_revision=None,
        )
    )
    original_link = documents.os.link

    def competing_link(source: Path, target: Path) -> None:
        pointer_path.write_bytes(b"competitor")
        original_link(source, target)

    monkeypatch.setattr(documents.os, "link", competing_link)
    with pytest.raises(ValueError, match="already exists"):
        documents.create_initial_active_runtime_pointer_document(pointer, document_path=pointer_path)
    assert pointer_path.read_bytes() == b"competitor"
