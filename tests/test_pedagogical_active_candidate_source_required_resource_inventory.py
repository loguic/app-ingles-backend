from dataclasses import FrozenInstanceError, fields
import inspect
import json
from pathlib import Path

import pytest

import app.services.pedagogical_active_candidate_source_required_resource_inventory as inventory
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
    CandidatePayloadIntegrityVerification,
)
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_candidate_payload_identity import (
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


def _candidate_bytes(
    *,
    unit_id: str,
    required_resource_ids: list[str],
) -> bytes:
    document = json.loads(CANDIDATE_FIXTURE_PATH.read_text())
    document["specification"]["unit_id"] = unit_id
    document["candidate_unit"]["id"] = unit_id
    document["required_resource_ids"] = required_resource_ids
    return json.dumps(document, ensure_ascii=False).encode("utf-8")


def _verification(
    resource_lists: tuple[list[str], ...],
) -> ActiveCandidateSourceCandidateIntegrityVerification:
    memberships: list[ActiveCandidateMembership] = []
    entries: list[CandidatePayloadIntegrityVerification] = []

    for index, resource_ids in enumerate(resource_lists, start=1):
        unit_id = f"a1-u{index}"
        candidate_bytes = _candidate_bytes(
            unit_id=unit_id,
            required_resource_ids=resource_ids,
        )
        candidate = PedagogicalUnitCandidate.model_validate_json(candidate_bytes)
        identity = derive_candidate_payload_identity(
            candidate,
            candidate_revision=f"candidate-r{index}",
        )
        membership = ActiveCandidateMembership(
            identity=identity,
            admission_id=f"admission-{index}",
        )
        memberships.append(membership)
        entries.append(
            CandidatePayloadIntegrityVerification(
                membership=membership,
                candidate_path=Path(f"/candidate/{index}.json"),
                candidate_bytes=candidate_bytes,
                derived_identity=identity,
            )
        )

    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(tuple(memberships)),
        snapshot_revision="source-r1",
    )
    return ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=snapshot,
        entries=tuple(entries),
    )


def test_inventory_has_exact_frozen_shape_and_preserves_b39_identity() -> None:
    verification = _verification((["resource-a"],))

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert [field.name for field in fields(result)] == [
        "candidate_integrity_verification",
        "required_resource_ids",
    ]
    assert result.candidate_integrity_verification is verification
    assert result.required_resource_ids == ("resource-a",)
    assert isinstance(result.required_resource_ids, tuple)

    with pytest.raises(FrozenInstanceError):
        result.required_resource_ids = ()  # type: ignore[misc]


def test_single_candidate_preserves_declared_resource_order() -> None:
    verification = _verification((["resource-z", "resource-a"],))

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert result.required_resource_ids == ("resource-z", "resource-a")


def test_multiple_candidates_form_stable_ordered_union() -> None:
    verification = _verification(
        (
            ["r2", "r1"],
            ["r1", "r3"],
        )
    )

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert result.required_resource_ids == ("r2", "r1", "r3")


def test_candidate_local_duplicates_do_not_fail_or_repeat_source_id() -> None:
    verification = _verification((["r1", "r1", "r2"],))

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert result.required_resource_ids == ("r1", "r2")


def test_resource_ids_are_preserved_literally() -> None:
    resource_ids = ["", " ", "Áudio", "audio", "AUDIO"]
    verification = _verification((resource_ids,))

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert result.required_resource_ids == tuple(resource_ids)


def test_empty_source_and_empty_candidate_resource_lists_are_valid() -> None:
    empty_source = _verification(())
    empty_candidate = _verification(([],))

    assert (
        inventory.build_active_candidate_source_required_resource_inventory(
            empty_source
        ).required_resource_ids
        == ()
    )
    assert (
        inventory.build_active_candidate_source_required_resource_inventory(
            empty_candidate
        ).required_resource_ids
        == ()
    )


def test_reconstructs_exactly_once_per_entry_from_b39_candidate_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verification = _verification((["r1"], ["r2"]))
    calls: list[bytes] = []
    original_reconstruct = PedagogicalUnitCandidate.model_validate_json

    def reconstruct_once(
        cls: type[PedagogicalUnitCandidate],
        candidate_bytes: bytes,
    ) -> PedagogicalUnitCandidate:
        calls.append(candidate_bytes)
        return original_reconstruct(candidate_bytes)

    monkeypatch.setattr(
        inventory.PedagogicalUnitCandidate,
        "model_validate_json",
        classmethod(reconstruct_once),
    )

    result = inventory.build_active_candidate_source_required_resource_inventory(
        verification
    )

    assert calls == [entry.candidate_bytes for entry in verification.entries]
    assert result.required_resource_ids == ("r1", "r2")


def test_rejects_non_b39_input() -> None:
    with pytest.raises(
        ValueError,
        match="ActiveCandidateSourceCandidateIntegrityVerification",
    ):
        inventory.build_active_candidate_source_required_resource_inventory(
            object()  # type: ignore[arg-type]
        )


def test_invalid_b39_candidate_bytes_fail_without_result() -> None:
    verification = _verification((["r1"],))
    invalid_entry = CandidatePayloadIntegrityVerification(
        membership=verification.entries[0].membership,
        candidate_path=verification.entries[0].candidate_path,
        candidate_bytes=b"not JSON",
        derived_identity=verification.entries[0].derived_identity,
    )
    invalid_verification = ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=verification.snapshot,
        entries=(verification.entries[0], invalid_entry),
    )

    with pytest.raises(ValueError):
        inventory.build_active_candidate_source_required_resource_inventory(
            invalid_verification
        )


def test_module_has_no_admission_expected_or_io_dependencies() -> None:
    source = inspect.getsource(inventory)

    for forbidden_reference in (
        "Path",
        "open(",
        "socket",
        "requests",
        "subprocess",
        "datetime",
        "time.",
        "random",
        "hashlib",
        "Admission",
        "ResourcePhysicalIdentity",
        "ExpectedResourceIdentityCollection",
        "coverage",
    ):
        assert forbidden_reference not in source
