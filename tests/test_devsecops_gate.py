import json
import socket
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.engineering.devsecops_gate import (
    GateValidationError,
    calculate_sha256,
    load_safety_plan,
    validate_safety_plan,
)


NOW = datetime(2026, 8, 6, 12, tzinfo=UTC)
MAX_AGE = timedelta(days=7)


def write_plan(tmp_path: Path, update=None):
    backup = tmp_path / "backup.dump"
    backup.write_bytes(b"safe synthetic backup fixture")
    restoration = tmp_path / "restoration.json"
    restoration.write_text('{"result":"succeeded"}\n', encoding="utf-8")
    digest = calculate_sha256(backup)
    data = {
        "environment": "development",
        "target": {
            "identifier": "local-diagnostic-db",
            "fingerprint": "development-cluster-01",
            "current_revision": "f81a78f8c1c4",
            "target_revision": "3c4f1a2b7d90",
        },
        "backup": {
            "artifact_path": str(backup),
            "sha256": digest,
            "created_at": "2026-08-06T08:00:00Z",
        },
        "restoration": {
            "evidence_path": str(restoration),
            "restored_at": "2026-08-06T09:00:00Z",
            "backup_sha256": digest,
            "result": "succeeded",
        },
        "migration_rehearsal": {
            "environment_id": "isolated-rehearsal-01",
            "initial_revision": "f81a78f8c1c4",
            "final_revision": "3c4f1a2b7d90",
            "upgrade_succeeded": True,
            "downgrade_succeeded": True,
            "performed_at": "2026-08-06T10:00:00Z",
        },
        "rollback": {
            "return_revision": "f81a78f8c1c4",
            "procedure": "Apply the reviewed downgrade in the isolated runner.",
        },
    }
    if update is not None:
        update(data)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    return plan_path, data


def validate_path(path: Path):
    plan = load_safety_plan(path)
    validate_safety_plan(plan, now=NOW, max_restoration_age=MAX_AGE)
    return plan


def test_accept_complete_development_plan(tmp_path):
    path, _ = write_plan(tmp_path)
    assert validate_path(path).environment == "development"


def test_reject_missing_environment(tmp_path):
    path, _ = write_plan(tmp_path, lambda data: data.pop("environment"))
    with pytest.raises(GateValidationError, match="environment is required"):
        load_safety_plan(path)


def test_reject_unknown_environment(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data.update(environment="sandbox"),
    )
    with pytest.raises(GateValidationError, match="environment is unknown"):
        validate_path(path)


def test_reject_production(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data.update(environment="production"),
    )
    with pytest.raises(GateValidationError, match="always rejected"):
        validate_path(path)


def test_reject_missing_backup(tmp_path):
    path, data = write_plan(tmp_path)
    Path(data["backup"]["artifact_path"]).unlink()
    with pytest.raises(GateValidationError, match="does not exist"):
        validate_path(path)


def test_reject_empty_backup(tmp_path):
    path, data = write_plan(tmp_path)
    Path(data["backup"]["artifact_path"]).write_bytes(b"")
    with pytest.raises(GateValidationError, match="must not be empty"):
        validate_path(path)


def test_reject_symbolic_link_backup(tmp_path):
    path, data = write_plan(tmp_path)
    backup = Path(data["backup"]["artifact_path"])
    linked = tmp_path / "linked-backup.dump"
    linked.symlink_to(backup)
    data["backup"]["artifact_path"] = str(linked)
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")

    with pytest.raises(GateValidationError, match="regular file"):
        validate_path(path)


def test_reject_wrong_backup_sha256(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["backup"].update(sha256="0" * 64),
    )
    with pytest.raises(GateValidationError, match="does not match"):
        validate_path(path)


def test_reject_restoration_for_another_backup(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["restoration"].update(
            backup_sha256="1" * 64
        ),
    )
    with pytest.raises(GateValidationError, match="backup SHA-256"):
        validate_path(path)


def test_reject_expired_restoration(tmp_path):
    def expire_restoration(data):
        data["backup"]["created_at"] = "2026-06-30T09:00:00Z"
        data["restoration"]["restored_at"] = "2026-07-01T09:00:00Z"

    path, _ = write_plan(
        tmp_path,
        expire_restoration,
    )
    with pytest.raises(GateValidationError, match="expired"):
        validate_path(path)


def test_reject_restoration_before_backup(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["restoration"].update(
            restored_at="2026-08-06T07:00:00Z"
        ),
    )
    with pytest.raises(GateValidationError, match="precede backup"):
        validate_path(path)


def test_reject_rehearsal_before_restoration(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["migration_rehearsal"].update(
            performed_at="2026-08-06T08:30:00Z"
        ),
    )
    with pytest.raises(GateValidationError, match="precede restoration"):
        validate_path(path)


def test_reject_rehearsal_without_downgrade(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["migration_rehearsal"].update(
            downgrade_succeeded=False
        ),
    )
    with pytest.raises(GateValidationError, match="downgrade"):
        validate_path(path)


@pytest.mark.parametrize("revision_field", ["initial_revision", "final_revision"])
def test_reject_incompatible_rehearsal_revisions(tmp_path, revision_field):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["migration_rehearsal"].update(
            {revision_field: "unrelated-revision"}
        ),
    )
    with pytest.raises(GateValidationError, match="revision differs"):
        validate_path(path)


def test_reject_empty_rollback_procedure(tmp_path):
    path, _ = write_plan(
        tmp_path,
        lambda data: data["rollback"].update(procedure="   "),
    )
    with pytest.raises(GateValidationError, match="procedure"):
        load_safety_plan(path)


def test_validation_never_starts_processes_or_network_connections(
    tmp_path,
    monkeypatch,
):
    path, _ = write_plan(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("external operation attempted")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    validate_path(path)
