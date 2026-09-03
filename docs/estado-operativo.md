# Estado operativo — LOGUIC English

Actualizado: 2026-09-03T01:12:51+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Método operativo canónico: `docs/loguic-engineering-operating-method-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
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
- `729e58e`: Strict Support Timing backend cerrado y corrección test-only del gate DevSecOps para la cabeza Alembic vigente.

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

No hay activación curricular v3 en curso.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

### Strict Support Timing

Estado: **CERRADO / VALIDADO / PUBLICADO / SINCRONIZADO** mediante `729e58e725dd7683405ab59e7aa8cb213507df77`. No existe activación de contenido canónico A1 L1 v3; el trabajo Flutter correspondiente permanece separado y futuro.
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
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.
- no activar `a1-u1-l1` v3, no modificar `content/content_tree.json` ni sustituir el contenido histórico 2.0 sin autorización explícita;
- Strict Support Timing backend está cerrado en `729e58e`; solo su slice Flutter permanece futuro y no iniciado, sin autorizar activación de contenido ni cambios de completion.

## Próximo objetivo

La recuperación del estado operativo y el backend Strict Support Timing están completos. El siguiente objetivo es decidir y, si se autoriza, ejecutar el slice Flutter de Strict Support Timing; no está iniciado ni implementado. Canonical A1 L1 v3 remains inactive; B181 remains paused.

## Archivos clave

- `docs/estado-operativo.md`, `docs/bitacora.md` y `docs/loguic-engineering-operating-method-v1.md`;
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
- `app/services/pedagogical_validation_service.py`.
