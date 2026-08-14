from dataclasses import FrozenInstanceError

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services import pedagogical_capability_claim_precedence_validation as subject
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    CapabilityClaimAvailabilityDerivation,
    CapabilityClaimAvailabilityError,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_validation_service import validate_pedagogical_candidate
from tests.test_pedagogical_validation_service import build_candidate_payload


VALIDATOR_ID = "capability_claim_state_precedence"


def _claim(
    state: str,
    lesson_index: int,
    stage_index: int,
    *,
    skill_id: str = "skill_a",
    marker: str | None = None,
) -> CapabilityClaimAvailability:
    marker = marker or f"{state}-{lesson_index}-{stage_index}"
    return CapabilityClaimAvailability(
        lesson_id=f"lesson-{lesson_index}",
        lesson_index=lesson_index,
        point=IntraLessonAvailabilityPoint(
            sort_index=stage_index + 1,
            stage_id=f"stage-{lesson_index}-{stage_index}",
            stage_index=stage_index,
        ),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=(marker,),
    )


def _candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(build_candidate_payload())


def _findings(monkeypatch, claims, errors=()):
    batch = CapabilityClaimAvailabilityDerivation(
        availabilities=tuple(claims),
        derivation_errors=tuple(errors),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda candidate: batch,
    )
    return subject.validate_capability_claim_state_precedence(_candidate())


def _derivation(monkeypatch, claims, errors=()):
    batch = CapabilityClaimAvailabilityDerivation(
        availabilities=tuple(claims),
        derivation_errors=tuple(errors),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda candidate: batch,
    )
    return subject.derive_capability_claim_state_precedence(_candidate())


def _causes(findings):
    return [finding.message.rsplit(": ", 1)[1].removesuffix(".") for finding in findings]


def test_exposure_needs_no_predecessor(monkeypatch):
    assert _findings(monkeypatch, [_claim("EXPOSURE_AVAILABLE", 0, 0)]) == []


def test_complete_chain_in_consecutive_stages(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("INSTRUCTION_AVAILABLE", 0, 1),
        _claim("PRACTICE_AVAILABLE", 0, 2),
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 3),
    ]
    assert _findings(monkeypatch, claims) == []


def test_complete_chain_across_lessons(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 3),
        _claim("INSTRUCTION_AVAILABLE", 1, 0),
        _claim("PRACTICE_AVAILABLE", 2, 0),
        _claim("EVIDENCE_GATE_AVAILABLE", 3, 0),
    ]
    assert _findings(monkeypatch, claims) == []


@pytest.mark.parametrize(
    ("state", "cause"),
    [
        ("INSTRUCTION_AVAILABLE", "required_state_absent"),
        ("PRACTICE_AVAILABLE", "required_state_absent"),
        ("EVIDENCE_GATE_AVAILABLE", "required_state_absent"),
    ],
)
def test_missing_immediate_predecessor(monkeypatch, state, cause):
    findings = _findings(monkeypatch, [_claim(state, 0, 1)])
    assert _causes(findings) == [cause]


def test_only_later_predecessor_has_specific_cause(monkeypatch):
    claims = [
        _claim("INSTRUCTION_AVAILABLE", 0, 0),
        _claim("EXPOSURE_AVAILABLE", 0, 1),
    ]
    assert _causes(_findings(monkeypatch, claims)) == ["required_state_only_later"]


def test_same_stage_is_not_precedence(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("INSTRUCTION_AVAILABLE", 0, 0),
    ]
    assert _causes(_findings(monkeypatch, claims)) == ["required_state_same_position"]


def test_ids_cannot_turn_equal_positions_into_precedence(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0, marker="z-artifact"),
        _claim("INSTRUCTION_AVAILABLE", 0, 0, marker="a-artifact"),
    ]
    assert _causes(_findings(monkeypatch, claims)) == ["required_state_same_position"]


def test_invalid_intermediate_claim_cannot_support_next_state(monkeypatch):
    claims = [
        _claim("PRACTICE_AVAILABLE", 0, 0),
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 1),
    ]
    assert _causes(_findings(monkeypatch, claims)) == [
        "required_state_absent",
        "required_state_not_validly_chained",
    ]


def test_valid_equivalent_claim_can_support_next_state(monkeypatch):
    claims = [
        _claim("INSTRUCTION_AVAILABLE", 0, 0, marker="invalid-instruction"),
        _claim("EXPOSURE_AVAILABLE", 0, 1),
        _claim("INSTRUCTION_AVAILABLE", 0, 2, marker="valid-instruction"),
        _claim("PRACTICE_AVAILABLE", 0, 3),
    ]
    findings = _findings(monkeypatch, claims)
    assert len(findings) == 1
    assert "invalid-instruction" in findings[0].reference_ids


def test_any_valid_earlier_predecessor_is_sufficient(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0, marker="first"),
        _claim("EXPOSURE_AVAILABLE", 0, 1, marker="second"),
        _claim("INSTRUCTION_AVAILABLE", 0, 2),
    ]
    assert _findings(monkeypatch, claims) == []


def test_problematic_higher_claims_get_independent_deterministic_findings(monkeypatch):
    claims = [
        _claim("PRACTICE_AVAILABLE", 1, 0, marker="later"),
        _claim("INSTRUCTION_AVAILABLE", 0, 1, marker="earlier"),
    ]
    findings = _findings(monkeypatch, claims)
    assert [finding.reference_ids[-1] for finding in findings] == ["earlier", "later"]
    assert all(finding.validator_id == VALIDATOR_ID for finding in findings)


def test_one_skill_never_supports_another(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0, skill_id="skill_a"),
        _claim("INSTRUCTION_AVAILABLE", 0, 1, skill_id="skill_b"),
    ]
    assert _causes(_findings(monkeypatch, claims)) == ["required_state_absent"]


def test_derivation_errors_are_ignored(monkeypatch):
    error = CapabilityClaimAvailabilityError(
        lesson_id="lesson-0",
        skill_id="skill_a",
        preparation_state="EXPOSURE_AVAILABLE",
        artifact_ids=("unpositionable",),
        cause="no canonical stage",
    )
    assert _findings(monkeypatch, [], [error]) == []


def test_omitted_claim_cannot_support_a_later_state(monkeypatch):
    error = CapabilityClaimAvailabilityError(
        lesson_id="lesson-0",
        skill_id="skill_a",
        preparation_state="EXPOSURE_AVAILABLE",
        artifact_ids=("unpositionable",),
        cause="no canonical stage",
    )
    findings = _findings(
        monkeypatch,
        [_claim("INSTRUCTION_AVAILABLE", 0, 1)],
        [error],
    )
    assert _causes(findings) == ["required_state_absent"]


def test_curriculum_positions_override_reverse_ids(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 1, marker="z-last-id"),
        _claim("INSTRUCTION_AVAILABLE", 1, 0, marker="a-first-id"),
    ]
    assert _findings(monkeypatch, claims) == []


def test_declaration_order_does_not_change_findings(monkeypatch):
    claims = [
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 3),
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("PRACTICE_AVAILABLE", 0, 2),
        _claim("INSTRUCTION_AVAILABLE", 0, 1),
    ]
    assert _findings(monkeypatch, claims) == []
    assert _findings(monkeypatch, list(reversed(claims))) == []


def test_legacy_candidate_and_empty_batch_have_no_findings(monkeypatch):
    assert _findings(monkeypatch, []) == []


def test_empty_plan_has_no_findings(monkeypatch):
    candidate = _candidate()
    candidate.lesson_capability_plans = []
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda value: CapabilityClaimAvailabilityDerivation((), ()),
    )
    assert subject.validate_capability_claim_state_precedence(candidate) == []


def test_required_stages_do_not_intervene(monkeypatch):
    candidate = _candidate()
    candidate.specification.skills[0].required_stages = ["consolidate"]
    batch = CapabilityClaimAvailabilityDerivation(
        (_claim("EXPOSURE_AVAILABLE", 0, 0),),
        (),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda value: batch,
    )
    assert subject.validate_capability_claim_state_precedence(candidate) == []


def test_batch_and_availabilities_remain_immutable():
    claim = _claim("EXPOSURE_AVAILABLE", 0, 0)
    batch = CapabilityClaimAvailabilityDerivation((claim,), ())
    with pytest.raises(FrozenInstanceError):
        batch.availabilities = ()
    with pytest.raises(FrozenInstanceError):
        claim.lesson_index = 4


def test_finding_contains_required_traceability(monkeypatch):
    claim = _claim("PRACTICE_AVAILABLE", 0, 1, marker="artifact-x")
    finding = _findings(monkeypatch, [claim])[0]
    assert finding.reference_ids == [
        "lesson-0",
        "skill_a",
        "PRACTICE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "artifact-x",
    ]
    assert "required_state_absent" in finding.message


def test_integrates_with_candidate_validation(monkeypatch):
    batch = CapabilityClaimAvailabilityDerivation(
        (_claim("INSTRUCTION_AVAILABLE", 0, 1),),
        (),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda value: batch,
    )
    report = validate_pedagogical_candidate(_candidate())
    assert any(finding.validator_id == VALIDATOR_ID for finding in report.findings)


def test_precedence_derivation_is_typed_and_immutable(monkeypatch):
    result = _derivation(
        monkeypatch,
        [_claim("EXPOSURE_AVAILABLE", 0, 0)],
    )

    assert isinstance(result, subject.CapabilityClaimPrecedenceDerivation)
    assert isinstance(result.valid_claims, tuple)
    assert isinstance(result.precedence_errors, tuple)
    with pytest.raises(FrozenInstanceError):
        result.valid_claims = ()


def test_public_canonical_state_order_is_exact_and_immutable():
    assert subject.CURRICULUM_PREPARATION_STATE_ORDER == (
        "EXPOSURE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "PRACTICE_AVAILABLE",
        "EVIDENCE_GATE_AVAILABLE",
    )
    assert isinstance(subject.CURRICULUM_PREPARATION_STATE_ORDER, tuple)
    with pytest.raises(TypeError):
        subject.CURRICULUM_PREPARATION_STATE_ORDER[0] = "PRACTICE_AVAILABLE"


@pytest.mark.parametrize(
    ("state", "expected_index"),
    [
        ("EXPOSURE_AVAILABLE", 0),
        ("INSTRUCTION_AVAILABLE", 1),
        ("PRACTICE_AVAILABLE", 2),
        ("EVIDENCE_GATE_AVAILABLE", 3),
    ],
)
def test_public_state_index_uses_canonical_order(state, expected_index):
    assert subject.curriculum_preparation_state_index(state) == expected_index


def test_public_state_index_rejects_unknown_state():
    with pytest.raises(ValueError, match="not in tuple"):
        subject.curriculum_preparation_state_index("UNKNOWN_AVAILABLE")


def test_no_private_duplicate_state_order_remains():
    assert not hasattr(subject, "_STATE_ORDER")
    assert not hasattr(subject, "_state_index")


def test_complete_chain_is_returned_as_individual_valid_claims(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("INSTRUCTION_AVAILABLE", 0, 1),
        _claim("PRACTICE_AVAILABLE", 0, 2),
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 3),
    ]

    result = _derivation(monkeypatch, claims)

    assert result.valid_claims == tuple(claims)
    assert result.precedence_errors == ()


def test_gaps_are_typed_errors_and_not_valid_claims(monkeypatch):
    claims = [
        _claim("INSTRUCTION_AVAILABLE", 0, 0),
        _claim("PRACTICE_AVAILABLE", 0, 1),
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 2),
    ]

    result = _derivation(monkeypatch, claims)

    assert result.valid_claims == ()
    assert all(
        isinstance(error, subject.CapabilityClaimPrecedenceError)
        for error in result.precedence_errors
    )
    assert [error.cause for error in result.precedence_errors] == [
        "required_state_absent",
        "required_state_not_validly_chained",
        "required_state_not_validly_chained",
    ]


def test_valid_equivalent_claims_and_positions_are_not_collapsed(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0, marker="first"),
        _claim("EXPOSURE_AVAILABLE", 0, 1, marker="second"),
        _claim("INSTRUCTION_AVAILABLE", 1, 0, marker="third"),
    ]

    result = _derivation(monkeypatch, claims)

    assert result.valid_claims == tuple(claims)
    assert [
        (claim.lesson_index, claim.point.stage_index)
        for claim in result.valid_claims
    ] == [(0, 0), (0, 1), (1, 0)]


def test_positioned_claims_are_partitioned_exactly_once(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("INSTRUCTION_AVAILABLE", 0, 0),
        _claim("INSTRUCTION_AVAILABLE", 0, 1, marker="valid-instruction"),
        _claim("PRACTICE_AVAILABLE", 0, 2),
    ]

    result = _derivation(monkeypatch, claims)
    partition = [*result.valid_claims, *(error.claim for error in result.precedence_errors)]

    assert len(partition) == len(claims)
    assert {id(claim) for claim in partition} == {id(claim) for claim in claims}
    assert not (
        {id(claim) for claim in result.valid_claims}
        & {id(error.claim) for error in result.precedence_errors}
    )


def test_slice_5_errors_are_outside_the_partition(monkeypatch):
    error = CapabilityClaimAvailabilityError(
        lesson_id="lesson-0",
        skill_id="skill_a",
        preparation_state="EXPOSURE_AVAILABLE",
        artifact_ids=("unpositionable",),
        cause="no canonical stage",
    )

    result = _derivation(monkeypatch, [], [error])

    assert result.valid_claims == ()
    assert result.precedence_errors == ()


def test_batch_is_independent_of_claim_declaration_order(monkeypatch):
    claims = [
        _claim("EVIDENCE_GATE_AVAILABLE", 0, 3),
        _claim("EXPOSURE_AVAILABLE", 0, 0),
        _claim("PRACTICE_AVAILABLE", 0, 2),
        _claim("INSTRUCTION_AVAILABLE", 0, 1),
    ]

    first = _derivation(monkeypatch, claims)
    second = _derivation(monkeypatch, list(reversed(claims)))

    assert first == second


def test_derivation_does_not_modify_candidate(monkeypatch):
    candidate = _candidate()
    before = candidate.model_dump(mode="json")
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_availabilities",
        lambda value: CapabilityClaimAvailabilityDerivation((), ()),
    )

    subject.derive_capability_claim_state_precedence(candidate)

    assert candidate.model_dump(mode="json") == before


def test_derivation_exposes_no_ledger_aggregation(monkeypatch):
    result = _derivation(
        monkeypatch,
        [_claim("EXPOSURE_AVAILABLE", 0, 0)],
    )

    assert not hasattr(result, "highest_preparation_state")
    assert not hasattr(result, "first_position")
    assert not hasattr(result, "last_position")
    assert not hasattr(result, "supporting_lesson_ids")
    assert not hasattr(result, "supporting_artifact_ids")


def test_validator_is_an_exact_adapter_for_precedence_errors(monkeypatch):
    claim = _claim("PRACTICE_AVAILABLE", 0, 1, marker="artifact-x")
    error = subject.CapabilityClaimPrecedenceError(
        claim=claim,
        required_preparation_state="INSTRUCTION_AVAILABLE",
        cause="required_state_absent",
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_state_precedence",
        lambda candidate: subject.CapabilityClaimPrecedenceDerivation(
            valid_claims=(),
            precedence_errors=(error,),
        ),
    )

    findings = subject.validate_capability_claim_state_precedence(_candidate())

    assert len(findings) == 1
    assert findings[0].validator_id == VALIDATOR_ID
    assert findings[0].severity == "error"
    assert findings[0].reference_ids == [
        "lesson-0",
        "skill_a",
        "PRACTICE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "artifact-x",
    ]
    assert findings[0].message.endswith("required_state_absent.")
