# Estado operativo — LOGUIC English

Actualizado: 2026-09-14T13:07:23+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`; contrato curricular: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Método operativo: `docs/loguic-engineering-operating-method-v1.md`; routing: `docs/loguic-ai-model-routing-policy-v1.md` (default `Terra / medium`).
- Repositorio: `app-ingles-backend`; branch: `master`.
- HEAD publicado: `4d26cf2f3557266b30c26328dbe6f7f76a5e61d9` (`fix reconcile blind reviews by private sample identity`). Al inicio de esta reconciliación, `origin/master` apuntaba al mismo commit.
- El estado final requerido para un bloque cerrado sigue siendo Git limpio y sincronizado; este checkpoint registra explícitamente el trabajo local no publicado.

## Último bloque cerrado

### Reconciliación privada A/B del benchmark TTS v1

Estado: **CLOSED / PUBLISHED / SYNCED** en `4d26cf2f3557266b30c26328dbe6f7f76a5e61d9`.

Cada reviewer conserva su propio `blind_review_id`. La frontera privada resuelve `blind_review_id → BlindReviewMapping → sample_id`; solo pueden reconciliarse reviews A/B cuyos mappings resuelven al mismo `sample_id`. No hay `blind_review_id` compartido, no se expone identidad técnica a reviewers y este cierre no inicia review humana ni selecciona winner.

### TTS WAV normalization profile y protocolo de benchmark v1

Estado: **PUBLISHED**. `c2897ba9e17b2f0477f6d2ba304a3831e8bdfc3c` publicó TTS WAV normalization profile v1. `a3b8b754a0cbb556fc80afaa2b22379953997561` publicó TTS Engine Benchmark Protocol v1. `4a6ce2f6b18e4f8bab4f8dee991a0c040f36278a` corrigió el scope de `DeterminismProbe`; `3e10e97a932f6be27cc05081ba02c555d4611565` aclaró la identidad de normalización y es la frontera canónica del benchmark externo.

### A1 v3/v4 publicada

A1 v3 publicó specification, candidate, admission, membership y bindings. A1 v4 publicó la corrección IPA en-GB de `help` (`/hɛlp/` → `/help/`), su admission y membership durable. A1 v4 es **MEMBER DURABLE / NOT ACTIVE**. Los únicos assets físicos A1 aprobados son cuatro visuales: `water`, `food`, `need` y `greeting`; los WAV del benchmark no son assets A1 aprobados.

## Bloque activo

### Recuperación documental fail-closed

La bitácora y el roadmap ya fueron reconciliados después de detectar documentación stale frente a Git y a la evidencia física del benchmark. Este archivo completa esa recuperación. No autoriza desarrollo, activación, loader, B52, B181, human review ni selección de winner.

### Benchmark externo TTS v1

Estado: **TÉCNICAMENTE FINALIZADO** en `/home/guiller/projects/loguic_tts_benchmark`, ejecución `063e6d8d-72dc-4f46-83df-ce533ddf938f`, anclada a `backend_canonical_commit=3e10e97a932f6be27cc05081ba02c555d4611565`.

- 8 voice attempts completados: cuatro Kokoro `0.9.4` y cuatro Piper `1.8.0`.
- 144 runs, 144 generaciones RAW, 144 WAV normalizados, 48 `SampleManifest` y 144 `SampleIdentity` únicos.
- El event log contiene 1170 eventos; existe exactamente un `FINALIZED`, es el último evento y tiene timestamp `2026-09-13T20:13:43.519741Z`.
- `finalize()` revalida cobertura, IDs, layout, RAW/normalizados, hashes, metadata, tamaños, records de normalización, `GenerationCase`, `SampleIdentity`, lifecycle, manifests e inventario antes de finalizar.

Esta finalización no equivale a assets A1 aprobados, B51/B52, loader ready, activación A1, human review, adjudicación, winner ni voz de producto. Las human blind reviews reales están **NOT STARTED** y el winner **NOT SELECTED**.

### Review-lock local

Estado: **LOCAL / IMPLEMENTED / TECHNICALLY REVIEWED / NOT CLOSED / NOT PUBLISHED**.

Los únicos cambios técnicos locales de este contrato son `app/schemas/tts_engine_benchmark.py`, `docs/loguic-tts-engine-benchmark-protocol-v1.md` y `tests/test_tts_engine_benchmark_schema.py`. Representan `HumanReviewRecord` final/locked, `locked_at` timezone-aware canonicalizado a UTC y `review_id` causal. El commit local anterior `962afec` fue descartado mediante `git reset --mixed 4d26cf2`; no es HEAD ni está publicado. Persistencia append-only/runtime y public reviewer package/workflow son gaps futuros separados.

### Fronteras A1 y B181

B52 para la source vigente está **NOT VERIFIED**; `LOADER = BLOCKED`. `content/content_tree.json` no se modifica. B181 permanece **PAUSED** en puerta pedagógica; no se reactiva mediante A1 v4, el benchmark ni esta reconciliación.

## Automatización disponible

- `operational_state.py` valida título, secciones, timestamp timezone-aware, antigüedad y baseline Git.
- `conversation_checkpoint.py prepare|resume` produce vistas efímeras; `docs/estado-operativo.md` sigue siendo la autoridad canónica.
- `block_close.py` y `git_close.py` realizan cierres controlados cuando un bloque esté autorizado y validado.
- `a1_resource_asset_close.py` solo opera sobre assets A1 humanamente aprobados; no convierte outputs del benchmark en assets A1.

## Método operativo vigente

Seguir `docs/loguic-engineering-operating-method-v1.md`: reutilizar evidencia vigente, separar contrato, implementación, postflight, documentación y cierre Git, y no avanzar desde trabajo local no cerrado. Bash es la autoridad preferida para operaciones deterministas; el routing default sigue siendo `Terra / medium`.

## Fronteras obligatorias

- benchmark técnicamente finalizado ≠ human review ≠ adjudicación ≠ winner ≠ voz de producto;
- WAV del benchmark ≠ assets A1 aprobados ≠ B51/B52 ≠ loader readiness;
- A1 v4 `MEMBER DURABLE` ≠ `ACTIVE`; no activar A1 ni modificar `content/content_tree.json`;
- reconciliación privada A/B ≠ exposición de `sample_id` a reviewer;
- review-lock local técnicamente revisado ≠ contrato cerrado/publicado ≠ persistencia append-only/runtime;
- no iniciar human review, adjudicación, reviewer package, B52, loader o B181 sin autorización y evidencia específicas.

## Próximo objetivo

Completar únicamente el cierre documental fail-closed de esta recuperación; no hay desarrollo técnico autorizado. Después de una aprobación humana separada, las fronteras siguen siendo: cerrar/publicar el contrato local de review-lock, resolver por separado el reviewer package/workflow y la persistencia append-only/runtime, y solo entonces preparar human reviews reales. Ninguna de esas fronteras autoriza actualmente adjudicación o selección de winner.

## Archivos clave

- `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `docs/loguic-engineering-operating-method-v1.md` y `docs/loguic-ai-model-routing-policy-v1.md`;
- `docs/loguic-tts-wav-normalization-profile-v1.md` y `docs/loguic-tts-engine-benchmark-protocol-v1.md`;
- `app/schemas/tts_engine_benchmark.py` y `tests/test_tts_engine_benchmark_schema.py` (cambios locales de review-lock, no publicados);
- `scripts/engineering/operational_state.py`, `scripts/engineering/conversation_checkpoint.py`, `scripts/engineering/block_close.py` y `scripts/engineering/git_close.py`;
- `content/candidates/a1-u1/pedagogical-unit-candidate-v4.json`, `content/admissions/a1-u1/adm-a1-u1-002.json` y `content/active-source/active-candidate-source-002.json`.
