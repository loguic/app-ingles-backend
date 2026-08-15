from dataclasses import FrozenInstanceError, fields
import inspect

import pytest

from app.schemas.content import ContentTreeResponse, Level, Unit
from app.services import content_service
from app.services.pedagogical_accumulated_curriculum_preparation import (
    AccumulatedSkillPreparation,
)
from app.services.pedagogical_authoritative_prerequisite_conclusion import (
    CurriculumPrerequisiteAuthoritativeConclusionDerivation,
    CurriculumPrerequisiteAuthoritativeUncertainty,
    CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin,
    derive_authoritative_prerequisite_conclusions,
)
from app.services.pedagogical_complete_from_authoritative_origin import (
    CompleteFromAuthoritativeOrigin,
)
from app.services.pedagogical_curriculum_context_scope import (
    CurriculumContextScope,
)
from app.services.pedagogical_curriculum_skill_prerequisite_assessment import (
    CurriculumSkillPrerequisiteAssessment,
    CurriculumSkillPrerequisiteAssessmentDerivation,
)
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)


def _proof(monkeypatch) -> CompleteFromAuthoritativeOrigin:
    tree = ContentTreeResponse(
        levels=[Level(code="B1", units=[Unit(id="b1-unit", title="B1")])]
    )
    monkeypatch.setattr(content_service, "build_content_tree", lambda: tree)
    authority = content_service.load_authoritative_curriculum_hierarchy()
    position = CurriculumUnitPosition("B1", 2, "b1-unit", 0)
    context = OrderedCurriculumCandidateContext(
        scope=CurriculumContextScope(
            start_position=position,
            target_position=position,
            required_positions=(position,),
        ),
        entries=(),
    )
    return CompleteFromAuthoritativeOrigin(
        authority=authority,
        context=context,
    )


def _assessment(
    *,
    outcome="unresolved_in_context",
    preparation=None,
    related_errors=(),
) -> CurriculumSkillPrerequisiteAssessment:
    return CurriculumSkillPrerequisiteAssessment(
        entry=object(),  # type: ignore[arg-type]
        consumption=object(),  # type: ignore[arg-type]
        accumulated_skill_preparation=preparation,
        related_precedence_errors=related_errors,
        outcome=outcome,
    )


def _assessment_derivation(
    assessments=(),
    *,
    consumption_errors=(),
    preparation_resolution_errors=(),
    precedence_observations=(),
) -> CurriculumSkillPrerequisiteAssessmentDerivation:
    return CurriculumSkillPrerequisiteAssessmentDerivation(
        assessments=assessments,
        consumption_errors=consumption_errors,
        preparation_resolution_errors=preparation_resolution_errors,
        precedence_observations=precedence_observations,
    )


def _derive(monkeypatch, proof, assessment_derivation):
    calls = []

    def derive(context):
        calls.append(context)
        return assessment_derivation

    monkeypatch.setattr(
        "app.services.pedagogical_authoritative_prerequisite_conclusion."
        "derive_curriculum_skill_prerequisite_assessments",
        derive,
    )
    result = derive_authoritative_prerequisite_conclusions(proof)
    assert calls == [proof.context]
    assert result.assessment_derivation is assessment_derivation
    return result


def test_models_are_frozen_and_do_not_duplicate_source_fields():
    models = (
        CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin,
        CurriculumPrerequisiteAuthoritativeUncertainty,
        CurriculumPrerequisiteAuthoritativeConclusionDerivation,
    )
    assert all(model.__dataclass_params__.frozen for model in models)
    assert tuple(
        field.name
        for field in fields(CurriculumPrerequisiteAuthoritativeUncertainty)
    ) == ("assessment",)
    uncertainty = CurriculumPrerequisiteAuthoritativeUncertainty(
        assessment=_assessment(related_errors=(object(),))
    )
    with pytest.raises(FrozenInstanceError):
        uncertainty.assessment = _assessment()


def test_api_accepts_only_proof():
    assert tuple(
        inspect.signature(
            derive_authoritative_prerequisite_conclusions
        ).parameters
    ) == ("proof",)


def test_missing_skill_unresolved_produces_one_conclusion(monkeypatch):
    proof = _proof(monkeypatch)
    assessment = _assessment(preparation=None)

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((assessment,)),
    )

    assert result.uncertainties == ()
    assert len(result.conclusions) == 1
    assert result.conclusions[0].proof is proof
    assert result.conclusions[0].assessment is assessment


def test_lower_state_unresolved_produces_one_conclusion(monkeypatch):
    proof = _proof(monkeypatch)
    preparation = AccumulatedSkillPreparation(
        skill_id="skill-a",
        highest_preparation_state="INSTRUCTION_AVAILABLE",
        available_claims=(),
    )
    assessment = _assessment(preparation=preparation)

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((assessment,)),
    )

    assert result.conclusions[0].assessment is assessment
    assert result.conclusions[0].assessment.accumulated_skill_preparation is preparation


def test_related_precedence_error_produces_uncertainty(monkeypatch):
    proof = _proof(monkeypatch)
    related_error = object()
    assessment = _assessment(related_errors=(related_error,))

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((assessment,)),
    )

    assert result.conclusions == ()
    assert len(result.uncertainties) == 1
    assert result.uncertainties[0].assessment is assessment
    assert result.uncertainties[0].assessment.related_precedence_errors == (
        related_error,
    )


def test_satisfied_assessment_is_not_applicable_even_with_related_error(
    monkeypatch,
):
    proof = _proof(monkeypatch)
    assessment = _assessment(
        outcome="satisfied_in_context",
        related_errors=(object(),),
    )

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((assessment,)),
    )

    assert result.conclusions == ()
    assert result.uncertainties == ()


def test_slice_19_derivation_errors_remain_source_only(monkeypatch):
    proof = _proof(monkeypatch)
    consumption_error = object()
    preparation_error = object()
    source = _assessment_derivation(
        consumption_errors=(consumption_error,),
        preparation_resolution_errors=(preparation_error,),
    )

    result = _derive(monkeypatch, proof, source)

    assert result.conclusions == ()
    assert result.uncertainties == ()
    assert result.assessment_derivation.consumption_errors == (
        consumption_error,
    )
    assert result.assessment_derivation.preparation_resolution_errors == (
        preparation_error,
    )


def test_other_skill_observation_does_not_block_assessment(monkeypatch):
    proof = _proof(monkeypatch)
    assessment = _assessment(related_errors=())
    other_skill_observation = object()
    source = _assessment_derivation(
        (assessment,),
        precedence_observations=(other_skill_observation,),
    )

    result = _derive(monkeypatch, proof, source)

    assert len(result.conclusions) == 1
    assert result.uncertainties == ()
    assert result.assessment_derivation.precedence_observations == (
        other_skill_observation,
    )


def test_context_without_prerequisites_is_empty(monkeypatch):
    proof = _proof(monkeypatch)

    result = _derive(monkeypatch, proof, _assessment_derivation())

    assert result.conclusions == ()
    assert result.uncertainties == ()


def test_multiple_assessments_preserve_order_and_point_specific_results(
    monkeypatch,
):
    proof = _proof(monkeypatch)
    first = _assessment()
    satisfied = _assessment(outcome="satisfied_in_context")
    uncertain = _assessment(related_errors=(object(),))
    last = _assessment()

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((first, satisfied, uncertain, last)),
    )

    assert tuple(item.assessment for item in result.conclusions) == (
        first,
        last,
    )
    assert tuple(item.assessment for item in result.uncertainties) == (
        uncertain,
    )


def test_intermediate_target_proof_is_sufficient(monkeypatch):
    proof = _proof(monkeypatch)
    assessment = _assessment()

    result = _derive(
        monkeypatch,
        proof,
        _assessment_derivation((assessment,)),
    )

    assert result.conclusions[0].proof is proof


def test_derivation_does_not_mutate_inputs(monkeypatch):
    proof = _proof(monkeypatch)
    assessment = _assessment()
    source = _assessment_derivation((assessment,))
    before_scope = proof.context.scope
    before_assessments = source.assessments

    _derive(monkeypatch, proof, source)

    assert proof.context.scope is before_scope
    assert source.assessments is before_assessments
