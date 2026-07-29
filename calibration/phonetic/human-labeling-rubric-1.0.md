# Phonetic Human Labeling Rubric 1.0

Rubric ID: `phonetic-rubric/1.0`

## Purpose
Provide a shared qualitative vocabulary for independent human review of controlled pronunciation samples.

## Labels
- `acceptable`: the evaluator judges the intended reference production understandable and without a pronunciation issue that materially changes the intended form.
- `variant`: the evaluator hears a noticeable pronunciation variation but does not classify it as a confirmed pronunciation error under this rubric.
- `known_error`: the evaluator identifies a concrete pronunciation mismatch against the reference production.

## Rules
- Evaluate the audio independently from the acoustic model score.
- Do not use model scores or thresholds when choosing a human label.
- Record only the pseudonymous `labeler_id`.
- Multiple evaluators may disagree; disagreement must be preserved rather than overwritten.
- This rubric does not establish mastery, retention, learner feedback or automated pedagogical thresholds.
