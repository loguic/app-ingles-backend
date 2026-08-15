import inspect
from types import SimpleNamespace

from app.services.pedagogical_authoritative_prerequisite_conclusion import (
    CurriculumPrerequisiteAuthoritativeConclusionDerivation,
    CurriculumPrerequisiteAuthoritativeUncertainty,
    CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin,
)
from app.services.pedagogical_authoritative_prerequisite_validation import (
    VALIDATOR_ID,
    validate_authoritative_prerequisite_conclusions,
)
from app.services.pedagogical_curriculum_skill_prerequisite_assessment import (
    CurriculumSkillPrerequisiteAssessmentDerivation,
)


def _assessment(
    *,
    unit_id="b1-unit",
    lesson_id="b1-lesson",
    stage_id="b1-stage",
    skill_id="structured_speaking",
    required_state="PRACTICE_AVAILABLE",
):
    prerequisite = SimpleNamespace(
        required_skill_id=skill_id,
        required_state=required_state,
    )
    point = SimpleNamespace(lesson_id=lesson_id, stage_id=stage_id)
    consumption = SimpleNamespace(
        prerequisite=prerequisite,
        before_point=point,
    )
    entry = SimpleNamespace(position=SimpleNamespace(unit_id=unit_id))
    return SimpleNamespace(entry=entry, consumption=consumption)


def _source_derivation(*, consumption_errors=(), preparation_errors=()):
    return CurriculumSkillPrerequisiteAssessmentDerivation(
        assessments=(),
        consumption_errors=consumption_errors,
        preparation_resolution_errors=preparation_errors,
        precedence_observations=(),
    )


def _conclusion(assessment):
    return CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin(
        proof=object(),  # type: ignore[arg-type]
        assessment=assessment,  # type: ignore[arg-type]
    )


def _derivation(*, conclusions=(), uncertainties=(), source=None):
    return CurriculumPrerequisiteAuthoritativeConclusionDerivation(
        assessment_derivation=source or _source_derivation(),
        conclusions=conclusions,
        uncertainties=uncertainties,
    )


def test_api_accepts_only_conclusion_derivation():
    assert tuple(
        inspect.signature(
            validate_authoritative_prerequisite_conclusions
        ).parameters
    ) == ("derivation",)


def test_one_conclusion_maps_to_one_exact_curriculum_finding():
    assessment = _assessment()

    findings = validate_authoritative_prerequisite_conclusions(
        _derivation(conclusions=(_conclusion(assessment),))
    )

    assert len(findings) == 1
    finding = findings[0]
    assert finding.validator_id == VALIDATOR_ID
    assert finding.validator_id == "authoritative_prerequisite_preparation"
    assert finding.severity == "error"
    assert finding.reference_ids == [
        "b1-unit",
        "b1-lesson",
        "b1-stage",
        "structured_speaking",
        "PRACTICE_AVAILABLE",
    ]
    assert all(isinstance(value, str) for value in finding.reference_ids)
    for value in finding.reference_ids[1:]:
        assert value in finding.message


def test_message_has_curriculum_not_learner_or_global_semantics():
    finding = validate_authoritative_prerequisite_conclusions(
        _derivation(conclusions=(_conclusion(_assessment()),))
    )[0]

    assert "authoritative curriculum prefix" in finding.message
    forbidden = (
        "learner",
        "student",
        "mastered",
        "mastery",
        "globally unsatisfied",
    )
    assert all(term not in finding.message.lower() for term in forbidden)


def test_same_skill_consumptions_remain_distinct_and_ordered():
    first = _assessment(
        unit_id="z-unit",
        lesson_id="z-lesson",
        stage_id="z-stage",
        skill_id="same_skill",
    )
    second = _assessment(
        unit_id="a-unit",
        lesson_id="a-lesson",
        stage_id="a-stage",
        skill_id="same_skill",
    )

    findings = validate_authoritative_prerequisite_conclusions(
        _derivation(
            conclusions=(_conclusion(first), _conclusion(second))
        )
    )

    assert [finding.reference_ids for finding in findings] == [
        [
            "z-unit",
            "z-lesson",
            "z-stage",
            "same_skill",
            "PRACTICE_AVAILABLE",
        ],
        [
            "a-unit",
            "a-lesson",
            "a-stage",
            "same_skill",
            "PRACTICE_AVAILABLE",
        ],
    ]


def test_empty_and_uncertain_derivations_produce_no_findings():
    assessment = _assessment()
    uncertainty = CurriculumPrerequisiteAuthoritativeUncertainty(
        assessment=assessment  # type: ignore[arg-type]
    )

    assert validate_authoritative_prerequisite_conclusions(
        _derivation()
    ) == []
    assert validate_authoritative_prerequisite_conclusions(
        _derivation(uncertainties=(uncertainty,))
    ) == []


def test_uncertainty_does_not_change_findings_for_conclusions():
    conclusive = _assessment(skill_id="conclusive_skill")
    uncertain = _assessment(skill_id="uncertain_skill")

    findings = validate_authoritative_prerequisite_conclusions(
        _derivation(
            conclusions=(_conclusion(conclusive),),
            uncertainties=(
                CurriculumPrerequisiteAuthoritativeUncertainty(
                    assessment=uncertain  # type: ignore[arg-type]
                ),
            ),
        )
    )

    assert len(findings) == 1
    assert findings[0].reference_ids[3] == "conclusive_skill"


def test_source_derivation_errors_never_create_additional_findings():
    source = _source_derivation(
        consumption_errors=(object(),),
        preparation_errors=(object(),),
    )
    derivation_without_conclusion = _derivation(source=source)
    derivation_with_conclusion = _derivation(
        source=source,
        conclusions=(_conclusion(_assessment()),),
    )

    assert validate_authoritative_prerequisite_conclusions(
        derivation_without_conclusion
    ) == []
    assert len(
        validate_authoritative_prerequisite_conclusions(
            derivation_with_conclusion
        )
    ) == 1


def test_validator_is_pure_and_does_not_integrate_or_recalculate():
    derivation = _derivation(
        conclusions=(_conclusion(_assessment()),),
        uncertainties=(
            CurriculumPrerequisiteAuthoritativeUncertainty(
                assessment=_assessment()  # type: ignore[arg-type]
            ),
        ),
        source=_source_derivation(consumption_errors=(object(),)),
    )
    before_assessment_derivation = derivation.assessment_derivation
    before_conclusions = derivation.conclusions
    before_uncertainties = derivation.uncertainties

    first = validate_authoritative_prerequisite_conclusions(derivation)
    second = validate_authoritative_prerequisite_conclusions(derivation)

    assert first == second
    assert derivation.assessment_derivation is before_assessment_derivation
    assert derivation.conclusions is before_conclusions
    assert derivation.uncertainties is before_uncertainties
    module_globals = validate_authoritative_prerequisite_conclusions.__globals__
    forbidden_names = {
        "derive_curriculum_skill_prerequisite_assessments",
        "derive_complete_from_authoritative_origin",
        "derive_authoritative_prerequisite_conclusions",
        "load_authoritative_curriculum_hierarchy",
        "validate_pedagogical_candidate",
    }
    assert forbidden_names.isdisjoint(module_globals)
