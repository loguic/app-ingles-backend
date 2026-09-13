# LOGUIC TTS Engine Benchmark Protocol v1

Estado: **IMPLEMENTED / PENDING POSTFLIGHT**. Este contrato define el benchmark aislado; no instala motores, no genera audio, no ejecuta el benchmark ni integra artefactos en producto.

## Identidad y límites

`protocol_version` es exactamente `loguic-tts-engine-benchmark/1.0`. El corpus procede exclusivamente de Candidate v4, `candidate_revision=a1-u1-candidate-v4`, con identidad lógica `sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d`. Su perfil único de normalización es `loguic-tts-wav-normalization/1.0`: RIFF/WAVE, PCM `pcm_s16le`, mono, 24 000 Hz, 16-bit y sin dither.

El benchmark no determina aprobación/rechazo automáticamente. Las validaciones WAV, hashes y probes son evidencia técnica; ASR, forced alignment, WavLM/GOP y duración/prosodia, si se añaden, son exclusivamente descriptivos. No hay umbral de aceptación automático, score decisorio, selección automática ni promedio único.

## Corpus derivado y matriz congelada

Se deriva, no se escribe a mano: abrir `content/candidates/a1-u1/pedagogical-unit-candidate-v4.json`, tomar `required_resource_ids` en su orden declarado y filtrar los doce IDs con prefijo `audio.`. Para cada ID, resolver texto, IPA y locale desde las entradas `pronunciations` del Candidate v4: `candidate_unit.lessons[*].experience.language_support[*].en` y, para `okay`, `candidate_unit.lessons[*].conversations[*].turns[*].en`. Las referencias repetidas deben coincidir; cualquier inconsistencia, ausencia, ID adicional o cambio de Candidate v4 invalida el slice y exige derivación y cegado nuevos.

Los doce IDs derivados, en el orden congelado, son:

```
audio.a1-u1-l1.i-need-water.en-us.v1
audio.a1-u1-l1.i-need-water.en-gb.v1
audio.a1-u1-l1.i-need-help.en-gb.v1
audio.a1-u1-l1.i-need-food.en-gb.v1
audio.a1-u1-l1.water.en-us.v1
audio.a1-u1-l1.water.en-gb.v1
audio.a1-u1-l1.help.en-us.v1
audio.a1-u1-l1.help.en-gb.v1
audio.a1-u1-l1.food.en-us.v1
audio.a1-u1-l1.food.en-gb.v1
audio.a1-u1-l1.okay.en-us.v1
audio.a1-u1-l1.okay.en-gb.v1
```

Candidate v4 fija así 7 targets en-GB y 5 en-US. Los textos, IPA y locales siguen derivándose en cada validación desde el Candidate; no existen copias manuales de esos valores en este contrato.

Los engines, versiones y voces aprobados son:

- Kokoro `0.9.4`: en-US `af_heart`, `af_bella`; en-GB `bf_emma`, `bf_isabella`.
- Piper `1.8.0`: en-GB `en_GB-cori-medium`, `en_GB-alba-medium`; en-US `en_US-kristin-medium`, `en_US-joe-medium`.

Cada target se sintetiza con las dos voces de su locale en cada engine: `(7 × 2) + (5 × 2) = 24` muestras base por engine, `48` en total. Engine, versión, modelo/voz, parámetros, entorno, Candidate v4, corpus y perfil WAV se congelan antes de escuchar resultados. No hay postprocesado especial por engine ni cambios de criterio posteriores; un cambio material regenera el slice afectado y lo vuelve a cegar. No se mezclan engines target por target como producto final sin una autorización futura.

## Replicación adaptativa

Para cada voz/configuración, antes del corpus real, se genera el mismo target tres veces con idénticos engine, versión, modelo/voz, parámetros, entorno e input.

- Las tres RAW byte-idénticas: `deterministic_for_benchmark`; una generación por target.
- Cualquier diferencia RAW: `replicated_for_benchmark`; tres replicaciones independientes por target.

No se elige la mejor réplica, no se descarta una por preferencia subjetiva y no se retunea tras escucharla. Toda réplica requerida pasa a review ciego. El resultado es 48 muestras normalizadas en caso determinista total y hasta 144 si las ocho voces requieren tres replicaciones.

El `DeterminismProbe` conserva el `GenerationCase` exacto de su medición; esa identidad incluye el target concreto empleado para medir determinismo. La aplicabilidad de su clasificación a otro `GenerationCase` no exige igualdad de esos targets: exige igualdad del scope generativo completo formado por `protocol_identity`, `engine`, `engine_version`, `model_pin`, `voice_id`, `target_locale`, `generation_parameters` y `runtime_environment_pin`. `generation_case_id`, `resource_id`, `reference_text` e `ipa` no forman parte de ese scope. Por tanto, *probe measurement identity* y *probe applicability scope* son distintos: se conserva el caso medido y se permite reutilizar su clasificación únicamente para otros targets canónicos con la misma configuración autorizada. En cambio, un `SampleManifest` agrupa réplicas de un único *replication-group target identity*: no puede mezclar targets y, para `replicated_for_benchmark`, las muestras con índices `{1,2,3}` comparten el `GenerationCase` target-specific completo. Esta es una corrección PATCH que alinea el contrato v1 existente; `protocol_version` permanece `loguic-tts-engine-benchmark/1.0`.

## Cegado, review y adjudicación

Cada `SampleIdentity` conserva hashes SHA-256 RAW y normalizado. La secuencia
causal de cada réplica es `GenerationCase` + `replication_index` →
`run_execution_id` → RAW → normalization record → normalized SHA-256 → final
`SampleIdentity` → `SampleManifest`. El `sample_id` del normalization record
es el `run_execution_id` preexistente, no un `SampleIdentity.sample_id`
provisional. El runner solo crea el `SampleIdentity` final después de validar
el record y el WAV normalizado; exige el mapping unívoco
`run_execution_id -> normalization record -> final sample_id`, con igualdad
de hashes RAW/normalizado y profile version. WAV normalizado y record comparten
el mismo directorio padre y ninguno se modifica después de publicarse.

El mapping privado `blind_review_id -> sample_id` usa IDs opacos `br_` más 32 hexadecimales, tiene orden específico por reviewer y no se entrega al reviewer. Los reviewers no ven engine, modelo ni voz. El mapping no se revela hasta bloquear ambos reviews originales.

Reviewer A y reviewer B trabajan de forma independiente. Primero escuchan sin transcript y registran transcripción percibida e `intelligibility`; solo después se revela `reference_text`, IPA y `target_locale`, y se evalúan las demás dimensiones. La rúbrica exacta es `intelligibility`, `pronunciation_correctness`, `locale_accent_conformance`, `naturalness`, `prosody_rhythm` y `a1_pedagogical_suitability`. La escala exacta es `meets`, `minor_issue`, `major_issue` y `not_assessable`.

Se conservan ambos labels originales. Solo un desacuerdo relevante recibe un `AdjudicationRecord` separado, que referencia los dos reviews y cubre únicamente sus dimensiones relevantes; nunca sustituye los originales. La comparación informa por target, locale, voz/configuración, dimensión, acuerdos/desacuerdos y adjudicaciones, y debe permitir `NO WINNER`.

## Licencias y salida permitida

Antes de ejecutar, registrar separadamente licencia de engine/runtime, modelo y voz/dataset. Piper está autorizado únicamente para este benchmark aislado; una integración o distribución de producto requiere revisión independiente.

Los contratos mínimos viven en `app/schemas/tts_engine_benchmark.py`. No definen DB, loader, frontend, ASR/alignment, WavLM/GOP decisorio, B51/B52 ni B181.
