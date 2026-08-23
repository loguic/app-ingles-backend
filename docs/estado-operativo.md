# Estado operativo — LOGUIC English

Actualizado: 2026-08-23
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Active candidate AdmissionRecord correspondence verification v1 — Slice 42

Estado técnico: contrato e implementación **CERRADOS / PUBLICADOS / SINCRONIZADOS**. Contrato `4e9dee40450f0c409d6e199c76473adc50327da1` (`docs define active candidate admission record correspondence verification v1`) e implementación `ac0b07ecf245996430ca7b178006f0d02c34ba6c` (`feat add active candidate admission record correspondence verification v1`) publicados; no hay cambios de código pendientes. Este cierre documental se prepara localmente y queda pendiente de su propio commit/publicación.

`verify_active_candidate_admission_record_correspondence(...)` consume exclusivamente `ActiveCandidateSourceAdmissionRecordAcquisition` B41 y devuelve `ActiveCandidateSourceAdmissionRecordCorrespondenceVerification` frozen, conservando exactamente el mismo aggregate B41. Para cada entry exige `admission_record.admission_id == membership.admission_id` y `admission_record.identity == membership.identity` como igualdad completa de unit, revision, payload schema y digest. Es in-memory, preserva orden B41/manifest, es all-or-nothing y admite vacío válido; no relee bytes/paths, no reconstruye record/candidate, no recalcula identity ni ejecuta B33.

B39 prueba candidate bytes → identity == membership; B42 prueba record identity == membership. Por transitividad, el record adquirido declara la identity verificada por B39 para esos candidate bytes. Esto es solo correspondence: `rejected` con ID e identity correctos pasa B42. Correspondence ≠ admitted decision ≠ gates actuales/históricos ≠ reviewer/record/timestamp authenticity ≠ candidate_revision provenance ≠ recursos ≠ active source integrity ≠ loader readiness. Validación: 9 específicas PASS en 0.13 s; regresión B31–B42, 150 passed en 0.48 s; suite backend completa, 1966 passed en 16.94 s; `git diff --check` PASS; postflights contractual y técnico PASS sin findings. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`. Routing: preflight `Sol / high`; contrato/implementación `Terra / medium`; postflights `Terra / high`.

## Bloque activo

### Cierre documental de Slice 42

Estado: preparación local de este cierre documental; no hay bloque funcional/técnico adicional activo. El microbloque tooling `git_close.py --publish-url` v1 permanece cerrado y publicado, sin relación con admission, source integrity o loader.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación, validación específica, revisión independiente y cierre documental. No repetir inspecciones ni validaciones ya confirmadas mientras no cambien los archivos cubiertos. Operar con Codex CLI + Bash; si una regresión en Codex queda indeterminada, ejecutarla una sola vez directamente en Bash. La suite backend completa se ejecuta directamente en Bash cuando corresponde.

Antes de cambiar de conversación: actualizar este documento, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar solo con checkpoint válido. Al reanudar: usar `conversation_checkpoint.py resume` antes de proponer comandos, inspecciones o cambios.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ active source snapshot ≠ representación física ≠ compatibilidad curricular autoritativa;
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ AdmissionRecord correspondence ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B42, reevaluar las reglas actuales de admission gates usando exclusivamente candidate bytes preservados, AdmissionRecord adquirido/correspondido y contratos B33/validation. No se diseña ni numera aquí ese bloque posterior ni se afirma historical gate execution; después seguirán pendientes recursos físicos, active source integrity y loader. `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

## Archivos clave

- `docs/estado-operativo.md` y `docs/bitacora.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `scripts/engineering/git_close.py`;
- `tests/test_git_close.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_candidate_admission_record_document.py`;
- `app/services/pedagogical_active_candidate_admission_record_acquisition.py`;
- `app/services/pedagogical_active_candidate_admission_record_correspondence.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `tests/test_pedagogical_active_candidate_admission_record_acquisition.py`;
- `tests/test_pedagogical_active_candidate_admission_record_correspondence.py`;
- `app/services/pedagogical_validation_service.py`.
