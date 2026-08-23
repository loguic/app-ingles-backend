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

### Local active candidate AdmissionRecord acquisition v1 — Slice 41

Estado técnico: contrato e implementación **CERRADOS / PUBLICADOS / SINCRONIZADOS**. Contrato `f07e3cfc3cac17ad507fc398b227cbb07e30cebd` (`docs define local active candidate admission record acquisition v1`) e implementación `2defc1b95508f0e61b95a05e2908c7684a7449ce` (`feat add local active candidate admission record acquisition v1`) publicados; no hay cambios de código pendientes. Este cierre documental se prepara localmente y queda pendiente de su propio commit/publicación.

`acquire_active_candidate_admission_records(...)` consume `ActiveCandidateSourceCandidateIntegrityVerification` B39 y bindings explícitos `admission_id -> document_path`; añade `ActiveCandidateAdmissionRecordBinding`, `AcquiredActiveCandidateAdmissionRecordEntry` y `ActiveCandidateSourceAdmissionRecordAcquisition` frozen. Adquiere exactamente un `AdmissionRecordDocumentV1` B40 por membership como `admission records acquired / unverified`: paths absolutos caller-provided, regulares y no symlink; read-once binario; UTF-8 sin BOM, JSON estricto, duplicate keys y constantes no estándar rechazadas; shape/schema B40, timestamp `YYYY-MM-DDTHH:MM:SS.ffffffZ`, reconstrucción bytes → `CandidatePayloadIdentity` → `AdmissionRecord` y byte-conformance con el serializer B40. `payload_schema_version` permanece metadata declarada/no verificada; `admitted` y `rejected` son adquiribles; entradas en orden B39/manifest, all-or-nothing y vacío válido.

La exact allowlist rechaza duplicate/missing/unexpected `admission_id` y duplicate `Path` por igualdad directa antes de todo I/O documental. El primer postflight detectó missing tardío; la corrección completa allowlist → PASS → filesystem acquisition, y el test con dos memberships intercepta `Path.open` y exige `opened_paths == []`. Validación: 16 específicas PASS en 0.14 s; regresión B31–B41, 141 passed en 0.44 s; suite backend completa, 1957 passed en 17.36 s; `git diff --check` PASS; postflight contractual PASS; primer postflight técnico corregido y re-postflight PASS, sin BLOCKING restantes. Permanecen gaps NONBLOCKING de cobertura directa para duplicate keys anidadas adicionales, `Infinity`/`-Infinity` y variantes timestamp; la lógica genérica fue revisada y los rechaza.

Admission record acquired / unverified ≠ membership correspondence ≠ admitted decision/gates ≠ provenance ≠ reviewer authenticity ≠ resource integrity ≠ active source integrity ≠ loader readiness. B41 no compara record↔membership, no reejecuta gates/B39, no relee candidate/manifest, no toca recursos, source integrity ni loader. Etapas posteriores consumen B39 + membership + `admission_record_bytes` + record reconstruido sin reabrir paths. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`. Routing: preflight `Sol / high`; contrato/implementación/corrección `Terra / medium`; postflights `Terra / high`.

## Bloque activo

### Cierre documental de Slice 41

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
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B41, comprobar la correspondencia entre AdmissionRecord adquiridos y memberships, y reejecutar gates usando exclusivamente la evidencia candidate preservada. No se diseña ni numera aquí ese bloque posterior ni se afirma provenance fuerte; después seguirán pendientes recursos físicos, active source integrity y loader. Las etapas posteriores consumen B39 + membership + `admission_record_bytes` + record reconstruido sin reabrir paths. `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `tests/test_pedagogical_active_candidate_admission_record_acquisition.py`;
- `app/services/pedagogical_validation_service.py`.
