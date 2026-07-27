# Estado operativo — App Inglés

Actualizado: 2026-07-27

## Fase actual

Fase 5 — Frontend y práctica conversacional.

## Último bloque cerrado

B128 — Reconocimiento de voz integrado en práctica conversacional.

Estado:
- implementado;
- validado manualmente en Flutter Linux;
- 37 pruebas frontend superadas;
- publicado en `origin/master`;
- frontend limpio y sincronizado.

Resultado real validado:
`Reconocido: Hello, I am John.`

## Bloque activo

B129 — Contrato trazable de evaluación de producciones personales — implementación técnica completada, pendiente de cierre Git/GitHub.

Objetivo aprobado:
crear contratos estáticos y runtime que permitan vincular una producción concreta con criterios evaluables y registrar posteriormente su resultado.

B129 no implementó:
- cálculo semántico;
- cálculo fonético;
- feedback adaptativo;
- mastery;
- retention;
- IA;
- publicación de contenido candidato.

## Secuencia vigente de Fase 5

1. Presentación de producciones personales en Flutter — completada.
2. Reconocimiento de voz y palabras — completado con B126–B128.
3. Evaluación semántica y fonética gradual — capacidad actual.
4. Retroalimentación pedagógica adaptativa.
5. Conversación libre.
6. Consolidación y comprobación diferida de retención por Skill.

## Contratos vigentes

- `Skill`: habilidad pedagógica medible del estudiante.
- `LessonExperience 2.0`: contrato pedagógico público vigente.
- `EvidenceDefinition`: definición estática de evidencia.
- `LearnerProduction`: producción capturada, nunca evaluación.
- `LearnerProductionRecord`: producción persistida y trazable.
- `SpeechRecognitionResult`: reconocimiento técnico, no evaluación.
- `contextual_response`: actualmente evidencia por `completion`, no corrección.
- `EvidenceRecord`: diseñado documentalmente, todavía no implementado como schema/runtime.

## Fronteras arquitectónicas

- reconocimiento, evaluación, persistencia e IA permanecen separados;
- `Lesson` y `ConversationTurn` no deben absorber lógica evaluativa;
- una grabación no demuestra pronunciación correcta;
- una transcripción reconocida no demuestra corrección semántica;
- una conversación completada no demuestra fluidez;
- ninguna evaluación implica automáticamente mastery o retention;
- `content/candidates/` permanece aislado del contenido activo hasta aprobación explícita.

## Hueco confirmado para B129

La candidata `a1-u1-l1` tiene tres prompts personales en `c3`:

- `p1`: decir un nombre;
- `p2`: indicar origen;
- `p3`: responder cortésmente.

La misión contiene esos tres criterios como texto, pero actualmente no existe una relación estructurada y estable:
`prompt -> criterio evaluable`.

B129 resolverá esa trazabilidad antes de introducir motores de evaluación.

## Diseño aprobado para B129

Nuevo módulo previsto:
`app/schemas/evaluation.py`

Contrato estático previsto:
`ProductionEvaluationCriterion`

Responsabilidad:
definir qué se evalúa en una producción concreta.

Contrato runtime previsto:
`ProductionEvaluationResult`

Responsabilidad:
representar el resultado de evaluar una producción concreta sin convertirlo en dominio de Skill.

Invariantes previstos:
- referencia explícita a producción/criterio/evidencia;
- compatibilidad con conversación y prompt;
- modalidades compatibles;
- evaluación fonética solo sobre voz;
- score normalizado cuando corresponda;
- sin duplicar `skill_ids`;
- sin modificar `LearnerProduction`;
- sin mastery, retention ni feedback.

## Decisión sobre EvidenceDefinition

`EvidenceDefinition.success_threshold` es el contrato real vigente:
- obligatorio para `measurement_mode=score`;
- rango `0.0–1.0`;
- prohibido para otros modos.

La antigua referencia documental a `success_condition` fue corregida durante B129 y todavía está pendiente de versionar.

## Archivos clave para B129

Backend:
- `app/schemas/evaluation.py` — nuevo, todavía no creado;
- `app/schemas/content.py`;
- `app/schemas/conversation_production.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/` — pruebas específicas de B129;
- `docs/lesson-experience-contract.md`;
- `docs/estado-operativo.md`;
- `docs/bitacora.md`;
- `docs/roadmap.md`.

Frontend:
- B128 ya cerrado; no modificar durante el contrato inicial de B129 salvo necesidad demostrada.

## Método operativo desde B129

Al iniciar o retomar un bloque:
1. leer este archivo;
2. inspección agrupada solo si falta información real;
3. diseñar el incremento;
4. construir;
5. prueba específica;
6. integración;
7. suite completa una sola vez al cierre;
8. actualizar documentación y este estado;
9. commit, push y Git limpio.

Si hacen falta varias inspecciones consecutivas sin producir cambio técnico, detener el bloque y revisar el método antes de continuar.

## Resultado técnico B129

- contratos de criterio, resultado y plan evaluativo implementados;
- validación contextual y runtime integrada;
- candidata piloto con tres criterios semánticos trazables;
- pipeline pedagógico integrado;
- 27 pruebas específicas superadas;
- 292 pruebas backend superadas;
- candidata no publicada;
- motor semántico/fonético real todavía pendiente.

