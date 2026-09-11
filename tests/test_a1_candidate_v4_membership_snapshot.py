import hashlib
import json
from datetime import datetime
from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    ActiveCandidateAdmissionRecordBinding,
    acquire_active_candidate_admission_records,
)
from app.services.pedagogical_active_candidate_admission_record_correspondence import (
    verify_active_candidate_admission_record_correspondence,
)
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    reevaluate_active_candidate_current_admission_gates,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    verify_active_candidate_source_candidate_integrity,
)
from app.services.pedagogical_active_candidate_membership import (
    declare_active_candidate_membership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceBinding,
    acquire_active_candidate_source,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_verification import (
    verify_candidate_admission,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_V4_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
ADMISSION_V4_PATH = ROOT / "content/admissions/a1-u1/adm-a1-u1-002.json"
SNAPSHOT_V4_PATH = ROOT / "content/active-source/active-candidate-source-002.json"
EXPECTED_DIGEST = (
    "sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d"
)
EXPECTED_SNAPSHOT_BYTES = (
    b'{"manifest_schema_version":"1.0",'
    b'"snapshot_revision":"active-candidate-source-002",'
    b'"memberships":[{"identity":{"unit_id":"a1-u1",'
    b'"candidate_revision":"a1-u1-candidate-v4",'
    b'"payload_schema_version":"1.0",'
    b'"content_digest":"sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d"},'
    b'"admission_id":"adm-a1-u1-002"}]}\n'
)
HISTORICAL_FILE_HASHES = {
    "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json": (
        "1e674bc6d4058f58ec7c6b21252c7aa26b3974e058db5e64aa6e4b4802b6894f"
    ),
    "content/admissions/a1-u1/adm-a1-u1-001.json": (
        "6bc89e19438076c1d31cb22ddd55e21de0ce3d6574cc939a52c377a5bb6885ce"
    ),
    "content/active-source/active-candidate-source-001.json": (
        "c442a6ca85218a2529f1bd0e02f36ddcf4ea7c71a754e0069c0552b2c2e47fab"
    ),
}


def _admission_record() -> AdmissionRecord:
    document = json.loads(ADMISSION_V4_PATH.read_text(encoding="utf-8"))
    return AdmissionRecord(
        admission_id=document["admission_id"],
        identity=CandidatePayloadIdentity(**document["identity"]),
        decision=document["decision"],
        reviewer_id=document["reviewer_id"],
        decided_at=datetime.fromisoformat(document["decided_at"].replace("Z", "+00:00")),
    )


def test_a1_v4_membership_snapshot_is_canonical_and_reacquirable() -> None:
    candidate = PedagogicalUnitCandidate.model_validate_json(
        CANDIDATE_V4_PATH.read_text(encoding="utf-8")
    )
    record = _admission_record()
    admission_verification = verify_candidate_admission(candidate, record)

    assert admission_verification.verified is True
    membership = declare_active_candidate_membership(admission_verification)
    assert membership.identity.unit_id == "a1-u1"
    assert membership.identity.candidate_revision == "a1-u1-candidate-v4"
    assert membership.identity.payload_schema_version == "1.0"
    assert membership.identity.content_digest == EXPECTED_DIGEST
    assert membership.admission_id == "adm-a1-u1-002"

    collection = build_active_candidate_membership_collection([membership])
    snapshot = build_active_candidate_source_snapshot(
        collection,
        snapshot_revision="active-candidate-source-002",
    )
    assert len(snapshot.collection.memberships) == 1
    assert serialize_active_candidate_source_snapshot_manifest(snapshot) == (
        EXPECTED_SNAPSHOT_BYTES
    )
    assert len(EXPECTED_SNAPSHOT_BYTES) == 328
    assert SNAPSHOT_V4_PATH == (
        ROOT / "content/active-source/active-candidate-source-002.json"
    )
    assert SNAPSHOT_V4_PATH.read_bytes() == EXPECTED_SNAPSHOT_BYTES
    assert b"candidate-v3" not in SNAPSHOT_V4_PATH.read_bytes()

    acquisition = acquire_active_candidate_source(
        SNAPSHOT_V4_PATH,
        candidate_bindings=[
            ActiveCandidateSourceBinding("a1-u1", CANDIDATE_V4_PATH),
        ],
    )
    candidate_integrity = verify_active_candidate_source_candidate_integrity(
        acquisition
    )
    admission_acquisition = acquire_active_candidate_admission_records(
        candidate_integrity,
        admission_record_bindings=[
            ActiveCandidateAdmissionRecordBinding("adm-a1-u1-002", ADMISSION_V4_PATH),
        ],
    )
    correspondence = verify_active_candidate_admission_record_correspondence(
        admission_acquisition
    )
    b43 = reevaluate_active_candidate_current_admission_gates(correspondence)
    assert len(candidate_integrity.entries) == 1
    assert b43.entries[0].admission_gate_verification.verified is True


def test_a1_v3_snapshot_history_remains_unchanged() -> None:
    for relative_path, expected_hash in HISTORICAL_FILE_HASHES.items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == (
            expected_hash
        )
