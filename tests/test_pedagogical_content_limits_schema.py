import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import (
    ContentLimits,
    PedagogicalUnitSpecification,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
)


def test_content_limits_are_optional():
    """Accept a specification without explicit quantitative limits.

    Acepta una especificación sin límites cuantitativos explícitos.
    """
    limits = ContentLimits()

    assert all(
        value is None
        for value in limits.model_dump().values()
    )


def test_valid_content_limits_are_accepted():
    """Accept measurable minimum and maximum content limits.

    Acepta límites mínimos y máximos de contenido medible.
    """
    limits = ContentLimits.model_validate(
        {
            "min_lessons": 1,
            "max_lessons": 4,
            "min_examples_per_lesson": 0,
            "max_examples_per_lesson": 6,
            "min_conversations_per_lesson": 0,
            "max_conversations_per_lesson": 3,
            "min_exercises_per_lesson": 0,
            "max_exercises_per_lesson": 5,
            "min_options_per_exercise": 2,
            "max_options_per_exercise": 5,
            "min_turns_per_conversation": 1,
            "max_turns_per_conversation": 12,
        }
    )

    assert limits.max_lessons == 4
    assert limits.min_options_per_exercise == 2


@pytest.mark.parametrize(
    "field",
    [
        "min_lessons",
        "max_lessons",
        "min_examples_per_lesson",
        "max_examples_per_lesson",
        "min_conversations_per_lesson",
        "max_conversations_per_lesson",
        "min_exercises_per_lesson",
        "max_exercises_per_lesson",
        "min_options_per_exercise",
        "max_options_per_exercise",
        "min_turns_per_conversation",
        "max_turns_per_conversation",
    ],
)
def test_content_limits_reject_negative_values(field):
    """Reject negative quantitative limits.

    Rechaza límites cuantitativos negativos.
    """
    with pytest.raises(ValidationError, match="greater_than_equal"):
        ContentLimits.model_validate({field: -1})


@pytest.mark.parametrize(
    ("minimum_field", "maximum_field"),
    [
        ("min_lessons", "max_lessons"),
        ("min_examples_per_lesson", "max_examples_per_lesson"),
        (
            "min_conversations_per_lesson",
            "max_conversations_per_lesson",
        ),
        ("min_exercises_per_lesson", "max_exercises_per_lesson"),
        ("min_options_per_exercise", "max_options_per_exercise"),
        (
            "min_turns_per_conversation",
            "max_turns_per_conversation",
        ),
    ],
)
def test_content_limits_reject_minimum_above_maximum(
    minimum_field,
    maximum_field,
):
    """Reject incoherent minimum and maximum pairs.

    Rechaza pares mínimo y máximo incoherentes.
    """
    payload = {minimum_field: 3, maximum_field: 2}

    with pytest.raises(
        ValidationError,
        match="minimum cannot exceed maximum",
    ):
        ContentLimits.model_validate(payload)


def test_unit_specification_accepts_structured_content_limits():
    """Attach structured limits to the approved unit specification.

    Vincula límites estructurados con la especificación aprobada.
    """
    payload = build_candidate_payload()["specification"]
    payload["content_limits"] = {
        "min_lessons": 1,
        "max_lessons": 3,
        "min_options_per_exercise": 2,
        "max_options_per_exercise": 4,
    }

    specification = PedagogicalUnitSpecification.model_validate(payload)

    assert specification.content_limits.min_lessons == 1
    assert specification.content_limits.max_options_per_exercise == 4
