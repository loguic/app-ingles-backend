# Estado operativo — LOGUIC English

Actualizado: 2026-08-16
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Admission gate verification — Slice 33

Estado: cerrada, publicada y sincronizada mediante los commits contractual `0802b2a` (`docs define candidate admission gate verification`), técnico `922b3dc` (`feat verify candidate admission gates`) y documental de cierre `9ed32e2` (`docs close candidate admission gate verification slice`).

`AdmissionGateVerification` es evidencia frozen de cuatro gates y solo cuatro: `identity_matches`, `local_validation_passed`, `pending_human_decisions_clear` y `human_decision_admitted`. `verified` es su AND derivado. `AdmissionRecord(decision="admitted")` no equivale a gates verificados; `verified` no equivale a publication, active source membership ni validación curricular autoritativa.

La verificación pura consume candidate y `AdmissionRecord`; toma la revision del record, deriva una identity una vez y la compara estructuralmente, recalcula local validation una vez e ignora el report embebido. Requiere `pending_human_decisions == []` y decisión `admitted`, sin short-circuit en negativos normales. Conserva identity derivada, record y report recalculado. Mismatch, local `failed`/`pending`, pendientes y `rejected` devuelven `verified=False`; versión de payload no soportada y errores de derivación/validator se propagan. No hay I/O, source integrity, publication, membership, snapshot, manifest, loader, findings nuevos, status propio ni flujo autoritativo.

Validación confirmada: 17 específicas PASS; postflight técnico PASS; regresión seleccionada 149 passed en 0.63s (`PYTEST_EXIT=0`); suite backend completa directa en Bash 1829 passed en 21.46s (`PYTEST_EXIT=0`); `git diff --check` técnico PASS. A1-U1 sigue pending / non-member. Loader continúa BLOCKED.

## Bloque activo

No hay implementación activa mientras finaliza este cierre documental. No desbloquear loader ni diseñar publication, membership, snapshot, manifest, loader, publisher, source format o filesystem enumeration.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación, validación específica, revisión independiente y cierre documental. No repetir inspecciones ni validaciones ya confirmadas mientras no cambien los archivos cubiertos. Operar con Codex CLI + Bash; si una regresión en Codex queda indeterminada, ejecutarla una sola vez directamente en Bash. La suite backend completa se ejecuta directamente en Bash cuando corresponde.

Antes de cambiar de conversación: actualizar este documento, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar solo con checkpoint válido. Al reanudar: usar `conversation_checkpoint.py resume` antes de proponer comandos, inspecciones o cambios.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ compatibilidad curricular autoritativa;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Hacer únicamente el preflight técnico de la capacidad posterior que consume una `AdmissionGateVerification` ya producida y define la frontera entre verified admission y publication / active source membership. No diseñar todavía modelo, manifest, snapshot, publisher, loader, source format ni filesystem enumeration.

## Archivos clave

- `docs/estado-operativo.md` y `docs/bitacora.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_validation_service.py`.
