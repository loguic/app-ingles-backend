# Revisión humana de la candidata A1-U1 v3

## Estado

`HUMAN APPROVED`

- `candidate_revision`: `a1-u1-candidate-v3`;
- artefacto: `pedagogical-unit-candidate-v3.json`;
- estado determinista de entrada: `READY_FOR_HUMAN_REVIEW`;
- Skill única: `a1_express_immediate_need_orally`;
- este documento registra únicamente la aprobación humana; no registra admission,
  publication, membership ni activación.

## Decisiones implementadas para revisar

La candidata mantiene una única lección para una persona con inglés muy bajo o
nulo. La producción se limita a `I need water.`, `I need help.` e `I need
food.`. El lenguaje visible de instrucción se ha reducido a `Listen.`,
`Choose.`, `Say it.` y `Say it again.`; no presenta `I want` ni explicaciones
metalingüísticas al alumno.

La secuencia pedagógica esperada es visual → observación breve → audio →
práctica → producción. El contrato actual no describe velocidad de audio ni
una secuencia de replay progresiva: el consumidor futuro deberá presentar el
primer modelo en-GB de forma clara y ligeramente lenta-natural, y los replays
algo más cerca de velocidad natural. Esta nota no es metadata inventada.

Antes de pedir producción para cada necesidad, el consumidor futuro deberá
presentar la palabra aislada y después el bloque completo correspondiente:
`water` → `I need water.`, `food` → `I need food.` y `help` → `I need help.`.
Los arrays de pronunciación sitúan en-GB primero; en-US no es el modelo inicial
equivalente de esta experiencia. Los modelos completos de `help` y `food` son
recursos lógicos en-GB independientes.

## Comprensión visual

Después de oír `I need water.`, la comprobación usa el MCQ visual homogéneo
`a1-u1-l1-q1`, con prompt visible mínimo `Choose.`. Sus tres recursos
independientes representan una necesidad, un saludo y una despedida; el
`answer_index` selecciona la escena de necesidad. No hay captions visibles ni
opciones textuales `water`, `food` o `help`, y no se introduce `want`.

El transcript de la conversación inicial queda oculto y el español de apoyo se
habilita solo después de la primera respuesta a ese MCQ. La comprensión prepara
la producción; no acredita mastery receptivo.

## Visuales y recursos

- `water`: `static_image`, una escena de botella vacía junto a un punto de
  recarga;
- `food`: `static_image`, una escena de bandeja de comida sin abrir;
- `help`: `microvideo`, donde la máquina funciona, se detiene, una persona
  intenta usarla y mira a un asistente; no contiene texto ni voz, tiene
  `autoplay_once=true` y `replay_allowed=true`.

Cada escena mantiene un foco comunicativo principal. Los tres recursos de
opción del MCQ visual son distintos de los `VisualContext` de etapa y todos
están en `required_resource_ids`. Sus `accessibility_label` son nombres
accesibles, no captions visibles; deben describir señales útiles sin revelar
la palabra objetivo ni una respuesta inglesa completa.

## Producción, ayudas y feedback

Las seis capturas quedan exactamente así:

1. `water` con `anchors`;
2. `water` con `initial_word`;
3. `food` con `none`;
4. `help` con `anchors`;
5. `help` con `initial_word`;
6. `food` con `none`.

Ambas transferencias conservan `support_level="none"` y `visible_support=[]`.
El español es rescate léxico breve y posterior al primer intento; el transcript
posterior es únicamente la frase objetivo completa. Ninguno está disponible en
la evidencia final.

Ante un error, el comportamiento esperado del futuro consumidor es: ajuste
breve → repetir el modelo cuando corresponda → reintento guiado. No debe usar
score punitivo ni regalar inmediatamente una respuesta completa para copiar.
El contrato actual solo representa `reinforcement_on_failure`, `allow_retry` y
prioridades de corrección; esta secuencia no se finge como metadata adicional.

## Evidencia y cierre

`guided` permanece práctica sin revisión cualitativa. La primera fuente directa
revisa `expanded` por `relevance` e `intelligibility`; la segunda fuente revisa
`transfer` por las mismas dos dimensiones. La automática no acredita esas
puertas.

El cierre usa `Okay.` solo con el recurso lógico en-GB declarado. Antes de un
binding físico o de presentar el cierre al alumnado, la revisión humana debe
confirmar que el audio real sea coherente, claro y natural.

## Checklist de revisión humana

- [ ] Confirmar que el MCQ visual mide intención comunicativa y que las tres
  alternativas accesibles no revelan léxico ni respuesta.
- [ ] Confirmar que los tres visuales de escena tienen un único foco y que el
  microvideo de `help` expresa la secuencia aprobada sin texto ni voz.
- [ ] Confirmar la secuencia visual → observación → audio → palabra → bloque →
  práctica → producción para `water`, `food` y `help`.
- [ ] Escuchar o encargar la revisión de los futuros bindings en-GB de las tres
  palabras, los tres bloques y `Okay.`.
- [ ] Confirmar que transcript y español se habilitan solo después del primer
  intento y no aparecen en evidencia final.
- [ ] Confirmar que los seis captures, los dos niveles `none` y la reducción de
  apoyo son adecuados para una persona principiante absoluta.
- [ ] Confirmar que la revisión cualitativa es `expanded` primero y `transfer`
  después, ambas con `relevance` e `intelligibility`, sin revisión de `guided`.
- [ ] Confirmar que completion no se interpreta como mastery, retención,
  aprendizaje demostrado, progreso curricular ni fluidez.

## Decisión humana

- Decisión: `HUMAN APPROVED` (opción 1).
- Findings BLOCKING: 0.
- Findings NONBLOCKING: 0.
- Cambios solicitados: ninguno.
- Identidad de reviewer: usuario.
- Fecha de decisión: 2026-09-09.

Esta aprobación humana permanece separada de admission, publicación,
membership y activación.
