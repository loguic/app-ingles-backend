# LOGUIC English — Checkpoint de investigación arquitectónica A1 v4

**Fecha:** 2026-11-22  
**Estado:** DIAGNÓSTICO EN CURSO · SOLO EVIDENCIA · NO IMPLEMENTADO · NO PUBLICADO EN GIT  
**Dominio:** **Niveles → A1 v4 → «I need water»**, no Estación.  
**Propósito:** preservar pruebas ya realizadas, hechos, contradicciones y siguiente paso; impedir análisis circulares y parches sin diagnóstico.  
**Autoridad:** registro de investigación; **no sustituye** `docs/modelo-pedagogico-maestro.md`, `docs/estado-operativo.md`, `docs/roadmap.md` ni `docs/bitacora.md`.

## 1. Problema y objetivo verificable

Investigar el **error lógico** en la secuencia *escuchar → grabar → STT → evaluación semántica → corrección/feedback → decisión adaptativa → avance*, diferenciando comprensión, intención comunicativa, gramática y pronunciación. Determinar si el sistema puede transmitir mensajes contradictorios o avanzar sin evidencia suficiente; distinguir defectos presentes de incidencias históricas ya corregidas.

**Caso histórico:** el usuario recuerda haber pronunciado «kneed water»; la transcripción de Moonshine observada fue «I knee the water» (no confundir las dos fuentes). Qwen sugirió «I need water». En una ejecución Flutter mostró «Great job!» de modo contradictorio. La observación histórica **no demuestra** que el estado actual continúe mostrando esa frase.

## 2. FE — evidencia recuperada por inspección de código (sin pruebas nuevas)

- `lib/screens/a1_v4_visible_demo_screen.dart`: `_A1V4ComprehensionCheck` permite seleccionar una imagen y muestra `_A1V4SuccessFeedback` con «Correct!» únicamente para la selección visual correcta. **Es evaluación de comprensión independiente**, no evaluación oral.
- En el código actual bajo `lib/` no apareció el literal «Great job!»; `test/a1_v4_visible_demo_screen_test.dart` verifica en varias posiciones que **no** se muestre. Estas son pruebas existentes; no se reejecutaron aquí.
- `_A1V4FeedbackPanel` alrededor de la línea 2133 solo muestra un objetivo estático; **no** decide sobre la evaluación oral.
- La presentación oral utiliza `evaluation.conversationalFeedback` y `evaluation.rationale` y traduce `evaluation.nextAction` a instrucciones de siguiente actividad (aprox. líneas 1540–1648).
- `_A1V4OwnProductionState` llama a `widget.apiService.evaluateSpokenTurn` pasando `transcript`, `audioReference` opcional, `target`, `context`, `currentTurn`, `priorTurnEvidence` (aprox. 1022–1046).
- `lib/services/api_service.dart`: POST `spoken-turn-evaluations` con `transcript_source: stt` y campos anteriores; parsea `SpokenTurnEvaluation` (aprox. 42–74).
- `lib/models/spoken_turn_evaluation.dart` identifica resultado como *non-authoritative coaching*; contiene `semanticStatus`, `contextRelevant`, `rationale`, `conversationalFeedback`, `nextAction`, `nextSupportLevel`, comparación y procedencia, **no** dictamen fonético GOP/WavLM ni corrección gramatical estructurada.
- `_applyAdaptiveDecision` aplica `nextAction`: para `own-production` desbloquea soporte reducido al recibir `reduce_support`; para `lower-support-own-production` desbloquea transferencia con `continue` **o** `reduce_support` (aprox. 115–134). Es una dependencia funcional directa de la decisión recibida desde BE.

## 3. BE — evidencia recuperada por inspección de código

- Endpoint `app/api/v1/endpoints/spoken_turns.py`, esquema `app/schemas/spoken_turn.py`, servicio `app/services/spoken_turn_evaluation_service.py`.
- El prompt de `spoken_turn_evaluation_service.py` indica a Qwen que evalúe **significado comunicativo**, no coincidencia exacta de frase; que emita feedback y una decisión adaptativa; prohíbe mastery, completion, notas y progreso.
- `_normalize_cross_turn_improvement` deriva metadatos de comparación desde estados semánticos de turnos anteriores.
- `_cross_field_error` comprueba principalmente consistencia de comparación/mejora entre turnos. **En el fragmento revisado no comprueba que `conversational_feedback` corresponda a `semantic_evaluation.status`**, ni que las recomendaciones de avance concuerden con el mensaje.
- `_apply_pedagogical_transition_guard` transforma `reduce_support` en `retry_with_support` cuando el estado semántico no es `adequate`; **no** bloquea explícitamente `continue` con estado `needs_repair`.
- `evaluate_spoken_turn` produce respuesta desde el modelo, normaliza comparación, corrige inconsistencias de comparación mediante un segundo intento de Qwen, aplica el guard y devuelve por separado evaluación semántica, feedback y decisión de siguiente turno.

## 4. Cobertura de pruebas encontrada — hallazgo decisivo

Archivos existentes: `tests/test_spoken_turn_evaluation_service.py` y `tests/test_spoken_turns.py`.

La búsqueda de casos localizó en `tests/test_spoken_turn_evaluation_service.py`:

- **Línea ~184:** `test_needs_repair_cannot_reduce_support_without_rewriting_semantics`.
- **Líneas ~201, 205:** `result.semantic_evaluation.status == "needs_repair"` y `result.next_turn.action == "retry_with_support"`.
- **Línea ~207:** `result.conversational_feedback == "Good. Your request is clear."`.

**Hallazgo confirmado al nivel de las aserciones existentes:** un caso de prueba exige mantener simultáneamente `needs_repair`, `retry_with_support` y un mensaje favorable. Eso evidencia una **separación no conciliada entre estado, feedback y transición** en ese escenario simulado. **Todavía no se ha leído el cuerpo completo de la prueba ni acreditado una ejecución nueva**; no se debe equiparar automáticamente con la salida «Great job!» histórica.

Otra brecha potencial identificada: al combinar la guarda BE que solo bloquea `reduce_support` con el desbloqueo FE por `continue` en el segundo turno, podría ser posible avanzar tras `needs_repair`; **pendiente de comprobar restricciones adicionales del contrato, pruebas y el código completo**.

## 5. Diagnóstico provisional (sin refactorización autorizada)

**Evidencia fuerte:** la decisión adaptativa y el texto del coaching se generan/transportan como campos separados; existe protección parcial para reducción de apoyo, pero no se ha visto una invariante integral que haga coherentes *estado semántico + texto + siguiente acción + evidencia fonética*. Que se comprenda la intención **no demuestra** buena pronunciación.

**Hipótesis arquitectónica:** falta definir y hacer cumplir una política única de decisión pedagógica según el objetivo y las evidencias disponibles. No presupone que haya que reemplazar Qwen, Flutter, STT ni el motor fonético.

**Patrones candidatos (no aprobados):** State Machine para flujo y estados; Ports & Adapters para aislar STT/TTS/IA/GOP; un componente de decisión/orquestación para invariantes; Strategy para políticas según objetivo. Elegir **solo** el patrón necesario tras terminar el diagnóstico y el contrato.

## 6. Próximo paso único, sin repetir pruebas

Leer íntegramente **`tests/test_spoken_turn_evaluation_service.py` alrededor de líneas 175–215**, para verificar preparación del caso, resultado esperado e intención de preservar feedback. Después comprobar restricciones del schema para `continue` con `needs_repair`. **No editar código ni correr audio, Ollama o Flutter** durante esta inspección. Cerrar el diagnóstico antes de iniciar refactor o redactar una skill genérica.

## 7. Continuidad y límites

- No confundir **Niveles A1 v4** con Estación. ISSUE_2 de audio de Estación fue publicado previamente en FE `c431c3534f34307726ecdf3f4e77da15541befbd`, pero no declara Estación completa cerrada.
- Cambios posteriores de A1 v4 en FE están preservados localmente y pendientes de revisión humana y publicación; **no sobrescribirlos**.
- Estado BE observado antes de este registro: `conversation_checkpoint.py prepare --format compact` devolvió `CHECKPOINT_STATUS=PASS`, `TREE=DIRTY`, `HEAD=f4cd7acafc92090c05a58f5a70fef99897281de2`; la actualización local de metadatos de `docs/estado-operativo.md` no estaba publicada. **PASS de compatibilidad no equivale a Closure Gate Git limpio/sincronizado.**
- Este documento descargable **no está todavía incorporado al repositorio**; solo será canónico cuando se revise, se integre sin crear autoridad paralela y se publique por el método aprobado.
- Objetivo dual de LOGUIC English: entregar el entrenador de inglés y servir como proyecto piloto de prácticas de ingeniería reutilizables en LOGUIC Labs. La eventual skill de diseño transversal pertenece a gobernanza LOGUIC OS; no crearla como sustituto del diagnóstico.

**Criterio de cierre de investigación:** mapa FE→BE completo, contradicción verificada o descartada, contrato/invariante faltante identificado, cobertura de pruebas conocida y recomendación arquitectónica mínima. Si no hay evidencia suficiente, registrar `BLOCKED` con causa exacta, sin inventar resolución.

## Causa histórica confirmada — Great job

Estado: CONFIRMED / HISTORICAL / FE.

Evidencia: commit FE `36f1273` (2026-10-11).

En `_A1V4FeedbackPanel`, el estado `received` se calculaba
mediante `evaluation != null`.

El encabezado mostraba `Great job!` cuando `received`
era verdadero, sin exigir un resultado semántico adecuado.

Causa lógica demostrada:
se confundía la disponibilidad de una evaluación con
la aprobación pedagógica de la respuesta.

La implementación FE actual ya no contiene ese literal
en `lib/`, y existen pruebas de su ausencia.

Este hallazgo explica la posibilidad de la felicitación
histórica, sin demostrar que toda respuesta positiva
dinámica de Qwen sea correcta.

Problema independiente pendiente:
el Backend puede corregir `nextAction` conservando
un `conversational_feedback` potencialmente incoherente.

Siguiente objetivo:
cerrar el diagnóstico de coherencia entre evaluación,
feedback y avance en Niveles A1 v4.

No modificar código ni repetir pruebas de audio.

## Hallazgo confirmado — Coherencia de evaluación y avance

Estado: CONFIRMED / STATIC CONTRACT ANALYSIS / BE.

Fuentes examinadas:
- `app/schemas/spoken_turn.py`
- `app/services/spoken_turn_evaluation_service.py`
- `app/api/v1/endpoints/spoken_turns.py`
- `tests/test_spoken_turn_evaluation_service.py`
- Contrato y decisiones adaptativas del Frontend A1 v4.

Hallazgo 1:
El contrato admite `needs_repair` y `continue`,
sin una restricción conjunta que prohíba esa combinación.

Hallazgo 2:
La protección pedagógica examinada corrige
`needs_repair` + `reduce_support` hacia
`retry_with_support`, pero no bloquea explícitamente
`needs_repair` + `continue`.

Hallazgo 3:
Una prueba existente confirma que el Backend puede
conservar un feedback positivo mientras modifica
la decisión de avance para exigir repetición.

Hallazgo 4:
Flutter utiliza la acción del Backend para desbloquear
la siguiente actividad. El contrato es no autoritativo
respecto a mastery y completion; esa limitación no
elimina el riesgo de navegación pedagógica incoherente.

Límite de evidencia:
Se demuestra una brecha contractual mediante análisis
estático. No se afirma reproducción real de todas las
combinaciones ni evaluación fonética mediante GOP/WavLM.

Hipótesis arquitectónica:
Evaluar una Pedagogical Decision Policy que compruebe
invariantes entre estado semántico, feedback y acción.
No implementar ni seleccionar patrones definitivamente
antes de revisar compatibilidad y criterios pedagógicos.

Estado del diagnóstico:
- Causa histórica Great job: CONFIRMED.
- Brecha de coherencia BE: CONFIRMED.
- Solución arquitectónica: PENDING DESIGN REVIEW.
- Pruebas nuevas: NOT EXECUTED.
- Cambios funcionales: NONE.

Próximo objetivo:
Definir una matriz explícita de decisiones permitidas,
rechazadas y pendientes de evidencia para A1 v4.

## Human Design Gate — Matriz V1 aprobada

Fecha: 2026-11-22.
Decisión humana: Opción 1 / APPROVED AS DESIGN BASE.

Alcance: evaluación semántica y decisión adaptativa
en Niveles A1 v4.

| Evaluación | Acción | Política propuesta |
|---|---|---|
| adequate | continue | Permitir |
| adequate | reduce_support | Permitir con evidencia |
| adequate | retry_with_support | Permitir con razón explícita |
| needs_repair | retry_with_support | Permitir |
| needs_repair | continue | Rechazar |
| needs_repair | reduce_support | Rechazar |
| No disponible | Cualquier avance | Bloquear avance |

La aprobación permite preparar el diseño, no implementar.

Restricciones:
- Contrastar con el Modelo Pedagógico Maestro.
- Preservar contratos y comportamientos existentes.
- Pronunciación y gramática son dimensiones independientes.
- No acreditar mastery, completion ni progreso.
- No utilizar búsquedas de palabras positivas como
  sustituto de evaluación estructurada.
- No modificar FE, BE funcional ni activar currículo.
- No autoriza commit ni push.

NEXT:
Revisión de compatibilidad pedagógica y arquitectónica.
Determinar si basta una política de decisión reutilizando
el servicio existente o si se justifica otro patrón.
Definir criterios de aceptación antes de implementar.

Capacidad transversal futura:
Skill experta en patrones de diseño para LOGUIC Labs,
bajo gobernanza de LOGUIC OS.

## Compatibilidad pedagógica y arquitectura mínima — V1

Fecha: 2026-11-22.
Estado: PEDAGOGICAL REVIEW COMPLETE / DESIGN PROPOSAL.
Implementación: NOT AUTHORIZED.

### Compatibilidad con el Modelo Pedagógico Maestro

Resultado: COMPATIBLE CON CONDICIONES.

Autoridades verificadas:
- Tres puertas humanas.
- Construcción directa en inglés.
- Retirada progresiva de apoyos.
- Corrección prioritaria.
- Pronunciación funcional transversal.
- Evidencia observable y transferencia.
- Regla anti-parche.

La continuidad de un turno no acredita dominio.
La evaluación semántica no acredita pronunciación.

### Diagnóstico lógico

FE histórico:
`evaluation != null` activaba `Great job!`
sin comprobar éxito pedagógico.

BE vigente:
la protección examinada impide reducir apoyo
con `needs_repair`, pero no bloquea explícitamente
`needs_repair` combinado con `continue`.

El feedback libre puede conservarse incluso
cuando la decisión adaptativa es corregida.

### Arquitectura mínima propuesta

Candidato: Pedagogical Decision Policy en BE.

Responsabilidades:
- Qwen: evaluación y orientación comunicativa.
- Policy: coherencia de decisiones estructuradas.
- Flutter: presentación sin felicitación automática.
- Evaluación fonética: evidencia independiente.

No modificar todavía contratos ni implementar patrones.

### Criterios de aceptación propuestos

- needs_repair + continue: no avanzar.
- needs_repair + reduce_support: no retirar apoyo.
- adequate + continue: permitir continuación.
- adequate + reduce_support: exigir evidencia.
- Evaluación ausente: no avanzar.
- Evaluación recibida: no equivale a éxito.
- Sin evaluación fonética: no afirmar pronunciación correcta.

No validar feedback mediante palabras positivas
aisladas; definir una representación estructurada
antes de implementar esa garantía.

### Fronteras y siguientes decisiones

La revisión pedagógica focalizada está completa.
La arquitectura es PROPUESTA / NOT APPROVED.

Pendiente:
- Contrato técnico mínimo y compatibilidad.
- Casos adversariales y pruebas de aceptación.
- Plan de implementación de Puerta 2.
- Human Gate correspondiente antes de código.

La integración fonética E2E sigue fuera de este
diagnóstico focalizado y no se declara resuelta.

Skill transversal de patrones de diseño:
candidata para LOGUIC OS, aún no implementada.

Documento local pendiente de versionado Git.

