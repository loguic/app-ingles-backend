# Estado operativo — LOGUIC English

Actualizado: 2026-08-22
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Physical AdmissionRecord document and atomic local publication v1 — Slice 40

Estado técnico: contrato e implementación **CERRADOS / PUBLICADOS / SINCRONIZADOS**. Contrato `60bb2693540f826ed15fd2e5562a74b7e016b705` (`docs define physical admission record document v1`) e implementación `f4a3eda438c85d1535de7837509656d6bed940e2` (`feat add physical admission record document v1`) publicados; no hay cambios de código pendientes. Este cierre documental se prepara localmente y queda pendiente de su propio commit/publicación.

`ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION = "1.0"`, `serialize_candidate_admission_record_document(...)` y `publish_candidate_admission_record_document(...)` representan/publican un `AdmissionRecord` sin crear otro domain model. El JSON ordenado contiene `document_schema_version`, `admission_id`, identity, decision, reviewer y `decided_at`; la identity se preserva literalmente, `admitted` y `rejected` son serializables, y el timestamp UTC se emite como `YYYY-MM-DDTHH:MM:SS.ffffffZ`. Los bytes usan UTF-8 sin BOM, `ensure_ascii=False`, separators compactos, `sort_keys=False`, `allow_nan=False` y newline final; no existe digest propio de documento.

`document_path` es absoluto y caller-provided; exige parent existente/directorio y target inexistente o regular, rechazando symlink, directorio y no-regular. La publicación serializa antes de filesystem y sigue temp en mismo parent → write/flush/fsync(temp) → close → `os.replace` → fsync(parent). Soporta publicación inicial y replacement; un fallo pre-replace conserva S1 y cleanup best-effort no oculta el error primario. Tras fallo de fsync(parent), S2 puede estar visible sin durabilidad confirmada, sin rollback, segundo replace ni retry.

Physical AdmissionRecord document ≠ admission provenance ≠ reviewer/decision authenticity ≠ candidate_revision provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource integrity ≠ active source integrity ≠ loader readiness. B40 no adquiere ni parsea records, no rerun de gates, no enlaza memberships, no usa B39/candidate bytes, no toca recursos, source integrity ni loader. Threat model: POSIX/Linux local, caller controlado, single writer y parent no adversarial. Validación: 8 específicas PASS en 0.11 s; regresión B31–B40, 125 passed en 0.39 s; suite backend completa, 1941 passed en 16.87 s; `git diff --check` PASS; postflight PASS sin findings BLOCKING/NONBLOCKING. Routing: preflight `Sol / high`; contrato/implementación `Terra / medium`; postflights `Terra / high`.

A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

### Cierre documental de Slice 40

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
- physical AdmissionRecord document ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B40, adquirir explícitamente AdmissionRecord documents publicados y comprobar su correspondencia con memberships y gates usando la evidencia candidate ya preservada/verificada. No se diseña ni numera aquí ese bloque posterior; después seguirán pendientes recursos físicos, active source integrity y loader. `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `app/services/pedagogical_validation_service.py`.
