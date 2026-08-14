# Contrato V1 de preparación curricular y prerrequisitos

## Estado del documento

- Versión conceptual: `1.0`.
- Estado: especificación formal para revisión humana previa a cualquier implementación.
- Alcance: preparación estructural del currículo y prerrequisitos entre puntos ordenados de una progresión.
- Este documento no diseña contenido, schemas, persistencia, runtime individual ni generación automática.

## Propósito

Definir el contrato mínimo que permita responder determinísticamente:

> ¿Puede esta lección exigir esta Skill en este punto de la progresión?

El contrato complementa el Constructor Pedagógico existente. Impide considerar suficiente una candidata solo porque sus referencias internas sean válidas cuando exige capacidades que el currículo anterior no preparó estructuralmente.

## Terminología y fronteras

`Skill` significa exclusivamente una habilidad pedagógica observable y medible del estudiante. `SkillSpecification` continúa siendo su identidad principal; no se crea una entidad pedagógica paralela equivalente.

El contrato separa obligatoriamente:

```text
preparación curricular
!= ejecución del estudiante
!= evidencia real
!= resultado de evaluación
!= aprendizaje
!= mastery
```

También separa el orden estructural de cualquier trayectoria individual:

```text
posición curricular
!= lección recorrida por un estudiante
!= progreso
!= evidencia positiva
!= aprendizaje
!= mastery
```

Que una lección aparezca antes en el currículo no demuestra que un estudiante concreto la haya realizado o aprovechado.

También conserva el principio pedagógico:

```text
EXPUESTO != ENSEÑADO != PRACTICADO != EVIDENCIADO != DOMINADO
```

Estos cinco términos conceptuales se refieren a acontecimientos o estados relacionados con un estudiante. No son valores del ledger curricular v1 y no se deriva entre ellos ninguna taxonomía runtime en este contrato.

Una `EvidenceDefinition` puede justificar que el currículo tiene una puerta de evidencia disponible. Nunca demuestra por sí sola que un estudiante produjo evidencia, obtuvo un resultado positivo, aprendió o alcanzó mastery.

## Granularidad canónica de `Skill`

La unidad de identidad de una Skill es algo que el estudiante puede hacer usando lenguaje, no una palabra, forma o pieza de lenguaje aislada.

### Norma aprobada

> Una Skill deberá representar una conducta del estudiante observable, practicable y evidenciable, con propósito comunicativo o cognitivo autónomo y valor reutilizable en la progresión. No se crearán Skills para palabras, formas lingüísticas, fonemas, recursos o actividades aislados. Una capacidad se descompondrá cuando sus componentes puedan prepararse, fallar, evidenciarse o reutilizarse independientemente; podrá conservarse además una Skill superior únicamente cuando su integración produzca una conducta observable propia. La granularidad final deberá ser aprobada por la puerta humana y no podrá inferirse exclusivamente mediante validación estructural o IA.

### Criterios mínimos obligatorios

Una capacidad merece un `skill_id` propio cuando representa una conducta:

- observable mediante una acción del estudiante;
- practicable de forma diferenciada;
- evidenciable de forma diferenciada;
- con propósito comunicativo o cognitivo reconocible;
- con valor curricular reutilizable;
- significativamente separable de capacidades próximas.

Reutilizable significa que tiene sentido modelarla independientemente dentro de la progresión, aunque no sea obligatoriamente prerrequisito de otra Skill. Significativamente separable implica que puede prepararse, manifestarse o fallar de manera distinta de una capacidad próxima y que distinguirla mejora alguna decisión pedagógica.

### Pruebas conceptuales de revisión

Toda candidata a Skill debe responder claramente:

> ¿Qué acción observable permitiría comprobar razonablemente que el estudiante puede realizar esta Skill?

Si no existe una respuesta clara, probablemente no tiene granularidad válida.

También debe responder:

> ¿Modelarla independientemente mejora realmente la práctica, evidencia, progresión, diagnóstico o reutilización curricular?

Si la respuesta es no, probablemente no merece un `skill_id` propio.

Estas pruebas orientan el modelado y la puerta humana; no constituyen por sí solas un algoritmo determinista de aprobación.

### Elementos que normalmente no son Skills

No se crearán automáticamente Skills para:

- palabras aisladas o vocabulario individual;
- expresiones fijas aisladas;
- preposiciones;
- conjugaciones o formas verbales;
- reglas o etiquetas gramaticales;
- fonemas o rasgos de pronunciación aislados;
- instrucciones;
- frases modelo;
- ejemplos o prompts;
- ayudas o anclas;
- traducciones;
- temas;
- actividades o ejercicios;
- audios o textos;
- recursos o artefactos técnicos.

Estos elementos pueden participar en la exposición, enseñanza, práctica o evidencia de una Skill funcional, pero no son por sí mismos la Skill.

### Señales de granularidad demasiado amplia

Una candidata es probablemente demasiado amplia cuando:

- contiene varias conductas que podrían fallar independientemente;
- necesita evidencias distintas para componentes diferentes;
- oculta prerrequisitos que pueden prepararse separadamente;
- agrupa múltiples acciones como comprender, responder, preguntar, reparar y continuar;
- solo puede evaluarse mediante una experiencia demasiado extensa;
- funciona mejor como objetivo de unidad, fase o curso;
- casi cualquier actividad podría vincularse con ella sin aportar precisión.

### Señales de granularidad demasiado microscópica

Una candidata es probablemente demasiado pequeña cuando:

- coincide con una palabra, forma, fonema o fragmento lingüístico;
- carece de propósito funcional independiente;
- solo aparece en un ejemplo o actividad;
- necesita una prueba artificial para evidenciarse separadamente;
- no mejora el mapa de prerrequisitos ni el diagnóstico pedagógico;
- siempre cambia junto con otra Skill;
- genera nodos curriculares sin autonomía.

### Capacidades compuestas

Una capacidad debe mantenerse como una única Skill cuando existe un único resultado observable, sus componentes se preparan conjuntamente, una evidencia acotada puede valorar la conducta y separarla no mejora la progresión ni el diagnóstico.

Debe descomponerse cuando sus componentes pueden enseñarse o practicarse separadamente, fallar independientemente, necesitar evidencias diferentes, aparecer como prerrequisitos en momentos distintos o aportar valor reutilizable por sí mismos.

Puede conservarse además una Skill superior solo cuando la integración produce una conducta observable nueva que necesita práctica y evidencia propias. No toda agrupación merece una Skill superior.

### Compatibilidad con `SkillSpecification`

Esta decisión no añade campos a `SkillSpecification`. En v1, `id` y `description` continúan siendo suficientes en combinación con claims, prerrequisitos, actividades, evidencias, reglas de modelado y puerta humana.

No se incorporan marcadores `atomic` o `composite`, `parent_skill_ids`, scores de granularidad ni taxonomías nuevas.

### Frontera con `required_stages`

El campo existente `SkillSpecification.required_stages`, con los valores heredados `introduce`, `practice`, `apply`, `evaluate` y `consolidate`, permanece como contrato de compatibilidad mientras existan validadores y candidatas anteriores que dependan de él. Puede seguir participando temporalmente en validaciones heredadas de cobertura.

`required_stages` no es una segunda fuente de verdad para `CurriculumPreparationState` y no existe una equivalencia automática entre ambas taxonomías. En particular, no se interpretará `introduce` como `EXPOSURE_AVAILABLE`, `practice` como `PRACTICE_AVAILABLE` ni se establecerá ningún otro mapeo implícito.

La fuente autoritativa de preparación y progresión curricular v1 es la combinación de `LessonCapabilityPlan`, `LessonCapabilityClaim`, `SkillPrerequisite` y el ledger derivado. Por tanto, `required_stages` no puede:

- crear un `CurriculumPreparationState`;
- satisfacer un `SkillPrerequisite`;
- modificar el ledger;
- sustituir un `LessonCapabilityClaim`;
- inferir exposición, instrucción, práctica o puerta de evidencia disponible.

Durante una futura transición pueden coexistir controles heredados basados en `required_stages` o `SkillCoverage` y controles v1 basados en claims y prerrequisitos. Son validaciones distintas, no dos fuentes sobre un mismo estado. Una candidata sometida al contrato v1 solo puede acreditar preparación mediante claims válidos y artefactos compatibles.

La estrategia concreta de retirada o migración de `required_stages` pertenece al posterior diseño de implementación. Este contrato no elimina el campo ni añade otros.

## Modelo conceptual

El modelo v1 consta de:

```text
SkillSpecification
  <- identificada por LessonCapabilityClaim
  <- requerida por SkillPrerequisite

LessonCapabilityPlan
  -> claims de preparación disponibles en una lección
  -> prerrequisitos consumidos por esa lección

progresión curricular explícitamente ordenada
  -> cálculo determinista
  -> CurriculumCapabilityPreparationLedger
```

El ledger representa únicamente qué preparación ofrece el currículo antes de cada punto de consumo. Es una vista calculada; no se declara, aprueba ni persiste como segunda fuente de verdad.

## `CurriculumPreparationState`

El enum curricular v1 contiene exclusivamente:

```text
EXPOSURE_AVAILABLE
INSTRUCTION_AVAILABLE
PRACTICE_AVAILABLE
EVIDENCE_GATE_AVAILABLE
```

Su orden estructural es:

```text
EXPOSURE_AVAILABLE
< INSTRUCTION_AVAILABLE
< PRACTICE_AVAILABLE
< EVIDENCE_GATE_AVAILABLE
```

Alcanzar un estado superior exige que los anteriores estén disponibles en orden, pero nunca permite inferir que un estudiante recorrió o aprovechó esa preparación.

### `EXPOSURE_AVAILABLE`

Existe en el currículo un artefacto accesible que presenta la Skill en contexto.

Puede justificarse mediante un encuentro contextual, intervención, ejemplo, texto, audio u otro artefacto de presentación vinculado explícitamente con la Skill.

No significa que un estudiante lo haya visto, escuchado o comprendido.

### `INSTRUCTION_AVAILABLE`

Existe enseñanza explícita, modelado o andamiaje que tiene como propósito hacer comprensible la Skill y su uso.

Exige `EXPOSURE_AVAILABLE` antes o en un punto anterior compatible. Debe referenciar una etapa o recurso instructivo con intención pedagógica explícita; la mera aparición de una forma lingüística no basta.

No significa que un estudiante haya recibido o comprendido esa enseñanza.

### `PRACTICE_AVAILABLE`

Existe una actividad ejecutable que permite recuperar, seleccionar o producir la Skill.

Exige `INSTRUCTION_AVAILABLE` en un punto anterior. La actividad debe requerir una acción observable del estudiante y una modalidad compatible con la Skill.

No significa que un estudiante haya iniciado o completado la práctica ni que su respuesta sea correcta.

### `EVIDENCE_GATE_AVAILABLE`

Existe una puerta evaluativa válida para recoger y valorar evidencia de la Skill.

Exige `PRACTICE_AVAILABLE`, una `EvidenceDefinition` válida y los contratos de evaluación o revisión necesarios para interpretar la futura evidencia. La modalidad, la Skill, la actividad, el prompt cuando corresponda y el plan evaluativo deben ser estructuralmente coherentes.

No significa que exista una producción real, que se haya recogido o evaluado evidencia, que el resultado sea positivo, que la Skill esté demostrada ni que exista mastery.

## Contratos conceptuales v1

### `LessonCapabilityClaim`

Declara preparación que una lección pone a disposición:

```text
skill_id
preparation_state
artifact_ids
```

- `skill_id`: identificador de una `SkillSpecification` existente.
- `preparation_state`: uno de los cuatro valores de `CurriculumPreparationState`.
- `artifact_ids`: lista no vacía de referencias concretas que justifican el claim.

Un claim es una afirmación estructural revisable, no una afirmación sobre conducta o aprendizaje individual. La posición de disponibilidad se deriva de la posición curricular de sus artefactos; no se añade un campo manual alternativo para ella.

### `SkillPrerequisite`

Declara la preparación mínima que debe existir antes de un punto de consumo:

```text
required_skill_id
required_state
before_stage_id  # opcional
reason
```

- `required_skill_id`: Skill cuya preparación se consume.
- `required_state`: estado curricular mínimo requerido; solo admite los cuatro estados `*_AVAILABLE`.
- `before_stage_id`: etapa antes de la cual debe estar satisfecho el requisito; si está ausente, debe satisfacerse antes de iniciar la lección.
- `reason`: justificación pedagógica breve y no vacía.

La lección consumidora se deriva del `LessonCapabilityPlan` que contiene el requisito. Git y la versión del candidato aportan la trazabilidad v1; no se añaden todavía campos especulativos de autoría o revisión a cada relación.

### `LessonCapabilityPlan`

Agrupa la preparación declarada y consumida por una lección:

```text
lesson_id
claims
prerequisites
```

- `lesson_id`: lección existente en la candidata.
- `claims`: claims de preparación justificados por artefactos de esa lección.
- `prerequisites`: requisitos que deben cumplirse antes de la lección o etapa indicada.

### `CurriculumCapabilityPreparationLedger`

Vista derivada conceptualmente por Skill:

```text
skill_id
highest_preparation_state
supporting_lesson_ids
supporting_artifact_ids
```

- `highest_preparation_state`: mayor estado estructural satisfecho hasta el punto calculado.
- `supporting_lesson_ids` y `supporting_artifact_ids`: trazabilidad de los claims que sostienen el resultado.

El ledger se recalcula recorriendo la progresión y las etapas en orden. No acepta edición manual, no representa un estudiante y no puede contener mastery.

## Orden curricular y puntos de consumo

### Currículo canónico lineal y fuente única de verdad

V1 asume un currículo canónico lineal. Su orden se deriva exclusivamente de la jerarquía ordenada existente:

```text
A1 < A2 < B1 < B2 < C1 < C2
  -> posición en Level.units
    -> posición en Unit.lessons
      -> posición en LessonExperience.stages
```

La secuencia CEFR determina el rango del nivel. El orden de unidades, lecciones y etapas se obtiene de sus posiciones en las listas que las contienen. Esas posiciones son índices derivados para comparación y validación; no son campos persistidos.

Los IDs expresan identidad, pertenencia y trazabilidad. No expresan orden curricular. Nunca se inferirá precedencia mediante sufijos numéricos o comparación lexicográfica de IDs, filesystem, fecha de creación, Git, runtime ni orden accidental no validado.

No se incorporan campos `order` o `position`, ordinales persistidos, una entidad `CurriculumSequence`, listas paralelas ni otra fuente redundante. La jerarquía ordenada es la única fuente de verdad v1.

### Autoridad curricular y completitud desde origen

V1 reconoce conceptualmente un proveedor curricular designado por contrato como autoridad. La autoridad pertenece al proveedor y a la garantía que emite, no a un archivo físico, una ruta, un `ContentTreeResponse` aislado, un booleano `is_authoritative` controlado por el caller ni una convención de IDs. La representación subyacente puede evolucionar de archivo a base de datos, paquete versionado u otra fuente sin alterar esta semántica contractual. V1 no introduce todavía `curriculum_version`, tracks, locales ni namespaces equivalentes porque esos conceptos no existen en el contrato actual.

Una hierarchy es autoritativa únicamente cuando procede de ese proveedor designado y este garantiza que representa el recorrido curricular canónico completo desde su propio origen. Una hierarchy arbitraria o parcial puede seguir siendo válida para análisis relativo a ella, pero no demuestra autoridad ni completitud desde origen.

El origen autoritativo es la primera `CurriculumUnitPosition` canónica derivada de esa hierarchy autoritativa mediante el orden ya definido. No se infiere mediante `level_code == "A1"`, `CEFR_LEVEL_ORDER[0]`, `unit_index == 0` de una hierarchy parcial, `unit_id == "a1-u1"` ni la forma léxica de ningún ID. Los IDs siguen expresando identidad y pertenencia, nunca orden; no se crea una segunda fuente de orden.

La mera presencia de la unidad de origen no demuestra completitud. El proveedor autoritativo debe garantizar además que la hierarchy no omite posiciones curriculares canónicas entre el origen y la target: `origin present` no equivale a `hierarchy complete from origin`.

`complete_within_hierarchy` significa únicamente que existe cobertura exacta de candidates para las posiciones presentes en el scope de la hierarchy suministrada. No implica autoridad. `complete_from_authoritative_origin` es una propiedad derivable únicamente cuando:

1. la hierarchy procede del proveedor curricular autoritativo;
2. el proveedor garantiza continuidad y completitud desde su origen;
3. el origen canónico de esa hierarchy coincide estructuralmente con `context.scope.start_position`;
4. la target pertenece al prefijo autoritativo;
5. existe cobertura uno a uno de candidates para todas las posiciones requeridas desde el origen hasta la target.

Esta prueba debe derivarse estructuralmente; no puede declararse mediante un booleano controlado por el caller como `is_complete_from_origin=True`. `complete_from_authoritative_origin` no equivale a `globally_complete`. V1 no introduce esa noción global mientras el producto no disponga de contratos adicionales que la requieran.

`satisfied_in_context` no equivale a `globally_satisfied`, y `unresolved_in_context` no equivale a `unsatisfied`. Incluso cuando exista prueba de `complete_from_authoritative_origin`, los errores de resolución de consumption y preparación siguen siendo errores derivativos, y los errores de precedencia relevantes pueden impedir una futura conclusión negativa fuerte. Antes de considerar esa conclusión deberá existir tanto la prueba de completitud desde origen autoritativo como ausencia de incertidumbre derivativa relevante; V1 no define todavía la regla final de `unsatisfied`.

Autoridad y completitud curricular estructural no equivalen a ejecución del estudiante, evidencia real, resultado de evaluación, aprendizaje, retention ni mastery. El contrato podrá incorporar versionado, tracks u otras dimensiones cuando exista una necesidad real, sin alterar el principio central: la autoridad la emite un proveedor contractual reconocido y el orden se deriva de la hierarchy canónica, nunca de IDs ni de metadata duplicada.

### Contexto curricular ordenado de una candidata

Una `PedagogicalUnitCandidate` aislada no permite validar prerrequisitos interunidad. Tampoco basta por sí solo `ContentTreeResponse`: aporta estructura y orden, pero no contiene necesariamente las especificaciones, planes, claims y prerrequisitos canónicos necesarios para reconstruir el ledger.

La validación de progresión debe recibir una vista curricular efímera y completa que reúna, como mínimo:

1. la estructura curricular ordenada formada por `Level`, `Unit`, `Lesson` y `LessonExperience.stages`;
2. las `SkillSpecification` canónicas necesarias para resolver todos los `skill_id` utilizados;
3. los `LessonCapabilityPlan` canónicos de las lecciones relevantes;
4. sus `LessonCapabilityClaim`;
5. sus `SkillPrerequisite`;
6. los artefactos referenciados necesarios para validar cada claim;
7. la candidata propuesta situada exactamente una vez en su posición.

La vista debe contener esa información desde el comienzo del recorrido pertinente hasta cada punto de consumo, además del contenido posterior necesario para comprobar ciclos y coherencia de la candidata. Debe permitir inspeccionar preparación anterior, resolver inequívocamente posiciones y recorrer el alcance validado como una secuencia determinista única.

Esta vista se construye exclusivamente para validación y no se persiste como segunda fuente de verdad. Cada dato procede de su contrato canónico correspondiente; la vista solo los reúne. V1 no crea una entidad nueva para representarla ni define todavía almacenamiento, API, schema u optimizaciones incrementales. Una candidata ausente o repetida en el contexto propuesto es inválida.

### Posición curricular comparable

Para comparar puntos curriculares se deriva conceptualmente:

```text
(
  cefr_rank,
  unit_index,
  lesson_index,
  stage_index
)
```

`cefr_rank` procede de la secuencia A1-C2; los demás componentes proceden de `Level.units`, `Unit.lessons` y `LessonExperience.stages`. Esta tupla es una representación calculada para validación, no un contrato persistido.

### Disponibilidad y consumo

Un `LessonCapabilityClaim` solo está disponible cuando todos los artefactos necesarios para justificarlo han sido alcanzados. Si depende de varios artefactos o etapas, su punto de disponibilidad es el más tardío. Solo los claims completamente disponibles antes del punto de consumo pueden satisfacer un prerrequisito.

Si `SkillPrerequisite.before_stage_id` está presente, el estado requerido debe estar disponible antes de esa etapa. Si es `null`, debe estar disponible antes de comenzar la lección. Un claim producido en el mismo punto de consumo, después de él o en una lección, unidad o nivel posterior no puede satisfacer el requisito.

### Recorrido del ledger

El cálculo sigue estas reglas:

1. recorrer niveles según la secuencia CEFR;
2. recorrer unidades según `Level.units`;
3. recorrer lecciones según `Unit.lessons`;
4. recorrer etapas según `LessonExperience.stages`;
5. antes de entrar en una lección, comprobar sus prerrequisitos sin `before_stage_id`;
6. antes de cada etapa, comprobar los prerrequisitos que apuntan a ella;
7. incorporar claims únicamente cuando estén completamente disponibles;
8. conservar el mayor estado satisfecho y la trazabilidad de sus lecciones y artefactos productores;
9. usar el ledger de salida de cada lección como ledger de entrada de la siguiente.

El mismo recorrido valida dependencias intraunidad, interunidad e internivel; no existen tres mecanismos conceptuales distintos. Una Skill de un nivel posterior puede depender de preparación ofrecida en uno anterior, pero una dependencia hacia un nivel futuro es inválida. Esta precedencia sigue describiendo preparación curricular estática, no finalización, aprendizaje ni mastery del estudiante.

Insertar una unidad o lección puede modificar índices derivados sin exigir el cambio de sus IDs. Todo cambio de posición requerirá revalidar la progresión curricular afectada; v1 no diseña optimizaciones incrementales.

### Norma aprobada de orden curricular

> El orden curricular canónico v1 será lineal y se derivará exclusivamente de la secuencia CEFR `A1 < A2 < B1 < B2 < C1 < C2` y de la posición de cada elemento en las listas jerárquicas `Level.units`, `Unit.lessons` y `LessonExperience.stages`. Los IDs expresan identidad y pertenencia, no orden. Toda candidata deberá validarse dentro de un contexto curricular ordenado que determine inequívocamente su posición. Un prerrequisito solo podrá satisfacerse mediante claims completamente disponibles antes de su punto de consumo; se rechazarán posiciones desconocidas, dependencias futuras, duplicidades y ciclos. Este orden describe preparación curricular estática y no permite inferir progreso, aprendizaje ni mastery individual.

### Combinaciones de orden inválidas

Son inválidos, como mínimo:

- un nivel desconocido o duplicado;
- una unidad duplicada dentro del mismo nivel;
- una lección duplicada dentro de la misma unidad;
- una candidata ausente o repetida en el contexto propuesto;
- cualquier posición curricular no resoluble;
- una dependencia hacia una unidad, lección o etapa futura;
- consumir una Skill antes de que termine el claim que satisface `required_state`;
- un ciclo directo o indirecto;
- inferir orden desde IDs, filesystem, fecha, Git o runtime;
- combinar el orden de las listas con ordinales contradictorios.

## Invariantes deterministas v1

### Identidad e integridad

1. Toda lección se procesa según el orden curricular lineal derivado de la jerarquía canónica.
2. Todo `skill_id` y `required_skill_id` debe resolver a una `SkillSpecification` existente.
3. Todo `lesson_id`, `before_stage_id` y `artifact_id` debe existir y pertenecer al contexto permitido.
4. `artifact_ids` debe ser no vacío y no contener duplicados.
5. `reason` debe contener texto no blanco.
6. El ledger siempre se calcula a partir de claims válidos; nunca se acepta como declaración manual.

### Precedencia de preparación

7. Una lección solo puede consumir preparación producida antes del punto de consumo.
8. `INSTRUCTION_AVAILABLE` requiere `EXPOSURE_AVAILABLE` previo.
9. `PRACTICE_AVAILABLE` requiere `INSTRUCTION_AVAILABLE` previo.
10. `EVIDENCE_GATE_AVAILABLE` requiere `PRACTICE_AVAILABLE` previo.
11. Cada estado solo puede justificarse mediante tipos de artefactos estructuralmente compatibles.
12. Un estado superior no puede aparecer por primera vez sin que la progresión previa contenga los estados requeridos.
13. Una evaluación o transferencia no puede introducir por primera vez una Skill necesaria para resolverla.
14. Una evidencia evaluativa no puede constituir simultáneamente la primera enseñanza de la Skill que pretende evaluar.

### Prerrequisitos y grafo

15. Todo prerrequisito identifica Skill, estado mínimo requerido y punto de consumo.
16. El ledger calculado inmediatamente antes del punto de consumo debe satisfacer `required_state` para `required_skill_id`.
17. Las dependencias deben respetar el orden curricular y no pueden satisfacerse retroactivamente.
18. Los ciclos directos e indirectos entre dependencias deben rechazarse.
19. Una Skill no puede depender circularmente de sí misma, aunque el ciclo atraviese otras Skills o lecciones.

### Evidencia y fronteras

20. `EVIDENCE_GATE_AVAILABLE` requiere una `EvidenceDefinition` válida vinculada con la Skill.
21. Skill, modalidad, actividad, evidencia, prompt y evaluación o revisión deben ser coherentes cuando sean aplicables.
22. Una medición `completion` describe finalización o registro; no equivale a éxito pedagógico.
23. Ningún estado curricular permite inferir ejecución, evidencia real, resultado, progreso, aprendizaje, retención o mastery individual.
24. `MASTERED` no pertenece al enum curricular, no puede declararse mediante claims y no puede derivarse por el ledger v1.
25. El contexto ordenado debe contener la candidata exactamente una vez y permitir resolver todas las posiciones relevantes.
26. Los IDs y fuentes externas a la jerarquía ordenada no pueden utilizarse para inferir precedencia.

## Compatibilidad de artefactos

La función pedagógica no deriva del tipo aislado de un artefacto. Deriva de una combinación coherente de:

```text
LessonCapabilityClaim
+ LessonStage
+ artefacto ejecutable o presentado
+ relaciones estructurales
+ vínculo con Skill
```

Una misma clase puede participar en varios estados cuando la etapa, la acción del estudiante y las relaciones expresan funciones diferentes. No se duplicarán `Conversation`, `ExerciseMCQ` u otros contratos para representar cada uso.

### Artefactos reales incluidos

La matriz cerrada v1 reconoce:

- `Mission`;
- `LessonStage`;
- `LanguageSupportItem`;
- `Example`;
- `Conversation`;
- `ConversationTurn`;
- `ConversationChoice`;
- `LearnerProductionPrompt`;
- `TransferPromptVariant`;
- `ExerciseMCQ`;
- `EvidenceDefinition`;
- `PronunciationReinforcement`;
- `ExternalReviewRequirement`;
- `LessonProductionEvaluationPlan`;
- `ProductionEvaluationCriterion`;
- `SemanticEvaluationRule`.

Son recursos o contratos subordinados y no justifican estados aisladamente:

- `Pronunciation` y `audio_asset`;
- textos `en` o `es`;
- `visible_support`;
- `CorrectionGuidancePolicy`;
- `feedback_plan` y `ProductionFeedbackRule`;
- metadata de lección;
- `CompletionPolicy`.

`PronunciationReinforcement` no tiene ID propio. Cuando participe en un claim, su posición y trazabilidad se expresarán mediante su `stage_id` y los artefactos propietarios, nunca mediante un `audio_asset` aislado.

### Matriz cerrada v1

`CONDICIONAL` significa que el tipo solo puede participar dentro de la combinación estructural definida después de la tabla. No significa que su mera presencia produzca el estado.

| Artefacto real | `EXPOSURE_AVAILABLE` | `INSTRUCTION_AVAILABLE` | `PRACTICE_AVAILABLE` | `EVIDENCE_GATE_AVAILABLE` |
|---|---|---|---|---|
| `Mission` | CONDICIONAL | NO | NO | NO |
| `LessonStage` | CONDICIONAL | CONDICIONAL | CONDICIONAL | CONDICIONAL |
| `LanguageSupportItem` | CONDICIONAL | CONDICIONAL | NO | NO |
| `Example` | CONDICIONAL | CONDICIONAL | NO | NO |
| `Conversation` | CONDICIONAL | CONDICIONAL | CONDICIONAL | CONDICIONAL |
| `ConversationTurn` | CONDICIONAL | CONDICIONAL | CONDICIONAL | CONDICIONAL |
| `ConversationChoice` | NO | NO | CONDICIONAL | CONDICIONAL |
| `LearnerProductionPrompt` | NO | NO | CONDICIONAL | CONDICIONAL |
| `TransferPromptVariant` | NO | NO | CONDICIONAL | CONDICIONAL |
| `ExerciseMCQ` | NO | NO | CONDICIONAL | CONDICIONAL |
| `EvidenceDefinition` | NO | NO | NO | CONDICIONAL |
| `PronunciationReinforcement` | CONDICIONAL | CONDICIONAL | CONDICIONAL | NO |
| `ExternalReviewRequirement` | NO | NO | NO | CONDICIONAL |
| `LessonProductionEvaluationPlan` | NO | NO | NO | CONDICIONAL |
| `ProductionEvaluationCriterion` | NO | NO | NO | CONDICIONAL |
| `SemanticEvaluationRule` | NO | NO | NO | CONDICIONAL |
| Recursos o contratos subordinados aislados | NO | NO | NO | NO |

### Condiciones de `EXPOSURE_AVAILABLE`

La combinación mínima exige:

- `LessonCapabilityClaim`;
- `LessonStage.type` igual a `encounter` o `comprehension`;
- un artefacto realmente presentado en esa etapa;
- vínculo del claim con una Skill de `LessonExperience.skill_ids`.

Pueden participar `Example`, `Conversation`, `ConversationTurn`, `LanguageSupportItem`, `Mission` acompañada por contenido contextual y `PronunciationReinforcement` integrado. Una presentación audio-first es válida cuando la conversación o el turno está enlazado a la experiencia y su política de presentación es coherente.

Cuando el artefacto sea una actividad deberá aparecer en `LessonStage.activity_ids`. Debe pertenecer a la misma lección y preceder al punto que consuma la preparación.

No bastan metadata, `objective`, `vocabulary` o `grammar` no integrados en `LessonExperience`, `required_resource_ids`, `audio_asset`, `Pronunciation` aislada, un prompt de evaluación, `EvidenceDefinition`, `evaluation_plan` ni `Mission` sin contenido que presente la capacidad.

### Condiciones de `INSTRUCTION_AVAILABLE`

La combinación mínima v1 exige:

- `LessonCapabilityClaim`;
- `LessonStage.type="language_support"`;
- `LessonStage.instruction` no vacía;
- `LanguageSupportItem` o contenido instructivo asociado;
- vínculo explícito con la Skill.

Pueden intervenir `Example` usado como modelo, `Conversation` o `ConversationTurn` usado como modelo y `PronunciationReinforcement` con propósito instructivo funcional. Los apoyos deben referenciar la etapa mediante `LanguageSupportItem.stage_ids`; las actividades asociadas deben pertenecer a la etapa cuando corresponda.

Debe existir `EXPOSURE_AVAILABLE` antes. Una aparición textual, un `Example`, una conversación o `support_level="model"` aislados no constituyen instrucción.

Los contratos actuales distinguen estructuralmente la instrucción mediante `LessonStage(type="language_support") + instruction + contenido asociado`. Esta señal es suficiente para v1; su calidad semántica permanece bajo puerta humana.

### Condiciones de `PRACTICE_AVAILABLE`

La combinación mínima exige:

- `LessonCapabilityClaim`;
- una etapa de práctica;
- `activity_id` ejecutable declarado por la etapa;
- una acción observable del estudiante;
- vínculo con la Skill.

Son etapas admisibles:

- `comprehension`;
- `guided_production`;
- `assisted_response`;
- `applied_conversation`;
- `adaptive_feedback`, solo cuando introduce una nueva acción del estudiante.

Una etapa `evidence` no puede ser la primera práctica.

Pueden participar:

- `ExerciseMCQ`, si declara la Skill compatible;
- `Conversation` con `ConversationChoice`, cuando pertenece a una conversación ejecutable, está en una etapa compatible, ofrece una elección real del estudiante y existe vínculo con la Skill;
- `Conversation` con turno learner y `LearnerProductionPrompt`;
- `TransferPromptVariant`, solo como parte de un production prompt ejecutable;
- `PronunciationReinforcement`, cuando existe acción productiva real, como shadowing soportado por la experiencia.

Debe existir `INSTRUCTION_AVAILABLE` antes. No constituyen práctica la exposición pasiva, `Example`, transcript, `LanguageSupportItem`, audio aislado, conversación sin acción learner ni turno learner que solo presenta texto modelo sin elección o producción.

### Condiciones de `EVIDENCE_GATE_AVAILABLE`

La combinación mínima exige:

- `LessonCapabilityClaim`;
- `LessonStage.type="evidence"`;
- `EvidenceDefinition` válida;
- actividad ejecutable;
- vínculo explícito con la Skill;
- mecanismo de captura o resultado;
- mecanismo compatible de valoración.

Debe existir `PRACTICE_AVAILABLE` antes. Skill, stage, activity, production prompt cuando exista, modalidad, `evidence_type` y mecanismo de evaluación o revisión deben ser coherentes.

Una puerta basada en ejercicio evaluable requiere:

```text
EvidenceDefinition(evidence_type="exercise_result")
+ ExerciseMCQ
+ Skill asociada
+ measurement_mode compatible
+ criterio determinista de la actividad
```

Una producción conversacional evaluable automáticamente puede requerir:

```text
EvidenceDefinition
+ Conversation
+ learner ConversationTurn
+ LearnerProductionPrompt
+ LessonProductionEvaluationPlan
+ ProductionEvaluationCriterion
+ regla o analizador compatible
```

Una producción con revisión humana o externa puede requerir:

```text
EvidenceDefinition
+ actividad o LearnerProductionPrompt ejecutable
+ ExternalReviewRequirement compatible
```

Una `ConversationChoice` solo puede participar en esta puerta cuando forma parte de la actividad evaluable, existe una `EvidenceDefinition` compatible y hay un mecanismo de valoración que satisface las condiciones generales de evidencia.

`completion` puede registrar finalización, pero no equivale a éxito pedagógico. Cuando una Skill exige valoración cualitativa, `completion` por sí solo no constituye una puerta suficiente de calidad. Una `EvidenceDefinition` aislada nunca basta.

### Combinaciones explícitamente inválidas

Son inválidas, entre otras:

- `Mission` sola para `EXPOSURE_AVAILABLE`;
- `Example` o `Conversation` sin etapa para cualquier estado;
- metadata, `vocabulary`, `grammar` u `objective` para `EXPOSURE_AVAILABLE`;
- `audio_asset` o `Pronunciation` aislados para exposición o práctica;
- `LanguageSupportItem` sin etapa instructiva para `INSTRUCTION_AVAILABLE`;
- mera aparición de una forma para `INSTRUCTION_AVAILABLE`;
- `Conversation` sin acción learner para `PRACTICE_AVAILABLE`;
- reproducción pasiva o transcript para `PRACTICE_AVAILABLE`;
- `LearnerProductionPrompt` o `TransferPromptVariant` aislados para práctica o evidencia;
- `ExerciseMCQ` sin vínculo con la Skill para práctica o evidencia de esa Skill;
- etapa `evidence` usada como primera exposición, instrucción o práctica;
- `EvidenceDefinition` sin actividad ejecutable para `EVIDENCE_GATE_AVAILABLE`;
- `evaluation_plan`, criterio, regla o revisión aislados para `EVIDENCE_GATE_AVAILABLE`;
- producción sin prompt, modalidad o valoración compatibles para `EVIDENCE_GATE_AVAILABLE`;
- `completion` interpretado como éxito;
- cualquier estado curricular interpretado como evidencia positiva, aprendizaje o mastery.

### Casos ambiguos

#### `Conversation`

Puede participar en exposición, instrucción, práctica o evidencia según la etapa, la acción learner, el claim y la `EvidenceDefinition` o evaluación aplicable. No se crearán variantes de clase por función.

#### `ConversationTurn`

Un partner turn puede participar en exposición; un learner turn con `ConversationChoice`, en práctica; y un learner turn con `LearnerProductionPrompt`, en práctica o evidencia según el contexto. El texto aislado no enseña ni evalúa.

#### `ConversationChoice`

Puede participar en práctica cuando representa una elección real dentro de una `Conversation` ejecutable, vinculada con la Skill y situada en una etapa compatible. Puede participar en evidencia únicamente dentro de una actividad evaluable con `EvidenceDefinition` y mecanismo de valoración compatibles. No puede justificar `EXPOSURE_AVAILABLE` ni `INSTRUCTION_AVAILABLE`; que su texto sea visible no convierte la elección en un artefacto canónico de exposición o instrucción.

#### `ExerciseMCQ`

Puede participar en práctica o evidencia, pero su existencia no permite inferir ambas funciones. Si se reutiliza, los claims y puntos curriculares deben ser explícitos, y la puerta humana debe comprobar que la misma ejecución no actúe indebidamente como primera preparación y evaluación.

#### `LanguageSupportItem`

Puede participar en exposición o instrucción según stage, instruction y claim. No constituye práctica.

#### `PronunciationReinforcement`

Puede participar en exposición, instrucción o práctica funcional según su integración. No justifica `EVIDENCE_GATE_AVAILABLE` por sí solo.

### Límites conocidos de los contratos actuales

1. `INSTRUCTION_AVAILABLE` v1 se reconoce mediante `LessonStage(type="language_support") + instruction + contenido asociado`.
2. No toda `EvidenceDefinition` actual dispone de un mecanismo general de valoración cualitativa: `evaluation_plan` se orienta a producciones conversacionales, `ExternalReviewRequirement` tiene dimensiones acotadas y `completion` no valora calidad.

Estos límites no exigen ampliar el contrato curricular v1. Cuando no exista evaluación o revisión compatible, una evidencia no puede justificar `EVIDENCE_GATE_AVAILABLE` para una Skill que requiera valoración de calidad.

### Norma aprobada de compatibilidad

> Un `LessonCapabilityClaim` solo podrá justificar un `CurriculumPreparationState` mediante una combinación permitida de etapa, artefacto y relaciones existentes. Ningún artefacto aislado determina por sí solo su función pedagógica. `EXPOSURE_AVAILABLE` exige presentación contextual accesible; `INSTRUCTION_AVAILABLE`, una etapa instructiva con enseñanza o apoyo explícito; `PRACTICE_AVAILABLE`, una actividad ejecutable con acción observable del estudiante; y `EVIDENCE_GATE_AVAILABLE`, una `EvidenceDefinition` vinculada con una actividad ejecutable, la Skill, la modalidad y un mecanismo compatible de evaluación o revisión. Metadata, recursos, audios, textos, prompts, criterios o definiciones aislados no justifican estados curriculares. La validez estructural no implica calidad pedagógica, ejecución, evidencia positiva, aprendizaje ni mastery.

La compatibilidad estructural no decide si el contenido es pedagógicamente bueno. Esa decisión permanece en la puerta humana.

## Relación con contratos existentes

### Reutilizar

- `SkillSpecification` como identidad de Skill;
- `PedagogicalUnitCandidate` como contenedor aislado;
- `LessonExperience` y su orden de etapas;
- `EvidenceDefinition` como contrato de puerta evaluativa;
- `evaluation_plan` para criterios aplicables;
- `validation_report` para findings reproducibles;
- aislamiento de candidatas respecto al contenido activo;
- puerta humana previa a publicación.

### Evolucionar posteriormente

- `SkillCoverage`, para que deje de ser una declaración agregada de presencia y pueda derivarse de claims validados;
- `PedagogicalUnitSpecification.prerequisites`, actualmente demasiado libre para expresar Skill, estado y punto de consumo;
- la asociación entre cada lección candidata y su `LessonCapabilityPlan`.

Estas evoluciones quedan definidas conceptualmente, no implementadas por este contrato documental.

### No tocar en v1

- producciones individuales;
- persistencia de evaluaciones;
- revisiones humanas runtime;
- contratos semánticos y fonéticos;
- `feedback_plan`;
- runtime conversacional;
- progreso individual;
- mastery;
- retención;
- adaptación;
- contratos específicos de B180 o B181.

## Responsabilidades

### Validación determinista

Puede comprobar:

- nivel CEFR reconocido y secuencia canónica;
- unicidad y pertenencia jerárquica de niveles, unidades y lecciones;
- presencia exacta de la candidata en el contexto ordenado;
- completitud del contexto y posición curricular derivada;
- precedencia entre claim productor y punto consumidor;
- claims todavía no disponibles y dependencias futuras;
- coherencia entre el ledger de salida de una lección y el ledger de entrada de la siguiente;
- formato y unicidad del identificador de Skill;
- descripción no vacía;
- identidad y existencia de referencias;
- tipo y pertenencia de los artefactos;
- tipo y orden de `LessonStage`;
- relaciones mediante `activity_ids` y `LanguageSupportItem.stage_ids`;
- uso real de Skills en claims, evidencias o prerrequisitos;
- Skills declaradas pero nunca utilizadas;
- duplicados exactos o normalizados;
- orden y precedencia;
- pertenencia contextual de artefactos;
- compatibilidad estructural entre estado y artefacto;
- presencia de acción learner, choices y production prompts;
- coherencia de modalidades;
- existencia y relaciones de `EvidenceDefinition`;
- coincidencia de Skill, stage, activity y prompt;
- presencia de evaluación o revisión compatible;
- saltos de preparación;
- satisfacción de prerrequisitos;
- ciclos directos e indirectos;
- presencia de enseñanza, práctica y puerta de evidencia;
- usos inválidos de metadata o recursos aislados;
- que `completion` no se interprete estructuralmente como éxito;
- coherencia estructural entre Skill, modalidad, actividad, evidencia y evaluación.

No puede decidir automáticamente si la granularidad pedagógica de una Skill es correcta. Tampoco puede comprobar por sí sola calidad instructiva, claridad, suficiencia de práctica, naturalidad, carga cognitiva, calidad de distractores, adecuación pedagógica, que la evidencia mida sustantivamente la Skill ni aprendizaje real.

### Constructor con IA futuro

Una futura IA podrá proponer Skills, detectar posibles capacidades monolíticas, sugerir descomposición, advertir atomización léxica o gramatical, detectar solapamientos y proponer Skills integradoras, prerrequisitos, `LessonCapabilityPlan`, actividades, evidencias, razones y correcciones a findings.

La IA deberá generar candidatas dentro del contrato. No podrá alterar el ledger calculado, inventar estados sin artefactos, saltarse prerrequisitos, aprobar su propia candidata ni convertir disponibilidad curricular en aprendizaje del estudiante.

Su regla de granularidad será:

> Crear una Skill solo para una conducta observable, practicable y evidenciable con valor curricular reutilizable; no convertir elementos lingüísticos aislados en Skills y descomponer toda capacidad cuyos componentes puedan prepararse, fallar o reutilizarse independientemente.

Este documento no diseña prompts, modelos, clientes ni integración con IA.

### Puerta humana

Debe revisar:

- valor pedagógico autónomo, granularidad y separabilidad de Skills;
- suficiencia de la evidencia propuesta para distinguir cada Skill;
- utilidad curricular de modelar una capacidad independientemente;
- casos fronterizos fonéticos, gramaticales o receptivos;
- mantenibilidad del grafo resultante;
- validez pedagógica de prerrequisitos y razones;
- calidad y comprensibilidad de la enseñanza;
- suficiencia y autenticidad de la práctica;
- validez de la puerta de evidencia;
- que cada artefacto desempeñe realmente la función declarada por el claim;
- cualquier reutilización de un mismo artefacto en varios estados;
- que `completion` no sustituya una valoración cualitativa cuando sea necesaria;
- carga cognitiva y progresión;
- lenguaje y UX;
- adecuación al estudiante objetivo;
- autorización explícita de publicación.

La puerta humana decide la validez pedagógica de los prerrequisitos aunque su identidad, posición y precedencia sean estructuralmente válidas.

Una candidata estructuralmente válida puede ser rechazada por la puerta humana. La aprobación humana no convierte preparación curricular en aprendizaje ni debe ocultar errores deterministas.

## Ejemplos abstractos

Los identificadores siguientes son ficticios y no diseñan contenido real.

### Válido 1 — preparación completa en orden

Una lección declara para `skill_alpha`:

```text
EXPOSURE_AVAILABLE       <- stage-1/context-item
INSTRUCTION_AVAILABLE    <- stage-2/instruction-item
PRACTICE_AVAILABLE       <- stage-3/practice-activity
EVIDENCE_GATE_AVAILABLE  <- stage-4/evidence-definition
```

Los artefactos existen, son compatibles y aparecen en ese orden. La puerta de evidencia tiene su `EvidenceDefinition` y contrato de evaluación o revisión. El ledger puede terminar la lección en `EVIDENCE_GATE_AVAILABLE`, sin afirmar que ningún estudiante recorrió la experiencia.

### Válido 2 — requisito satisfecho por una lección anterior

La primera lección deja `skill_beta` en `PRACTICE_AVAILABLE`. La segunda declara:

```text
required_skill_id: skill_beta
required_state: PRACTICE_AVAILABLE
before_stage_id: null
reason: "La nueva actividad necesita recuperar esta capacidad previamente practicable."
```

El ledger de entrada de la segunda lección satisface el requisito.

### Inválido 1 — primera aparición en evaluación

`skill_gamma` no tiene claims anteriores. Su primer artefacto es una `EvidenceDefinition` dentro de una evaluación. Se rechaza porque faltan exposición, instrucción y práctica previas; la evaluación no puede introducir lo que pretende valorar.

### Inválido 2 — práctica sin instrucción

Una lección declara `PRACTICE_AVAILABLE` para `skill_delta`, pero el ledger solo contiene `EXPOSURE_AVAILABLE` y no existe claim instructivo anterior. Se rechaza por salto de preparación.

### Inválido 3 — requisito ausente del ledger

La segunda lección exige `skill_epsilon` en `PRACTICE_AVAILABLE`, pero las lecciones anteriores no produjeron ese estado. Que una cadena relacionada aparezca en un texto previo no satisface el requisito.

### Inválido 4 — ciclo entre Skills

```text
skill_zeta requiere skill_eta en INSTRUCTION_AVAILABLE
skill_eta requiere skill_zeta en INSTRUCTION_AVAILABLE
```

Ninguna puede prepararse sin consumir previamente la otra. El ciclo se rechaza aunque las relaciones estén distribuidas entre varias lecciones.

### Inválido 5 — confundir puerta disponible con evidencia positiva

Existe una `EvidenceDefinition` válida para `skill_theta`. Esto permite declarar `EVIDENCE_GATE_AVAILABLE` si también existe la preparación previa requerida.

No permite declarar que:

- un estudiante produjo evidencia;
- la evidencia fue revisada;
- el resultado fue positivo;
- la Skill quedó evidenciada o dominada.

Producción, revisión y resultado pertenecen al runtime y deben conservar sus identidades separadas.

## Origen de la necesidad

B181 aportó evidencia histórica de que una candidata puede ser estructuralmente consistente y, aun así, exigir capacidades que el currículo previo no preparó. Este contrato responde a esa clase general de defecto; no rediseña ni repara B181.

## Regla anti-parche

Cuando evidencia humana revele un problema generalizable, primero deberá evaluarse si corresponde mejorar el contrato, los prerrequisitos, los validadores, las reglas del Constructor o los criterios de la puerta humana antes de parchear contenido aislado.

## Fuera de alcance de v1

V1 asume explícitamente un currículo canónico lineal. Quedan fuera de alcance:

- mastery probabilístico;
- knowledge tracing;
- retención;
- spaced repetition;
- adaptación individual;
- rutas opcionales o ramificadas;
- currículo adaptativo;
- scheduling;
- DAG general de itinerarios;
- prerrequisitos dinámicos;
- progreso individual;
- equivalencias entre rutas;
- planner automático;
- versionado temporal complejo;
- recomendadores;
- embeddings;
- LLM;
- MCP;
- generación automática;
- promoción automática;
- circuito automático runtime → Constructor;
- taxonomía runtime de estados individuales del estudiante.

## Decisiones humanas pendientes antes de implementar

Quedan resueltas y aprobadas mediante las normas de este documento:

1. la granularidad canónica de Skill;
2. la compatibilidad entre artefactos y `CurriculumPreparationState`;
3. el orden curricular intraunidad, interunidad e internivel.

Ninguna decisión humana conceptual pendiente identificada para el contrato v1.

Esto no aprueba todavía la implementación. Antes de abrirla deberá realizarse una revisión humana final integral de este documento.
