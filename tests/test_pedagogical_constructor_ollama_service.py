import json
from copy import deepcopy
from pathlib import Path

import httpx
import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from app.schemas.pedagogical_unit import ContentLimits, PedagogicalUnitSpecification
from app.services.pedagogical_constructor_ollama_service import (
    OllamaPedagogicalConstructor,
    OllamaPedagogicalConstructorConfig,
    OllamaPedagogicalConstructorRuntimeError,
    _content_graph_json_schema,
    _prompt,
    generate_pedagogical_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
SPECIFICATION = PedagogicalUnitSpecification.model_validate_json(
    (
        ROOT
        / "content/candidates/a1-u1/pedagogical-unit-specification-v3.json"
    ).read_bytes()
)
CANDIDATE_DOCUMENT = json.loads(
    (
        ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
    ).read_text()
)
GENERATED_CONTENT_DOCUMENT = {
    field: value
    for field, value in CANDIDATE_DOCUMENT.items()
    if field != "specification"
}
CONTENT_GRAPH_DOCUMENT = {
    field: GENERATED_CONTENT_DOCUMENT[field]
    for field in (
        "candidate_unit",
        "evaluation_plans",
        "feedback_plans",
        "lesson_capability_plans",
        "required_resource_ids",
        "pending_human_decisions",
        "proposed_change_summary",
    )
    if field in GENERATED_CONTENT_DOCUMENT
}
PEDAGOGICAL_LINKS_DOCUMENT = {
    "skill_coverage": GENERATED_CONTENT_DOCUMENT["skill_coverage"],
    "exercise_skill_links": [
        {
            "exercise_id": exercise["id"],
            "skill_ids": exercise["skill_ids"],
        }
        for lesson in CANDIDATE_DOCUMENT["candidate_unit"]["lessons"]
        for exercise in lesson.get("exercises", [])
    ],
}


def _constructor(handler) -> OllamaPedagogicalConstructor:
    client = httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    )
    return OllamaPedagogicalConstructor(
        OllamaPedagogicalConstructorConfig(
            base_url="http://ollama.test",
            model="qwen3:8b",
            timeout_seconds=5,
        ),
        client=client,
    )


def _two_phase_constructor(handler) -> OllamaPedagogicalConstructor:
    return _constructor(handler)


def _two_phase_handler(responses, observed=None):
    response_iterator = iter(responses)

    def handler(request):
        if observed is not None:
            observed.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"response": json.dumps(next(response_iterator))},
        )

    return handler


def _content_graph_without_experience() -> dict[str, object]:
    graph = dict(CONTENT_GRAPH_DOCUMENT)
    graph["candidate_unit"] = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"])
    lesson = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"]["lessons"][0])
    lesson.pop("experience")
    graph["candidate_unit"]["lessons"] = [lesson]
    return graph


def _external_review_requirement_validator() -> Draft202012Validator:
    schema = _content_graph_json_schema(SPECIFICATION)
    return Draft202012Validator(schema["$defs"]["ExternalReviewRequirement"])


def _external_review_requirement(
    dimension: str,
    production_function: str | None = None,
) -> dict[str, object]:
    requirement = {
        "dimension": dimension,
        "allowed_results": ["positive", "negative", "pending"],
        "question": "Can an external reviewer confirm this requirement?",
    }
    if production_function is not None:
        requirement["production_function"] = production_function
    return requirement


def test_content_graph_schema_rejects_relevance_without_production_function():
    with pytest.raises(ValidationError):
        _external_review_requirement_validator().validate(
            _external_review_requirement("relevance")
        )


def test_content_graph_schema_rejects_intelligibility_without_production_function():
    with pytest.raises(ValidationError):
        _external_review_requirement_validator().validate(
            _external_review_requirement("intelligibility")
        )


@pytest.mark.parametrize("dimension", ["relevance", "intelligibility"])
def test_content_graph_schema_accepts_qualitative_review_with_valid_production_function(
    dimension,
):
    _external_review_requirement_validator().validate(
        _external_review_requirement(dimension, "transfer")
    )


def test_content_graph_schema_rejects_invalid_qualitative_production_function():
    with pytest.raises(ValidationError):
        _external_review_requirement_validator().validate(
            _external_review_requirement("relevance", "unsupported")
        )


def test_content_graph_schema_preserves_historical_review_without_production_function():
    _external_review_requirement_validator().validate(
        _external_review_requirement("intention_understanding")
    )


def test_a1_u1_content_graph_schema_requires_lesson_experience_v3():
    schema = _content_graph_json_schema(SPECIFICATION)

    lesson = schema["$defs"]["Lesson"]
    assert "experience" in lesson["required"]
    assert schema["$defs"]["LessonExperience"]["properties"][
        "contract_version"
    ] == {"const": "3.0"}


def test_a1_u1_content_graph_schema_rejects_missing_lesson_experience():
    validator = Draft202012Validator(_content_graph_json_schema(SPECIFICATION))

    with pytest.raises(ValidationError):
        validator.validate(_content_graph_without_experience())


def test_a1_u1_content_graph_schema_rejects_non_v3_lesson_experience():
    graph = dict(CONTENT_GRAPH_DOCUMENT)
    graph["candidate_unit"] = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"])
    lesson = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"]["lessons"][0])
    lesson["experience"] = dict(lesson["experience"])
    lesson["experience"]["contract_version"] = "2.0"
    graph["candidate_unit"]["lessons"] = [lesson]
    validator = Draft202012Validator(_content_graph_json_schema(SPECIFICATION))

    with pytest.raises(ValidationError):
        validator.validate(graph)


def test_content_graph_schema_keeps_optional_experience_without_v3_obligation():
    specification = SPECIFICATION.model_copy(
        update={"technical_constraints": []}
    )
    validator = Draft202012Validator(_content_graph_json_schema(specification))

    validator.validate(_content_graph_without_experience())


def test_content_graph_schema_does_not_mutate_approved_specification():
    before = SPECIFICATION.model_dump(mode="json")

    _content_graph_json_schema(SPECIFICATION)

    assert SPECIFICATION.model_dump(mode="json") == before


def test_content_graph_schema_projects_exactly_one_lesson():
    specification = SPECIFICATION.model_copy(
        update={"content_limits": ContentLimits(min_lessons=1, max_lessons=1)}
    )

    lessons = _content_graph_json_schema(specification)["$defs"]["Unit"][
        "properties"
    ]["lessons"]

    assert lessons["minItems"] == 1
    assert lessons["maxItems"] == 1


def test_content_graph_schema_projects_defined_content_limits():
    specification = SPECIFICATION.model_copy(
        update={
            "content_limits": ContentLimits(
                min_lessons=1,
                max_lessons=2,
                min_examples_per_lesson=3,
                max_examples_per_lesson=4,
                min_conversations_per_lesson=2,
                max_conversations_per_lesson=3,
                min_exercises_per_lesson=1,
                max_exercises_per_lesson=2,
                min_options_per_exercise=3,
                max_options_per_exercise=4,
                min_turns_per_conversation=2,
                max_turns_per_conversation=5,
            )
        }
    )
    definitions = _content_graph_json_schema(specification)["$defs"]

    assert definitions["Unit"]["properties"]["lessons"]["minItems"] == 1
    assert definitions["Unit"]["properties"]["lessons"]["maxItems"] == 2
    assert definitions["Lesson"]["properties"]["examples"]["minItems"] == 3
    assert definitions["Lesson"]["properties"]["examples"]["maxItems"] == 4
    assert definitions["Lesson"]["properties"]["conversations"]["minItems"] == 2
    assert definitions["Lesson"]["properties"]["conversations"]["maxItems"] == 3
    assert definitions["Lesson"]["properties"]["exercises"]["minItems"] == 1
    assert definitions["Lesson"]["properties"]["exercises"]["maxItems"] == 2
    assert definitions["ExerciseMCQ"]["properties"]["options"]["minItems"] == 3
    assert definitions["ExerciseMCQ"]["properties"]["options"]["maxItems"] == 4
    assert definitions["Conversation"]["properties"]["turns"]["minItems"] == 2
    assert definitions["Conversation"]["properties"]["turns"]["maxItems"] == 5


def test_content_graph_schema_does_not_add_undefined_content_limits():
    specification = SPECIFICATION.model_copy(
        update={"content_limits": ContentLimits()}
    )
    definitions = _content_graph_json_schema(specification)["$defs"]

    assert "minItems" not in definitions["Unit"]["properties"]["lessons"]
    assert "maxItems" not in definitions["Unit"]["properties"]["lessons"]
    assert "minItems" not in definitions["Lesson"]["properties"]["examples"]
    assert "maxItems" not in definitions["Lesson"]["properties"]["examples"]
    assert "maxItems" not in definitions["Lesson"]["properties"]["conversations"]
    assert "maxItems" not in definitions["Lesson"]["properties"]["exercises"]
    assert "maxItems" not in definitions["ExerciseMCQ"]["properties"]["options"]
    assert "minItems" not in definitions["Conversation"]["properties"]["turns"]
    assert "maxItems" not in definitions["Conversation"]["properties"]["turns"]


@pytest.mark.parametrize(
    "limits",
    [
        ContentLimits(max_lessons=0),
        ContentLimits(max_options_per_exercise=1),
    ],
)
def test_content_graph_schema_rejects_limits_incompatible_with_semantic_minima(limits):
    specification = SPECIFICATION.model_copy(update={"content_limits": limits})

    with pytest.raises(OllamaPedagogicalConstructorRuntimeError):
        _content_graph_json_schema(specification)


def test_phase_one_prompt_explicitly_requires_a1_u1_lesson_experience_v3():
    prompt = _prompt(SPECIFICATION)

    assert (
        "Each candidate_unit lesson must include LessonExperience with "
        "contract_version exactly 3.0; do not omit experience or use another "
        "version."
    ) in prompt


@pytest.mark.parametrize("field", ["exercises", "conversations"])
def test_optional_lesson_activity_is_required_only_by_explicit_minimum(field):
    graph = deepcopy(CONTENT_GRAPH_DOCUMENT)
    lesson = graph["candidate_unit"]["lessons"][0]
    lesson.pop(field)
    Draft202012Validator(_content_graph_json_schema(SPECIFICATION)).validate(graph)
    limits = ContentLimits(**{f"min_{field}_per_lesson": 1})
    explicit = SPECIFICATION.model_copy(update={"content_limits": limits})
    validator = Draft202012Validator(_content_graph_json_schema(explicit))
    for empty in (False, True):
        if empty:
            lesson[field] = []
        with pytest.raises(ValidationError):
            validator.validate(graph)


def test_phase_one_schema_requires_executable_activities_and_binary_comprehension():
    validator = Draft202012Validator(_content_graph_json_schema(SPECIFICATION))

    missing_required_stage_activity = deepcopy(CONTENT_GRAPH_DOCUMENT)
    missing_required_stage_activity["candidate_unit"]["lessons"][0][
        "experience"
    ]["stages"][1].pop("activity_ids")
    with pytest.raises(ValidationError):
        validator.validate(missing_required_stage_activity)

    invalid_comprehension = deepcopy(CONTENT_GRAPH_DOCUMENT)
    invalid_comprehension["candidate_unit"]["lessons"][0]["experience"][
        "evidence_definitions"
    ][0]["measurement_mode"] = "completion"
    with pytest.raises(ValidationError):
        validator.validate(invalid_comprehension)


def test_phase_one_prompt_requires_real_activity_references():
    prompt = _prompt(SPECIFICATION)

    assert "activity_id must name an existing exercise or conversation" in prompt
    assert "Every evidence stage must declare its activity_id" in prompt
    assert "comprehension_result must use binary measurement" in prompt


def test_rejects_graph_when_evidence_activity_is_not_declared_by_its_stage():
    graph = deepcopy(CONTENT_GRAPH_DOCUMENT)
    graph["candidate_unit"]["lessons"][0]["experience"]["stages"][1][
        "activity_ids"
    ] = ["a1-u1-l1-q1"]

    def handler(_request):
        return httpx.Response(200, json={"response": json.dumps(graph)})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="activity_id must be declared by stage",
    ):
        generate_pedagogical_candidate(SPECIFICATION, constructor=_constructor(handler))


def test_phase_one_prompt_leaves_lesson_experience_optional_without_v3_obligation():
    specification = SPECIFICATION.model_copy(
        update={"technical_constraints": []}
    )

    assert "do not omit experience or use another version" not in _prompt(
        specification
    )


def test_generates_content_graph_then_pedagogical_links():
    requests = []
    responses = iter((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT))

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"response": json.dumps(next(responses))})

    result = generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_two_phase_constructor(handler),
    )

    assert [request["format"]["title"] for request in requests] == [
        "GeneratedContentGraph",
        "GeneratedPedagogicalLinks",
    ]
    assert result.candidate.specification == SPECIFICATION
    assert result.validation_report.status == "passed"


def test_rejects_content_graph_without_activities():
    graph = dict(CONTENT_GRAPH_DOCUMENT)
    graph["candidate_unit"] = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"])
    graph["candidate_unit"]["lessons"] = [{"id": "a1-u1-l1", "title": "Empty"}]

    def handler(_request):
        return httpx.Response(200, json={"response": json.dumps(graph)})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="lacks structural activities",
    ):
        generate_pedagogical_candidate(SPECIFICATION, constructor=_constructor(handler))


def test_rejects_a1_graph_without_required_lesson_experience():
    graph = dict(CONTENT_GRAPH_DOCUMENT)
    graph["candidate_unit"] = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"])
    lesson = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"]["lessons"][0])
    lesson.pop("experience")
    graph["candidate_unit"]["lessons"] = [lesson]

    def handler(_request):
        return httpx.Response(200, json={"response": json.dumps(graph)})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="lacks required LessonExperience 3.0",
    ):
        generate_pedagogical_candidate(SPECIFICATION, constructor=_constructor(handler))


def test_rejects_links_to_nonexistent_exercises():
    links = dict(PEDAGOGICAL_LINKS_DOCUMENT)
    links["exercise_skill_links"] = [{
        "exercise_id": "a1-u1-l1-q99",
        "skill_ids": ["a1_express_immediate_need_orally"],
    }]
    responses = iter((CONTENT_GRAPH_DOCUMENT, links))

    def handler(_request):
        return httpx.Response(200, json={"response": json.dumps(next(responses))})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="must match existing exercises exactly",
    ):
        generate_pedagogical_candidate(SPECIFICATION, constructor=_constructor(handler))


def test_generates_an_isolated_candidate_and_runs_existing_validators():
    observed = []

    result = generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT), observed)
        ),
    )

    graph_request = observed[0]
    assert graph_request["model"] == "qwen3:8b"
    assert graph_request["stream"] is False
    assert graph_request["think"] is False
    assert graph_request["options"] == {"temperature": 0, "seed": 42}
    assert graph_request["format"]["title"] == "GeneratedContentGraph"
    assert "specification" not in graph_request["format"]["properties"]
    assert graph_request["format"]["additionalProperties"] is False
    assert result.candidate.specification == SPECIFICATION
    assert result.validation_report.status == "passed"
    assert result.raw_response == json.dumps({
        "content_graph": CONTENT_GRAPH_DOCUMENT,
        "pedagogical_links": PEDAGOGICAL_LINKS_DOCUMENT,
    }, ensure_ascii=False)


def test_instructs_the_model_to_keep_comprehension_and_oral_evidence_distinct():
    observed = []

    generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT), observed)
        ),
    )

    prompt = observed[0]["prompt"]
    assert (
        "comprehension_result is only for a comprehension exercise and requires "
        "comprehension_exercise_id"
    ) in prompt
    assert (
        "guided_production is for own oral production and requires "
        "production_prompt_id"
    ) in prompt
    assert (
        "contextual_response is for oral transfer and requires "
        "production_prompt_id"
    ) in prompt


def test_instructs_the_model_to_copy_the_approved_unit_id_to_candidate_unit():
    observed = []

    generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT), observed)
        ),
    )

    assert (
        "candidate_unit.id must be exactly a1-u1; do not create, replace, or "
        "infer a unit ID"
    ) in observed[0]["prompt"]


def test_binds_candidate_unit_id_to_the_approved_specification_in_ollama_schema():
    observed = []

    generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT), observed)
        ),
    )

    assert observed[0]["format"]["$defs"]["Unit"]["properties"]["id"] == {
        "const": "a1-u1"
    }


def test_requires_structurally_complete_coverage_and_valid_mcq_shapes():
    observed = []

    generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, PEDAGOGICAL_LINKS_DOCUMENT), observed)
        ),
    )

    coverage = observed[1]["format"]["$defs"]["SkillCoverage"]
    assert set(coverage["required"]) >= {
        "skill_id",
        "introduced_in_lesson_id",
        "practice_activity_ids",
        "application_activity_ids",
        "evaluation_evidence_ids",
        "consolidation_activity_ids",
        "modalities",
        "status",
    }
    assert coverage["properties"]["status"] == {"const": "complete"}

    exercise = observed[0]["format"]["$defs"]["ExerciseMCQ"]
    assert exercise["properties"]["id"] == {
        "pattern": "^.+-q[1-9][0-9]*$"
    }
    assert exercise["properties"]["options"]["minItems"] == 2
    assert exercise["properties"]["answer_index"]["minimum"] == 0

    prompt = observed[0]["prompt"]
    assert "Do not represent oral production or transfer as ExerciseMCQ" in prompt
    assert "references to existing candidate artifacts" in prompt


def test_rejects_a_model_candidate_with_a_replaced_unit_id_without_repair():
    changed = dict(CONTENT_GRAPH_DOCUMENT)
    changed["candidate_unit"] = dict(CONTENT_GRAPH_DOCUMENT["candidate_unit"])
    changed["candidate_unit"]["id"] = "a1-u2"

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="candidate unit ID must match specification unit_id",
    ):
        generate_pedagogical_candidate(
            SPECIFICATION,
            constructor=_constructor(
                _two_phase_handler((changed, PEDAGOGICAL_LINKS_DOCUMENT))
            ),
        )


def test_rejects_a_model_response_that_includes_specification():
    changed = dict(CONTENT_GRAPH_DOCUMENT)
    changed["specification"] = CANDIDATE_DOCUMENT["specification"]

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="must not include specification",
    ):
        generate_pedagogical_candidate(
            SPECIFICATION,
            constructor=_constructor(_two_phase_handler((changed,))),
        )


def test_rejects_unauthorized_top_level_model_fields():
    changed = dict(CONTENT_GRAPH_DOCUMENT)
    changed["unapproved_field"] = "must not reach the candidate"

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="unauthorized fields: unapproved_field",
    ):
        generate_pedagogical_candidate(
            SPECIFICATION,
            constructor=_constructor(_two_phase_handler((changed,))),
        )


def test_rejects_invalid_model_json_explicitly():
    def handler(_request):
        return httpx.Response(200, json={"response": '{"candidate_unit": {}}'})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="content graph failed Pydantic validation",
    ):
        generate_pedagogical_candidate(
            SPECIFICATION,
            constructor=_constructor(handler),
        )


def test_surfaces_ollama_failures_explicitly():
    def handler(_request):
        return httpx.Response(503, json={"error": "model unavailable"})

    with pytest.raises(
        OllamaPedagogicalConstructorRuntimeError,
        match="503",
    ):
        generate_pedagogical_candidate(
            SPECIFICATION,
            constructor=_constructor(handler),
        )


def test_preserves_a_pydantic_valid_candidate_when_existing_validation_fails():
    invalid_links = dict(PEDAGOGICAL_LINKS_DOCUMENT)
    invalid_links["skill_coverage"] = [
        dict(PEDAGOGICAL_LINKS_DOCUMENT["skill_coverage"][0])
    ]
    invalid_links["skill_coverage"][0]["practice_activity_ids"] = []

    result = generate_pedagogical_candidate(
        SPECIFICATION,
        constructor=_constructor(
            _two_phase_handler((CONTENT_GRAPH_DOCUMENT, invalid_links))
        ),
    )

    assert result.candidate.specification == SPECIFICATION
    assert result.validation_report.status == "failed"
    assert result.validation_report.findings[0].validator_id == "skill_stage_coverage"
