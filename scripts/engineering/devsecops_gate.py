"""Validate migration safety evidence without performing operations.

Valida evidencias de seguridad sin ejecutar operaciones de migración.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


ALLOWED_ENVIRONMENTS = {"test", "development", "staging", "production"}


class GateValidationError(ValueError):
    """Report a fail-closed validation error without sensitive values.

    Informa un fallo cerrado sin incluir valores sensibles.
    """


@dataclass(frozen=True)
class TargetIdentity:
    identifier: str
    fingerprint: str
    current_revision: str
    target_revision: str


@dataclass(frozen=True)
class BackupEvidence:
    artifact_path: Path
    sha256: str
    created_at: datetime


@dataclass(frozen=True)
class RestorationEvidence:
    evidence_path: Path
    restored_at: datetime
    backup_sha256: str
    result: str


@dataclass(frozen=True)
class MigrationRehearsal:
    environment_id: str
    initial_revision: str
    final_revision: str
    upgrade_succeeded: bool
    downgrade_succeeded: bool
    performed_at: datetime


@dataclass(frozen=True)
class RollbackPlan:
    return_revision: str
    procedure: str


@dataclass(frozen=True)
class SafetyPlan:
    environment: str
    target: TargetIdentity
    backup: BackupEvidence
    restoration: RestorationEvidence
    migration_rehearsal: MigrationRehearsal
    rollback: RollbackPlan


def calculate_sha256(path: Path) -> str:
    """Calculate SHA-256 for one local regular file.

    Calcula SHA-256 para un archivo regular local.
    """
    digest = hashlib.sha256()
    try:
        with path.open("rb") as artifact:
            for chunk in iter(lambda: artifact.read(65536), b""):
                digest.update(chunk)
    except OSError as exc:
        raise GateValidationError("backup.artifact_path is unreadable") from exc
    return digest.hexdigest()


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GateValidationError(f"{field} must be an object")
    return value


def _required(mapping: dict[str, Any], field: str, parent: str = "") -> Any:
    if field not in mapping:
        name = f"{parent}.{field}" if parent else field
        raise GateValidationError(f"{name} is required")
    return mapping[field]


def _text(mapping: dict[str, Any], field: str, parent: str) -> str:
    value = _required(mapping, field, parent)
    if not isinstance(value, str) or not value.strip():
        raise GateValidationError(f"{parent}.{field} must be non-empty text")
    return value.strip()


def _boolean(mapping: dict[str, Any], field: str, parent: str) -> bool:
    value = _required(mapping, field, parent)
    if not isinstance(value, bool):
        raise GateValidationError(f"{parent}.{field} must be boolean")
    return value


def _timestamp(mapping: dict[str, Any], field: str, parent: str) -> datetime:
    value = _text(mapping, field, parent)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateValidationError(
            f"{parent}.{field} must be a valid ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GateValidationError(
            f"{parent}.{field} must include a timezone"
        )
    return parsed.astimezone(UTC)


def load_safety_plan(path: Path) -> SafetyPlan:
    """Load a safety plan from JSON without validating external evidence.

    Carga un plan JSON sin validar todavía evidencias externas.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateValidationError("safety plan is missing or unreadable") from exc

    root = _mapping(raw, "plan")
    environment = _required(root, "environment")
    if not isinstance(environment, str) or not environment.strip():
        raise GateValidationError("environment must be explicit")

    target = _mapping(_required(root, "target"), "target")
    backup = _mapping(_required(root, "backup"), "backup")
    restoration = _mapping(_required(root, "restoration"), "restoration")
    rehearsal = _mapping(
        _required(root, "migration_rehearsal"),
        "migration_rehearsal",
    )
    rollback = _mapping(_required(root, "rollback"), "rollback")

    return SafetyPlan(
        environment=environment.strip(),
        target=TargetIdentity(
            identifier=_text(target, "identifier", "target"),
            fingerprint=_text(target, "fingerprint", "target"),
            current_revision=_text(target, "current_revision", "target"),
            target_revision=_text(target, "target_revision", "target"),
        ),
        backup=BackupEvidence(
            artifact_path=Path(_text(backup, "artifact_path", "backup")),
            sha256=_text(backup, "sha256", "backup").lower(),
            created_at=_timestamp(backup, "created_at", "backup"),
        ),
        restoration=RestorationEvidence(
            evidence_path=Path(
                _text(restoration, "evidence_path", "restoration")
            ),
            restored_at=_timestamp(restoration, "restored_at", "restoration"),
            backup_sha256=_text(
                restoration,
                "backup_sha256",
                "restoration",
            ).lower(),
            result=_text(restoration, "result", "restoration"),
        ),
        migration_rehearsal=MigrationRehearsal(
            environment_id=_text(
                rehearsal,
                "environment_id",
                "migration_rehearsal",
            ),
            initial_revision=_text(
                rehearsal,
                "initial_revision",
                "migration_rehearsal",
            ),
            final_revision=_text(
                rehearsal,
                "final_revision",
                "migration_rehearsal",
            ),
            upgrade_succeeded=_boolean(
                rehearsal,
                "upgrade_succeeded",
                "migration_rehearsal",
            ),
            downgrade_succeeded=_boolean(
                rehearsal,
                "downgrade_succeeded",
                "migration_rehearsal",
            ),
            performed_at=_timestamp(
                rehearsal,
                "performed_at",
                "migration_rehearsal",
            ),
        ),
        rollback=RollbackPlan(
            return_revision=_text(
                rollback,
                "return_revision",
                "rollback",
            ),
            procedure=_text(rollback, "procedure", "rollback"),
        ),
    )


def _validate_regular_nonempty_file(path: Path, field: str) -> None:
    try:
        if not path.exists():
            raise GateValidationError(f"{field} does not exist")
        if path.is_symlink() or not path.is_file():
            raise GateValidationError(f"{field} must be a regular file")
        if path.stat().st_size <= 0:
            raise GateValidationError(f"{field} must not be empty")
    except OSError as exc:
        raise GateValidationError(f"{field} is unreadable") from exc


def validate_safety_plan(
    plan: SafetyPlan,
    *,
    now: datetime,
    max_restoration_age: timedelta,
) -> None:
    """Fail closed unless every S1 safety invariant is satisfied.

    Falla de forma cerrada salvo que se cumplan todos los invariantes S1.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise GateValidationError("validation time must include a timezone")
    current_time = now.astimezone(UTC)
    if max_restoration_age <= timedelta(0):
        raise GateValidationError("max_restoration_age must be positive")

    if plan.environment not in ALLOWED_ENVIRONMENTS:
        raise GateValidationError("environment is unknown")
    if plan.environment == "production":
        raise GateValidationError("production is always rejected in S1")

    if plan.target.current_revision == plan.target.target_revision:
        raise GateValidationError("target revisions must differ")

    _validate_regular_nonempty_file(
        plan.backup.artifact_path,
        "backup.artifact_path",
    )
    if len(plan.backup.sha256) != 64 or any(
        character not in "0123456789abcdef"
        for character in plan.backup.sha256
    ):
        raise GateValidationError("backup.sha256 must be a SHA-256 digest")
    if calculate_sha256(plan.backup.artifact_path) != plan.backup.sha256:
        raise GateValidationError("backup.sha256 does not match the artifact")
    if plan.backup.created_at > current_time:
        raise GateValidationError("backup.created_at cannot be in the future")

    _validate_regular_nonempty_file(
        plan.restoration.evidence_path,
        "restoration.evidence_path",
    )
    if plan.restoration.evidence_path == plan.backup.artifact_path:
        raise GateValidationError("restoration evidence must be separate")
    if plan.restoration.backup_sha256 != plan.backup.sha256:
        raise GateValidationError("restoration backup SHA-256 does not match")
    if plan.restoration.result != "succeeded":
        raise GateValidationError("restoration result must be succeeded")
    if plan.restoration.restored_at > current_time:
        raise GateValidationError("restoration.restored_at cannot be in the future")
    if plan.restoration.restored_at < plan.backup.created_at:
        raise GateValidationError("restoration cannot precede backup creation")
    if current_time - plan.restoration.restored_at > max_restoration_age:
        raise GateValidationError("restoration evidence is expired")

    rehearsal = plan.migration_rehearsal
    if rehearsal.performed_at > current_time:
        raise GateValidationError(
            "migration_rehearsal.performed_at cannot be in the future"
        )
    if rehearsal.performed_at < plan.restoration.restored_at:
        raise GateValidationError("migration rehearsal cannot precede restoration")
    if not rehearsal.upgrade_succeeded:
        raise GateValidationError("migration rehearsal upgrade did not succeed")
    if not rehearsal.downgrade_succeeded:
        raise GateValidationError("migration rehearsal downgrade did not succeed")
    if rehearsal.initial_revision != plan.target.current_revision:
        raise GateValidationError("migration rehearsal initial revision differs")
    if rehearsal.final_revision != plan.target.target_revision:
        raise GateValidationError("migration rehearsal final revision differs")
    if plan.rollback.return_revision != plan.target.current_revision:
        raise GateValidationError("rollback return revision differs")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a local DevSecOps safety plan without executing it."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument(
        "--max-restoration-age-hours",
        type=int,
        required=True,
    )
    args = parser.parse_args()
    try:
        plan = load_safety_plan(args.plan)
        validate_safety_plan(
            plan,
            now=datetime.now(UTC),
            max_restoration_age=timedelta(
                hours=args.max_restoration_age_hours
            ),
        )
    except GateValidationError as exc:
        raise SystemExit(f"DevSecOps gate rejected: {exc}") from exc
    print("DevSecOps gate accepted the local safety evidence")


if __name__ == "__main__":
    main()
