# LOGUIC TTS Engine Benchmark Protocol v1

Estado: benchmark **TÉCNICAMENTE FINALIZADO**; tercer intento de `TTS Public Reviewer Package / Workflow v1` **IMPLEMENTED LOCALLY / VALIDATED / POSTFLIGHT PASS / READY_FOR_CLOSURE**, tras dos postflights históricos **FAIL** y preflight Astra posterior **PASS**; human reviews **NOT STARTED** y consumidor B **CONTRACT APPROVED / NOT IMPLEMENTED**. Este contrato define el benchmark aislado, su frontera pública de review y el contrato aprobado de aceptación durable; no instala motores, no genera audio, no ejecuta reviews ni integra artefactos en producto.

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

El mapping privado `blind_review_id -> sample_id` usa IDs opacos `br_` más 32 hexadecimales, tiene orden específico por reviewer y no se entrega al reviewer. `blind_review_id` es una identidad de entrega cegada específica de reviewer: para una misma muestra, reviewer A y reviewer B reciben IDs distintos. Por tanto, con 144 muestras hay 288 IDs globalmente únicos, 144 por reviewer. Durante la review, cada `HumanReviewRecord` conserva únicamente su propio `blind_review_id`; los reviewers no ven engine, modelo, voz, `sample_id` ni el mapping privado.

Reviewer A y reviewer B trabajan de forma independiente. Primero escuchan sin transcript y registran transcripción percibida e `intelligibility`; solo después se revela `reference_text`, IPA y `target_locale`, y se evalúan las demás dimensiones. La rúbrica exacta es `intelligibility`, `pronunciation_correctness`, `locale_accent_conformance`, `naturalness`, `prosody_rhythm` y `a1_pedagogical_suitability`. La escala exacta es `meets`, `minor_issue`, `major_issue` y `not_assessable`.

`HumanReviewRecord` representa exclusivamente una review completa, final y bloqueada; los drafts no tienen su autoridad. Su `locked_at` es obligatorio, timezone-aware y se canonicaliza a UTC antes de formar parte del `review_id` causal. El lock es por review: A y B pueden bloquear en cualquier orden y una pareja puede reconciliarse y adjudicarse cuando sus dos reviews estén bloqueadas, sin esperar las 288 reviews. La secuencia es entrega cegada → primera escucha → transcripción percibida/intelligibility → disclosure permitido → rúbrica restante → review completa → lock → ambos locks de la pareja → frontera privada. Solo entonces la frontera privada resuelve cada `blind_review_id -> sample_id`. Solo puede emparejarse para adjudicación un review A y un review B cuyos mappings resuelvan al mismo `sample_id`. `AdjudicationRecord` separado referencia ambos reviews y cubre únicamente sus dimensiones relevantes; no depende de un `blind_review_id` compartido ni persiste el `sample_id` resuelto, y nunca sustituye los originales. La comparación informa por target, locale, voz/configuración, dimensión, acuerdos/desacuerdos y adjudicaciones, y debe permitir `NO WINNER`.

## TTS Public Reviewer Package / Workflow v1

`package_version` es exactamente `loguic-tts-public-reviewer-package/1.0`. Un `PrivateReviewerPackageBinding` compromete de forma determinista el conjunto completo y ordenado de entregas de un reviewer: versión, reviewer, `blind_review_id`, `sample_id`, SHA-256 del audio normalizado y posición. La frontera privada aplica HMAC-SHA-256 con una clave de al menos 32 bytes y solo ese commitment opaco cruza a `PublicReviewerPackage` como `delivery_set_commitment`; la clave, los valores privados y el binding completo no se entregan al reviewer ni forman parte del handoff. `package_id` compromete ese ID y los items, y cada `audio_delivery_id` depende causalmente del commitment, ID ciego y posición. Cambiar mapping, audio, reviewer, orden, versión o clave cambia una identidad causal o falla cerrado.

La frontera pública contiene únicamente versión de paquete/protocolo, commitment opaco, asignación `reviewer_a|reviewer_b`, IDs ciegos, orden y handles opacos de entrega de audio. No contiene `sample_id`, hash del audio, engine, versión de engine, model, voice ni mapping privado. El handle no es una ruta de filesystem ni autoriza una implementación de entrega concreta.

Cada transición ocurre dentro de la autoridad privada. Desde la clave de commitment se deriva mediante HMAC-SHA-256 una subclave de workflow con dominio versionado y contexto de `package_version`, `protocol_version`, `package_id` y `delivery_set_commitment`. Cada `PublicReviewWorkflowEvent` lleva autenticación obligatoria `loguic-tts-public-review-workflow-auth/1.0`. Su `event_id` se deriva primero del contenido normalizado sin incluir el MAC; después el MAC compromete dominio y versión, package, commitment, `audio_delivery_id`, posición, reviewer, `blind_review_id`, stage, payload completo, `event_id`, predecessor `event_id` y predecessor MAC. `delivered` usa los valores raíz explícitos `review_event_root_v1` y `review_event_mac_root_v1`. `model_validate()` valida y puede reconstruir identidades causales públicas, pero nunca emite ni repara un MAC; la verificación privada usa `hmac.compare_digest`.

`PublicReviewWorkflowState` contiene siempre el prefijo completo frozen y solo acepta `delivered → first_listen → initial_capture → disclosed → rubric_complete → locked`. Antes de emitir cualquier transición, el helper revalida binding privado, package, item, reviewer, prefijo completo, todos los MAC, stage y predecessors. Una cadena manual puede recalcular todos sus hashes públicos y seguir siendo inválida porque carece de emisión autorizada. Un MAC acredita autenticidad e integridad de la evidencia presentada y emisión bajo la autoridad del package; no prueba consumo único ni impide que esa autoridad emita dos ramas auténticas.

`initial_capture` exige transcripción percibida e `intelligibility`. `PublicReviewDisclosure` se deriva exclusivamente de la asignación y del manifiesto privados autorizados; ningún helper acepta disclosure arbitrario aportado por el consumidor. La validación del handoff vuelve a resolver el disclosure esperado y rechaza incluso una cadena autenticada cuyo contenido revelado no corresponda a la asignación. Solo después se completan las cinco dimensiones restantes.

Los estados anteriores a `locked` son drafts efímeros, no son `HumanReviewRecord`, no acreditan review final y no definen persistencia. La transición `locked` también se autentica y compromete predecessor, `lock_transition_id`, `locked_review_id`, contenido final exacto y `locked_at`. Produce exactamente el `HumanReviewRecord` contractual publicado, sin cambios semánticos. A demuestra la validez individual de ese lock, no su aceptación global única.

`LockedReviewHandoff` permanece como envelope JSON UTF-8 canónico. `validate_locked_review_handoff()` revalida binding/commitment privado, package, autenticación y secuencia completa, disclosure autorizado, lock, IDs causales y correspondencia exacta con `HumanReviewRecord`. Solo entonces proyecta un `LockClaim` frozen con `review_slot_id`, `lock_transition_id`, `handoff_id` y el `HumanReviewRecord` exacto. `review_slot_id` usa el dominio versionado `loguic-tts-public-review-slot/1.0` y depende únicamente de `package_id`, reviewer y `blind_review_id`, por lo que permanece estable ante resultados de rúbrica o timestamps distintos. El claim conserva las identidades que B necesita y no representa persistencia ni aceptación.

A garantiza autenticidad e integridad de la evidencia presentada, secuencia causal autenticada, validez individual del lock e identidades suficientes para detectar conflictos conocidos. A, por ser stateless, no garantiza consumo único de un prefijo auténtico, ausencia global de ramas, aceptación única durable, resolución de carreras/concurrencia ni append-only. B tiene contrato aprobado, pero sigue **NOT IMPLEMENTED**: su responsabilidad es aceptar atómicamente el primer handoff confirmado por slot, tratar el mismo handoff como retry y rechazar otro handoff para ese slot. La persistencia append-only/runtime sigue siendo un gap de implementación bloqueante antes de iniciar human reviews reales. Este workflow no abre reconciliación, adjudicación, winner, API, DB, filesystem, frontend ni ejecución real.

## Durable / Atomic Human Review Claim Acceptance — contrato B aprobado

Estado: **CONTRACT APPROVED / NOT IMPLEMENTED**. Esta aprobación fija el diseño de B; no crea tabla, migración, servicio, repositorio, API ni autorización para iniciar human reviews reales. El siguiente paso es un preflight de implementación separado.

### Frontera A → B y autoridad

B no acepta como autoridad un `LockClaim` externo aislado ni considera suficiente `LockClaim.model_validate()`: esa validación estructural no verifica los MAC privados. La entrada conserva el handoff JSON UTF-8 canónico y el contexto privado de A: `LockedReviewHandoff + contexto privado de A → validate_locked_review_handoff() → LockClaim validado por A → aceptación durable/transaccional de B`. El claim y el mismo payload validado llegan juntos a la operación interna de persistencia. A conserva autoridad sobre autenticidad, integridad, disclosure y causalidad individual; B adquiere autoridad solo sobre aceptación durable, unicidad por slot, idempotencia, conflicto, atomicidad y persistencia append-only/runtime.

### Invariantes y resultado

- Como máximo un handoff aceptado por `review_slot_id`. El primer handoff que logra **commit** queda aceptado durablemente; el orden de llegada de peticiones no decide al ganador.
- El mismo `handoff_id` para ese slot es `already_accepted`: devuelve la aceptación original, sin fila, escritura ni `accepted_at` nuevos. Exige además igualdad del payload canónico y de las proyecciones almacenadas; una divergencia bajo el mismo ID es `StoredReviewIntegrityError`, no un retry.
- Otro `handoff_id` para el slot es `ReviewSlotConflict`; el claim, la review, la evidencia y el timestamp originalmente aceptados permanecen intactos.
- `accepted` solo se devuelve después de confirmar el commit. Un fallo o resultado incierto de commit no acredita aceptación; un retry posterior del mismo handoff resuelve el estado durable.
- La review y su provenance aceptadas son inmutables. PostgreSQL, no una lectura o comprobación previa en Python, impone la unicidad en presencia de concurrencia.

### Persistencia mínima y protección de base de datos

Una única tabla `tts_human_review_acceptances` contiene una fila por `review_slot_id`. Sus columnas conceptuales, todas `NOT NULL`, son `review_slot_id`, `review_slot_version`, `package_id`, `handoff_id`, `lock_transition_id`, `review_id`, `canonical_handoff` y `accepted_at`. `canonical_handoff` guarda los bytes JSON UTF-8 canónicos exactos validados por A e incluye la `HumanReviewRecord` completa y el linaje autenticado; la review se reconstruye desde ese envelope. `review_id` es solo una proyección consultable, no otra autoridad. Deben persistirse así todos los campos del `LockClaim`, incluida su review exacta, sin separar una segunda tabla de review ni duplicar su cuerpo en otro JSON.

`review_slot_id` es **PRIMARY KEY**, arbitraje durable de la aceptación única. `handoff_id` es **UNIQUE**; las columnas son obligatorias; un check fija la versión de slot y otro rechaza `canonical_handoff` vacío. La base de datos protege la tabla contra `UPDATE`, `DELETE` y `TRUNCATE` para sostener append-only; la sintaxis exacta de migración y trigger queda para el preflight técnico. No hay `DO UPDATE` ni reemplazo destructivo. No se persisten claves, secretos, mapping privado ni contexto privado en esta tabla. La custodia futura de ese contexto para replay criptográfico pertenece a otra frontera.

### Transacción, carrera y fallos

En PostgreSQL `READ COMMITTED`, el camino esperado es `INSERT ... ON CONFLICT (review_slot_id) DO NOTHING RETURNING ...`. Si devuelve la fila insertada, se hace commit antes de responder `accepted`. Si no devuelve fila, se lee en una sentencia posterior la aceptación del slot: mismo handoff y evidencia/proyecciones idénticas → `already_accepted`; handoff diferente → `ReviewSlotConflict`; mismo ID con evidencia divergente → `StoredReviewIntegrityError`. Si no se puede establecer el estado durable, la operación falla cerrada. Dos transacciones concurrentes quedan arbitradas por la PK: si la primera confirma, la otra observa su fila; si revierte, la otra puede insertar.

El camino esperado con `ON CONFLICT` no transforma un `IntegrityError` genérico en retry. Si otra estrategia de inserción produce un conflicto de unicidad del slot reconocible, se hace rollback y se relee en una transacción nueva antes de clasificar; un error de otro constraint o una falla DB ajena al slot nunca se convierte automáticamente en retry o conflicto de dominio. Ningún resultado de `flush` sustituye un commit confirmado.

### Boundary interna, errores y verificación posterior

El servicio de aceptación recibe handoff y contexto privado, invoca A, obtiene el `LockClaim`, coordina la transacción y devuelve un resultado tipado. El repositorio solo inserta, consulta por slot y reconstruye datos; no autentica A ni ofrece update/delete. Los errores de dominio previstos son `InvalidLockedHandoff`, `ReviewSlotConflict`, `StoredReviewIntegrityError` y `ReviewAcceptancePersistenceError`. La implementación posterior deberá comprobar first accept, retry, conflicto, payload divergente, rollback/fallo de commit, constraints y carreras reales con transacciones independientes en PostgreSQL, además de que la DB rechaza update/delete/truncate.

Fuera de B: human reviews reales **NOT STARTED**; winner **NOT SELECTED**; reconciliación de reviews, adjudicación, API, frontend, entrega de audio, selección de voz, loader **BLOCKED**, B52 **NOT VERIFIED**, B181 **PAUSED** y A1 v4 **MEMBER DURABLE / NOT ACTIVE**. `content/content_tree.json` permanece intacto.

## Licencias y salida permitida

Antes de ejecutar, registrar separadamente licencia de engine/runtime, modelo y voz/dataset. Piper está autorizado únicamente para este benchmark aislado; una integración o distribución de producto requiere revisión independiente.

Los contratos de esquema ejecutables viven en `app/schemas/tts_engine_benchmark.py`. No implementan DB, loader, frontend, ASR/alignment, WavLM/GOP decisorio, B51/B52 ni B181. La sección B anterior fija solo el contrato documental de la futura persistencia DB.
