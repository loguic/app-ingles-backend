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

### Local active candidate source acquisition v1 — Slice 38

Estado: contrato e implementación **CERRADOS / PUBLICADOS / SINCRONIZADOS**. Contrato `48b99340f6e9900b24956e67187aaece06468822` (`docs define local active candidate source acquisition v1`) e implementación `a6c96f816b9c960607b4ae85e272994ad31a2fe5` (`feat add local active candidate source acquisition v1`) publicados; no hay cambios técnicos pendientes. Este cierre documental se prepara localmente y queda pendiente de su propio commit/publicación.

`acquire_active_candidate_source(...)` compone manifest físico, bindings explícitos y lectura/parse de candidates en `ActiveCandidateSourceBinding`, `AcquiredActiveCandidateSourceEntry` y `ActiveCandidateSourceAcquisition`: paths absolutos caller-provided, sin symlinks, read-once, bindings exactos y entries en orden del manifest. El manifest exige UTF-8 sin BOM, JSON con duplicate keys rechazadas, shape/schema v1 estricto y byte-conformance exacta frente al serializer B37; cada candidate exige UTF-8 sin BOM, duplicate keys rechazadas y parse de `PedagogicalUnitCandidate`. El resultado exterior frozen preserva `candidate_bytes`, admite manifest vacío con bindings vacíos y es all-or-nothing.

La capacidad es `acquired / unverified`: acquired ≠ verified ≠ candidate identity verified ≠ digest verified ≠ source integrity ≠ loader readiness. No deriva `CandidatePayloadIdentity`, no verifica `content_digest`, no calcula hash raw, no adquiere `required_resource_ids` ni `AdmissionRecord` físico, no enumera filesystem, no usa red y no ejecuta loader. `payload_schema_version` no soportada se conserva como metadata unverified. La futura candidate integrity deberá consumir los `candidate_bytes` adquiridos, sin reabrir `candidate_path`; `content_digest` no es hash del archivo candidate raw.

Postflight técnico final PASS, sin findings BLOCKING ni NONBLOCKING. Validación: 14 específicas PASS en 0.15 s; regresión B31–B38, 102 passed en 0.33 s; suite backend completa, 1918 passed en 16.63 s; `git diff --check` PASS. Routing: preflight contractual `Sol / high`; implementación/correcciones `Terra / medium`; postflight `Terra / high`; Sol no fue necesario para el postflight final.

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

Tras publicar este cierre documental de B38, la siguiente frontera conceptual es candidate integrity verification sobre la evidencia adquirida: debe consumir `candidate_bytes` preservados sin reabrir `candidate_path`. No se declara B39 iniciada ni se diseña aquí; `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_validation_service.py`.
