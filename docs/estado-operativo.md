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

### Active candidate membership — Slice 34

Estado técnico completado localmente mediante los commits contractual `df3a9cd` (`docs define active candidate membership`) y técnico `6c481a5` (`feat add active candidate membership`). Publicación y cierre documental aún pendientes.

`ActiveCandidateMembership` es un value object frozen con exactamente `identity: CandidatePayloadIdentity` y `admission_id: str`. Se construye exclusivamente mediante `declare_active_candidate_membership(admission_verification)` y solo cuando `AdmissionGateVerification.verified` es verdadero; una verification no verificada produce `ValueError`.

La membership preserva exactamente `admission_verification.derived_identity` y `admission_verification.admission_record.admission_id`. No recalcula identity, validación local, gates, schema version ni digest. No incorpora candidate, AdmissionRecord completo, status, findings, timestamp, actor, publication ID, source ID, orden curricular ni estado de snapshot.

`AdmissionGateVerification.verified` no equivale por sí solo a membership activa: la declaración explícita `ActiveCandidateMembership` representa el salto contractual hacia active membership. La entidad atómica no equivale a persistencia física, snapshot, source integrity, curriculum order ni compatibilidad curricular autoritativa. La regla de máximo una revisión activa por unit pertenece a una futura colección/snapshot.

Validación confirmada: 3 pruebas específicas PASS; revisión técnica manual PASS; regresión seleccionada 152 passed en 0.64s (`PYTEST_EXIT=0`); suite backend completa directa en Bash 1832 passed en 20.47s (`PYTEST_EXIT=0`); `git diff --check` PASS. A1-U1 sigue pending / non-member. Loader continúa BLOCKED.

## Bloque activo

Cierre documental de la slice 34 en curso. Los commits `df3a9cd` y `6c481a5` permanecen locales hasta completar documentación, validación y publicación. No implementar todavía snapshot, collection, manifest, source integrity ni loader.

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

Después de cerrar y publicar la slice 34, hacer únicamente el preflight técnico de la futura colección/snapshot de `ActiveCandidateMembership`: agrupación, máximo una revisión activa por unit y frontera de replacement/consistencia. No diseñar todavía representación física, manifest, source acquisition, source integrity ni loader.

## Archivos clave

- `docs/estado-operativo.md` y `docs/bitacora.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_validation_service.py`.
