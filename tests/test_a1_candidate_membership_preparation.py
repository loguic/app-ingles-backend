import json
from datetime import datetime
from pathlib import Path

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_membership import (
    declare_active_candidate_membership,
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
from app.services.pedagogical_candidate_admission_verification import (
    verify_candidate_admission,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json"
ADMISSION_RECORD_PATH = ROOT / "content/admissions/a1-u1/adm-a1-u1-001.json"
FUTURE_MANIFEST_RELATIVE_PATH = Path(
    "content/active-source/active-candidate-source-001.json"
)
SNAPSHOT_REVISION = "active-candidate-source-001"
EXPECTED_DIGEST = (
    "sha256:23e0d0e1eba8fb7c6b1c73097f01350abe06c84af30fab49f9e646fd9f095018"
)
EXPECTED_MANIFEST_BYTES = (
    b'{"manifest_schema_version":"1.0",'
    b'"snapshot_revision":"active-candidate-source-001",'
    b'"memberships":[{"identity":{"unit_id":"a1-u1",'
    b'"candidate_revision":"a1-u1-candidate-v3",'
    b'"payload_schema_version":"1.0",'
    b'"content_digest":"sha256:23e0d0e1eba8fb7c6b1c73097f01350abe06c84af30fab49f9e646fd9f095018"},'
    b'"admission_id":"adm-a1-u1-001"}]}\n'
)


def _resolve_future_manifest_path(relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("manifest path must stay under repository root")
    manifest_path = ROOT / relative_path
    if not manifest_path.is_relative_to(ROOT):
        raise ValueError("manifest path must stay under repository root")
    return manifest_path


def _load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate_json(
        CANDIDATE_PATH.read_text(encoding="utf-8")
    )


def _load_admission_record() -> AdmissionRecord:
    document = json.loads(ADMISSION_RECORD_PATH.read_text(encoding="utf-8"))
    identity = CandidatePayloadIdentity(**document["identity"])
    return AdmissionRecord(
        admission_id=document["admission_id"],
        identity=identity,
        decision=document["decision"],
        reviewer_id=document["reviewer_id"],
        decided_at=datetime.fromisoformat(
            document["decided_at"].replace("Z", "+00:00")
        ),
    )


def test_a1_membership_preparation_matches_one_published_snapshot() -> None:
    candidate = _load_candidate()
    admission_record = _load_admission_record()

    assert (
        ADMISSION_RECORD_PATH.read_bytes()
        == serialize_candidate_admission_record_document(admission_record)
    )
    assert admission_record.identity.content_digest == EXPECTED_DIGEST
    assert derive_candidate_payload_identity(
        candidate,
        candidate_revision="a1-u1-candidate-v3",
    ) == admission_record.identity

    admission_verification = verify_candidate_admission(
        candidate,
        admission_record,
    )
    assert admission_verification.verified is True

    membership = declare_active_candidate_membership(admission_verification)
    assert membership.identity is admission_verification.derived_identity
    assert membership.admission_id == "adm-a1-u1-001"

    collection = build_active_candidate_membership_collection([membership])
    assert collection.memberships == (membership,)
    assert collection.memberships[0].identity.unit_id == "a1-u1"

    snapshot = build_active_candidate_source_snapshot(
        collection,
        snapshot_revision=SNAPSHOT_REVISION,
    )
    assert snapshot.snapshot_revision == SNAPSHOT_REVISION
    assert snapshot.collection is collection
    assert serialize_active_candidate_source_snapshot_manifest(snapshot) == (
        EXPECTED_MANIFEST_BYTES
    )

    future_manifest_path = _resolve_future_manifest_path(
        FUTURE_MANIFEST_RELATIVE_PATH
    )
    assert future_manifest_path == (
        ROOT / "content/active-source/active-candidate-source-001.json"
    )
    assert future_manifest_path.is_relative_to(ROOT)
    assert future_manifest_path.read_bytes() == EXPECTED_MANIFEST_BYTES


def test_a1_membership_preparation_rejects_manifest_escape() -> None:
    with pytest.raises(ValueError, match="stay under repository root"):
        _resolve_future_manifest_path(Path("../active-manifest.json"))
