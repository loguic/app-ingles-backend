"""Generate one isolated pedagogical candidate through the local Ollama runtime."""

import json
import os
from dataclasses import dataclass

import httpx

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    PedagogicalUnitSpecification,
    ValidationReport,
)
from app.schemas.content import Unit
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)


_GENERATED_CONTENT_FIELDS = frozenset(
    PedagogicalUnitCandidate.model_fields
) - {"specification"}
_LESSON_EXPERIENCE_V3_TECHNICAL_CONSTRAINT = (
    "Use LessonExperience contract_version 3.0 in the future candidate."
)


class OllamaPedagogicalConstructorRuntimeError(RuntimeError):
    """The configured Ollama runtime did not return a usable candidate."""


@dataclass(frozen=True)
class OllamaPedagogicalConstructorConfig:
    base_url: str
    model: str
    timeout_seconds: float

    @classmethod
    def from_environment(cls) -> "OllamaPedagogicalConstructorConfig":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
        model = os.getenv("OLLAMA_CONSTRUCTOR_MODEL", "qwen3:8b").strip()
        try:
            timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
        except ValueError as error:
            raise OllamaPedagogicalConstructorRuntimeError(
                "OLLAMA_TIMEOUT_SECONDS must be a positive number"
            ) from error
        if not base_url or not model or timeout_seconds <= 0:
            raise OllamaPedagogicalConstructorRuntimeError(
                "Ollama base URL, constructor model, and timeout must be configured"
            )
        return cls(
            base_url=base_url.rstrip("/"),
            model=model,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class GeneratedPedagogicalCandidate:
    """Keep one generated candidate and its deterministic validation isolated."""

    candidate: PedagogicalUnitCandidate
    validation_report: ValidationReport
    raw_response: str


def _requires_lesson_experience_v3(
    specification: PedagogicalUnitSpecification,
) -> bool:
    """Recognize only the approved, explicit LessonExperience 3.0 requirement."""
    return (
        _LESSON_EXPERIENCE_V3_TECHNICAL_CONSTRAINT
        in specification.technical_constraints
    )


def _project_content_limits(
    schema: dict[str, object],
    specification: PedagogicalUnitSpecification,
) -> None:
    """Project declarative cardinality limits onto the phase-one schema."""
    limits = specification.content_limits
    projections = (
        ("Unit", "lessons", "min_lessons", "max_lessons", 1),
        (
            "Lesson",
            "examples",
            "min_examples_per_lesson",
            "max_examples_per_lesson",
            0,
        ),
        (
            "Lesson",
            "conversations",
            "min_conversations_per_lesson",
            "max_conversations_per_lesson",
            0,
        ),
        (
            "Lesson",
            "exercises",
            "min_exercises_per_lesson",
            "max_exercises_per_lesson",
            0,
        ),
        (
            "ExerciseMCQ",
            "options",
            "min_options_per_exercise",
            "max_options_per_exercise",
            2,
        ),
        (
            "Conversation",
            "turns",
            "min_turns_per_conversation",
            "max_turns_per_conversation",
            0,
        ),
    )
    definitions = schema["$defs"]

    for definition_name, property_name, minimum_name, maximum_name, semantic_minimum in projections:
        property_schema = definitions[definition_name]["properties"][property_name]
        minimum = getattr(limits, minimum_name)
        maximum = getattr(limits, maximum_name)
        effective_minimum = max(
            semantic_minimum,
            property_schema.get("minItems", 0),
            minimum if minimum is not None else 0,
        )
        if maximum is not None and maximum < effective_minimum:
            raise OllamaPedagogicalConstructorRuntimeError(
                f"{maximum_name}={maximum} conflicts with the required minimum "
                f"of {effective_minimum} for {property_name}"
            )
        if minimum is not None:
            property_schema["minItems"] = effective_minimum
            definition = definitions[definition_name]
            if minimum > 0 and property_name not in definition.get("required", []):
                definition.setdefault("required", []).append(property_name)
        if maximum is not None:
            property_schema["maxItems"] = maximum


def _prompt(specification: PedagogicalUnitSpecification) -> str:
    experience_instruction = ""
    if _requires_lesson_experience_v3(specification):
        experience_instruction = (
            "Each candidate_unit lesson must include LessonExperience with "
            "contract_version exactly 3.0; do not omit experience or use another "
            "version. "
        )
    return (
        "You are the LOGUIC English Pedagogical Constructor. Generate one new "
        "isolated content payload for the approved specification below. Do not "
        "return specification: the Constructor owns and inserts that immutable "
        "approved input before Pydantic validation. Use only the "
        "existing backend contracts, and remain unpublished: do not activate, "
        "publish, or modify curricular content. Supply every required field and "
        "return only JSON matching the supplied schema. The candidate will be "
        "rejected unless deterministic validators pass. Evidence definitions "
        "must reference activities that you create: activity_id must name an "
        "existing exercise or conversation declared by its stage, never a "
        "mission ID. Every evidence stage must declare its activity_id in "
        "stage.activity_ids. Preserve the distinct purposes of evidence: comprehension_result is only "
        "for a comprehension exercise and requires comprehension_exercise_id; "
        "comprehension_result must use binary measurement; "
        "guided_production is for own oral production and requires "
        "production_prompt_id; contextual_response is for oral transfer and "
        "requires production_prompt_id. Do not label oral evidence as "
        "comprehension_result. candidate_unit.id must be exactly "
        + specification.unit_id
        + "; do not create, replace, or infer a unit ID. Every SkillCoverage "
        "must declare introduce, practice, apply, evaluate, and consolidate "
        "with references to existing candidate artifacts; status complete "
        "means structural coverage only, never learner accreditation. Do not "
        "represent oral production or transfer as ExerciseMCQ. Model them as "
        "conversations with production_prompt and their matching evidence. "
        "Use ExerciseMCQ only for a genuine selection task: its ID ends in "
        "-q plus a positive integer, it has at least two meaningful options, "
        "and answer_index selects one of them.\n\n"
        + experience_instruction
        + "APPROVED SPECIFICATION:\n"
        + json.dumps(specification.model_dump(mode="json"), ensure_ascii=False)
    )


def _candidate_json_schema(
    specification: PedagogicalUnitSpecification,
) -> dict[str, object]:
    """Bind the generated unit identity to the approved specification."""
    schema = PedagogicalUnitCandidate.model_json_schema()
    schema["$defs"]["Unit"]["properties"]["id"] = {
        "const": specification.unit_id
    }
    coverage = schema["$defs"]["SkillCoverage"]
    coverage["required"] = [
        "skill_id",
        "introduced_in_lesson_id",
        "practice_activity_ids",
        "application_activity_ids",
        "evaluation_evidence_ids",
        "consolidation_activity_ids",
        "modalities",
        "status",
    ]
    coverage["properties"]["status"] = {"const": "complete"}
    exercise = schema["$defs"]["ExerciseMCQ"]
    exercise["properties"]["id"] = {"pattern": r"^.+-q[1-9][0-9]*$"}
    exercise["properties"]["options"]["minItems"] = 2
    exercise["properties"]["answer_index"]["minimum"] = 0
    lesson = schema["$defs"]["Lesson"]
    evidence = schema["$defs"]["EvidenceDefinition"]
    evidence["allOf"] = [
        *evidence.get("allOf", []),
        {
            "if": {
                "properties": {"evidence_type": {"const": "comprehension_result"}},
                "required": ["evidence_type"],
            },
            "then": {
                "required": ["comprehension_exercise_id"],
                "properties": {"measurement_mode": {"const": "binary"}},
            },
        },
    ]
    stage = schema["$defs"]["LessonStage"]
    stage["allOf"] = [
        *stage.get("allOf", []),
        {
            "if": {
                "properties": {
                    "completion_condition": {
                        "enum": [
                            "any_activity_completed",
                            "all_activities_completed",
                            "evidence_recorded",
                        ]
                    }
                },
                "required": ["completion_condition"],
            },
            "then": {
                "required": ["activity_ids"],
                "properties": {"activity_ids": {"minItems": 1}},
            },
        },
    ]
    external_review_requirement = schema["$defs"]["ExternalReviewRequirement"]
    external_review_requirement["allOf"] = [
        {
            "if": {
                "properties": {
                    "dimension": {"enum": ["relevance", "intelligibility"]}
                },
                "required": ["dimension"],
            },
            "then": {
                "required": ["production_function"],
                "properties": {
                    "production_function": {
                        "enum": ["guided", "expanded", "transfer"]
                    }
                },
            },
        }
    ]
    if _requires_lesson_experience_v3(specification):
        lesson["required"] = [*lesson["required"], "experience"]
        schema["$defs"]["LessonExperience"]["properties"][
            "contract_version"
        ] = {"const": "3.0"}
    _project_content_limits(schema, specification)
    return schema


def _generated_content_json_schema(
    specification: PedagogicalUnitSpecification,
) -> dict[str, object]:
    """Expose only the LLM-owned candidate content fields to Ollama."""
    schema = _candidate_json_schema(specification)
    schema["title"] = "GeneratedPedagogicalUnitContent"
    schema["properties"].pop("specification")
    schema["required"] = [
        field
        for field in schema["required"]
        if field != "specification"
    ]
    schema["additionalProperties"] = False
    return schema


def _content_graph_json_schema(
    specification: PedagogicalUnitSpecification,
) -> dict[str, object]:
    schema = _generated_content_json_schema(specification)
    schema["title"] = "GeneratedContentGraph"
    schema["properties"].pop("skill_coverage")
    schema["properties"].pop("validation_report")
    schema["required"] = [
        field for field in schema["required"]
        if field not in {"skill_coverage", "validation_report"}
    ]
    return schema


def _pedagogical_links_json_schema(
    specification: PedagogicalUnitSpecification,
) -> dict[str, object]:
    schema = _generated_content_json_schema(specification)
    schema["title"] = "GeneratedPedagogicalLinks"
    schema["properties"] = {
        "skill_coverage": schema["properties"]["skill_coverage"],
        "exercise_skill_links": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["exercise_id", "skill_ids"],
                "properties": {
                    "exercise_id": {"type": "string"},
                    "skill_ids": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"},
                    },
                },
            },
        },
    }
    schema["required"] = ["skill_coverage", "exercise_skill_links"]
    return schema


class OllamaPedagogicalConstructor:
    """Call Ollama once to obtain a schema-constrained candidate."""

    def __init__(
        self,
        config: OllamaPedagogicalConstructorConfig | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._config = config or OllamaPedagogicalConstructorConfig.from_environment()
        self._client = client

    @property
    def config(self) -> OllamaPedagogicalConstructorConfig:
        return self._config

    def generate(self, prompt: str, response_schema: dict[str, object]) -> str:
        payload = {
            "model": self._config.model,
            "prompt": prompt,
            "format": response_schema,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42},
        }
        try:
            if self._client is not None:
                response = self._client.post("/api/generate", json=payload)
            else:
                with httpx.Client(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout_seconds,
                ) as client:
                    response = client.post("/api/generate", json=payload)
            response.raise_for_status()
            generated = response.json()["response"]
            if not isinstance(generated, str):
                raise TypeError("Ollama response field must be a JSON string")
            return generated
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise OllamaPedagogicalConstructorRuntimeError(
                "Ollama pedagogical constructor generation failed: " + str(error)
            ) from error


def generate_pedagogical_candidate(
    specification: PedagogicalUnitSpecification,
    *,
    constructor: OllamaPedagogicalConstructor | None = None,
) -> GeneratedPedagogicalCandidate:
    """Generate, parse, and deterministically validate one isolated candidate."""
    runtime = constructor or OllamaPedagogicalConstructor()
    graph_response = runtime.generate(
        _prompt(specification), _content_graph_json_schema(specification)
    )
    try:
        graph = json.loads(graph_response)
    except (TypeError, ValueError) as error:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Ollama pedagogical constructor generation failed JSON validation: "
            + str(error)
        ) from error

    if not isinstance(graph, dict):
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content must be a JSON object"
        )
    if "specification" in graph:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content must not include specification"
        )

    graph_fields = _GENERATED_CONTENT_FIELDS - {"skill_coverage", "validation_report"}
    unexpected_fields = sorted(
        set(graph) - graph_fields
    )
    if unexpected_fields:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content contains unauthorized fields: "
            + ", ".join(unexpected_fields)
        )

    try:
        Unit.model_validate(graph["candidate_unit"])
    except (KeyError, ValueError) as error:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content graph failed Pydantic validation: "
            + str(error)
        ) from error

    lessons = graph["candidate_unit"].get("lessons", [])
    if not lessons or not any(
        lesson.get("examples") or lesson.get("conversations") or lesson.get("exercises")
        for lesson in lessons
    ):
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content graph lacks structural activities"
        )

    required_stages = {
        stage for skill in specification.skills for stage in skill.required_stages
    }
    requires_experience = _requires_lesson_experience_v3(specification)
    if requires_experience and any(
        lesson.get("experience", {}).get("contract_version") != "3.0"
        for lesson in lessons
    ):
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content graph lacks required LessonExperience 3.0"
        )
    if "apply" in required_stages and not any(
        lesson.get("conversations") for lesson in lessons
    ):
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated content graph lacks conversations required for application"
        )
    lessons_with_evaluation = {
        plan.get("lesson_id") for plan in graph.get("evaluation_plans", [])
    }
    if any(
        lesson["id"] in lessons_with_evaluation and not lesson.get("experience")
        for lesson in lessons
    ):
        raise OllamaPedagogicalConstructorRuntimeError(
            "Production evaluation requires LessonExperience"
        )

    link_prompt = (
        "Declare only pedagogical links for this approved specification and "
        "existing content graph. Do not create content, IDs, or specification. "
        "Use only IDs present in the graph. practice may reference an example, "
        "conversation, or exercise; application only a conversation; evaluation "
        "only an exercise or evidence definition; consolidation only a lesson or "
        "activity. Do not declare complete coverage without every required stage. "
        "Return every SkillCoverage and one skill_ids link for every existing "
        "exercise.\n\nAPPROVED SPECIFICATION:\n"
        + json.dumps(specification.model_dump(mode="json"), ensure_ascii=False)
        + "\n\nCONTENT GRAPH:\n"
        + json.dumps(graph, ensure_ascii=False)
    )
    links_response = runtime.generate(
        link_prompt, _pedagogical_links_json_schema(specification)
    )
    try:
        links = json.loads(links_response)
    except (TypeError, ValueError) as error:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated pedagogical links failed JSON validation: " + str(error)
        ) from error
    if not isinstance(links, dict) or set(links) != {
        "skill_coverage", "exercise_skill_links"
    }:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Generated pedagogical links contain unauthorized fields"
        )

    exercise_ids = {
        exercise["id"] for lesson in lessons for exercise in lesson.get("exercises", [])
    }
    declared_links = links["exercise_skill_links"]
    linked_ids = [item["exercise_id"] for item in declared_links]
    if len(linked_ids) != len(set(linked_ids)) or set(linked_ids) != exercise_ids:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Exercise skill links must match existing exercises exactly"
        )
    skill_ids_by_exercise = {
        item["exercise_id"]: item["skill_ids"] for item in declared_links
    }
    for lesson in lessons:
        for exercise in lesson.get("exercises", []):
            exercise["skill_ids"] = skill_ids_by_exercise[exercise["id"]]

    try:
        candidate = PedagogicalUnitCandidate.model_validate({
            "specification": specification.model_dump(mode="json"),
            **graph,
            "skill_coverage": links["skill_coverage"],
            "validation_report": {"status": "pending", "findings": []},
        })
    except ValueError as error:
        raise OllamaPedagogicalConstructorRuntimeError(
            "Two-phase candidate failed Pydantic validation: " + str(error)
        ) from error

    validation_report = validate_pedagogical_candidate(candidate)
    candidate = candidate.model_copy(
        update={"validation_report": validation_report}
    )
    return GeneratedPedagogicalCandidate(
        candidate=candidate,
        validation_report=validation_report,
        raw_response=json.dumps(
            {"content_graph": graph, "pedagogical_links": links},
            ensure_ascii=False,
        ),
    )
