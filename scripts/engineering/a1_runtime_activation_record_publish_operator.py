"""Publish one immutable A1 activation record without updating its pointer."""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.pedagogical_runtime_activation_documents import (
    acquire_active_runtime_pointer_document,
    acquire_runtime_activation_record_document,
    acquire_runtime_content_projection_document,
    build_runtime_activation_record_document,
    publish_runtime_activation_record_document,
)


_RUNTIME_ACTIVATIONS_RELATIVE_ROOT = Path("content/runtime-activations")
_ACTIVE_POINTER_RELATIVE_PATH = Path("content/runtime-active.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Publish one immutable A1 activation record; this never updates "
            "the active-runtime pointer."
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--projection-document", required=True, type=Path)
    parser.add_argument("--activation-revision", required=True)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--previous-activation-revision")
    parser.add_argument("--previous-projection-document", type=Path)
    return parser


def _require_absolute_path(path: Path, name: str) -> Path:
    if not path.is_absolute():
        raise ValueError(f"{name} must be an absolute path")
    return path


def _require_nonblank_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-blank string")
    return value


def _validate_inputs(args: argparse.Namespace) -> None:
    _require_absolute_path(args.projection_document, "projection_document")
    _require_absolute_path(args.repository_root, "repository_root")
    _require_nonblank_string(args.activation_revision, "activation_revision")
    if not args.repository_root.exists() or not args.repository_root.is_dir():
        raise ValueError("repository_root must be an existing directory")
    if args.previous_projection_document is not None:
        _require_absolute_path(
            args.previous_projection_document,
            "previous_projection_document",
        )
    if args.previous_activation_revision is not None:
        _require_nonblank_string(
            args.previous_activation_revision,
            "previous_activation_revision",
        )


def _activation_record_path(repository_root: Path, activation_revision: str) -> Path:
    revision = _require_nonblank_string(activation_revision, "activation_revision")
    revision_digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    document_path = (
        repository_root
        / _RUNTIME_ACTIVATIONS_RELATIVE_ROOT
        / f"sha256-{revision_digest}.json"
    )
    if not document_path.parent.exists() or not document_path.parent.is_dir():
        raise ValueError("runtime activations parent must be an existing directory")
    return document_path


def _previous_activation_revision(
    *,
    repository_root: Path,
    previous_activation_revision: str | None,
    previous_projection_document: Path | None,
) -> str | None:
    pointer_path = repository_root / _ACTIVE_POINTER_RELATIVE_PATH
    pointer_present = pointer_path.exists() or pointer_path.is_symlink()
    if not pointer_present:
        if (
            previous_activation_revision is not None
            or previous_projection_document is not None
        ):
            raise ValueError("previous activation inputs require an active pointer")
        return None
    if previous_activation_revision is None or previous_projection_document is None:
        raise ValueError(
            "active pointer requires previous activation revision and projection document"
        )
    previous_projection = acquire_runtime_content_projection_document(
        previous_projection_document
    )
    previous_record = acquire_runtime_activation_record_document(
        _activation_record_path(repository_root, previous_activation_revision),
        projection_document=previous_projection,
    )
    acquire_active_runtime_pointer_document(pointer_path, activation_record=previous_record)
    return previous_record.activation_revision


def _success_output(*, activation_revision: str, document_path: Path) -> str:
    return urlencode(
        (
            ("ACTIVATION_RECORD_PUBLICATION", "PASS"),
            ("ACTIVATION_REVISION", activation_revision),
            ("DOCUMENT_PATH", str(document_path)),
            ("POINTER_CHANGED", "NO"),
            ("ACTIVATION_EXECUTED", "NO"),
        )
    )


def _failure_output(error: Exception) -> str:
    message = " ".join(str(error).split()) or error.__class__.__name__
    return urlencode(
        (
            ("ACTIVATION_RECORD_PUBLICATION", "FAIL"),
            ("ERROR_TYPE", error.__class__.__name__),
            ("ERROR", message),
            ("POINTER_CHANGED", "NO"),
            ("ACTIVATION_EXECUTED", "NO"),
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        _validate_inputs(args)
        document_path = _activation_record_path(
            args.repository_root,
            args.activation_revision,
        )
        projection_document = acquire_runtime_content_projection_document(
            args.projection_document
        )
        previous_revision = _previous_activation_revision(
            repository_root=args.repository_root,
            previous_activation_revision=args.previous_activation_revision,
            previous_projection_document=args.previous_projection_document,
        )
        record = build_runtime_activation_record_document(
            activation_revision=args.activation_revision,
            projection_document=projection_document,
            previous_activation_revision=previous_revision,
        )
        publish_runtime_activation_record_document(record, document_path=document_path)
        acquire_runtime_activation_record_document(
            document_path,
            projection_document=projection_document,
        )
        print(
            _success_output(
                activation_revision=record.activation_revision,
                document_path=document_path,
            )
        )
        return 0
    except (OSError, ValueError) as error:
        print(_failure_output(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
