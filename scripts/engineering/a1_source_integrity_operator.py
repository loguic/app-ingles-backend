"""Run one explicitly configured B38–B51 source-integrity operation.

The operator must separately authorize any real run: this command reads local
resources through B49 and deliberately stops before B52.
"""

from __future__ import annotations

import argparse
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
from app.services.pedagogical_active_candidate_source_integrity_orchestrator import (
    ActiveCandidateSourceIntegrityOrchestration,
    run_active_candidate_source_integrity,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one explicit B38–B51 source-integrity operation.",
        allow_abbrev=False,
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--candidate-unit-id", required=True)
    parser.add_argument("--candidate-path", required=True, type=Path)
    parser.add_argument("--admission-id", required=True)
    parser.add_argument("--admission-path", required=True, type=Path)
    parser.add_argument("--expected-document", required=True, type=Path)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--report", type=Path)
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
    if args.report is not None:
        _validate_report_path(args.report, args.repository_root)


def _validate_report_path(report_path: Path, repository_root: Path) -> None:
    _require_absolute_path(report_path, "report")
    if report_path.exists() or report_path.is_symlink():
        raise ValueError("report must not already exist or be a symlink")
    parent = report_path.parent
    if not parent.exists() or not parent.is_dir():
        raise ValueError("report parent must be an existing directory")
    try:
        report_path.relative_to(repository_root.resolve(strict=True))
    except ValueError:
        return
    raise ValueError("report must be outside repository_root")


def _shared_b39(
    result: ActiveCandidateSourceIntegrityOrchestration,
) -> bool:
    b43 = (
        result.current_admission_gate_reevaluation
        .admission_record_correspondence_verification
        .admission_record_acquisition.candidate_integrity_verification
    )
    b51 = (
        result.resource_integrity_verification
        .observed_resource_identity_collection.resource_acquisition
        .resource_binding_collection.expected_resource_coverage_verification
        .required_resource_inventory.candidate_integrity_verification
    )
    return b43 is b51


def _success_output(
    result: ActiveCandidateSourceIntegrityOrchestration,
) -> str:
    source_revision = (
        result.resource_integrity_verification
        .observed_resource_identity_collection.resource_acquisition
        .resource_binding_collection.expected_resource_coverage_verification
        .required_resource_inventory.candidate_integrity_verification.snapshot
        .snapshot_revision
    )
    resource_count = len(
        result.resource_integrity_verification
        .observed_resource_identity_collection.entries
    )
    return urlencode(
        (
            ("SOURCE_INTEGRITY_RUN", "PASS"),
            ("SOURCE_REVISION", source_revision),
            ("B43", "PASS"),
            ("RESOURCE_COUNT", str(resource_count)),
            ("B51", "PASS"),
            ("SAME_B39", "PASS" if _shared_b39(result) else "FAIL"),
            ("B52_INVOKED", "NO"),
            ("CONTENT_TREE_CHANGED", "NO"),
        )
    )


def _failure_output(error: Exception) -> str:
    message = " ".join(str(error).split()) or error.__class__.__name__
    return urlencode(
        (
            ("SOURCE_INTEGRITY_RUN", "FAIL"),
            ("ERROR_TYPE", error.__class__.__name__),
            ("ERROR", message),
            ("B52_INVOKED", "NO"),
        )
    )


def _report_text(args: argparse.Namespace, output: str) -> str:
    return "\n".join(
        (
            "# A1 Source Integrity Operator Run",
            "",
            "## Explicit inputs",
            "",
            f"- manifest: `{args.manifest}`",
            f"- candidate: `{args.candidate_path}` ({args.candidate_unit_id})",
            f"- admission: `{args.admission_path}` ({args.admission_id})",
            f"- expected document: `{args.expected_document}`",
            f"- repository root: `{args.repository_root}`",
            "",
            "## Result",
            "",
            output,
            "",
            "B52 was not invoked. No activation, loader, runtime, content-tree, or verification-state persistence occurs through this CLI.",
            "",
        )
    )


def _write_report(report_path: Path, text: str) -> None:
    with report_path.open("x", encoding="utf-8", newline="\n") as report_file:
        report_file.write(text)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        _validate_inputs(args)
        result = run_active_candidate_source_integrity(
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
        output = _success_output(result)
        if args.report is not None:
            _write_report(args.report, _report_text(args, output))
        print(output)
        return 0
    except (OSError, ValueError) as error:
        print(_failure_output(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
