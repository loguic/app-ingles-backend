"""Create the first A1 runtime pointer under a separately authorized execution."""

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
    acquire_active_runtime_document_chain,
    acquire_runtime_activation_record_document,
    acquire_runtime_content_projection_document,
    build_active_runtime_pointer_document,
    create_initial_active_runtime_pointer_document,
)


_ACTIVATIONS_ROOT = Path("content/runtime-activations")
_PROJECTIONS_ROOT = Path("content/runtime-projections")
_POINTER_PATH = Path("content/runtime-active.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create one initial A1 active-runtime pointer; execution requires "
            "a separate Human Gate."
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--activation-revision", required=True)
    parser.add_argument("--activation-record-document", required=True, type=Path)
    parser.add_argument("--projection-document", required=True, type=Path)
    return parser


def _require_absolute_path(path: Path, name: str) -> None:
    if not path.is_absolute():
        raise ValueError(f"{name} must be an absolute path")


def _require_nonblank(value: object, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a non-blank string")
    return value


def _revision_path(root: Path, relative_root: Path, revision: str) -> Path:
    digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    return root / relative_root / f"sha256-{digest}.json"


def _validate_inputs(args: argparse.Namespace) -> None:
    for name in (
        "repository_root",
        "activation_record_document",
        "projection_document",
    ):
        _require_absolute_path(getattr(args, name), name)
    _require_nonblank(args.activation_revision, "activation_revision")
    if not args.repository_root.exists() or not args.repository_root.is_dir():
        raise ValueError("repository_root must be an existing directory")


def _acquire_expected_documents(
    args: argparse.Namespace,
):
    projection = acquire_runtime_content_projection_document(args.projection_document)
    expected_projection_path = _revision_path(
        args.repository_root,
        _PROJECTIONS_ROOT,
        projection.source_snapshot_revision,
    )
    if args.projection_document != expected_projection_path:
        raise ValueError("projection_document must match its canonical repository path")

    expected_record_path = _revision_path(
        args.repository_root,
        _ACTIVATIONS_ROOT,
        args.activation_revision,
    )
    if args.activation_record_document != expected_record_path:
        raise ValueError("activation_record_document must match its canonical repository path")
    record = acquire_runtime_activation_record_document(
        args.activation_record_document,
        projection_document=projection,
    )
    if record.activation_revision != args.activation_revision:
        raise ValueError("activation_revision must match activation record")
    if record.previous_activation_revision is not None:
        raise ValueError("initial activation record must have no predecessor")
    return projection, record


def _pointer_is_present(pointer_path: Path) -> bool:
    return pointer_path.exists() or pointer_path.is_symlink()


def _observation(root: Path, *, expected_record: object, expected_projection: object) -> str:
    pointer_path = root / _POINTER_PATH
    if not _pointer_is_present(pointer_path):
        return "ABSENT"
    try:
        chain = acquire_active_runtime_document_chain(root)
    except (OSError, ValueError):
        return "VISIBLE_UNVERIFIED"
    if (
        chain.activation_record_document != expected_record
        or chain.projection_document != expected_projection
    ):
        return "VISIBLE_UNEXPECTED"
    return "VISIBLE_VERIFIED"


def _output(
    *,
    result: str,
    publication_state: str,
    observation: str,
    activation_revision: str,
    error: Exception | None = None,
) -> str:
    values: list[tuple[str, str]] = [
        ("INITIAL_POINTER_TRANSITION", result),
        ("PUBLICATION_STATE", publication_state),
        ("OBSERVATION", observation),
        ("ACTIVATION_REVISION", activation_revision),
        ("A1_ACTIVATED", "NO"),
    ]
    if error is not None:
        values.extend(
            (
                ("ERROR_TYPE", error.__class__.__name__),
                ("ERROR", " ".join(str(error).split()) or error.__class__.__name__),
            )
        )
    return urlencode(values)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        _validate_inputs(args)
        projection, record = _acquire_expected_documents(args)
        pointer_path = args.repository_root / _POINTER_PATH
        if _pointer_is_present(pointer_path):
            raise ValueError("initial active runtime pointer must be absent")
        pointer = build_active_runtime_pointer_document(activation_record=record)
    except (OSError, ValueError) as error:
        print(
            _output(
                result="FAIL",
                publication_state="PRECONDITION_FAILURE",
                observation="NOT_ATTEMPTED",
                activation_revision=getattr(locals().get("args", None), "activation_revision", ""),
                error=error,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        create_initial_active_runtime_pointer_document(pointer, document_path=pointer_path)
    except (OSError, ValueError) as error:
        visible_durability_failure = (
            isinstance(error, OSError) and "visible but durable" in str(error)
        )
        print(
            _output(
                result="FAIL",
                publication_state=(
                    "VISIBLE_DURABILITY_INCOMPLETE"
                    if visible_durability_failure
                    else "PRE_VISIBILITY_FAILURE"
                ),
                observation=_observation(
                    args.repository_root,
                    expected_record=record,
                    expected_projection=projection,
                ),
                activation_revision=record.activation_revision,
                error=error,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        observation = _observation(
            args.repository_root,
            expected_record=record,
            expected_projection=projection,
        )
        if observation != "VISIBLE_VERIFIED":
            raise ValueError("initial pointer publication verification failed")
    except (OSError, ValueError) as error:
        print(
            _output(
                result="FAIL",
                publication_state="VISIBLE_VERIFICATION_FAILURE",
                observation=_observation(
                    args.repository_root,
                    expected_record=record,
                    expected_projection=projection,
                ),
                activation_revision=record.activation_revision,
                error=error,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        _output(
            result="PASS",
            publication_state="CONFIRMED",
            observation="VISIBLE_VERIFIED",
            activation_revision=record.activation_revision,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
