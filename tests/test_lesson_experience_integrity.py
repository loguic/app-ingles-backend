import pytest
from pydantic import ValidationError

from app.schemas.content import Lesson
from tests.test_lesson_experience_schema import build_experience_payload


def assert_invalid(payload: dict, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Lesson.model_validate({
            'id': 'a1-u1-l1',
            'title': 'Invalid lesson experience',
            'experience': payload,
        })


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        ('skill', 'LessonExperience skill_ids must be unique'),
        ('stage', 'LessonExperience stage IDs must be unique'),
        ('support', 'Language support IDs must be unique'),
        ('evidence', 'Evidence definition IDs must be unique'),
    ],
)
def test_rejects_duplicate_root_identifiers(case, message):
    payload = build_experience_payload()

    if case == 'skill':
        payload['skill_ids'].append(payload['skill_ids'][0])
    elif case == 'stage':
        payload['stages'].append(dict(payload['stages'][0]))
    elif case == 'support':
        payload['language_support'].append(
            dict(payload['language_support'][0])
        )
    else:
        payload['evidence_definitions'].append(
            dict(payload['evidence_definitions'][0])
        )

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        (
            'duplicate',
            'Language support a1-u1-l1-ls1 stage_ids must be unique',
        ),
        (
            'unknown',
            'Language support a1-u1-l1-ls1 references unknown stages',
        ),
    ],
)
def test_rejects_invalid_language_support_stage_ids(case, message):
    payload = build_experience_payload()
    stage_ids = payload['language_support'][0]['stage_ids']

    if case == 'duplicate':
        stage_ids.append(stage_ids[0])
    else:
        stage_ids[0] = 'a1-u1-l1-s999'

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        (
            'duplicate',
            'Evidence a1-u1-l1-ev1 skill_ids must be unique',
        ),
        (
            'unknown',
            'Evidence a1-u1-l1-ev1 references unknown Skills',
        ),
    ],
)
def test_rejects_invalid_evidence_skill_ids(case, message):
    payload = build_experience_payload()
    skill_ids = payload['evidence_definitions'][0]['skill_ids']

    if case == 'duplicate':
        skill_ids.append(skill_ids[0])
    else:
        skill_ids[0] = 'a1_unknown_skill'

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        ('stage', 'references unknown stage'),
        ('activity', 'activity_id must be declared by stage'),
    ],
)
def test_rejects_invalid_evidence_stage_or_activity(case, message):
    payload = build_experience_payload()
    evidence = payload['evidence_definitions'][0]

    if case == 'stage':
        evidence['stage_id'] = 'a1-u1-l1-s999'
    else:
        evidence['activity_id'] = 'a1-u1-l1-q999'

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        (
            'duplicate',
            'Completion policy practiced_stage_ids must be unique',
        ),
        (
            'unknown',
            'references unknown practiced stages',
        ),
    ],
)
def test_rejects_invalid_practiced_stage_ids(case, message):
    payload = build_experience_payload()
    stage_ids = payload['completion_policy']['practiced_stage_ids']

    if case == 'duplicate':
        stage_ids.append(stage_ids[0])
    else:
        stage_ids[0] = 'a1-u1-l1-s999'

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    ('case', 'message'),
    [
        (
            'duplicate',
            'Completion policy required_evidence_ids must be unique',
        ),
        (
            'unknown',
            'references unknown required evidence',
        ),
    ],
)
def test_rejects_invalid_required_evidence_ids(case, message):
    payload = build_experience_payload()
    evidence_ids = payload['completion_policy'][
        'required_evidence_ids'
    ]

    if case == 'duplicate':
        evidence_ids.append(evidence_ids[0])
    else:
        evidence_ids[0] = 'a1-u1-l1-ev999'

    assert_invalid(payload, message)


@pytest.mark.parametrize('case', ['missing', 'unexpected'])
def test_requires_exact_required_evidence_set(case):
    payload = build_experience_payload()
    extra = dict(payload['evidence_definitions'][0])
    extra['id'] = 'a1-u1-l1-ev2'

    if case == 'missing':
        extra['required'] = True
    else:
        extra['required'] = False
        payload['completion_policy'][
            'required_evidence_ids'
        ].append(extra['id'])

    payload['evidence_definitions'].append(extra)

    assert_invalid(
        payload,
        'required_evidence_ids must match required evidence',
    )


@pytest.mark.parametrize(
    'condition',
    [
        'any_activity_completed',
        'all_activities_completed',
        'evidence_recorded',
    ],
)
def test_activity_completion_conditions_require_activity(condition):
    payload = build_experience_payload()
    stage = payload['stages'][0]
    stage['activity_ids'] = []
    stage['completion_condition'] = condition

    assert_invalid(payload, 'requires at least one activity')
