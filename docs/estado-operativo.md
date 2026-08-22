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

### Candidate integrity verification from acquired evidence v1 — Slice 39

Estado: contrato e implementación **CERRADOS / PUBLICADOS / SINCRONIZADOS**. Contrato `bf7f966662cf87283f05c5f510be95a351c0ee13` (`docs define candidate payload integrity verification v1`) e implementación `151673d2e266617012f741705bf287c9a2ea2ff7` (`feat add candidate payload integrity verification v1`) publicados; no hay cambios de código pendientes. Este cierre documental se prepara localmente y queda pendiente de su propio commit/publicación.

`verify_active_candidate_source_candidate_integrity(...)` consume `ActiveCandidateSourceAcquisition` y produce `CandidatePayloadIntegrityVerification` / `ActiveCandidateSourceCandidateIntegrityVerification` frozen: reconstruye un candidate desde `candidate_bytes`, reutiliza B31 y exige `derived_identity == membership.identity`. `candidate_bytes` son la evidencia autoritativa; no confía en `entry.candidate` mutable, no relee filesystem ni `candidate_path`, preserva orden del manifest, admite vacío y es all-or-nothing. Solo `payload_schema_version="1.0"` es soportada; una versión distinta falla antes de derivar. `candidate_revision` se transmite literalmente desde la membership, sin demostrar provenance desde bytes.

Candidate payload integrity verified ≠ active source integrity verified ≠ loader readiness. `content_digest` sigue siendo el digest del payload lógico canónico B31 de siete campos, no un hash raw; `required_resource_ids` participa lógicamente sin adquirir ni verificar recursos. No hay `AdmissionRecord` lookup ni rerun de gates. Las etapas futuras consumirán `candidate_bytes` + derived identity + membership, sin confiar en el candidate mutable ni reabrir `candidate_path` para volver a demostrar payload integrity.

Postflight técnico final PASS, sin findings BLOCKING ni NONBLOCKING. El finding inicial de bytes authority se cerró al mutar `entry.candidate.specification.title`, campo canónico B31; el recheck confirmó que los bytes son materialmente la autoridad. Validación: 15 específicas PASS en 0.15 s; regresión B31–B39, 117 passed en 0.36 s; suite backend completa, 1933 passed en 16.87 s; `git diff --check` PASS. Routing: preflight `Sol / high`; contrato/implementación/corrección `Terra / medium`; postflights `Terra / high`.

A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

### Microbloque tooling — `git_close.py --publish-url` v1

Estado: técnicamente cerrado y publicado. Microcontrato `ead2422` (`docs define git close publish url contract`) e implementación `da13cb96a32a549b0a57f559be50f4415d67f47d` (`feat add git close publish url`), publicada mediante el propio helper; este commit es el checkpoint técnico sincronizado previo al cierre documental actual, no un HEAD permanente.

`--publish-url <https-url>` es opcional, explícito y HTTPS-only. `--upstream` mantiene la referencia canónica local; la URL es transporte alternativo caller-provided, sin modificar `origin`, upstream ni `.git/config`. Valida URL absoluta, hostname, ausencia de userinfo/query/fragment/whitespace/control y puerto válido; compara OID del ref remoto con upstream antes del commit, verifica `HEAD` tras push y actualiza la tracking ref por fetch explícito. OID equality acredita coherencia del branch, no identidad criptográfica del repositorio. Usa argv/shell=False, push non-force y redacción del destino en diagnósticos alternativos.

Sin `--publish-url`, el flujo v1 anterior permanece. Uso recomendado: `git_close.py` normal cuando `origin` funciona; `git_close.py --publish-url <https-url>` solo cuando el usuario necesita transporte HTTPS explícito. No hay fallback SSH→HTTPS, retry, rollback, segundo push, `set-upstream`, `remote set-url` ni configuración persistente. Push fallido produce `PUSH_FAILED` y conserva commit local; fallo posterior a publicación posible produce `FINAL_SYNC_FAILED` con `the commit may already be published remotely`, sin revertir. El uso real generó `da13cb96a32a549b0a57f559be50f4415d67f47d` y completó precheck → stage exacto → verify → commit → push HTTPS → actualización de `origin/master` → clean/sync final, sin `git push`, `git fetch` ni `git status` manual posterior. Este microbloque no es slice 38 ni modifica source integrity, acquisition o loader.

Validación: 41 directas PASS en 3.37 s; postflight técnico final PASS sin findings BLOCKING/NONBLOCKING; regresión tooling 88 passed en 3.78 s; suite backend completa 1904 passed en 16.64 s; `git diff --check` PASS.

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
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B39, integrar candidate payload integrity verificada con las demás evidencias necesarias antes de poder afirmar active source integrity y habilitar posteriormente un loader. No se diseña ni numera aquí ese bloque posterior; `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `app/services/pedagogical_validation_service.py`.
