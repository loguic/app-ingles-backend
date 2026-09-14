# Estado operativo — LOGUIC English

Actualizado: 2026-09-14T17:57:36+02:00
Baseline Git previa a este checkpoint: 7e62908809087f6314d6e17058bbee90d0c967c9
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

La recuperación documental anterior quedó completada. `HumanReviewRecord` representa una review final/locked, exige `locked_at` timezone-aware canonicalizado a UTC y deriva `review_id` causal. Persistencia append-only/runtime y public reviewer package/workflow siguen siendo gaps separados. Este cierre no inició human reviews, adjudicación ni selección de winner.

### Benchmark externo TTS v1

Estado semántico: **TÉCNICAMENTE FINALIZADO** en `/home/guiller/projects/loguic_tts_benchmark`, ejecución `063e6d8d-72dc-4f46-83df-ce533ddf938f`, anclada a `backend_canonical_commit=3e10e97a932f6be27cc05081ba02c555d4611565`.

- 8 voice attempts completados: cuatro Kokoro `0.9.4` y cuatro Piper `1.8.0`.
- 144 runs, 144 generaciones RAW, 144 WAV normalizados, 48 `SampleManifest` y 144 `SampleIdentity` únicos.
- El event log contiene 1170 eventos; existe exactamente un `FINALIZED`, es el último evento y tiene timestamp `2026-09-13T20:13:43.519741Z`.
- Las human blind reviews reales están **NOT STARTED** y el winner **NOT SELECTED**.

### A1 v3/v4 publicada

A1 v4 permanece **MEMBER DURABLE / NOT ACTIVE**. Los únicos assets físicos A1 aprobados son cuatro visuales: `water`, `food`, `need` y `greeting`; los WAV del benchmark no son assets A1 aprobados.

## Bloque activo

### Microbloque tooling — METHOD_GAP checkpoint/closure

Estado semántico: **READY_FOR_CLOSURE / NOT FUNCTIONAL DEVELOPMENT**.

El METHOD_GAP confirmado provenía de declarar un HEAD vivo dentro del documento que debía ser contenido por ese mismo commit. Este microbloque separa la autoridad semántica durable de Git vivo, introduce la baseline previa no circular y hace que `conversation_checkpoint.py prepare|resume` componga ambas capas sin persistir otra fuente de verdad.

Implementación: **PASS**. Postflight independiente: **PASS**; BLOCKING: **0**; NONBLOCKING: **0**. Evidencia vigente: 60 tests focales PASS, `tests/test_block_workflow.py` 3 PASS, integración temporal `prepare → close_git_changes() → prepare` PASS, `operational_state.py validate` PASS, `conversation_checkpoint.py prepare` PASS y `git diff --check` PASS. Se confirmaron baseline única/completa/no circular, pre-cierre `baseline == HEAD`, post-cierre limpio `baseline == HEAD^`, sentinel root exclusivo `0000000000000000000000000000000000000000`, checkpoint stale fail-closed, dirty-path coverage, timestamps timezone-aware y `prepare|resume` read-only.

Scope local exacto reconocido:

- `docs/loguic-engineering-operating-method-v1.md`;
- `docs/estado-operativo.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_operational_state.py`;
- `tests/test_conversation_checkpoint.py`.

No se modifica `scripts/engineering/git_close.py`, `scripts/engineering/block_close.py` ni código funcional del producto.

### Fronteras A1, B52 y B181

B52 para la source vigente está **NOT VERIFIED**; `LOADER = BLOCKED`. `content/content_tree.json` permanece intacto. B181 permanece **PAUSED** en puerta pedagógica; no se reactiva mediante A1 v4, el benchmark, el review-lock ni este microbloque.

## Automatización disponible

- `operational_state.py` valida estructura, timestamp timezone-aware, baseline Git previa y ausencia de campos Git vivos.
- `conversation_checkpoint.py prepare|resume` compone estado semántico y Git vivo en una vista efímera read-only.
- `block_close.py` y `git_close.py` realizan preflight y cierre controlado cuando un bloque esté autorizado y validado.
- `a1_resource_asset_close.py` solo opera sobre assets A1 humanamente aprobados; no convierte outputs del benchmark en assets A1.

## Método operativo vigente

Seguir `docs/loguic-engineering-operating-method-v1.md`: Git real es autoridad exclusiva para sus hechos vivos; este documento conserva exclusivamente continuidad semántica y una baseline previa validable. Bash sigue siendo la vía preferida para operaciones deterministas; el routing default sigue siendo `Terra / medium`.

## Fronteras obligatorias

- baseline Git previa ≠ HEAD actual; una diferencia válida post-cierre no es contradicción;
- benchmark técnicamente finalizado ≠ human review ≠ adjudicación ≠ winner ≠ voz de producto;
- WAV del benchmark ≠ assets A1 aprobados ≠ B51/B52 ≠ loader readiness;
- A1 v4 `MEMBER DURABLE` ≠ `ACTIVE`; no activar A1 ni modificar `content/content_tree.json`;
- review-lock cerrado ≠ persistencia append-only/runtime ≠ public reviewer package/workflow;
- no iniciar human review, adjudicación, reviewer package, B52, loader o B181 sin autorización y evidencia específicas.

## Próximo objetivo

Ejecutar únicamente las validaciones deterministas de cierre aplicables; cerrar/publicar este microbloque mediante el mecanismo Git canónico; verificar Git limpio/sincronizado; y ejecutar `conversation_checkpoint.py prepare` post-cierre. Después del Closure Gate, cualquier trabajo sobre reviewer package/workflow o persistencia append-only/runtime requiere scope y autorización separados; human reviews reales y winner permanecen fuera de alcance.

## Archivos clave

- `docs/loguic-engineering-operating-method-v1.md`, `docs/estado-operativo.md`, `scripts/engineering/operational_state.py`, `scripts/engineering/conversation_checkpoint.py`, `tests/test_operational_state.py` y `tests/test_conversation_checkpoint.py`;
- `scripts/engineering/block_close.py` y `scripts/engineering/git_close.py` permanecen sin cambios;
- `app/schemas/tts_engine_benchmark.py`, `docs/loguic-tts-engine-benchmark-protocol-v1.md` y `tests/test_tts_engine_benchmark_schema.py` contienen el review-lock ya publicado;
- `content/candidates/a1-u1/pedagogical-unit-candidate-v4.json`, `content/admissions/a1-u1/adm-a1-u1-002.json` y `content/active-source/active-candidate-source-002.json`.
