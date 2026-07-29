# Phonetic calibration corpus

## Purpose
Build reproducible human acoustic evidence before any pedagogical pronunciation threshold is defined.

## Corpus rules
- Use pseudonymous `speaker_id`; do not store personal identity in the manifest.
- Identify recording sessions with `session_id`.
- Keep every `sample_id` unique.
- Preserve the exact reference text and SHA-256 of each WAV.
- Keep real human audio, local manifests, runtime configuration and local measurements outside Git.
- Treat `expected_class: unlabeled` as the default until an independent human labeling process exists.
- Measure coverage by sample count, unique speakers and unique `(speaker_id, session_id)` pairs.

## Limits
Coverage counts do not prove representativeness or pedagogical validity.
No score is a pronunciation percentage and no pedagogical threshold may be inferred from this corpus without later calibration and independent labeling.
