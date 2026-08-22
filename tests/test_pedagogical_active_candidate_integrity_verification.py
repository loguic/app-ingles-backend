from dataclasses import FrozenInstanceError, fields, replace
import json
from pathlib import Path

import pytest

import app.services.pedagogical_active_candidate_integrity_verification as verification
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    AcquiredActiveCandidateSourceEntry,
    ActiveCandidateSourceAcquisition,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_FIXTURE_PATH = (
    ROOT
    / "content"
    / "candidates"
    / "a1-u1"
    / "pedagogical-unit-candidate-v2.json"
)


def _candidate_bytes() -> bytes:
    return CANDIDATE_FIXTURE_PATH.read_bytes()


def _candidate(raw_bytes: bytes) -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(
        json.loads(raw_bytes.decode("utf-8"))
    )


def _acquisition(
    *,
    candidate_bytes: bytes | None = None,
    identity: CandidatePayloadIdentity | None = None,
    candidate_path: Path = Path("/candidate/source.json"),
    parsed_candidate: PedagogicalUnitCandidate | None = None,
) -> ActiveCandidateSourceAcquisition:
    raw_bytes = _candidate_bytes() if candidate_bytes is None else candidate_bytes
    candidate = parsed_candidate or _candidate(raw_bytes)
    declared_identity = identity or derive_candidate_payload_identity(
        candidate,
        candidate_revision="  candidate-r1  ",
    )
    membership = ActiveCandidateMembership(
        identity=declared_identity,
        admission_id="admission-1",
    )
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection((membership,)),
        snapshot_revision="source-r1",
    )
    entry = AcquiredActiveCandidateSourceEntry(
        membership=membership,
        candidate_path=candidate_path,
        candidate_bytes=raw_bytes,
        candidate=candidate,
    )
    return ActiveCandidateSourceAcquisition(snapshot=snapshot, entries=(entry,))


def test_verifies_candidate_payload_identity_from_acquired_bytes() -> None:
    acquisition = _acquisition()

    result = verification.verify_active_candidate_source_candidate_integrity(
        acquisition
    )

    assert result.snapshot is acquisition.snapshot
    assert result.entries[0].membership is acquisition.entries[0].membership
    assert result.entries[0].candidate_path == Path("/candidate/source.json")
    assert result.entries[0].candidate_bytes == _candidate_bytes()
    assert (
        result.entries[0].derived_identity
        == acquisition.entries[0].membership.identity
    )


def test_verification_shapes_are_frozen_and_exclude_mutable_candidate() -> None:
    acquisition = _acquisition()
    result = verification.verify_active_candidate_source_candidate_integrity(
        acquisition
    )

    assert [field.name for field in fields(
        verification.CandidatePayloadIntegrityVerification
    )] == [
        "membership",
        "candidate_path",
        "candidate_bytes",
        "derived_identity",
    ]
    assert [field.name for field in fields(
        verification.ActiveCandidateSourceCandidateIntegrityVerification
    )] == ["snapshot", "entries"]
    with pytest.raises(FrozenInstanceError):
        result.entries = ()  # type: ignore[misc]


def test_uses_candidate_bytes_not_mutable_acquired_candidate() -> None:
    acquisition = _acquisition()
    acquisition.entries[0].candidate.specification.title = "Mutated title"

    result = verification.verify_active_candidate_source_candidate_integrity(
        acquisition
    )

    assert result.entries[0].derived_identity == acquisition.entries[0].membership.identity


def test_never_opens_candidate_path_during_verification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_bytes(_candidate_bytes())
    acquisition = _acquisition(candidate_path=candidate_path)
    candidate_path.unlink()

    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("verification must not open candidate paths")

    monkeypatch.setattr(Path, "open", fail_open)

    result = verification.verify_active_candidate_source_candidate_integrity(
        acquisition
    )

    assert result.entries[0].candidate_path == candidate_path


def test_rejects_unsupported_schema_before_candidate_reconstruction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(_candidate_bytes())
    unsupported_identity = replace(
        derive_candidate_payload_identity(candidate, candidate_revision="candidate-r1"),
        payload_schema_version="2.0",
    )
    acquisition = _acquisition(
        candidate_bytes=b"not valid JSON",
        identity=unsupported_identity,
        parsed_candidate=candidate,
    )

    def fail_reconstruct(candidate_bytes: bytes) -> PedagogicalUnitCandidate:
        raise AssertionError("candidate reconstruction must not run")

    monkeypatch.setattr(verification, "_reconstruct_candidate", fail_reconstruct)

    with pytest.raises(ValueError, match="unsupported payload schema version"):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)


def test_rejects_candidate_from_another_unit() -> None:
    candidate = _candidate(_candidate_bytes())
    wrong_identity = replace(
        derive_candidate_payload_identity(candidate, candidate_revision="  candidate-r1  "),
        unit_id="a1-u2",
    )
    acquisition = _acquisition(identity=wrong_identity)

    with pytest.raises(ValueError, match="candidate payload identity mismatch"):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)


def test_rejects_canonical_payload_digest_mismatch() -> None:
    candidate = _candidate(_candidate_bytes())
    wrong_identity = replace(
        derive_candidate_payload_identity(candidate, candidate_revision="  candidate-r1  "),
        content_digest="sha256:" + "f" * 64,
    )
    acquisition = _acquisition(identity=wrong_identity)

    with pytest.raises(ValueError, match="candidate payload identity mismatch"):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)


@pytest.mark.parametrize(
    ("candidate_bytes", "message"),
    [
        (b"\xff", "valid UTF-8"),
        (b"\xef\xbb\xbf{}", "UTF-8 BOM"),
        (b'{"specification":1,"specification":2}', "valid JSON"),
        (b"{", "valid JSON"),
    ],
)
def test_rejects_invalid_candidate_bytes_during_verification(
    candidate_bytes: bytes,
    message: str,
) -> None:
    candidate = _candidate(_candidate_bytes())
    identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision="  candidate-r1  ",
    )
    acquisition = _acquisition(
        candidate_bytes=candidate_bytes,
        identity=identity,
        parsed_candidate=candidate,
    )

    with pytest.raises(ValueError, match=message):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)


def test_rejects_candidate_bytes_that_fail_pydantic_validation() -> None:
    document = json.loads(_candidate_bytes().decode("utf-8"))
    document["candidate_unit"]["id"] = "a1-u2"
    invalid_bytes = json.dumps(document, ensure_ascii=False).encode("utf-8")
    candidate = _candidate(_candidate_bytes())
    identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision="  candidate-r1  ",
    )
    acquisition = _acquisition(
        candidate_bytes=invalid_bytes,
        identity=identity,
        parsed_candidate=candidate,
    )

    with pytest.raises(ValueError, match="valid PedagogicalUnitCandidate"):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)


def test_accepts_noncanonical_json_with_equivalent_candidate_payload() -> None:
    raw_bytes = json.dumps(
        json.loads(_candidate_bytes().decode("utf-8")),
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    acquisition = _acquisition(candidate_bytes=raw_bytes)

    result = verification.verify_active_candidate_source_candidate_integrity(
        acquisition
    )

    assert result.entries[0].candidate_bytes == raw_bytes


def test_preserves_literal_declared_candidate_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acquisition = _acquisition()
    revisions: list[str] = []
    original_derive = verification.derive_candidate_payload_identity

    def track_derive(
        candidate: PedagogicalUnitCandidate,
        *,
        candidate_revision: str,
    ) -> CandidatePayloadIdentity:
        revisions.append(candidate_revision)
        return original_derive(
            candidate,
            candidate_revision=candidate_revision,
        )

    monkeypatch.setattr(
        verification,
        "derive_candidate_payload_identity",
        track_derive,
    )

    verification.verify_active_candidate_source_candidate_integrity(acquisition)

    assert revisions == ["  candidate-r1  "]


def test_is_all_or_nothing_and_empty_acquisition_is_valid() -> None:
    candidate = _candidate(_candidate_bytes())
    first_identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision="candidate-r1",
    )
    second_identity = replace(first_identity, unit_id="a1-u2")
    first_membership = ActiveCandidateMembership(
        identity=first_identity,
        admission_id="admission-1",
    )
    second_membership = ActiveCandidateMembership(
        identity=second_identity,
        admission_id="admission-2",
    )
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(
            (first_membership, second_membership)
        ),
        snapshot_revision="source-r1",
    )
    entries = (
        AcquiredActiveCandidateSourceEntry(
            membership=first_membership,
            candidate_path=Path("/candidate/first.json"),
            candidate_bytes=_candidate_bytes(),
            candidate=candidate,
        ),
        AcquiredActiveCandidateSourceEntry(
            membership=second_membership,
            candidate_path=Path("/candidate/second.json"),
            candidate_bytes=_candidate_bytes(),
            candidate=candidate,
        ),
    )
    acquisition = ActiveCandidateSourceAcquisition(
        snapshot=snapshot,
        entries=entries,
    )

    with pytest.raises(ValueError, match="candidate payload identity mismatch"):
        verification.verify_active_candidate_source_candidate_integrity(acquisition)

    empty_snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(()),
        snapshot_revision="source-empty",
    )
    empty = ActiveCandidateSourceAcquisition(
        snapshot=empty_snapshot,
        entries=(),
    )

    assert verification.verify_active_candidate_source_candidate_integrity(
        empty
    ).entries == ()
