# Estado operativo — LOGUIC English

Actualizado: 2026-08-16
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `1b7dea5`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 32

Estado: cerrada técnicamente; commits contractual `bdcba96` (`docs define candidate admission decision record`) y técnico `d6d0a16` (`feat add candidate admission decision record`). Cierre documental y publicación pendientes.

`CandidatePayloadIdentity` queda formalizada como value object frozen de `unit_id`, `candidate_revision`, `payload_schema_version` y `content_digest`. `AdmissionRecord` frozen contiene exactamente `admission_id`, `identity`, `decision`, `reviewer_id` y `decided_at`; consume identity conforme sin recanonicalizar ni recalcular digest.

Solo admite/rechaza decisiones `admitted`/`rejected`; pending es ausencia de decisión final y `admitted` != gates verificados. IDs opacos caller-provided no blank se preservan literalmente. `decided_at` exige `datetime` UTC-aware con offset cero y conserva microsegundos. No hay I/O, validación local, membership ni flow. A1-U1 sigue pending/non-member; loader BLOCKED.

El postflight corrigió antes de regresión el chequeo runtime de `decision`: exige `str` antes del literal y cubre non-str ordinario e igualdad personalizada. Validación vigente: 24 específicas PASS; re-postflight PASS; regresión 132 passed in 0.61s y suite completa Bash 1812 passed in 21.30s, ambos `PYTEST_EXIT=0`; `git diff --check` PASS.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada para cambiar de conversación.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no se considera fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación técnica, validación específica, revisión independiente y cierre documental. Las regresiones y suites amplias se ejecutan solo cuando el alcance y riesgo las justifican. Los commits y la publicación permanecen bajo confirmación humana.

El protocolo operativo conserva Codex CLI + Bash y `docs/estado-operativo.md` como fuente canónica para cambiar de conversación. No deben repetirse inspecciones ni validaciones vigentes si los archivos cubiertos no han cambiado. Si una regresión queda indeterminada en Codex, se ejecuta una sola vez directamente en Bash; la suite completa también se ejecuta directamente en Bash cuando corresponda.

Antes de cambiar: actualizar `docs/estado-operativo.md`, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar únicamente si genera un checkpoint válido. Al reanudar: ejecutar `conversation_checkpoint.py resume`, recuperar ese estado antes de proponer comandos, inspecciones o cambios, y no repetir validaciones vigentes.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ resultado de evaluación ≠ aprendizaje ≠ mastery;
- `required_stages` y `SkillCoverage` son contratos heredados y no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`;
- no modificar `SkillCoverage` ni `required_stages`;
- no exigir un plan por lección ni implementar ledger, agregación curricular definitiva por `Skill`, orden interunidad o CEFR, ciclos, orden intra-stage o prerrequisitos;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.
- disponibilidad curricular ≠ recorrido del learner ≠ evidencia real ≠ progreso ≠ mastery.

## Bloque activo

### Admission gate verification — preflight técnico

Definir únicamente una verificación pura que combine candidate exacto, `CandidatePayloadIdentity`, validación local recalculada, decisiones pendientes y `AdmissionRecord`, sin circularidad. No asumir servicio, resultado, status, findings ni integración con membership/snapshot.

AdmissionRecord no verifica gates ni publica; membership/snapshot, loader y publisher siguen fuera. Loader continúa BLOCKED. Si el background de Codex se interrumpe, conservar Codex CLI + Bash y ejecutar la suite completa directamente en Bash; no repetir validaciones vigentes sin cambios técnicos.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer un preflight técnico separado para definir únicamente la representación machine-readable de AdmissionRecord sobre `CandidatePayloadIdentity`: admission ID, decisión admitted/rejected, reviewer, timestamp UTC e invariantes. Membership/snapshot quedan después.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_conversation_checkpoint.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `app/services/pedagogical_capability_artifact_reference_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `tests/test_pedagogical_capability_artifact_reference_validation.py`;
- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `tests/test_pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_capability_claim_availability.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`;
- `app/services/pedagogical_capability_preparation_snapshot.py`;
- `tests/test_pedagogical_capability_preparation_snapshot.py`;
- `app/services/pedagogical_local_capability_preparation_view.py`;
- `tests/test_pedagogical_local_capability_preparation_view.py`;
- `app/services/pedagogical_local_skill_prerequisite_consumption.py`;
- `tests/test_pedagogical_local_skill_prerequisite_consumption.py`;
- `app/services/pedagogical_local_skill_prerequisite_assessment.py`;
- `tests/test_pedagogical_local_skill_prerequisite_assessment.py`;
- `app/services/pedagogical_curriculum_order.py`;
- `tests/test_pedagogical_curriculum_order.py`;
- `app/services/pedagogical_curriculum_unit_position.py`;
- `tests/test_pedagogical_curriculum_unit_position.py`;
- `app/services/pedagogical_curriculum_candidate_correspondence.py`;
- `tests/test_pedagogical_curriculum_candidate_correspondence.py`;
- `app/services/pedagogical_curriculum_context_scope.py`;
- `tests/test_pedagogical_curriculum_context_scope.py`;
- `app/services/pedagogical_ordered_curriculum_candidate_context.py`;
- `tests/test_pedagogical_ordered_curriculum_candidate_context.py`;
- `app/services/pedagogical_accumulated_curriculum_preparation.py`;
- `tests/test_pedagogical_accumulated_curriculum_preparation.py`;
- `app/services/pedagogical_curriculum_skill_prerequisite_assessment.py` y `tests/test_pedagogical_curriculum_skill_prerequisite_assessment.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
