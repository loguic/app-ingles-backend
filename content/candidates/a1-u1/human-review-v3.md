# Revisión humana de la candidata A1-U1 v3

## Estado

`PENDING HUMAN REVIEW`

- `candidate_revision`: `a1-u1-candidate-v3`
- artefacto: `pedagogical-unit-candidate-v3.json`
- estado determinista de entrada: `READY_FOR_HUMAN_REVIEW`
- Skill única: `a1_express_immediate_need_orally`
- este documento no registra aprobación, admission, publication, membership ni activación;
- todas las decisiones siguientes permanecen abiertas y corresponden a una persona revisora.

## Resumen de la candidata corregida

La candidata contiene una única lección para una persona con inglés muy bajo o nulo. El lenguaje productivo obligatorio sigue limitado a `I need water.`, `I need help.` e `I need food.`. Las instrucciones que recibe el alumno se han reducido a mensajes breves como `Look. Listen.`, `Speak.` y `The picture changes.`.

La comprensión sigue audio-first: el alumno oye `I need water.` antes de responder `What does the person want?`. El transcript y el español siguen bloqueados hasta la primera respuesta. La comprobación prepara la producción; no acredita mastery receptivo.

La experiencia mantiene seis etapas, cuatro conversaciones, una comprobación de comprensión, dos actividades Direct English y seis capturas obligatorias. La secuencia corregida es:

1. primera actividad: `I need water.` con anclajes;
2. primera actividad: `I need water.` con `I` visible;
3. primera actividad: `I need food.` sin apoyo;
4. segunda actividad, nueva estación y nueva necesidad: `I need help.` con anclajes;
5. segunda actividad: `I need help.` con `I` visible;
6. segunda actividad, nueva imagen de comida: `I need food.` sin apoyo.

Cada actividad conserva `guided → expanded → transfer`. El reinicio de apoyo introduce `help` en una situación nueva y no vuelve a dar anclajes para la misma respuesta `food` acabada de producir sin apoyo. La configuración cualitativa propuesta sigue siendo `relevance` + `intelligibility` para `expanded` de la primera actividad y para `transfer` de la segunda; `guided` sigue siendo práctica.

Existe un modelo completo y shadowing de `I need water.`, modelos léxicos de `water`, `help` y `food`, y audio lógico para el cierre `Okay.`. Ninguno supone Skill fonética, threshold fonético ni requisito de acento nativo.

## Checklist pedagógico y lingüístico

- [ ] Confirmar que las instrucciones breves son comprensibles para una persona principiante absoluta sin asumir inglés previo.
- [ ] Confirmar la utilidad inmediata de expresar una necesidad con este único patrón.
- [ ] Confirmar que `water`, `help` y `food` son naturales, suficientes y adecuados en las situaciones propuestas.
- [ ] Confirmar que no se exige como producción ninguna palabra, frase o estructura fuera de las tres respuestas aprobadas.
- [ ] Confirmar que `What does the person want?` comprueba la intención comunicativa del audio y permanece como preparación, no como mastery receptivo independiente.
- [ ] Confirmar que `I` + `need` + elemento funciona como construcción y no como una frase completa ofrecida para copiar.
- [ ] Confirmar que la producción `expanded` de la primera actividad es propia y no recupera un modelo completo visible.
- [ ] Confirmar que la producción `transfer` de la segunda actividad es propia y no recupera un modelo completo visible.
- [ ] Valorar si las seis capturas Direct English tienen una carga total apropiada para esta entrada A1.
- [ ] Valorar si la secuencia `water → water → food → help → help → food` ofrece variación suficiente y evita una sensación mecánica.
- [ ] Confirmar que práctica, evidencia y revisión cualitativa conservan responsabilidades distintas.

## Visual, audio y accesibilidad

- [ ] Revisar el contexto lógico inicial: botella cerrada, comida envuelta y campana deben mantener varias necesidades plausibles antes de escuchar.
- [ ] Confirmar que el visual inicial ayuda a interpretar la situación sin regalar la respuesta inglesa.
- [ ] Revisar el contexto lógico de variación: máquina detenida, trabajador cercano, punto de recarga y mostrador de comida deben distinguirse del contexto inicial.
- [ ] Confirmar que las dos `accessibility_label` describen señales útiles sin contener `water`, `help`, `food` ni una respuesta inglesa completa.
- [ ] Confirmar neutralidad cultural, ausencia de estereotipos y legibilidad para personas con distintas experiencias vitales.
- [ ] Confirmar que los recursos lógicos de visual, modelos léxicos, modelo completo y `Okay.` están inventariados, sin URLs, paths ni bindings físicos.
- [ ] Escuchar o encargar la revisión de los futuros bindings de `I need water.`, `water`, `help`, `food` y `Okay.` para comprobar claridad, naturalidad y velocidad apropiada.
- [ ] Confirmar que el modelo completo, el shadowing breve, los modelos léxicos y las grabaciones forman una preparación funcional suficiente para las tres respuestas.
- [ ] Confirmar que inteligibilidad del bloque completo, y no acento nativo ni perfección fonética, es la expectativa.
- [ ] Confirmar que `Okay.` tiene audio real antes de presentar el cierre como escucha.

## Ayudas y Strict Support Timing

- [ ] Confirmar que el primer contacto es audio-first y permite repetición del audio.
- [ ] Confirmar que el transcript está inicialmente oculto y solo puede revelarse después de la primera respuesta a `a1-u1-l1-q1`.
- [ ] Confirmar que el español es rescate opcional y solo queda disponible después de esa primera respuesta.
- [ ] Confirmar que transcript y español no aparecen ni forman parte de la evidencia productiva final.
- [ ] Confirmar la progresión global: mapa de construcción → `water` con anclajes → `water` con `I` → `food` sin apoyo → `help` con anclajes en una situación nueva → `help` con `I` → `food` sin apoyo en una nueva imagen.
- [ ] Confirmar que `support_level="none"` se usa solo en las dos transferencias exigidas y que ambas tienen `visible_support=[]`.
- [ ] Confirmar que las transferencias sin apoyo no muestran frase completa, transcript ni español.

## Evidencia y puertas cualitativas propuestas

- [ ] Confirmar la separación entre `comprehension_result`, `guided_production`, `contextual_response` y `conversation_completion`.
- [ ] Confirmar que la fuente de producción primaria es la primera actividad Direct English y que su puerta propuesta revisa solo `expanded`.
- [ ] Confirmar que la fuente contextual/de transferencia es la segunda actividad Direct English y que su puerta propuesta revisa solo `transfer`.
- [ ] Confirmar explícitamente que `guided` permanece práctica y no se convierte en evaluación cualitativa.
- [ ] Aprobar, modificar o rechazar la propuesta `expanded → relevance + intelligibility` para la primera actividad.
- [ ] Aprobar, modificar o rechazar la propuesta `transfer → relevance + intelligibility` para la segunda actividad.
- [ ] Confirmar que relevance juzga la necesidad pertinente para cada situación concreta y que intelligibility juzga comprensibilidad funcional sin exigir acento nativo.
- [ ] Confirmar que una evaluación automática, semántica o fonética no puede satisfacer estas puertas cualitativas.
- [ ] Confirmar que `conversation_completion` solo registra el cierre estructural `Okay.` y no demuestra producción, aprendizaje o fluidez.

## Transferencia y límites de interpretación

- [ ] Confirmar que la transferencia final cambia el contexto visual, la necesidad relevante, el prompt/intervención y la respuesta esperada respecto de la producción primaria.
- [ ] Confirmar que conserva la misma intención, el mismo patrón y la misma Skill.
- [ ] Confirmar que la producción cualitativamente revisada pasa de `initial_word` en `expanded` a `none` en `transfer`, con apoyo estrictamente menor.
- [ ] Confirmar que la repetición de `food` como transferencia final se siente como reutilización en una nueva situación y no como una copia mecánica.
- [ ] Confirmar que los claims están en el orden `EXPOSURE_AVAILABLE → INSTRUCTION_AVAILABLE → PRACTICE_AVAILABLE → EVIDENCE_GATE_AVAILABLE` y apuntan a artefactos reales.
- [ ] Confirmar que `prerequisites=[]` sigue siendo correcto para esta entrada canónica A1.
- [ ] Confirmar que `SkillCoverage` cubre introducción, práctica, aplicación, evaluación y consolidación, pero permanece `pending_approval`.
- [ ] Confirmar que completion no equivale a mastery, retention, progreso curricular, aprendizaje demostrado ni fluidez.

## Decisión humana

- Decisión: pendiente.
- Findings BLOCKING: pendientes de revisión humana.
- Findings NONBLOCKING: pendientes de revisión humana.
- Cambios solicitados: pendientes.
- Identidad de reviewer: pendiente.
- Fecha de decisión: pendiente.

No completar este documento mediante validación automática. Una futura decisión humana sobre esta revisión deberá permanecer separada de cualquier admission o publicación posterior.
