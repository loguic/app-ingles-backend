"""Tests for current active-candidate admission gate reevaluation."""

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
    ValidationReport,
)
from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    AcquiredActiveCandidateAdmissionRecordEntry,
    ActiveCandidateSourceAdmissionRecordAcquisition,
)
from app.services.pedagogical_active_candidate_admission_record_correspondence import (
    ActiveCandidateSourceAdmissionRecordCorrespondenceVerification,
    verify_active_candidate_admission_record_correspondence,
)
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateCurrentAdmissionGateReevaluationEntry,
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
    reevaluate_active_candidate_current_admission_gates,
)
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
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_verification import (
    AdmissionGateVerification,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)
import app.services.pedagogical_active_candidate_current_admission_gate_reevaluation as reevaluation


def _candidate_payload(index: int) -> dict:
    unit_id = f"a1-u{index}"
    lesson_id = f"{unit_id}-l1"
    skill_id = f"a1_introduce_yourself_{index}"
    return {
        "specification": {
            "unit_id": unit_id,
            "level": "A1",
            "title": "Introductions",
            "learner_outcome": "Introduce yourself.",
            "skills": [{
                "id": skill_id,
                "description": "Introduce yourself.",
                "required_stages": ["introduce"],
            }],
            "required_evidence": ["One introduction."],
            "lesson_scope": ["Introductions."],
            "language_scope": ["My name is..."],
            "pronunciation_scope": ["Sentence stress."],
            "content_constraints": ["Use A1 language."],
            "technical_constraints": ["Use existing contracts."],
            "acceptance_criteria": ["Produce one introduction."],
        },
        "candidate_unit": {
            "id": unit_id,
            "title": "Introductions",
            "lessons": [{"id": lesson_id, "title": "Names"}],
        },
        "evaluation_plans": [{
            "lesson_id": lesson_id,
            "criteria": [{
                "id": f"{lesson_id}-semantic",
                "evidence_definition_id": f"{lesson_id}-ev1",
                "conversation_id": f"{lesson_id}-c1",
                "prompt_id": f"{lesson_id}-p1",
                "dimension": "semantic",
                "description": "States a name.",
                "measurement_mode": "score",
                "success_threshold": 0.0,
                "applicable_modalities": ["text"],
            }],
        }],
        "feedback_plans": [{
            "lesson_id": lesson_id,
            "rules": [{
                "id": f"{lesson_id}-semantic-feedback",
                "criterion_id": f"{lesson_id}-semantic",
                "passed_message": "Clear introduction.",
                "passed_guidance": "Continue.",
                "failed_message": "Introduction incomplete.",
                "failed_guidance": "State your name.",
            }],
        }],
        "lesson_capability_plans": [{
            "lesson_id": lesson_id,
            "claims": [],
            "prerequisites": [],
        }],
        "skill_coverage": [{
            "skill_id": skill_id,
            "introduced_in_lesson_id": lesson_id,
            "modalities": ["speaking"],
            "status": "complete",
        }],
        "required_resource_ids": [],
        "validation_report": {"status": "passed", "findings": []},
        "pending_human_decisions": [],
        "proposed_change_summary": ["Candidate ready for review."],
    }


def _report(status: str = "passed") -> ValidationReport:
    if status == "passed":
        return ValidationReport(status="passed", findings=[])
    severity = "error" if status == "failed" else "warning"
    return ValidationReport(
        status=status,  # type: ignore[arg-type]
        findings=[
            ValidationFinding(
                validator_id="controlled_gate",
                severity=severity,
                message="Controlled gate result.",
            )
        ],
    )


def _gate_verification(
    admission_record: AdmissionRecord,
    *,
    identity_matches: bool = True,
    local_validation_passed: bool = True,
    pending_human_decisions_clear: bool = True,
    human_decision_admitted: bool = True,
) -> AdmissionGateVerification:
    return AdmissionGateVerification(
        derived_identity=admission_record.identity,
        admission_record=admission_record,
        local_validation_report=_report(
            "passed" if local_validation_passed else "failed"
        ),
        identity_matches=identity_matches,
        local_validation_passed=local_validation_passed,
        pending_human_decisions_clear=pending_human_decisions_clear,
        human_decision_admitted=human_decision_admitted,
    )


def _correspondence(
    indexes: tuple[int, ...] = (1,),
) -> ActiveCandidateSourceAdmissionRecordCorrespondenceVerification:
    memberships: list[ActiveCandidateMembership] = []
    candidate_integrity_entries: list[CandidatePayloadIntegrityVerification] = []
    acquired_entries: list[AcquiredActiveCandidateAdmissionRecordEntry] = []

    for index in indexes:
        candidate = PedagogicalUnitCandidate.model_validate(
            _candidate_payload(index)
        )
        candidate_bytes = json.dumps(
            _candidate_payload(index), separators=(",", ":")
        ).encode("utf-8")
        identity = derive_candidate_payload_identity(
            candidate,
            candidate_revision=f"candidate-r{index}",
        )
        membership = ActiveCandidateMembership(
            identity=identity,
            admission_id=f"admission-{index}",
        )
        record = AdmissionRecord(
            admission_id=membership.admission_id,
            identity=identity,
            decision="admitted",
            reviewer_id="reviewer-1",
            decided_at=datetime(2026, 8, 25, 12, 0, index, tzinfo=timezone.utc),
        )
        memberships.append(membership)
        candidate_integrity_entries.append(
            CandidatePayloadIntegrityVerification(
                membership=membership,
                candidate_path=Path(f"/candidate/{index}.json"),
                candidate_bytes=candidate_bytes,
                derived_identity=identity,
            )
        )
        acquired_entries.append(
            AcquiredActiveCandidateAdmissionRecordEntry(
                membership=membership,
                document_path=Path(f"/admission/{index}.json"),
                admission_record_bytes=b"preserved-admission-record",
                admission_record=record,
            )
        )

    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(tuple(memberships)),
        snapshot_revision="source-r1",
    )
    candidate_integrity_verification = (
        ActiveCandidateSourceCandidateIntegrityVerification(
            snapshot=snapshot,
            entries=tuple(candidate_integrity_entries),
        )
    )
    acquisition = ActiveCandidateSourceAdmissionRecordAcquisition(
        candidate_integrity_verification=candidate_integrity_verification,
        entries=tuple(acquired_entries),
    )
    return verify_active_candidate_admission_record_correspondence(
        acquisition
    )


def _patch_b33(
    monkeypatch: pytest.MonkeyPatch,
    *,
    values: tuple[AdmissionGateVerification, ...],
) -> list[tuple[PedagogicalUnitCandidate, AdmissionRecord]]:
    calls: list[tuple[PedagogicalUnitCandidate, AdmissionRecord]] = []
    iterator = iter(values)

    def verify(
        candidate: PedagogicalUnitCandidate,
        admission_record: AdmissionRecord,
    ) -> AdmissionGateVerification:
        calls.append((candidate, admission_record))
        return next(iterator)

    monkeypatch.setattr(reevaluation, "verify_candidate_admission", verify)
    return calls


def test_reevaluates_single_and_multiple_entries_in_preserved_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence((2, 1))
    records = tuple(
        entry.admission_record
        for entry in correspondence.admission_record_acquisition.entries
    )
    calls = _patch_b33(
        monkeypatch,
        values=tuple(_gate_verification(record) for record in records),
    )

    result = reevaluate_active_candidate_current_admission_gates(correspondence)

    assert result.admission_record_correspondence_verification is correspondence
    assert [
        entry.candidate_integrity_verification.membership.admission_id
        for entry in result.entries
    ] == ["admission-2", "admission-1"]
    assert [
        entry.acquired_admission_record_entry
        for entry in result.entries
    ] == list(correspondence.admission_record_acquisition.entries)
    assert [call[1] for call in calls] == list(records)
    assert len(calls) == 2


def test_result_shapes_are_frozen_and_empty_correspondence_is_valid() -> None:
    correspondence = _correspondence(())

    result = reevaluate_active_candidate_current_admission_gates(correspondence)

    assert [field.name for field in fields(
        ActiveCandidateCurrentAdmissionGateReevaluationEntry
    )] == [
        "candidate_integrity_verification",
        "acquired_admission_record_entry",
        "admission_gate_verification",
    ]
    assert [field.name for field in fields(
        ActiveCandidateSourceCurrentAdmissionGateReevaluation
    )] == ["admission_record_correspondence_verification", "entries"]
    assert result.entries == ()
    assert result.admission_record_correspondence_verification is correspondence
    with pytest.raises(FrozenInstanceError):
        result.entries = ()  # type: ignore[misc]


def test_reconstructs_candidate_only_from_preserved_candidate_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence()
    candidate_bytes = (
        correspondence.admission_record_acquisition.candidate_integrity_verification
        .entries[0]
        .candidate_bytes
    )
    reconstructed_candidate = object()
    model_calls: list[bytes] = []

    class FakeCandidateModel:
        @staticmethod
        def model_validate_json(value: bytes) -> object:
            model_calls.append(value)
            return reconstructed_candidate

    record = correspondence.admission_record_acquisition.entries[0].admission_record
    gate_verification = _gate_verification(record)
    monkeypatch.setattr(reevaluation, "PedagogicalUnitCandidate", FakeCandidateModel)
    calls = _patch_b33(monkeypatch, values=(gate_verification,))

    result = reevaluate_active_candidate_current_admission_gates(correspondence)

    assert model_calls == [candidate_bytes]
    assert calls == [(reconstructed_candidate, record)]
    assert result.entries[0].admission_gate_verification is gate_verification


@pytest.mark.parametrize(
    ("gate_name", "gate_values"),
    [
        ("local_validation_passed", {"local_validation_passed": False}),
        (
            "pending_human_decisions_clear",
            {"pending_human_decisions_clear": False},
        ),
        ("human_decision_admitted", {"human_decision_admitted": False}),
    ],
)
def test_rejects_normal_unverified_gates(
    monkeypatch: pytest.MonkeyPatch,
    gate_name: str,
    gate_values: dict[str, bool],
) -> None:
    correspondence = _correspondence()
    record = correspondence.admission_record_acquisition.entries[0].admission_record
    _patch_b33(
        monkeypatch,
        values=(_gate_verification(record, **gate_values),),
    )

    with pytest.raises(ValueError, match=gate_name):
        reevaluate_active_candidate_current_admission_gates(correspondence)


def test_rejected_record_prevents_a_positive_reevaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence()
    acquisition = correspondence.admission_record_acquisition
    admitted_record = acquisition.entries[0].admission_record
    rejected_record = AdmissionRecord(
        admission_id=admitted_record.admission_id,
        identity=admitted_record.identity,
        decision="rejected",
        reviewer_id=admitted_record.reviewer_id,
        decided_at=admitted_record.decided_at,
    )
    rejected_entry = AcquiredActiveCandidateAdmissionRecordEntry(
        membership=acquisition.entries[0].membership,
        document_path=acquisition.entries[0].document_path,
        admission_record_bytes=acquisition.entries[0].admission_record_bytes,
        admission_record=rejected_record,
    )
    rejected_correspondence = (
        verify_active_candidate_admission_record_correspondence(
            ActiveCandidateSourceAdmissionRecordAcquisition(
                candidate_integrity_verification=(
                    acquisition.candidate_integrity_verification
                ),
                entries=(rejected_entry,),
            )
        )
    )
    _patch_b33(
        monkeypatch,
        values=(
            _gate_verification(
                rejected_record,
                human_decision_admitted=False,
            ),
        ),
    )

    with pytest.raises(ValueError, match="human_decision_admitted"):
        reevaluate_active_candidate_current_admission_gates(
            rejected_correspondence
        )


def test_rejects_identity_mismatch_as_technical_contradiction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence()
    record = correspondence.admission_record_acquisition.entries[0].admission_record
    _patch_b33(
        monkeypatch,
        values=(_gate_verification(record, identity_matches=False),),
    )

    with pytest.raises(ValueError, match="identity contradiction"):
        reevaluate_active_candidate_current_admission_gates(correspondence)


def test_rejects_membership_alignment_mismatch_before_gate_reevaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence((1, 2))
    acquisition = correspondence.admission_record_acquisition
    mismatched_entry = AcquiredActiveCandidateAdmissionRecordEntry(
        membership=acquisition.entries[1].membership,
        document_path=acquisition.entries[0].document_path,
        admission_record_bytes=acquisition.entries[0].admission_record_bytes,
        admission_record=acquisition.entries[0].admission_record,
    )
    malformed = ActiveCandidateSourceAdmissionRecordCorrespondenceVerification(
        admission_record_acquisition=ActiveCandidateSourceAdmissionRecordAcquisition(
            candidate_integrity_verification=(
                acquisition.candidate_integrity_verification
            ),
            entries=(mismatched_entry, acquisition.entries[1]),
        )
    )

    def fail_verify(*args: object, **kwargs: object) -> AdmissionGateVerification:
        raise AssertionError("B33 must not run before alignment succeeds")

    monkeypatch.setattr(reevaluation, "verify_candidate_admission", fail_verify)

    with pytest.raises(ValueError, match="membership alignment failure"):
        reevaluate_active_candidate_current_admission_gates(malformed)


def test_reconstruction_errors_propagate_without_partial_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence()

    class FailingCandidateModel:
        @staticmethod
        def model_validate_json(value: bytes) -> PedagogicalUnitCandidate:
            raise ValueError("candidate reconstruction failed")

    monkeypatch.setattr(
        reevaluation,
        "PedagogicalUnitCandidate",
        FailingCandidateModel,
    )

    with pytest.raises(ValueError, match="candidate reconstruction failed"):
        reevaluate_active_candidate_current_admission_gates(correspondence)


def test_is_all_or_nothing_when_a_later_entry_is_not_verified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correspondence = _correspondence((1, 2))
    records = tuple(
        entry.admission_record
        for entry in correspondence.admission_record_acquisition.entries
    )
    _patch_b33(
        monkeypatch,
        values=(
            _gate_verification(records[0]),
            _gate_verification(records[1], local_validation_passed=False),
        ),
    )

    with pytest.raises(ValueError, match="local_validation_passed"):
        reevaluate_active_candidate_current_admission_gates(correspondence)
