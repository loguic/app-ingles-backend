"""Publish one inactive A1 runtime projection under an external Human Gate."""

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

from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateAdmissionRecordBinding,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
)
from app.services.pedagogical_active_candidate_source_integrity_controlled_execution import (
    run_active_candidate_source_integrity_controlled,
)
from app.services.pedagogical_runtime_activation_documents import (
    publish_runtime_content_projection_document,
)
from app.services.pedagogical_runtime_projection_builder import (
    build_eligible_runtime_content_projection,
)


_RUNTIME_PROJECTIONS_RELATIVE_ROOT = Path("content/runtime-projections")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Publish one inactive A1 runtime projection; a separate Human Gate "
            "is required for every real execution."
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--candidate-unit-id", required=True)
    parser.add_argument("--candidate-path", required=True, type=Path)
    parser.add_argument("--admission-id", required=True)
    parser.add_argument("--admission-path", required=True, type=Path)
    parser.add_argument("--expected-document", required=True, type=Path)
    parser.add_argument("--repository-root", required=True, type=Path)
    return parser


def _require_absolute_path(path: Path, name: str) -> Path:
    if not path.is_absolute():
        raise ValueError(f"{name} must be an absolute path")
    return path


def _validate_inputs(args: argparse.Namespace) -> None:
    for name in (
        "manifest",
        "candidate_path",
        "admission_path",
        "expected_document",
        "repository_root",
    ):
        _require_absolute_path(getattr(args, name), name)
    if not args.repository_root.exists() or not args.repository_root.is_dir():
        raise ValueError("repository_root must be an existing directory")


def _projection_document_path(repository_root: Path, snapshot_revision: str) -> Path:
    if not isinstance(snapshot_revision, str):
        raise ValueError("snapshot_revision must be a string")
    revision_digest = hashlib.sha256(snapshot_revision.encode("utf-8")).hexdigest()
    document_path = (
        repository_root
        / _RUNTIME_PROJECTIONS_RELATIVE_ROOT
        / f"sha256-{revision_digest}.json"
    )
    if not document_path.parent.exists() or not document_path.parent.is_dir():
        raise ValueError("runtime projections parent must be an existing directory")
    return document_path


def _success_output(*, snapshot_revision: str, document_path: Path) -> str:
    return urlencode(
        (
            ("INACTIVE_PROJECTION_PUBLICATION", "PASS"),
            ("SOURCE_REVISION", snapshot_revision),
            ("DOCUMENT_PATH", str(document_path)),
            ("B52", "PASS"),
            ("ACTIVATION_EXECUTED", "NO"),
            ("CONTENT_TREE_CHANGED", "NO"),
        )
    )


def _failure_output(error: Exception) -> str:
    message = " ".join(str(error).split()) or error.__class__.__name__
    return urlencode(
        (
            ("INACTIVE_PROJECTION_PUBLICATION", "FAIL"),
            ("ERROR_TYPE", error.__class__.__name__),
            ("ERROR", message),
            ("ACTIVATION_EXECUTED", "NO"),
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        _validate_inputs(args)
        # Validate the deterministic destination before consuming fresh B52 evidence.
        _projection_document_path(args.repository_root, "")
        active_source_integrity = run_active_candidate_source_integrity_controlled(
            args.manifest,
            candidate_bindings=(
                ActiveCandidateSourceBinding(
                    args.candidate_unit_id,
                    args.candidate_path,
                ),
            ),
            admission_record_bindings=(
                ActiveCandidateAdmissionRecordBinding(
                    args.admission_id,
                    args.admission_path,
                ),
            ),
            expected_resource_identity_document_path=args.expected_document,
            repository_root=args.repository_root,
        )
        projection_document = build_eligible_runtime_content_projection(
            active_source_integrity
        )
        document_path = _projection_document_path(
            args.repository_root,
            projection_document.source_snapshot_revision,
        )
        publish_runtime_content_projection_document(
            projection_document,
            document_path=document_path,
        )
        print(
            _success_output(
                snapshot_revision=projection_document.source_snapshot_revision,
                document_path=document_path,
            )
        )
        return 0
    except (OSError, ValueError) as error:
        print(_failure_output(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
