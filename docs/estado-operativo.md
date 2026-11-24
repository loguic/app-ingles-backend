# Estado operativo — LOGUIC English

Actualizado: 2026-11-24T03:09:06+01:00
Baseline Git previa a este checkpoint: d00712c1a8c968982bbb79980a0189d635673565
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Autoridad semántica durable: este documento; Git vivo se obtiene únicamente mediante inspección read-only de `conversation_checkpoint.py`.
- Método vigente: `docs/loguic-engineering-operating-method-v1.md`; routing default `Terra / medium`.
- El historial de cierres y decisiones permanece en `docs/bitacora.md`, `docs/roadmap.md` y Git publicado.

## Último bloque cerrado

Último cierre técnico acreditado: RECOVERY-IDLE-FAIL-CLOSED-2026-11-23 — CLOSED / PUBLISHED / SYNCED. F0 conserva su cierre histórico en el roadmap.


`A1-V4-REAL-VERTICAL-SLICE`: **CLOSED / PUBLISHED / SYNCED** por este Closure Gate. El milestone de tres turnos —producción propia de agua → agua con menor apoyo → transferencia cercana a comida— queda satisfecho y publicado en backend y frontend; el frontend se publicó en `36f12735006db893a701a10825edc8281dc617fa`.

El postflight final acreditó **19 PASS / 5 skipped**, `git diff --check` PASS, estado operativo PASS, checkpoint PASS y `UNEXPECTED_FILES = NONE`. Qwen runtime/provenance `qwen3:8b` permanece evidencia PASS existente, sin repetición. Loader/runtime pointer/B181/mastery/progreso/completion y cambios a `content/content_tree.json` siguen no autorizados.

`Development Supervisor v1` queda **CLOSED / PUBLISHED / SYNCED** en `0349fa8d3928c98a83de0449b49d4dc5a8146c64` (`fix close development supervisor v1 routing and continuity`). El Closure Gate acreditó 14 tests PASS, block-close PASS, git-close PASS y checkpoint-prepare PASS, con árbol limpio y sincronizado.

`Mission Control V2` queda **CLOSED / PUBLISHED / SYNCED**: `loguic.py progress` es read-only sobre matriz V0 de 24 entregables y 8 resultados; MVP sigue **NO MEDIBLE**, sin acreditación pedagógica nueva. Evidencia: 10 tests focales PASS y `git diff --check` PASS; NEXT del Constructor IA se conserva.

La consolidación documental de decisiones iniciales del MVP Pre-A1 + A1 quedó publicada y sincronizada en `d10a99a9f17ffc29fe34308b0398975096b04a88`.

La publicación de BASELINE V0 quedó recuperada y sincronizada en `90bf9e780124b2dc1ffc43c4526e83aedf215af4`. La ejecución original del Closure
Gate falló durante `git_close` al hacer push por error DNS de resolución de
`github.com`, después de crear el commit local. Posteriormente se publicó el
commit existente con `git push origin master` y
`conversation_checkpoint.py prepare` terminó PASS, CLEAN y SYNCED. Esto no reclasifica retrospectivamente la ejecución original como Closure Gate PASS.

## Bloque activo
Sin incremento técnico abierto. STARTUP_RULE=LOGUIC-COMPACT-STARTUP-GATE-2026-11-24 (STATUS/DETAIL/NEXT; COPY START/END; logs locales; no repetir evidencias; método canónico). Corrección adaptativa A1 v4: **CLOSED / PUBLISHED / SYNCED**. BE `3a0a666c793ebbee6d5f65804ad55152ed460846`; FE `092b575ee61e8977bc5b314f9aecbac1467bce78`. Primera transición anchors → initial_word validada en Flutter con BE y Qwen. Documentos de cierre: `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`. A1 v4 sigue siendo demo no curricular. A1-V4-PRACTICE-PERSISTENCE-2026-11-23: **CLOSED / PUBLISHED / SYNCED** (BE `222d7d20a7e6a748fd90f23c733619c63fbef5bb`, FE `232be242703b366ff3d4c415ac4dc68bc0072fb0`); persistencia PostgreSQL, tres WAV, concurrencia y validación Flutter PASS; sin mastery/completion. Estación NOT CLOSED; MB1 DRAFT / NOT ACTIVE; MVP NO MEDIBLE.
Reconciliación documental F1 publicada en 53de563e; Git CLEAN / SYNCED. Checkpoint prepare pendiente; F1 integral NOT CLOSED.
BASELINE V0 del MVP: **PUBLISHED / SYNCED** tras recuperación de publicación.
Measurement V1 está documentada y sus cinco decisiones metodológicas fueron
aprobadas humanamente. La Accreditation Matrix V1 queda aprobada humanamente
en sus 24 criterios funcionales, ocho distribuciones internas de pesos,
funciones responsables, política de evidencia, condiciones de acreditación y
entradas económicas necesarias. No implica cumplimiento ni acreditación nueva:
faltan protocolos, umbrales observables, responsables nominales, evidencia
representativa y aplicación individual. Ningún incremento técnico está
autorizado.

Por decisión humana confirmada, la prioridad operativa pasa a materializar la
experiencia pedagógica renovada del MVP Pre-A1 + A1 inicial conforme al Modelo
Pedagógico Maestro. Debe desarrollar comprensión, construcción directa en
inglés, producción oral, feedback útil, interacción, transferencia y
recuperación como capacidades observables. Accreditation Matrix V1 permanece
vigente como instrumento de verificación, sin desplazar la construcción del
producto ni acreditar entregables individualmente.

Human Authority aprobó cuatro condiciones observables V1 para los entregables
3.1, 5.3, 6.1 y 7.2: recuperar audio propio tras interrupción controlada;
aplicar una orientación en un reintento con menor apoyo; expresar una necesidad
diferente con pertinencia e inteligibilidad según revisión humana; y distinguir
escucha, grabación y evaluación para repetir o continuar sin ayuda imprevista.
Se reutiliza la evidencia histórica de BASELINE V0 y A1-V4-REAL-VERTICAL-SLICE
(audio/producción/reproducción, feedback adaptativo, `water → food`, cierre 19
PASS / 5 skipped y revisión visual de grabación/reproducción). Las condiciones
no añaden umbrales numéricos ni acreditan individualmente los cuatro
entregables; permanecen pendientes protocolos, responsables nominales,
evidencia representativa y aplicación individual.

Human Gate 1 de MB1 queda **APPROVED**. MB1 — «Comprender y expresar una
necesidad» — pertenece a Fase 1, entrada Pre-A1 hacia A1 inicial. La capacidad
aprobada es comprender una situación cotidiana, construir directamente en
inglés una petición sencilla y expresarla oralmente con pertinencia e
inteligibilidad funcional. La experiencia aprobada es comprender → descubrir →
construir → hablar → recibir orientación → reintentar → transferir; evidencia:
producción oral, apoyos, respuesta a corrección y transferencia; recuperación
posterior en otro contexto y sin modelo completo. A1 v4 sigue siendo demo
histórica y no la entrada curricular definitiva. MB1 DRAFT CIERRE-02: 9 archivos preservados; Integración master 2026-11-17: backend e60d3f8 y frontend ae4a3d4, CLEAN/SYNCED; 48 archivos originales preservados en ZIP y stashes. CIERRE-04 demo interna: backend 2 pruebas PASS, Flutter analyze y widget tests PASS, recovery frontend ae4a3d42107d; sin Human Review visual ni conexión Flutter-FastAPI. CIERRE-03 recurso MB1: imagen SHA-256 302873df04d41ac4d6a80bd0a21369d040a8c5bc18ee1ad2e30cc5d5eef0aeb9 y 2 adaptadores parametrizados con 53 tests PASS tras aislar fixture legacy A1; contenido local, sin manifest de publicación, binding curricular, admisión ni activación. Entry-point legacy A1 requiere marcadores históricos ausentes en estado vivo; no se declara reparado. 42 tests PASS con DB aislada; postflight de paquete PASS; sin admisión, activación, Qwen ni acreditación humana.

Documentación recuperada (histórico): `docs/bitacora.md`, `docs/estado-operativo.md`, `docs/roadmap.md`, `docs/loguic-english-cierre-04-demostracion-recuperacion.md`, `docs/loguic-english-uiux-design-review-v1-decision-2026-11-16.md`, `docs/loguic-english-weekly-goals-v1-decision-2026-11-16.md`.
Backend recuperado (histórico): `app/schemas/internal_station_demo.py`, `app/services/internal_station_demo_content_service.py`, `content/internal_demo/station_situations.v1.json`, `docs/bitacora.md`, `docs/estado-operativo.md`, `docs/loguic-english-cierre-04-demostracion-recuperacion.md`, `docs/loguic-english-uiux-design-review-v1-decision-2026-11-16.md`, `docs/loguic-english-weekly-goals-v1-decision-2026-11-16.md`, `docs/roadmap.md`, `tests/test_internal_station_demo_content.py`.

### AI CONSTRUCTOR INTEGRATION V1

Estado anterior: IMPLEMENTED / LOCAL / NOT CLOSED / NOT PUBLISHED. Corrección CIERRE-01: PUBLISHED/SYNCED exclusivamente en recovery/cierre-01-constructor, commit 9d67d178; checkpoint de recuperación pendiente; MB1 DRAFT; sin fusión a master.
Autorizado: generación pedagógica IA con Ollama/Qwen3:8b,
reutilizando contratos y validadores existentes.
Implementación: dos fases locales —grafo de contenido y vínculos pedagógicos
sobre IDs existentes— con ensamblado determinista antes de Pydantic.
Correcciones: Fase 1 exige LessonExperience 3.0 para A1-U1 cuando la
especificación lo exige; relevance/intelligibility exigen production_function
válida (guided, expanded o transfer). Pruebas: `jsonschema==4.25.1`.
Ejecuciones Qwen: primer intento agotó timeout de 30 s; el segundo generó grafo y Pydantic rechazó cuatro requisitos cualitativos incompletos. No existe candidato MB1 acreditado. Postflight: 28 focales PASS, 101 y 126 regresiones PASS, BLOCKING=0 y resultado CONDITIONAL.
Verificación aislada: REQUEST_COUNT=1 con `qwen3:8b`, OLLAMA_SCHEMA_ACCEPTANCE=PASS, RESPONSE_VALIDATION=PASS y CONDITIONAL_ENFORCEMENT=UNVERIFIED.
CANONICAL RESUME V1: `python3 scripts/engineering/loguic.py resume` es read-only; backend/frontend, incremento vigente, restricciones, NEXT y routing recuperan PASS. Evidencia autorizada: 21 tests PASS, preflight `block_close.py` PASS y `git diff --check` PASS.
Incidencia preexistente separada: `test_a1_v4_expected_resource_identity_document_is_source_bound_and_complete` exige `A1 ASSET STATE:` ausente también en HEAD; no se declara suite completa PASS.
NEXT: cualquier nueva inferencia o verificación adversarial del condicional
requiere autorización humana; no ejecutar Qwen antes de ella.
Restricciones: no activar/publicar currículo ni iniciar otro incremento.

No activar ni publicar A1: loader/runtime pointer permanecen no autorizados; no modificar `content/content_tree.json`; no iniciar B181, human review, adjudicación, winner, mastery, progreso ni completion.
## Automatización disponible

- `scripts/engineering/validation_recipe.py approved-v1` ejecuta, en orden y fail-closed, pytest con rutas explícitas, `git diff --check`, `operational_state.py validate` y `conversation_checkpoint.py prepare --format compact`; no cierra Git.

## Método operativo vigente

Git real es autoridad exclusiva para hechos vivos; este documento conserva continuidad semántica y baseline previa validable. Las operaciones deterministas usan la receta approved-v1.

## Fronteras obligatorias

- La baseline Git debe corresponder al contrato del checkpoint según el estado local; evidencia no equivale a progreso, mastery ni finalización curricular.
- No iniciar human review, adjudicación, B52, loader, runtime o B181 sin autorización y evidencia específicas.

## Próximo objetivo

NEXT = F1: teclado y escalado de texto PASS; evaluar requisitos integrales WCAG AA y recorrido Inicio-Estación reutilizando evidencias existentes; determinar alcance de segunda ilustración. F2 mediante Human Gate. MB1 DRAFT / NOT ACTIVE; MVP NO MEDIBLE.

## Decisiones pedagógicas y comerciales consolidadas

El primer MVP se encuadra provisionalmente en Pre-A1 + A1 inicial, dentro de
la visión Pre-A1 hasta C2; Pre-A1 no es todavía un nivel curricular
independiente aprobado definitivamente. La matriz provisional es: 15 %
Pre-A1/diagnóstico, 20 % experiencias A1, 15 % escucha-habla-pronunciación,
15 % tutor adaptativo, 10 % feedback, 10 % transferencia-retención, 10 %
experiencia-accesibilidad y 5 % preparación para lanzamiento.

El seguimiento distingue avance acreditado del producto, avance técnico
aprovechable, coste y esfuerzo económico, y confianza de las estimaciones.
Siguen pendientes de validación el desglose provisional de 24 entregables,
criterios de aceptación, horas/costes, escenarios/precios, auditoría de
reutilización técnica y recomendaciones condicionadas sobre repositorios.

Los hallazgos A1 V4 incluyen dificultad con instrucciones iniciales, confusión
entre grabación, reconocimiento y feedback, “Great job!” sin comprobación
necesaria del resultado evaluado y necesidad de revisión para principiantes.
La publicación técnica del vertical slice no acredita por sí sola aprendizaje
humano.

## Archivos clave

`docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `scripts/engineering/operational_state.py`, `scripts/engineering/validation_recipe.py` y `scripts/engineering/conversation_checkpoint.py`; `docs/loguic-engineering-operating-method-v1.md`.
