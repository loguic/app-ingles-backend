# Estado operativo — LOGUIC English

Actualizado: 2026-09-10T18:13:39+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Método operativo canónico: `docs/loguic-engineering-operating-method-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (v1.1 Astra vigente; default `Terra / medium`, por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B184 — Runtime autoritativo de experiencia y enmiendas v3

Estado: **CERRADO / PUBLICADO / SINCRONIZADO** en el backend hasta `729e58e725dd7683405ab59e7aa8cb213507df77` (`feat strict support timing with devsecops head correction`). Cabeza Alembic: `c1844e9f2a31`.

- `d54a47e`: lifecycle autoritativo de `ExperienceAttempt`.
- `18bb755`: runtime autoritativo de evidencia y finalización.
- `e4dbe04`: runtime/adaptador HTTP público de Direct English.
- `9619243`: compatibilidad de versiones de contrato de experiencia.
- `6b044e5`: mapeo de evidencia Direct English v3.
- `105b431`: bancos de transferencia v3 de una a cuatro variantes, preservando v2.
- `729e58e`: Strict Support Timing backend cerrado y corrección test-only del gate DevSecOps para la cabeza Alembic vigente; el slice Flutter cross-repo está cerrado en `1b1835405c324d0189d46bcb0a6a4e869da193f1`.

Las enmiendas B184.4 preservan la lectura histórica 2.0, mantienen start/resume sobre contenido activo y no activan contenido curricular canónico v3. Strict Support Timing valida metadata v3 opcional y deriva historial de respuestas por intento; no cambia correctness, evidence, completion, mastery, retention ni progress. El backend sigue sin una lección canónica A1 L1 v3 activa.

### B52 — Active source integrity v1

Estado: **CERRADO / DOCUMENTADO / PUBLICADO / SINCRONIZADO**. Contrato publicado: `5d318c125acdc7128b0af73abafae0bee8c7b454`. Implementación técnica publicada: `605564ecbeb9079fef248d348ad26f52f042ca30`.

`ActiveCandidateSourceIntegrityVerification` frozen contiene exactamente B43 `current_admission_gate_reevaluation` y B51 `resource_integrity_verification`. `verify_active_candidate_source_integrity(...)` consume únicamente ambos aggregates y exige que sus rutas transitivas conserven exactamente el mismo B39 por identidad Python; no recibe B39 como tercer input ni alinea entries de dominios distintos.

B52 es positive-only, frozen y all-or-nothing. Un mismo B39 produce verification conservando B43+B51 por identidad; B39 distintos producen `ValueError("active source integrity causal source mismatch")` fail-closed, sin resultado parcial, status, findings ni pairs. Una source vacía común es positiva.

La garantía se limita a la conjunción causal sobre una misma source B39: candidate payload integrity B39, current admission gates B43 y expected-vs-observed resource integrity B51. B52 no reejecuta upstream, no usa filesystem, parsing, bytes, hashing o I/O y no acredita authenticity, provenance, chronology, corrección semántica/pedagógica, curriculum compatibility ni loader readiness.

Validación: 7 tests específicos PASS; regresión seleccionada B43+B51+B52, 29 PASS; postflight técnico independiente PASS; findings BLOCKING: 0; findings NONBLOCKING: 0; suite backend completa ejecutada directamente en Bash, 2118 passed en 17.49 s; `git diff --check` técnico PASS. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`.
### B43 — Current admission gate reevaluation v1

Garantía histórica cerrada; no sustituye integridad de source activa ni loader readiness.

### B42.1 — Timestamp preciso del estado operativo

El timestamp ISO 8601 con offset y la comparación contra baseline Git siguen siendo obligatorios.

### B183 — Checkpoint Visual Flutter: recorrido demo A1

Checkpoint visual frontend histórico y aislado; no activa currículo A1 ni modifica el estado B181.

## Bloque activo

Entrada A1 canónica — **HUMAN GATE 1 y HUMAN GATE 2 = APPROVED**. Para alumnado con inglés muy bajo o nulo se aprueba una unidad mínima completa centrada en una Skill integrada: ante una intención inmediata con contexto visual y audio, producir una respuesta oral mínima, pertinente e inteligible mediante Persona + Acción y reutilizarla en una variación cercana con apoyo estrictamente menor. Comprensión, producción y transferencia conservan evidencias separables; comprensión es preparación/comprobación, no mastery receptivo. Construcción propia se operacionaliza mediante producción personal, ausencia de modelo completo, apoyo decreciente y variación. Transcript y español son práctica/rescate; la evidencia final deberá producirse sin ellos. La evaluación inicial de pertinencia e inteligibilidad podrá ser humana/externa; automatización solo de apoyo. Incremento 1 — contexto visual v3: **CERRADO / PUBLICADO / SINCRONIZADO** mediante `f40abca7abcb36b742404fbfd5e2c7575f3db2f8`; `VisualContext` opcional/accesible vincula una o más etapas a un recurso lógico inventariado y preserva v2/v3 sin contexto; 64 tests y repostflight PASS. Incremento 2 — puente de evaluación oral cualitativa: **CERRADO / PUBLICADO / SINCRONIZADO** mediante `1485309a80c63c1786b831703c89920e68c9b70d`; contratos, validación Direct English, DB y runtime postflight PASS, cabeza Alembic `d1842b7f3a91`, 206 tests focales/regresión y migración PostgreSQL aislada PASS. En v3, captura elegible con pareja cualitativa requerida pasa a `needs_review`; cobertura positiva completa de una misma identidad y fuente efectiva promueve a `satisfied` mediante el acreditador autoritativo, sin degradar `satisfied` ni promover captura estructural `pending`. Compatibilidad v2/v3/B181 preservada; `ExperienceEvidenceState` y completion no se rediseñaron; automática no acredita. `content/candidates/a1-u1/pedagogical-unit-specification-v3.json` está **HUMAN-APPROVED / PUBLISHED / SYNCED** y define la Skill integrada `a1_express_immediate_need_orally` con las identidades curriculares aprobadas `a1-u1` y `a1-u1-l1`. La extensión local mínima de `VisualContext` ya declara `static_image` o `microvideo` y, solo para microvídeo, `autoplay_once` y `replay_allowed`; preserva los contextos v3 legacy sin inferir tipo, el inventario lógico y v2. No introduce MIME, codec, URL, path, bytes, duración, player UI, preload, buffering, analytics, descriptor global, frontend, loader, DB ni B181. La candidata A1 v3 permanece **NOT APPROVED / BLOCKED** hasta una corrección pedagógica posterior y una nueva revisión humana; no se ha modificado la candidata ni la revisión humana. No existe admission, publication, membership, activación, cambio de `content/content_tree.json` o trabajo B181. Incremento 3 — opciones visuales de `ExerciseMCQ`: extensión local mínima en postflight. Mantiene MCQ textuales y su identidad canónica; añade opciones visuales homogéneas por `resource_id` lógico y nombre accesible, inventariadas y evaluadas por `answer_index`. No modifica Candidate A1 v3, `VisualContext`, frontend, loader, DB, `content_tree` ni B181.
Corrección y preparación A1 v3 local: `content/candidates/a1-u1/pedagogical-unit-candidate-v3.json` conserva comprensión MCQ visual, tres contextos visuales tipados, modelos en-GB-first y decisiones de ayuda/feedback documentadas. `content/candidates/a1-u1/human-review-v3.md` queda **HUMAN APPROVED**; esta actualización sustituye la indicación histórica anterior de bloqueo. HUMAN DECISION = **ADMIT**. Formal `AdmissionRecord` = **ADMITTED** mediante `content/admissions/a1-u1/adm-a1-u1-001.json`, con `admission_id=adm-a1-u1-001`, `reviewer_id=reviewer-human-001` e identidad `a1-u1` / `a1-u1-candidate-v3` / `1.0` / `sha256:23e0d0e1eba8fb7c6b1c73097f01350abe06c84af30fab49f9e646fd9f095018`. La convención está en `content/admissions/README.md` y la verificación focal en `tests/test_a1_candidate_admission_record.py`. MEMBERSHIP PREPARATION = **READY** y MANIFEST = **PUBLISHED** en `content/active-source/active-candidate-source-001.json`, cuya convención local está en `content/active-source/README.md`: contiene exclusivamente la membership durable `a1-u1` / `a1-u1-candidate-v3` / `1.0` / `sha256:23e0d0e1eba8fb7c6b1c73097f01350abe06c84af30fab49f9e646fd9f095018` / `adm-a1-u1-001`, con snapshot `active-candidate-source-001` y bytes v1 canónicos fijados en `tests/test_a1_candidate_membership_preparation.py`. RESOURCE BINDING PREPARATION = **READY**: `content/resources/a1-u1/README.md` y `tests/test_a1_resource_binding_preparation.py` fijan exactamente los 18 bindings relativos (12 WAV, 5 PNG, 1 MP4). PHYSICAL ASSETS = **2/18 APPROVED**: `visual.a1-u1-l1.scene.water.v1` está producido y aprobado en `content/resources/a1-u1/visual/scene-water.png`, con SHA-256 `7f923e4d276863ad60dbf8d7ffbb476e3c4921e3b32da4c9991e8779f419e7db`; `visual.a1-u1-l1.scene.food.v1` está producido y aprobado en `content/resources/a1-u1/visual/scene-food.png`, con SHA-256 `cfcc09e29879e65944b8f9ba8d313189fdfe0b228c80b065587998fafa231d5b`; los otros 16 assets siguen pendientes. Todavía no existe catálogo ni manifest de expected `ResourcePhysicalIdentity`; no se inventarán identities adicionales y estas se derivarán solo de bytes finales semánticamente/humanamente aprobados. A1 v3 queda **MEMBER DURABLE / NOT ACTIVE**; B52 = **NOT VERIFIED**, `LOADER = BLOCKED` y B181 sigue PAUSED. No hay B52, activación, frontend, loader, DB ni cambio de `content/content_tree.json`.
### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

### Strict Support Timing

Estado backend: **CERRADO / VALIDADO / PUBLICADO / SINCRONIZADO** mediante `729e58e725dd7683405ab59e7aa8cb213507df77`. Estado B184.4 Flutter: **CERRADO / PUBLICADO / SINCRONIZADO** mediante `1b1835405c324d0189d46bcb0a6a4e869da193f1` (`feat enforce strict support timing B184.4`), con 98 tests y `flutter analyze` sin issues. No existe activación de contenido canónico A1 L1 v3.
## Automatización disponible

- `operational_state.py` valida este checkpoint con `Actualizado:` timezone-aware.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

El método completo y canónico, incluido su guard de continuidad y anti-degradación, está en `docs/loguic-engineering-operating-method-v1.md`. Este documento conserva únicamente el checkpoint operativo compacto.

La configuración operativa Codex esperada es `Permissions: Workspace (Approve for me)`; `approvals_reviewer = "auto_review"` está confirmado.

La selección de herramienta es `Codex-first` para trabajo agentic y `Bash-first` para operaciones deterministas; la regla detallada permanece en el método canónico.

Al reanudar, ejecutar primero `python3 scripts/engineering/conversation_checkpoint.py resume` y continuar desde su salida más este checkpoint, sin repetir evidencia vigente. Antes de cambiar de conversación, actualizar y validar este estado y ejecutar `conversation_checkpoint.py prepare`.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ active source snapshot ≠ representación física ≠ compatibilidad curricular autoritativa;
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ AdmissionRecord correspondence ≠ current admission gate reevaluation ≠ historical gate execution proof ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource physical identity ≠ expected resource identity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no rediseñar `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, `ExperienceEvidenceState`, completion, progreso, mastery, fonética, feedback ni B181; Incremento 2 está cerrado y preserva exclusivamente los estados existentes;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.
- no activar `a1-u1-l1` v3, no modificar `content/content_tree.json` ni sustituir el contenido histórico 2.0 sin autorización explícita;
- Strict Support Timing backend y B184.4 Flutter están cerrados; este cierre cross-repo no autoriza activación de contenido ni cambios adicionales de completion.

## Próximo objetivo

Producir únicamente los 16 assets A1-U1 restantes una vez aprobados humanamente, siguiendo `content/resources/a1-u1/README.md`; después se fijarán expected identities y podrá prepararse B52. No iniciar B52, activación, frontend, loader ni trabajo B181. A1 L1 v3 permanece inactiva, A1-U1 es `member durable / not active` y `LOADER = BLOCKED`.

## Archivos clave

- `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `docs/loguic-engineering-operating-method-v1.md` y `docs/loguic-ai-model-routing-policy-v1.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `scripts/engineering/block_close.py`;
- `scripts/engineering/git_close.py`;
- `tests/test_git_close.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_candidate_admission_record_document.py`;
- `app/services/pedagogical_active_candidate_admission_record_acquisition.py`;
- `app/services/pedagogical_active_candidate_admission_record_correspondence.py`;
- `app/services/pedagogical_active_candidate_current_admission_gate_reevaluation.py`;
- `app/services/pedagogical_resource_physical_identity.py`;
- `app/services/pedagogical_active_candidate_source_resource_acquisition.py`;
- `app/services/pedagogical_active_candidate_source_observed_resource_identity_collection.py`;
- `app/services/pedagogical_active_candidate_source_resource_integrity_verification.py`;
- `app/services/pedagogical_active_candidate_source_integrity_verification.py`;
- `app/services/pedagogical_expected_resource_identity_collection.py`;
- `app/services/pedagogical_active_candidate_source_required_resource_inventory.py`;
- `app/services/pedagogical_active_candidate_source_expected_resource_coverage_verification.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `tests/test_pedagogical_active_candidate_admission_record_acquisition.py`;
- `tests/test_pedagogical_active_candidate_admission_record_correspondence.py`;
- `tests/test_pedagogical_active_candidate_current_admission_gate_reevaluation.py`;
- `tests/test_pedagogical_resource_physical_identity.py`;
- `tests/test_pedagogical_active_candidate_source_resource_acquisition.py`;
- `tests/test_pedagogical_active_candidate_source_observed_resource_identity_collection.py`;
- `tests/test_pedagogical_active_candidate_source_resource_integrity_verification.py`;
- `tests/test_pedagogical_active_candidate_source_integrity_verification.py`;
- `tests/test_pedagogical_expected_resource_identity_collection.py`;
- `tests/test_pedagogical_active_candidate_source_required_resource_inventory.py`;
- `tests/test_pedagogical_active_candidate_source_expected_resource_coverage_verification.py`;
- `app/db/models.py`, `app/schemas/content.py`, `app/schemas/direct_english_construction_review.py`, `app/services/direct_english_construction_content_validation.py`, `app/services/direct_english_construction_execution_service.py`, `app/services/direct_english_construction_review_persistence_service.py`, `app/services/direct_english_construction_review_execution_service.py`, `app/services/pedagogical_duplicate_validation.py`, `app/services/pedagogical_exercise_integrity_validation.py`, `app/services/pedagogical_validation_service.py`, `alembic/versions/d1842b7f3a91_add_direct_english_qualitative_reviews.py`, `docs/lesson-experience-contract.md`, `tests/test_direct_english_construction_review_schema.py`, `tests/test_direct_english_construction_review_persistence.py`, `tests/test_direct_english_construction_review_migration.py`, `tests/test_direct_english_construction_content_validation.py`, `tests/test_experience_evidence_runtime.py`, `tests/test_lesson_experience_schema.py`, `tests/test_pedagogical_duplicate_validation.py`, `tests/test_pedagogical_exercise_integrity_validation.py`, `tests/test_pedagogical_validation_service.py`, `tests/test_pedagogical_candidate_payload_identity.py` y `tests/test_experience_contract_versioning.py`.
