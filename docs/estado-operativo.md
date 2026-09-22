# Estado operativo — LOGUIC English

Actualizado: 2026-09-23T01:45:00+02:00
Baseline Git previa a este checkpoint: 1c1c67dbe0e366f876a0d2aac442e94390920cab
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`; contrato curricular: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Método operativo: `docs/loguic-engineering-operating-method-v1.md`; routing: `docs/loguic-ai-model-routing-policy-v1.md` (default `Terra / medium`).
- Este documento es la autoridad semántica durable; HEAD, branch, upstream, ahead/behind y working tree actuales proceden exclusivamente de la inspección read-only de Git realizada por `conversation_checkpoint.py`.
- La baseline es la frontera Git previa no circular de este checkpoint, no una declaración del HEAD actual.

## Último bloque cerrado
### Reconciliación documental fail-closed y human review lock

Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `7e62908809087f6314d6e17058bbee90d0c967c9`.

La recuperación documental anterior quedó completada. `HumanReviewRecord` representa una review final/locked, exige `locked_at` timezone-aware canonicalizado a UTC y deriva `review_id` causal. La persistencia append-only/runtime sigue siendo un gap separado; el public reviewer package/workflow quedó cerrado como microbloque posterior. Este cierre no inició human reviews, adjudicación ni selección de winner.

### Microbloque tooling — METHOD_GAP checkpoint/closure

Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `93cef0e770dd1e2a2566c2f4192f58bb7a6fb268`.

El microbloque separó autoridad semántica durable y Git vivo, introdujo la baseline Git previa no circular y mantuvo `conversation_checkpoint.py prepare|resume` como composición efímera read-only. Implementación y postflight independiente: **PASS**; BLOCKING: **0**; NONBLOCKING: **0**. La evidencia vigente incluyó 60 tests focales PASS, `tests/test_block_workflow.py` 3 PASS, integración temporal `prepare → close_git_changes() → prepare` PASS, `operational_state.py validate` PASS y `git diff --check` PASS.

El `prepare` post-cierre histórico confirmó HEAD vivo `93cef0e770dd1e2a2566c2f4192f58bb7a6fb268`, baseline previa `7e62908809087f6314d6e17058bbee90d0c967c9 == HEAD^`, árbol limpio y ahead 0 / behind 0. No hubo circularidad ni fue necesaria modificación posterior para satisfacer ese contrato. Quedan confirmados baseline única/completa/no circular, pre-cierre `baseline == HEAD`, post-cierre limpio `baseline == HEAD^`, sentinel root exclusivo `0000000000000000000000000000000000000000`, checkpoint stale fail-closed, dirty-path coverage, timestamps timezone-aware y `prepare|resume` read-only.

### Benchmark externo TTS v1

Estado semántico: **TÉCNICAMENTE FINALIZADO** en `/home/guiller/projects/loguic_tts_benchmark`, ejecución `063e6d8d-72dc-4f46-83df-ce533ddf938f`, anclada a `backend_canonical_commit=3e10e97a932f6be27cc05081ba02c555d4611565`.

- 8 voice attempts completados: cuatro Kokoro `0.9.4` y cuatro Piper `1.8.0`.
- 144 runs, 144 generaciones RAW, 144 WAV normalizados, 48 `SampleManifest` y 144 `SampleIdentity` únicos.
- El event log contiene 1170 eventos; existe exactamente un `FINALIZED`, es el último evento y tiene timestamp `2026-09-13T20:13:43.519741Z`.
- Las human blind reviews reales están **NOT STARTED** y el winner **NOT SELECTED**.

### A1 v3/v4 publicada

A1 v4 permanece **MEMBER DURABLE / NOT ACTIVE**. Los únicos assets físicos A1 aprobados son cuatro visuales: `water`, `food`, `need` y `greeting`; los WAV del benchmark no son assets A1 aprobados.

## Último bloque cerrado

### TTS Public Reviewer Package / Workflow v1

Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `fb2652a601019e20e3b2bb2959c66172522b941f`.

Scope: paquete público determinista por reviewer ligado mediante HMAC-SHA-256 y clave privada a un commitment del mapping y SHA-256 normalizado, identidad/versión inmutables, orden congelado, handles opacos de audio, workflow event-sourced `delivered → first_listen → initial_capture → disclosed → rubric_complete → locked`, disclosure derivado de la asignación privada y handoff JSON canónico con provenance replayable más el `HumanReviewRecord` final existente. La frontera pública no contiene clave, `sample_id`, hash del audio, engine, model, voice ni mapping privado. Los drafts son estados efímeros sin autoridad de review final; únicamente el linaje completo autenticado puede producir `HumanReviewRecord`.

Corrección final de A del tercer intento: cada evento lleva MAC obligatorio/versionado bajo una subclave HMAC-SHA-256 derivada con separación explícita de dominio y contexto de package. El MAC cubre versiones, package, commitment, item/delivery, reviewer, ID ciego, stage, payload completo, `event_id`, predecessor ID y predecessor MAC; `delivered` tiene raíces explícitas. Todos los helpers revalidan binding privado, package, prefijo completo, MAC, stage y contexto antes de emitir. `model_validate()` no emite ni repara MAC. Disclosure se obtiene exclusivamente del manifiesto/asignación privados. El lock autenticado compromete predecessor, transición, review final exacta y timestamp, preservando sin cambios semánticos `HumanReviewRecord`.

`LockedReviewHandoff` permanece como envelope canónico. Su validación privada completa devuelve el `LockClaim` frozen, frontera canónica hacia B, con `review_slot_id`, `lock_transition_id`, `handoff_id` y el `HumanReviewRecord` exacto. El slot usa dominio versionado más package, reviewer e ID ciego y no depende del resultado o timestamp. A garantiza autenticidad, integridad de evidencia, secuencia causal autenticada y validez individual del lock, además de las identidades para detectar conflictos conocidos. A no garantiza stateless consumo único, ausencia global de ramas, aceptación única durable, carreras/concurrencia ni append-only. B sigue **NOT IMPLEMENTED** y será responsable de aceptar atómicamente el primer claim por slot, tratar el mismo handoff como retry y rechazar otro handoff para ese slot.

Evidencia histórica del tercer intento: implementación local, tests focales del package/workflow **17 PASS**, regresión restante de benchmark, blind review y adjudicación **85 PASS**, y postflight independiente final **PASS** con BLOCKING **0** y NONBLOCKING **0**. El primer y el segundo postflight independientes fueron **FAIL** históricos y el preflight Astra posterior fue **PASS**; sus findings motivaron las correcciones locales sucesivas. El postflight final confirmó autenticidad completa `delivered → locked`, rechazo de cadenas con hashes públicos fabricados, MAC de otra clave y payload/predecessor/stage/context alterados, disclosure y binding privado incompatibles; `LockClaim` frozen, slot estable ante rúbrica/timestamp, retry idéntico estable y ramas auténticas divergentes detectables como conflicto. Confirmó también que `HumanReviewRecord` no cambia semánticamente y que A no promete unicidad global ni durable. Las human reviews reales siguen **NOT STARTED**.

Exclusiones: implementación de B, DB, migraciones, repositorios, API, filesystem persistence, runtime append-only, frontend/UX, ejecución real, reconciliación A/B, adjudicación, winner, selección de voz, B51/B52, loader, B181, activación A1 y `content/content_tree.json`. La aceptación durable/atómica y la persistencia append-only/runtime permanecen como el siguiente gap separado después del cierre de este microbloque.

Scope técnico cerrado:

- `app/schemas/tts_engine_benchmark.py`
- `app/services/tts_public_reviewer_workflow.py`
- `docs/estado-operativo.md`
- `docs/loguic-tts-engine-benchmark-protocol-v1.md`
- `tests/test_tts_engine_benchmark_schema.py`

### Microbloque tooling — orquestador fiable del Closure Gate

Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `96641759d1aec8d95ed47f9ffccc7d9c59510318`.

`block_workflow.py` orquesta explícitamente el tramo determinista ya aprobado `checkpoint validation → block_close.py → git_close.py → conversation_checkpoint.py prepare`, en orden estricto y con fallo cerrado. Su CLI separa los argumentos técnicos posteriores a `--block-close-args` de `--branch`, `--upstream`, `--message`, la allowlist repetida `--file` y el timeout por fase. No reconstruye validaciones técnicas, lógica Git ni composición del checkpoint.

Cada helper se ejecuta sin shell, con `stdin=DEVNULL`, stdout/stderr capturados y propagados, timeout configurable y sesión/grupo de procesos propio. El orquestador actúa como child subreaper en el entorno Linux canónico: después de recolectar al líder comprueba que el process group haya desaparecido. Si quedan descendientes, la fase falla aunque el líder haya terminado con status 0; aplica SIGTERM, espera acotada, escala a SIGKILL, verifica la desaparición del grupo y recolecta los descendientes reparentados que correspondan. Timeout, interrupción o fallo de comunicación siguen la misma limpieza acotada, devuelven estado no cero y no inician fases posteriores. La implementación no decide readiness: postflight independiente, documentación semántica, scope/allowlist, mensaje y lectura del checkpoint siguen bajo orquestación de ChatGPT antes o después del tramo determinista correspondiente.

El primer postflight independiente fue **FAIL**: detectó falso PASS con un descendiente vivo, cobertura adversarial insuficiente y documentación incompleta del cierre parcial posterior a Git. Los tres findings fueron corregidos localmente. La validación vigente registra `tests/test_block_workflow.py` **18 PASS**, incluida prueba real de líder status 0 con descendiente residual terminado y fase rechazada, y regresión directamente relacionada de `block_close.py`, `git_close.py` y `conversation_checkpoint.py` **86 PASS**. El re-postflight independiente final fue **PASS**, con BLOCKING **0** y NONBLOCKING **0**: revalidó que el líder status 0 con descendiente vivo produce FAIL, no reporta PASS, termina el descendiente, elimina el process group residual y no deja hijos recolectables; un proceso externo al grupo permanece intacto. Confirmó además orden estricto, fallo cerrado, propagación exacta de argumentos, ausencia de lógica Git duplicada y de `shell=True`, `stdin=DEVNULL`, y que timeout, interrupción, señal y launcher failure no pueden producir PASS.

El cierre fue publicado y su `conversation_checkpoint.py prepare` post-cierre terminó correctamente: la baseline histórica pre-cierre `e4fb910b2731ad8323a23ff700b27ee5fc2fdbe4` quedó como `HEAD^`, con árbol limpio y sincronizado. Por tanto, `scripts/engineering/block_workflow.py` es el orquestador canónico para Closure Gates futuros, únicamente después de que postflight independiente haya pasado, la documentación semántica esté preparada y scope/allowlist y mensaje estén aprobados. Su tramo determinista canónico es `checkpoint validation → block_close.py → git_close.py → conversation_checkpoint.py prepare`.

Si `git_close.py` completa commit/push y el `prepare` posterior falla, existe **PARTIAL CLOSURE / PUBLISHED BUT CHECKPOINT-INCOMPLETE**: el cierre Git ya está publicado y el workflow devuelve FAIL global. No intenta rollback ni repite automáticamente commit/push. Se debe reconciliar mediante inspección read-only de Git y estado semántico, corregir la causa y continuar desde el estado publicado real hasta completar el checkpoint correspondiente; no se clasifica como fallo Git.

Scope local reconocido:

- `scripts/engineering/block_workflow.py`
- `tests/test_block_workflow.py`
- `docs/estado-operativo.md`
- `docs/loguic-engineering-operating-method-v1.md`

B permanece **NOT IMPLEMENTED** y no se abre mediante este microbloque.
## Último bloque cerrado

### Incremento 1 — LOGUIC Operational Automation / Token Reduction — Compact/JSON Checkpoint

Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `f2c4ca9e6d1e1f394499a7943c8df98914382316`.

Primer incremento local: `conversation_checkpoint.py` conserva `prepare|resume` y su Markdown por defecto, y añade `--format compact` y `--format json`. Las tres representaciones reutilizan una única validación de estado/baseline, inspección Git y validación fail-closed del scope dirty antes de representar el resultado; upstream resoluble y ahead/behind calculables son obligatorios. JSON conserva completos `active_block` y `next`. Compact usa `application/x-www-form-urlencoded` `compact-v1`, se parsea con `urllib.parse.parse_qsl`, y declara para ambos textos `*_TRUNCATED` y `*_LENGTH`; el contenido completo es recuperable mediante JSON o Markdown. `CHECKPOINT_STATUS=PASS` acredita validez del checkpoint y puede coexistir con `TREE=DIRTY` únicamente cuando todos los dirty paths están reconocidos por el checkpoint vigente. Ningún formato infiere readiness, test selection, scope, postflight o decisiones semánticas.

La implementación inicial preservó Markdown default, añadió compact/JSON y logró ~96 % de ahorro; su primer postflight independiente fue **FAIL**: detectó upstream ausente/irresoluble fail-open, truncación semántica de `next`, `STATUS` ambiguo y delimitador compacto no apto para split ingenuo. La corrección exige upstream resoluble y ahead/behind calculables, conserva `active_block` y `next` completos en JSON, hace explícita y recuperable la truncación compacta, usa `CHECKPOINT_STATUS`, `compact-v1`, `application/x-www-form-urlencoded` y parsing canónico `urllib.parse.parse_qsl`. El re-postflight final fue **PASS**, con BLOCKING **0** y NONBLOCKING **0**: focales **51 PASS**, regresión relacionada vigente **34 PASS**, upstream ausente/irresoluble rechazado, ahead real `1/0`, behind real `0/1`, dirty conocido PASS con `TREE=DIRTY`, dirty desconocido rechazado, round-trip compacto de `|`, `=`, `&`, `%`, comillas, backslash, newline y Unicode, parser JSON y read-only PASS. El Closure Gate confirmó block-close, git-close, prepare y `[closure-gate]` PASS con árbol limpio y sincronizado. Ahorro final: Markdown **14.400 bytes**, compact **898 bytes** (**93,76 %**) y JSON **3.029 bytes** (**78,97 %**). Este incremento reduce tokens y contexto, pero no sustituye el checkpoint Markdown completo ni automatiza readiness, postflight, selección de tests, scope o una nueva autoridad.

Scope local reconocido: `scripts/engineering/conversation_checkpoint.py`, `tests/test_conversation_checkpoint.py`, `docs/estado-operativo.md` y `docs/loguic-engineering-operating-method-v1.md`.
### Incremento 2 — LOGUIC Operational Automation / Token Reduction — Compact prepare en Closure Gate
Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `9b2bd7898c02461e9b376e7ad44abbf4c52c9c2a` (`feat add compact prepare output to closure gate`). `--checkpoint-prepare-format {markdown,compact}` deja `markdown` como default compatible con una ejecución exacta de `conversation_checkpoint.py prepare`; `compact` modifica exclusivamente el prepare final y ejecuta una vez `conversation_checkpoint.py prepare --format compact`. Checkpoint inicial directo/breve sin invocar `conversation_checkpoint.py`, orden, fail-closed y **PARTIAL CLOSURE / PUBLISHED BUT CHECKPOINT-INCOMPLETE** intactos; no rollback, retry, segundo git-close ni fallback Markdown. stdout/stderr se preservan y `block_workflow.py` no interpreta `compact-v1`; process-group cleanup, timeout, `stdin=DEVNULL`, señales, launcher failure, allowlist, branch/upstream/message, lógica Git y límites externos de readiness/postflight/scope/tests no cambian. Postflight PASS (BLOCKING **0**, NONBLOCKING **0**), `tests/test_block_workflow.py` **23 PASS** y Closure Gate real (block-close, git-close, checkpoint-prepare compact y closure-gate) PASS; prepare compacto emitido correctamente con `TREE=CLEAN`, `ahead 0 / behind 0`, `master`/`origin/master` y baseline no circular `6d70cc6c22205cc42ad6a306aa7b96e965685705 == HEAD^`. Ahorro: Markdown **7.933 bytes**, compact **901 bytes**, reducción **88,64 %**. Scope cerrado: `scripts/engineering/block_workflow.py`, `tests/test_block_workflow.py`, `docs/estado-operativo.md` y `docs/loguic-engineering-operating-method-v1.md`.
### Incremento 3 — LOGUIC Operational Automation / Token Reduction — Validation Recipe approved-v1
Estado semántico: **CLOSED / PUBLISHED / SYNCED** históricamente en `8bc469595807926bd1e05cb8916486bfea332c5f` (`feat add validation recipe approved v1`). Implementación inicial PASS; primer postflight independiente FAIL por el único finding BLOCKING, abreviaturas `argparse` como `--foc` y `--verb`; corrección `ArgumentParser(..., allow_abbrev=False)`; re-postflight PASS con BLOCKING **0**, NONBLOCKING **0**, focales **22 PASS** y Closure Gate real PASS (block-close, git-close, checkpoint-prepare compacto y closure-gate), con árbol limpio/sincronizado y baseline histórica pre-cierre `1b902c2f424c5d0bec76654c25f160977e036737 == HEAD^`. Contrato final único `approved-v1`: un pytest con rutas focal/regression explícitas preseleccionadas por ChatGPT/Codex, luego `git diff --check`, `operational_state.py validate` y `conversation_checkpoint.py prepare --format compact`, en orden/fallo cerrado, read-only, `shell=False`, `stdin=DEVNULL` y cwd raíz; sin selección automática de tests, readiness, postflight, scope ni autorización automática de Closure Gate. Solo acepta `--focal`, `--regression` y `--verbose` completos; abreviaturas exit 2, sin passthrough genérico, comandos arbitrarios ni shell snippets. Ahorro final: flujo manual **1.153 bytes**, receta PASS **63 bytes**, reducción aproximada **94,54 %**. Scope cerrado: `scripts/engineering/validation_recipe.py`, `tests/test_validation_recipe.py`, `docs/estado-operativo.md` y `docs/loguic-engineering-operating-method-v1.md`.
## Bloque activo
`Durable / Atomic Human Review Claim Acceptance` (B): contrato **CONTRACT APPROVED** en `docs/loguic-tts-engine-benchmark-protocol-v1.md`; B completo **NOT IMPLEMENTED**. Decisión local registrada en `docs/bitacora.md` y `docs/roadmap.md`. Frontera: handoff canónico más contexto privado → `validate_locked_review_handoff()` de A → `LockClaim` validado con el mismo handoff → aceptación transaccional de B; nunca claim externo aislado. El contrato exige PK por slot, retry idéntico sin escritura, conflicto sin reemplazo y commit confirmado. Subpasos 1, 2 y 3: **CLOSED / PUBLISHED / SYNCED**; el Subpaso 3 quedó publicado en `1c1c67dbe0e366f876a0d2aac442e94390920cab` con tres carreras PostgreSQL reales, handoffs A auténticos, `READ COMMITTED`, bloqueo observado mediante `pg_blocking_pids`, una fila durable por escenario, focales **14 PASS**, regresiones **104 PASS** y postflight independiente **PASS**. Human reviews reales **NOT STARTED**. Dirty paths reconocidos: `docs/estado-operativo.md`, `docs/loguic-tts-engine-benchmark-protocol-v1.md`, `docs/bitacora.md` y `docs/roadmap.md`.
### Fronteras A1, B52 y B181

B52 para la source vigente está **NOT VERIFIED**; `LOADER = BLOCKED`. `content/content_tree.json` permanece intacto. B181 permanece **PAUSED** en puerta pedagógica; no se reactiva mediante A1 v4, el benchmark, el review-lock ni este microbloque.

## Automatización disponible

- `operational_state.py` valida estructura, timestamp timezone-aware, baseline Git previa y ausencia de campos Git vivos.
- `conversation_checkpoint.py prepare|resume` compone estado semántico y Git vivo en una vista efímera read-only con upstream obligatorio. `--format compact` entrega `compact-v1` parseable mediante `urllib.parse.parse_qsl`; `--format json` conserva las secciones semánticas completas. Ambos reutilizan las validaciones del checkpoint Markdown y no crean una nueva autoridad.
- `block_workflow.py` es el orquestador canónico del tramo determinista de Closure Gates futuros: `checkpoint validation → block_close.py → git_close.py → conversation_checkpoint.py prepare`.
- ChatGPT conserva readiness, postflight independiente, decisiones semánticas, scope/allowlist, mensaje e interpretación del checkpoint post-cierre; también realiza la reconciliación read-only si existe partial closure.
- `a1_resource_asset_close.py` solo opera sobre assets A1 humanamente aprobados; no convierte outputs del benchmark en assets A1.

## Método operativo vigente

Seguir `docs/loguic-engineering-operating-method-v1.md`: Git real es autoridad exclusiva para sus hechos vivos; este documento conserva exclusivamente continuidad semántica y una baseline previa validable. Bash sigue siendo la vía preferida para operaciones deterministas; el routing default sigue siendo `Terra / medium`.

## Fronteras obligatorias

- baseline Git previa ≠ HEAD actual; una diferencia válida post-cierre no es contradicción;
- benchmark técnicamente finalizado ≠ human review ≠ adjudicación ≠ winner ≠ voz de producto;
- WAV del benchmark ≠ assets A1 aprobados ≠ B51/B52 ≠ loader readiness;
- A1 v4 `MEMBER DURABLE` ≠ `ACTIVE`; no activar A1 ni modificar `content/content_tree.json`;
- review-lock cerrado ≠ public reviewer package/workflow cerrado ≠ contrato B aprobado ≠ Subpaso 1 cerrado ≠ Subpaso 2 cerrado ≠ Subpaso 3 de concurrencia ≠ autorización para iniciar human reviews reales;
- no iniciar human review, adjudicación, reviewer package, B52, loader o B181 sin autorización y evidencia específicas.

## Próximo objetivo

La única siguiente acción es un **preflight read-only para determinar si B completo ya cumple todos sus criterios de cierre o si queda algún subpaso pendiente**, sin declarar B completo cerrado ni iniciar human reviews reales. B completo permanece **CONTRACT APPROVED / NOT IMPLEMENTED**. Las human reviews reales permanecen **NOT STARTED**, el winner **NOT SELECTED**; reconciliación de reviews y adjudicación siguen fuera de alcance. A1 v4 sigue **MEMBER DURABLE / NOT ACTIVE**, B52 **NOT VERIFIED**, loader **BLOCKED** y B181 **PAUSED**; ninguno se reactiva automáticamente.

## Archivos clave

- `docs/loguic-engineering-operating-method-v1.md`, `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `docs/devsecops-gate.md`, `scripts/engineering/operational_state.py`, `scripts/engineering/conversation_checkpoint.py`, `tests/test_operational_state.py` y `tests/test_conversation_checkpoint.py`;
- `scripts/engineering/block_workflow.py`, `tests/test_block_workflow.py`, `scripts/engineering/block_close.py` y `scripts/engineering/git_close.py` definen y cubren el tramo determinista de cierre; los dos últimos permanecen sin cambios;
- `app/schemas/tts_engine_benchmark.py`, `app/services/tts_public_reviewer_workflow.py`, `docs/loguic-tts-engine-benchmark-protocol-v1.md` y `tests/test_tts_engine_benchmark_schema.py` contienen el review-lock publicado y el public reviewer workflow local;
- `content/candidates/a1-u1/pedagogical-unit-candidate-v4.json`, `content/admissions/a1-u1/adm-a1-u1-002.json` y `content/active-source/active-candidate-source-002.json`.
