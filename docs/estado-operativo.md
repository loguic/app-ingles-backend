# Estado operativo — LOGUIC English

Actualizado: 2026-09-15T21:42:33+02:00
Baseline Git previa a este checkpoint: cb626f14e8a3a03ef1cbf234202fb50b7c25ca42
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

## Bloque activo

No existe bloque técnico automáticamente autorizado. B permanece **NOT IMPLEMENTED** y no se abre mediante este checkpoint.

### Fronteras A1, B52 y B181

B52 para la source vigente está **NOT VERIFIED**; `LOADER = BLOCKED`. `content/content_tree.json` permanece intacto. B181 permanece **PAUSED** en puerta pedagógica; no se reactiva mediante A1 v4, el benchmark, el review-lock ni este microbloque.

## Automatización disponible

- `operational_state.py` valida estructura, timestamp timezone-aware, baseline Git previa y ausencia de campos Git vivos.
- `conversation_checkpoint.py prepare|resume` compone estado semántico y Git vivo en una vista efímera read-only.
- La secuencia canónica de Closure Gate es `block_close.py → git_close.py → conversation_checkpoint.py prepare`; ChatGPT orquesta postflight independiente, documentación semántica, scope/allowlist, mensaje de commit e interpretación del checkpoint post-cierre.
- `block_workflow.py` está **UNRELIABLE / NOT CANONICAL FOR CLOSURE GATES**: solo valida el checkpoint y delega a `block_close.py`; no ejecuta `git_close.py` ni `prepare` post-cierre y conserva deuda de espera/interrupción por subprocess sin timeout, `stdin=DEVNULL`, gestión de grupo de procesos ni captura controlada. Su corrección es deuda de tooling separada y no abre ahora un microbloque de implementación.
- `a1_resource_asset_close.py` solo opera sobre assets A1 humanamente aprobados; no convierte outputs del benchmark en assets A1.

## Método operativo vigente

Seguir `docs/loguic-engineering-operating-method-v1.md`: Git real es autoridad exclusiva para sus hechos vivos; este documento conserva exclusivamente continuidad semántica y una baseline previa validable. Bash sigue siendo la vía preferida para operaciones deterministas; el routing default sigue siendo `Terra / medium`.

## Fronteras obligatorias

- baseline Git previa ≠ HEAD actual; una diferencia válida post-cierre no es contradicción;
- benchmark técnicamente finalizado ≠ human review ≠ adjudicación ≠ winner ≠ voz de producto;
- WAV del benchmark ≠ assets A1 aprobados ≠ B51/B52 ≠ loader readiness;
- A1 v4 `MEMBER DURABLE` ≠ `ACTIVE`; no activar A1 ni modificar `content/content_tree.json`;
- review-lock cerrado ≠ public reviewer package/workflow cerrado ≠ persistencia append-only/runtime;
- no iniciar human review, adjudicación, reviewer package, B52, loader o B181 sin autorización y evidencia específicas.

## Próximo objetivo

No existe otro bloque automáticamente autorizado. La siguiente frontera candidata es B: aceptación durable/atómica y persistencia append-only/runtime de human reviews; requiere decisión y scope explícitos antes de cualquier implementación. Las human reviews reales permanecen `NOT STARTED`; adjudicación y winner siguen fuera de alcance, y B52, loader, B181 y A1 no se reactivan automáticamente.

## Archivos clave

- `docs/loguic-engineering-operating-method-v1.md`, `docs/estado-operativo.md`, `scripts/engineering/operational_state.py`, `scripts/engineering/conversation_checkpoint.py`, `tests/test_operational_state.py` y `tests/test_conversation_checkpoint.py`;
- `scripts/engineering/block_close.py` y `scripts/engineering/git_close.py` permanecen sin cambios;
- `app/schemas/tts_engine_benchmark.py`, `app/services/tts_public_reviewer_workflow.py`, `docs/loguic-tts-engine-benchmark-protocol-v1.md` y `tests/test_tts_engine_benchmark_schema.py` contienen el review-lock publicado y el public reviewer workflow local;
- `content/candidates/a1-u1/pedagogical-unit-candidate-v4.json`, `content/admissions/a1-u1/adm-a1-u1-002.json` y `content/active-source/active-candidate-source-002.json`.
