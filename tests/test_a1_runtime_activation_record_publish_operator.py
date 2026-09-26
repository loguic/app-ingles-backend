"""Exercise activation-record publication only with temporary documents."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from app.schemas.content import ContentTreeResponse
from app.services import pedagogical_runtime_activation_documents as documents


ROOT = Path(__file__).resolve().parents[1]
OPERATOR_PATH = ROOT / "scripts/engineering/a1_runtime_activation_record_publish_operator.py"
SPEC = importlib.util.spec_from_file_location(
    "a1_runtime_activation_record_publish_operator",
    OPERATOR_PATH,
)
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


def _projection(revision: str) -> documents.RuntimeContentProjectionDocumentV1:
    return documents.build_runtime_content_projection_document(
        source_snapshot_revision=revision,
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=ContentTreeResponse(levels=[]),
    )


def _source(tmp_path: Path) -> tuple[Path, Path, documents.RuntimeContentProjectionDocumentV1]:
    root = tmp_path / "repository"
    (root / "content/runtime-activations").mkdir(parents=True)
    (root / "content/runtime-projections").mkdir()
    projection_path = root / "content/runtime-projections/current.json"
    projection = _projection("source-current")
    documents.publish_runtime_content_projection_document(
        projection,
        document_path=projection_path,
    )
    return root, projection_path, projection


def _arguments(root: Path, projection_path: Path) -> list[str]:
    return [
        "--projection-document", str(projection_path),
        "--activation-revision", "activation-current",
        "--repository-root", str(root),
    ]


def _record_path(root: Path, revision: str) -> Path:
    return root / "content/runtime-activations" / (
        "sha256-" + hashlib.sha256(revision.encode("utf-8")).hexdigest() + ".json"
    )


def test_publishes_and_reacquires_an_immutable_record_without_pointer(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, projection_path, projection = _source(tmp_path)

    assert operator.main(_arguments(root, projection_path)) == 0

    record_path = _record_path(root, "activation-current")
    acquired = documents.acquire_runtime_activation_record_document(
        record_path,
        projection_document=projection,
    )
    assert acquired.activation_revision == "activation-current"
    assert acquired.previous_activation_revision is None
    assert not (root / "content/runtime-active.json").exists()
    output = parse_qs(capsys.readouterr().out.strip())
    assert output["ACTIVATION_RECORD_PUBLICATION"] == ["PASS"]
    assert output["POINTER_CHANGED"] == ["NO"]


def test_same_record_is_idempotent(
    tmp_path: Path,
) -> None:
    root, projection_path, _ = _source(tmp_path)

    assert operator.main(_arguments(root, projection_path)) == 0
    assert operator.main(_arguments(root, projection_path)) == 0


def test_conflicting_destination_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, projection_path, projection = _source(tmp_path)
    conflicting = documents.build_runtime_activation_record_document(
        activation_revision="activation-current",
        projection_document=projection,
        previous_activation_revision="activation-prior",
    )
    documents.publish_runtime_activation_record_document(
        conflicting,
        document_path=_record_path(root, "activation-current"),
    )

    assert operator.main(_arguments(root, projection_path)) == 1
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["ERROR_TYPE"] == ["ValueError"]
    assert "already exists with different bytes" in output["ERROR"][0]


def test_invalid_predecessor_pointer_fails_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, projection_path, _ = _source(tmp_path)
    previous_projection = _projection("source-previous")
    previous_projection_path = root / "content/runtime-projections/previous.json"
    documents.publish_runtime_content_projection_document(
        previous_projection,
        document_path=previous_projection_path,
    )
    previous_record = documents.build_runtime_activation_record_document(
        activation_revision="activation-previous",
        projection_document=previous_projection,
        previous_activation_revision=None,
    )
    documents.publish_runtime_activation_record_document(
        previous_record,
        document_path=_record_path(root, "activation-previous"),
    )
    invalid_pointer = documents.ActiveRuntimePointerDocumentV1(
        activation_revision="activation-previous",
        activation_record_digest="sha256:" + "0" * 64,
    )
    pointer_path = root / "content/runtime-active.json"
    pointer_path.write_bytes(documents.serialize_active_runtime_pointer_document(invalid_pointer))

    arguments = _arguments(root, projection_path) + [
        "--previous-activation-revision", "activation-previous",
        "--previous-projection-document", str(previous_projection_path),
    ]
    assert operator.main(arguments) == 1
    assert not _record_path(root, "activation-current").exists()
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["ERROR"] == ["active runtime pointer activation record digest mismatch"]


def test_projection_acquisition_failure_does_not_publish(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, projection_path, _ = _source(tmp_path)
    projection_path.unlink()

    assert operator.main(_arguments(root, projection_path)) == 1
    assert list((root / "content/runtime-activations").iterdir()) == []
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["ERROR_TYPE"] == ["ValueError"]
    assert output["ERROR"] == ["runtime projection document path must exist"]
