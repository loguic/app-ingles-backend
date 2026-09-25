"""Exercise inactive A1 projection publication only with mocks and temp paths."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs

import pytest


ROOT = Path(__file__).resolve().parents[1]
OPERATOR_PATH = ROOT / "scripts/engineering/a1_inactive_runtime_projection_publish_operator.py"
SPEC = importlib.util.spec_from_file_location(
    "a1_inactive_runtime_projection_publish_operator", OPERATOR_PATH
)
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


def _source(tmp_path: Path, *, create_parent: bool = True) -> dict[str, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    if create_parent:
        (root / "content/runtime-projections").mkdir(parents=True)
    return {
        "root": root,
        "manifest": tmp_path / "manifest.json",
        "candidate": tmp_path / "candidate.json",
        "admission": tmp_path / "admission.json",
        "expected": tmp_path / "expected.json",
    }


def _arguments(source: dict[str, Path]) -> list[str]:
    return [
        "--manifest", str(source["manifest"]),
        "--candidate-unit-id", "a1-u1",
        "--candidate-path", str(source["candidate"]),
        "--admission-id", "admission-1",
        "--admission-path", str(source["admission"]),
        "--expected-document", str(source["expected"]),
        "--repository-root", str(source["root"]),
    ]


def test_hands_the_same_in_memory_b52_to_builder_and_publishes_derived_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _source(tmp_path)
    b52 = object()
    revision = "Revisión Á / exact"
    projection = SimpleNamespace(source_snapshot_revision=revision)
    calls: list[object] = []

    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity_controlled",
        lambda *args, **kwargs: b52,
    )

    def build(value: object) -> object:
        calls.append(value)
        return projection

    def publish(document: object, *, document_path: Path) -> None:
        calls.extend((document, document_path))

    monkeypatch.setattr(operator, "build_eligible_runtime_content_projection", build)
    monkeypatch.setattr(operator, "publish_runtime_content_projection_document", publish)

    assert operator.main(_arguments(source)) == 0

    expected_name = "sha256-" + hashlib.sha256(revision.encode("utf-8")).hexdigest() + ".json"
    assert calls == [b52, projection, source["root"] / "content/runtime-projections" / expected_name]
    output = parse_qs(capsys.readouterr().out.strip())
    assert output["INACTIVE_PROJECTION_PUBLICATION"] == ["PASS"]
    assert output["DOCUMENT_PATH"] == [str(calls[-1])]
    assert output["B52"] == ["PASS"]
    assert output["ACTIVATION_EXECUTED"] == ["NO"]


def test_missing_runtime_projection_parent_fails_before_b52(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _source(tmp_path, create_parent=False)
    calls: list[object] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity_controlled",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    assert operator.main(_arguments(source)) == 1

    assert calls == []
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["ERROR"] == ["runtime projections parent must be an existing directory"]


def test_builder_failure_is_fail_fast_without_publication_or_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source(tmp_path)
    calls: list[str] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity_controlled",
        lambda *args, **kwargs: calls.append("b52") or object(),
    )

    def build(_: object) -> object:
        calls.append("builder")
        raise ValueError("synthetic builder failure")

    monkeypatch.setattr(operator, "build_eligible_runtime_content_projection", build)
    monkeypatch.setattr(
        operator,
        "publish_runtime_content_projection_document",
        lambda *args, **kwargs: calls.append("publisher"),
    )

    assert operator.main(_arguments(source)) == 1
    assert calls == ["b52", "builder"]


def test_visible_but_durability_incomplete_error_has_no_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _source(tmp_path)
    projection = SimpleNamespace(source_snapshot_revision="source-1")
    calls: list[str] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity_controlled",
        lambda *args, **kwargs: calls.append("b52") or object(),
    )
    monkeypatch.setattr(
        operator,
        "build_eligible_runtime_content_projection",
        lambda _: calls.append("builder") or projection,
    )

    def durability_failure(*args: object, **kwargs: object) -> None:
        calls.append("publisher")
        raise OSError("runtime projection document publication is visible but durable directory sync failed")

    monkeypatch.setattr(operator, "publish_runtime_content_projection_document", durability_failure)

    assert operator.main(_arguments(source)) == 1
    assert calls == ["b52", "builder", "publisher"]
    output = parse_qs(capsys.readouterr().err.strip())
    assert output["ERROR_TYPE"] == ["OSError"]
    assert "visible but durable" in output["ERROR"][0]


@pytest.mark.parametrize(
    ("flag", "value"),
    (("--manifest", "relative.json"), ("--repository-root", "relative-root")),
)
def test_rejects_relative_paths_before_b52(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    flag: str,
    value: str,
) -> None:
    source = _source(tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        operator,
        "run_active_candidate_source_integrity_controlled",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    args = _arguments(source)
    args[args.index(flag) + 1] = value

    assert operator.main(args) == 1
    assert calls == []


def test_module_excludes_activation_loader_and_authorization_substitutes() -> None:
    source = inspect.getsource(operator)
    for forbidden_reference in (
        "content_tree.json",
        "from app.services.content",
        "activation_record",
        "publish_active_runtime_pointer",
        "subprocess",
        "git ",
        "--human-authorization",
    ):
        assert forbidden_reference not in source
