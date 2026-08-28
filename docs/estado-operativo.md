# Estado operativo — LOGUIC English

Actualizado: 2026-08-28T09:55:13+02:00
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

### B52 — Active source integrity v1

Estado: **CERRADO / DOCUMENTADO / PUBLICADO / SINCRONIZADO**. Contrato publicado: `5d318c125acdc7128b0af73abafae0bee8c7b454`. Implementación técnica publicada: `605564ecbeb9079fef248d348ad26f52f042ca30`.

`ActiveCandidateSourceIntegrityVerification` frozen contiene exactamente B43 `current_admission_gate_reevaluation` y B51 `resource_integrity_verification`. `verify_active_candidate_source_integrity(...)` consume únicamente ambos aggregates y exige que sus rutas transitivas conserven exactamente el mismo B39 por identidad Python; no recibe B39 como tercer input ni alinea entries de dominios distintos.

B52 es positive-only, frozen y all-or-nothing. Un mismo B39 produce verification conservando B43+B51 por identidad; B39 distintos producen `ValueError("active source integrity causal source mismatch")` fail-closed, sin resultado parcial, status, findings ni pairs. Una source vacía común es positiva.

La garantía se limita a la conjunción causal sobre una misma source B39: candidate payload integrity B39, current admission gates B43 y expected-vs-observed resource integrity B51. B52 no reejecuta upstream, no usa filesystem, parsing, bytes, hashing o I/O y no acredita authenticity, provenance, chronology, corrección semántica/pedagógica, curriculum compatibility ni loader readiness.

Validación: 7 tests específicos PASS; regresión seleccionada B43+B51+B52, 29 PASS; postflight técnico independiente PASS; findings BLOCKING: 0; findings NONBLOCKING: 0; suite backend completa ejecutada directamente en Bash, 2118 passed en 17.49 s; `git diff --check` técnico PASS. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`.

### B43 — Active candidate current admission gate reevaluation v1

Estado técnico: **CERRADO / PUBLICADO** mediante `7427f2b78b7030883ec3e8b8cfff0d707d2ff0c4` (`feat add active candidate current admission gate reevaluation v1`). Contrato publicado: `287f2fcbfb40cf89c9af05ceb2790773dce17b76`. Este cierre documental queda local y pendiente de su propio commit/publicación.

`reevaluate_active_candidate_current_admission_gates(...)` consume exclusivamente B42 correspondence y, por cada entry alineada B39/B41, reconstruye un candidate efímero solo desde `candidate_bytes`, llama una vez a B33 y conserva `AdmissionGateVerification`. El aggregate frozen existe solo si los cuatro gates actuales verifican: identity, local validation, pending human decisions y decisión admitted. `identity_matches=False` tras B39+B42 es contradicción técnica fail-closed; rejected, pending decisions o validation no passed impiden resultado positivo sin crear resultado parcial. No hay reread de filesystem, manifest, candidate/document paths, red ni recursos.

La garantía es actual, no histórica: current admission gate reevaluation ≠ historical gate execution proof. B39 sigue siendo autoridad de candidate payload integrity y B42 de AdmissionRecord correspondence. B43 no acredita reviewer/decision/timestamp/record authenticity, candidate_revision provenance, recursos, active source integrity ni loader. B31 excluye del digest `validation_report`, `pending_human_decisions` y `proposed_change_summary`; B43 evalúa pending decisions presentes en los bytes completos preservados sin afirmar autenticidad histórica. Validación: 11 directas PASS en 0.21 s; regresión B31–B43 161 PASS en 0.52 s; suite backend 1991 PASS en 18.28 s; `git diff --check`, postflight contractual y postflight técnico PASS, sin findings BLOCKING ni NONBLOCKING materiales.

### B42.1 — Timestamp preciso del estado operativo

Estado técnico: **CERRADO / PUBLICADO** mediante `46020c1e91577dc4929298f3198ce3b91e54143e` (`feat add precise operational state timestamp`); este cierre documental queda local y pendiente de su propio commit/publicación. `Actualizado:` ahora exige fecha, hora y offset ISO 8601 (`YYYY-MM-DDTHH:MM:SS±HH:MM`), con comparación aware por instante; `OperationalStateReport` migró de `updated_on` a `updated_at`.

La validación usa `%cI` y compara contra HEAD, o contra HEAD^ cuando HEAD contiene este documento; un root que lo contiene no tiene baseline Git. Esto evita la autorreferencia del commit de cierre. `conversation_checkpoint.py` reutiliza el validador sin cambio productivo; `block_workflow.py` solo consume/imprime `updated_at`.

B42 permanece cerrado: `AdmissionRecord correspondence verified`; B43 posterior verificó los admission gates actuales sobre la evidencia preservada. Siguen unresolved historical admission gates, reviewer authenticity, candidate_revision provenance, resource integrity y active source integrity. Los postflights B42.1 cerraron dos findings BLOCKING; permanecen solo gaps de cobertura temporal/Git NONBLOCKING, sin fallo funcional observado. Validación: 45 tests de infraestructura PASS en 0.82 s; suite backend completa 1980 PASS en 17.66 s; `git diff --check` y validación real del estado PASS. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

### B183 — Checkpoint Visual Flutter: recorrido demo A1

Estado: **CERRADO / DOCUMENTADO / PUBLICADO / SINCRONIZADO**. Commit técnico frontend: `f49a0df4e308a6e22bdad53a087029fea0728a13`; commit documental: `9860b883304019733c959f58ef81f01352bde0f5`. Infraestructura Git segura frontend publicada en `004b0bdb281d9a29bc1a6550f091fd24047d2078`.

B183 ofrece un recorrido humano validado `Inicio → mapa A1–C2 → portada demo A1 → escucha/pronunciación → conversación breve → portada → mapa → Inicio`. La demo es estrictamente provisional bajo `demo-visual-*`; no define currículo A1, no usa `a1-u1-l1` como autoridad, presenta A1 como demo disponible y A2–C2 como horizonte neutral.

Validación final: humana PASS; `flutter analyze` sin issues; `flutter test` completo 51 passed; postflight 0 BLOCKING y 4 NONBLOCKING aceptados. B181 permanece **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. No se introducen progreso, mastery, evaluación pedagógica ni persistencia curricular inventados.

## Bloque activo

No hay bloque nuevo iniciado. La próxima decisión pendiente es determinar profesionalmente el siguiente bloque de LOGUIC English manteniendo B181 PAUSED y preservando el carácter provisional de la demo B183.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint con `Actualizado:` timezone-aware.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

El método completo y canónico está en `docs/loguic-engineering-operating-method-v1.md`. Este documento conserva únicamente el checkpoint operativo compacto.

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

## Próximo objetivo

Determinar el siguiente bloque sin asumir B184, loader ni currículo A1. La frontera técnica backend posterior continúa siendo un futuro loader consumidor de evidencia B52 positiva: `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member` y la compatibilidad curricular autoritativa sigue posterior.

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
