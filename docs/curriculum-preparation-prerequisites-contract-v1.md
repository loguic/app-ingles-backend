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

## Candidate admission and active source membership v1

Esta sección define qué revisión de una `PedagogicalUnitCandidate` puede ser elegible y qué significa publicarla en la fuente productiva. No define todavía modelos, archivos, loaders ni formato físico.

### Vocabulario y separación de estados

- **candidate artifact**: representación física de un candidate payload;
- **candidate payload**: contenido interpretable como `PedagogicalUnitCandidate`;
- **local validation**: resultado recalculado por `validate_pedagogical_candidate(...)` sobre ese payload concreto;
- **human review**: revisión humana pedagógica y lingüística explícita;
- **admitted candidate revision**: revisión exacta que satisfizo las condiciones de admisión y puede publicarse;
- **published / active source member**: revisión admitida incorporada explícitamente al snapshot productivo activo.

La expresión «approved candidate» deberá evitarse sin calificador porque no distingue revisión humana, admisión y publicación. Se mantiene obligatoriamente:

```text
candidate exists
!= candidate parseable
!= candidate locally valid
!= candidate human reviewed
!= candidate admitted
!= candidate published
!= candidate curricularly compatible at target
```

Admission establece la elegibilidad de una revisión exacta. Publication establece su pertenencia efectiva a la fuente activa. Una revisión admitida puede no estar todavía publicada.

### Puertas de admission

La admisión v1 exige conjuntamente:

1. payload interpretable mediante el contrato de `PedagogicalUnitCandidate` aplicable;
2. `validate_pedagogical_candidate(candidate).status == "passed"`, recalculado sobre el payload exacto;
3. `candidate.pending_human_decisions == []`;
4. revisión humana final y decisión explícita `admitted` sobre esa revisión exacta.

Local validation passed es condición necesaria, pero no suficiente. El `validation_report` embebido puede quedar obsoleto porque no está ligado contractualmente a una revisión o digest; por ello no demuestra admission y deberá recalcularse durante el proceso de admisión.

Las únicas decisiones humanas finales son `admitted` y `rejected`. Pending se representa mediante ausencia de decisión final. La mera existencia de un documento de human review no constituye admission machine-readable y no existen excepciones silenciosas para decisiones humanas pendientes.

### Identidad exacta y admission record

`unit_id` no identifica suficientemente el payload revisado. La identidad conceptual mínima de una revisión admitida incluye:

- `unit_id`;
- `candidate_revision` machine-readable;
- `payload_schema_version`;
- `content_digest`.

Un filename como `pedagogical-unit-candidate-v2.json` no define `candidate_revision` ni `payload_schema_version`. Tampoco deberá reutilizarse `LessonExperience.contract_version` como versión del payload completo.

`candidate_revision` es un string opaco, machine-readable, no vacío y no compuesto exclusivamente por whitespace, suministrado externamente. Se valida que `candidate_revision.strip() != ""`, pero su valor se conserva literalmente sin strip, lowercase, slugification ni otra normalización. No se deriva del filename, `payload_schema_version`, digest, timestamp ni posición curricular, y no expresa orden curricular o de publication.

#### Canonical admission payload v1

El canonical admission payload identifica exclusivamente el contenido pedagógico/autoral concreto sometido a review y admission; no equivale a serializar `PedagogicalUnitCandidate` completo sin distinguir responsabilidades. La proyección v1 incluye exactamente:

- `specification`;
- `candidate_unit`;
- `evaluation_plans`;
- `feedback_plans`;
- `lesson_capability_plans`;
- `skill_coverage`;
- `required_resource_ids`.

Para esta identidad se clasifican como **pedagogical/authored payload** esos siete campos; como **derived validation metadata**, `validation_report`; y como **human/editorial process metadata**, `pending_human_decisions` y `proposed_change_summary`. Esta clasificación no modifica el schema de `PedagogicalUnitCandidate`.

`validation_report` queda excluido de la proyección: es metadata derivada que `validate_pedagogical_candidate(...)` recalcula y no contenido autoral. Incluirlo introduciría la dependencia circular payload digest → local validation → report → payload digest. La validación local recalculada con status `passed` sigue siendo un gate obligatorio, pero su resultado no participa en la identidad canónica.

`pending_human_decisions` queda excluido porque representa proceso de review y funciona como gate: cualquier valor no vacío impide admission, aunque resolverlo sin cambiar contenido pedagógico no crea por sí solo una nueva identidad. `proposed_change_summary` también queda excluido porque describe editorialmente cambios propuestos; modificar solo el resumen no cambia el digest. Si resolver una decisión o aplicar un cambio altera cualquier campo incluido, sí cambia potencialmente la identidad canónica.

El literal inicial `payload_schema_version = "1.0"` identifica exclusivamente esta proyección v1 para calcular identidad. No es la versión general de `PedagogicalUnitCandidate`, `LessonExperience.contract_version`, `candidate_revision`, versión curricular, revisión de publication ni versión de filename, y no se añade al candidate. La futura metadata de identidad/admission lo portará externamente. Todo cambio futuro en los datos incluidos o en su interpretación semántica que pueda alterar la identidad exige una nueva `payload_schema_version`; v1 no define una política SemVer general.

`candidate_revision`, `payload_schema_version`, `content_digest` y `unit_id` son dimensiones distintas: respectivamente identificador operativo de revisión, versión del contrato de proyección, identidad criptográfica del contenido canónico e identidad curricular nominal. Ninguna sustituye a las demás.

Excluir metadata del digest no permite ignorarla durante admission: canonical payload define identidad del contenido pedagógico y admission gates define las condiciones para autorizarla. Un cambio limitado a `validation_report`, `pending_human_decisions` o `proposed_change_summary` no cambia por sí mismo la identidad; tampoco elimina la obligación de recalcular validation, resolver decisiones pendientes y completar human review.

#### Canonical serialization and content digest v1

La representación v1 se construye mediante una whitelist explícita con exactamente las siete keys enumeradas en la proyección anterior. No se serializa el `PedagogicalUnitCandidate` completo para excluir campos después: ningún campo futuro entrará accidentalmente en `payload_schema_version = "1.0"`. El orden escrito de las keys no aporta semántica porque los mappings se canonicalizan al serializar.

Cada componente modelado parte de su instancia Pydantic ya validada y se proyecta con comportamiento equivalente a:

```text
model_dump(
    mode="json",
    by_alias=False,
    exclude_unset=False,
    exclude_defaults=False,
    exclude_none=False,
    round_trip=False,
    serialize_as_any=False,
)
```

Esta regla usa nombres reales de campos, produce valores JSON-compatible e incluye defaults, valores normalizados aunque estuvieran unset en el input y `None` como JSON `null`. La identidad depende del estado modelado validado, no de cómo fue escrito el artifact de origen. Una implementación compatible no necesita exponer literalmente esa llamada, pero deberá producir exactamente la misma representación contractual.

Todos los mappings neutralizan recursivamente su orden de keys. Todas las lists/sequences conservan exactamente su orden modelado, sin sorting, deduplication, conversión a set ni normalización lexical, incluido `required_resource_ids`. Sequence order puede formar parte de la identidad modelada y no equivale a curriculum order.

El canonical JSON se produce con comportamiento equivalente a:

```text
json.dumps(
    canonical_payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
```

No contiene indentación, pretty printing, whitespace adicional, trailing spaces ni newline final. No se aplica normalización Unicode NFC/NFD: strings visualmente equivalentes con secuencias Unicode distintas pueden producir digests distintos deliberadamente. El JSON se codifica en UTF-8 sin BOM, newline ni terminador adicional; las reglas de EOF de archivos no aplican a estos bytes en memoria.

Los floats proceden de modelos Pydantic ya validados y siguen la representación numérica del runtime Python 3.12 soportado por v1. No se usan `Decimal`, quantization, redondeo artificial ni RFC 8785/JCS. Los campos tipados como float se serializan como float; `0.0` y `-0.0` permanecen distintos si así existen en el modelo. NaN e Infinity no son válidos y `allow_nan=False` actúa fail-closed. Una implementación en otro lenguaje deberá reproducir exactamente estos bytes y no podrá asumir que su serializer JSON por defecto es compatible.

`canonical_bytes` son exclusivamente el canonical JSON anterior codificado en UTF-8. El preimage de SHA-256 contiene exclusivamente esos bytes derivados de las siete keys. No incluye adicionalmente `candidate_revision`, `payload_schema_version`, un `unit_id` externo, `reviewer_id`, `admission_id`, metadata de publication/snapshot ni prefijo de domain separation. `unit_id` ya está representado dentro de `specification` y `candidate_unit`; dos revisions operativas con contenido canónico idéntico comparten `content_digest`.

`payload_schema_version` y `content_digest` se interpretan conjuntamente: la primera identifica la receta/proyección y el segundo el contenido producido bajo ella. La versión no es un octavo dato del payload ni participa en el preimage. `content_digest` aislado no identifica completamente el contrato de canonicalización. Todo cambio futuro de boundary, normalization, JSON, numbers o cualquier regla capaz de cambiar canonical bytes exige una nueva versión y nunca modifica retrospectivamente `"1.0"`.

El digest se calcula como SHA-256 de `canonical_bytes` y se representa exactamente como `sha256:<64 lowercase hexadecimal characters>`, conforme a `^sha256:[0-9a-f]{64}$`, sin uppercase, espacios ni multihash. Aporta identidad e integridad del contenido canónico; no equivale a admission, firma, MAC, prueba de autenticidad, publication ni membership.

Una proyección que no pueda representarse conforme a v1, incluyendo NaN, Infinity o un tipo incompatible con JSON v1, deberá fallar sin producir silenciosamente otro digest. Este contrato no fija todavía clase de excepción, enum ni wrapper de source integrity; la derivación futura recibirá un `PedagogicalUnitCandidate` ya validado y no reparseará artifacts.

Toda implementación de `payload_schema_version = "1.0"` deberá protegerse con al menos un golden vector que fije canonical payload conocido, canonical bytes conocidos y `content_digest` literal conocido. El vector concreto se establecerá con la primera implementación y formará parte de la compatibilidad v1.

#### Candidate payload identity v1

`CandidatePayloadIdentity` es un value object machine-readable e inmutable que contiene exactamente:

- `unit_id`: `str`;
- `candidate_revision`: `str`;
- `payload_schema_version`: `str`;
- `content_digest`: `str`.

`unit_id` es el identificador curricular nominal de la unidad, cumple el contrato ya definido por `PedagogicalUnitSpecification` y se deriva internamente de `candidate.specification.unit_id`; no lo aporta separadamente el caller. `unit_id`, `candidate_revision`, `payload_schema_version` y `content_digest` son dimensiones distintas.

`candidate_revision` es un string machine-readable, obligatorio, no vacío ni exclusivamente whitespace, suministrado por el caller y preservado literalmente. Se valida que `candidate_revision.strip() != ""`, pero no se almacena con trim ni se normaliza mediante lowercase o slugification. No se deriva de filename, timestamp ni orden curricular.

`payload_schema_version` es un string. La única derivación autorizada por este contrato produce `"1.0"`, proveniente del contrato/canonicalizer y no del caller: identifica `Canonical admission payload v1` y `Canonical serialization and content digest v1`, no `candidate_revision`, `LessonExperience.contract_version`, orden curricular ni orden de publication. `CandidatePayloadIdentity` podrá portar una futura `payload_schema_version` cuando un contrato posterior la defina; `AdmissionRecord` no hardcodea `"1.0"` como única versión válida para siempre.

`content_digest` es un string. Para `payload_schema_version == "1.0"` cumple exactamente `^sha256:[0-9a-f]{64}$` y representa el SHA-256 de los canonical bytes definidos por `Canonical serialization and content digest v1`. Aporta identidad e integridad del contenido canónico; no significa admission, aprobación humana, signature, authenticity, publication ni membership.

La capacidad de derivación v1 conforme construye la identidad con `unit_id` derivado internamente de `candidate.specification.unit_id`, `candidate_revision` recibido del caller, `payload_schema_version` recibido del contrato vigente y `content_digest` recibido de la derivación canónica vigente. El caller no suministra arbitrariamente `unit_id`, `payload_schema_version` ni `content_digest`.

Una `CandidatePayloadIdentity` conforme satisface las invariantes de sus cuatro campos y, una vez construida, sus componentes no cambian. Que exista una representación Python manualmente construible no altera este contrato: una instancia que viole esas invariantes no es una `CandidatePayloadIdentity` conforme. Este contrato no exige que cada consumidor recalcule o revalide todos sus componentes.

`CandidatePayloadIdentity` es únicamente identidad machine-readable del payload canónico. No significa local validation passed, human reviewed, admitted, rejected, published, active member ni authoritative validation passed. No define JSON file, database row, filesystem path, API resource ni manifest entry.

Un consumidor como `AdmissionRecord` recibe una `CandidatePayloadIdentity` conforme ya establecida. No canonicaliza nuevamente el candidate, no recalcula `content_digest`, no reconstruye `candidate_revision`, no duplica `unit_id` ni vuelve a ejecutar la derivación: responsabilidad de `CandidatePayloadIdentity` != responsabilidad de `AdmissionRecord`.

#### Admission decision record v1

`AdmissionRecord` representa machine-readably una decisión humana final e inmutable sobre una `CandidatePayloadIdentity` exacta. Es independiente de `PedagogicalUnitCandidate`, local validation, human-review artifacts, publication y membership, y contiene exactamente:

- `admission_id`;
- `identity`: `CandidatePayloadIdentity`;
- `decision`;
- `reviewer_id`;
- `decided_at`.

`identity` compone unit, candidate revision, payload schema version y digest ya derivados; el record no los repite como campos planos, no recibe `unit_id` separado, no reconstruye revision ni recalcula digest. La dirección de dependencia es `AdmissionRecord` → `CandidatePayloadIdentity`, nunca la inversa.

`admission_id` es el identificador machine-readable estable del record. Es string opaco, obligatorio, no vacío ni exclusivamente whitespace, caller-provided y preservado literalmente. No se normaliza ni deriva de UUID, ULID, timestamp, filesystem path, curriculum order o publication order. No se define aún mecanismo global de unicidad, repositorio ni allocator: una futura source/membership deberá detectar referencias duplicadas o ambiguas en su colección. El ID permite que future active membership refiera inequívocamente el record sin depender de path, storage o composición reviewer/timestamp.

Las únicas decisiones finales almacenables son `admitted` y `rejected`; pending sigue significando ausencia de decisión final. `decision="admitted"` significa únicamente que una persona registró una decisión humana favorable sobre esa identity:

```text
recorded human decision
!= verified admission gates
```

No demuestra por sí sola local validation `passed`, `pending_human_decisions == []`, todos los gates de admission, publication, active membership ni validación curricular autoritativa. Una capacidad posterior podrá verificar esos gates sobre identity, candidate y record. `decision="rejected"` es un hecho final válido de historial/auditoría, pero nunca puede justificar active source membership.

`reviewer_id` es string opaco, obligatorio, no vacío ni exclusivamente whitespace y preservado literalmente. No se normaliza ni exige email, username schema, auth, RBAC o namespace de identity provider. La trazabilidad humana mínima del record es identity exacta, decision, reviewer ID, timestamp y admission ID; v1 no exige `human_review_id`, artifact path, referencia Markdown ni parser de documentos. La presencia de un human-review artifact por sí sola no equivale a `AdmissionRecord`.

`decided_at` es `datetime` timezone-aware en UTC: debe tener `tzinfo` efectivo y `utcoffset() == timedelta(0)`. Datetimes naive o con offset distinto de cero son inválidos; se aceptan tzinfo equivalentes a UTC sin normalizar obligatoriamente el objeto recibido. Los microsegundos se permiten y preservan. El timestamp sirve solo para auditoría y no determina curriculum order, candidate revision order, publication precedence ni source membership order.

Machine-readable en esta etapa significa representación tipada, campos e invariantes deterministas e integración explícita con `CandidatePayloadIdentity`; no define todavía JSON, JSON Schema, database row, filesystem path, manifest entry ni API resource. `AdmissionRecord` confía en la identity ya recibida: no canonicaliza candidate, valida source artifacts, ejecuta `validate_pedagogical_candidate` ni reevalúa sus garantías. La futura source integrity podrá comprobar un payload físico contra su identity.

Los gates permanecen fuera de la representación: ejecutar local validation, comprobar status `passed`, leer o resolver `pending_human_decisions`, parsear human review, publication, membership y snapshot. Esto no elimina los gates del contrato general; separa record representation de gate verification. No se añaden provenance, generator, reason, comments, notes, signature, approval chain, role, tenant u organization en v1.

Admission se aplica solo a la combinación exacta de revision y digest. Un cambio del payload pedagógico exige nueva validación local, revisión humana y decisión; una variación física que conserve el payload canónico no invalida la decisión.

#### Admission gate verification v1

Esta capacidad verifica pura y determinísticamente si una decisión humana favorable está respaldada por todos los gates contractuales de admission para un `PedagogicalUnitCandidate` proporcionado. No representa publication, active source membership ni validación curricular autoritativa.

Sus únicos inputs son `candidate: PedagogicalUnitCandidate` y `admission_record: AdmissionRecord`. No recibe `CandidatePayloadIdentity`, `unit_id`, `candidate_revision`, `payload_schema_version` ni digest separados: la identity aplicable es exclusivamente `admission_record.identity`. Recibir un `PedagogicalUnitCandidate` ya construido y validado por Pydantic satisface aquí la precondición de payload interpretable. Errores previos de lectura, JSON, parsing, schema o acquisition pertenecen a candidate source/acquisition integrity y quedan fuera.

Para v1 existen exactamente cuatro gates, sin condiciones ocultas ni quinto gate:

1. `identity_matches`;
2. `local_validation_passed`;
3. `pending_human_decisions_clear`;
4. `human_decision_admitted`.

`identity_matches` exige recalcular exactamente una `CandidatePayloadIdentity` con `candidate` y `candidate_revision=admission_record.identity.candidate_revision`. La revisión procede exclusivamente del `AdmissionRecord` y nunca se inventa. Para una versión de payload soportada, el gate es true únicamente si la equality estructural completa satisface `derived_identity == admission_record.identity`; por tanto compara conjuntamente `unit_id`, `candidate_revision`, `payload_schema_version` y `content_digest`, nunca solo el digest. Esto demuestra que el candidate proporcionado produce la identidad del record bajo esa revisión; no demuestra que un artifact físico hubiera declarado esa revisión, responsabilidad futura de source integrity.

La derivación v1 disponible soporta únicamente `payload_schema_version == "1.0"`. Antes de recalcular identity, una `admission_record.identity.payload_schema_version` no soportada es un error técnico explícito de verificación, no un identity mismatch ni un gate negativo. Mientras solo exista el canonicalizer `"1.0"`, toda versión distinta debe fallar explícitamente —la implementación mínima podrá usar `ValueError`— sin reinterpretarla con v1, crear finding curricular ni devolver `identity_matches=False`. Un contrato posterior podrá ampliar las versiones soportadas; v1 no crea registry ni framework de versiones.

`local_validation_passed` exige ejecutar exactamente una vez `validate_pedagogical_candidate(candidate)` y usar únicamente su `ValidationReport` recién producido. El gate es true solo si su `status == "passed"`; `"failed"` y `"pending"` son conclusiones negativas normales. `candidate.validation_report` embebido no es evidencia suficiente y debe ignorarse como fuente de verdad: puede estar stale. La verificación no muta ese report del candidate.

`pending_human_decisions_clear` es true exactamente si `candidate.pending_human_decisions == []`. Una lista no vacía produce false como conclusión normal; no se transforma en `ValidationStatus`, finding ni estado pending del `AdmissionRecord`. `human_decision_admitted` es true exactamente si `admission_record.decision == "admitted"`. `decision="rejected"` produce false como decisión humana válida, no como error técnico, record inválido ni source error. `admission_id`, `reviewer_id` y `decided_at` preservan trazabilidad del record, pero no son gates: no se autorizan reviewer, comparan timestamps, ordenan decisiones ni se usan para matching de payload.

El resultado machine-readable v1 es el value object lógico e inmutable `AdmissionGateVerification`, con exactamente estos campos de evidencia:

- `derived_identity: CandidatePayloadIdentity`;
- `admission_record: AdmissionRecord`;
- `local_validation_report: ValidationReport`;
- `identity_matches: bool`;
- `local_validation_passed: bool`;
- `pending_human_decisions_clear: bool`;
- `human_decision_admitted: bool`.

`verified` no es un campo almacenado ni caller-provided: es una conclusión derivada exactamente como `identity_matches and local_validation_passed and pending_human_decisions_clear and human_decision_admitted`. El resultado conserva la identity derivada y el report local recalculado para auditoría, pero no copia innecesariamente candidate completo, pending decisions ni metadata de reviewer ya presente en `AdmissionRecord`. No es un `ValidationReport` y no crea `ValidationFinding`, `validator_id`, severity, `ValidationStatus`, publication, membership ni source state.

Identity mismatch, validation local `"failed"` o `"pending"`, pending decisions no vacías y decisión `"rejected"` son resultados válidos con `verified == false`, no excepciones. Version de payload no soportada, error de derivación de identity, violación inesperada de invariantes o excepción inesperada del validador son errores técnicos que deben propagarse explícitamente; no se degradan a `verified=false` porque distinguen un gate no satisfecho de una verificación no ejecutable o no confiable.

Para una versión soportada se evalúan los cuatro gates completos, sin short-circuit por rechazo, identity mismatch, pendientes o validation no passed: se realiza exactamente una derivación de identity y una recalculación de local validation para conservar evidencia completa. La comprobación de versión soportada ocurre antes porque una versión desconocida impide una verificación identitaria correcta.

La verificación es pura respecto a I/O: no accede a filesystem, environment, DB, network, clock, random, Markdown review, candidate source ni manifest; no muta candidate, `AdmissionRecord`, `CandidatePayloadIdentity` ni `ValidationReport`. Machine-readable aquí significa entidad tipada, evidencia estructurada e invariantes deterministas, no JSON persistido, formato filesystem, DB model, API resource ni manifest entry.

`AdmissionGateVerification.verified == true` no equivale a publication, active source membership ni authoritative prerequisite validation. No comprueba artifact físico, revisión declarada físicamente, digest contra bytes de archivo, duplicados de `AdmissionRecord`, unicidad global de `admission_id` ni membership declaration; esas responsabilidades permanecen posteriores. Tampoco ejecuta ni reinterpreta slices 25–29. A1-U1 permanece pending / non-member: esta capacidad no se ejecuta sobre ese artifact ni infiere verified admission.

#### Active candidate membership v1

`ActiveCandidateMembership` es el value object lógico, machine-readable e inmutable que declara el estado activo actual de una revisión exacta incorporada a la fuente productiva. No representa evento ni historial de publication, acción de publisher, snapshot completo, source integrity ni posición curricular. Contiene exactamente:

- `identity: CandidatePayloadIdentity`;
- `admission_id: str`.

No contiene `active`, `publication_id`, timestamp, actor, reviewer, `AdmissionRecord`, `AdmissionGateVerification`, `ValidationReport`, candidate, status, findings, `source_id`, ordinal, position ni `snapshot_id`. Que una instancia se denomine active membership ya expresa su estado activo; la metadata de reviewer, decisión y timestamp permanece exclusivamente en el `AdmissionRecord` referido por `admission_id`.

La única derivación conceptual v1 es `declare_active_candidate_membership(admission_verification: AdmissionGateVerification) -> ActiveCandidateMembership`. Consume exclusivamente esa verification, sin recibir identity, admission ID, unit, revision, digest, candidate ni record separados. Su precondición es `admission_verification.verified is True`; si es false, no existe una membership que construir y la implementación futura deberá fallar explícitamente como violación de precondición/invariante —por ejemplo, mediante `ValueError`—, nunca devolver una membership inactiva, status, finding, `None` silencioso ni resultado negativo paralelo.

Una derivación válida conserva exactamente `identity=admission_verification.derived_identity` y `admission_id=admission_verification.admission_record.admission_id`. Con `verified=True`, la identity derivada ya coincide estructuralmente con la identity del record; la factory no la recalcula, no compara digest, no vuelve a ejecutar admission gates, local validation, pending decisions o decision humana, ni revalida schema version. Evidence ya demostrada no se recalcula por cada consumidor.

La creación de un `ActiveCandidateMembership` válido es la declaración machine-readable de que esa revisión exacta pasó a ser miembro activo: verified admission más esta declaración establece el salto contractual hacia active membership. Crear este value object puro no es persistir físicamente un manifest, snapshot o file ni prueba source integrity. No se introduce `PublicationEligibility`: `AdmissionGateVerification.verified` ya es la precondición necesaria. Tampoco se introducen `PublicationRecord`, `PublicationEvent` o publication ID porque v1 no requiere historial de actos de publication.

Una entry individual no puede probar que exista como máximo una revisión activa por `identity.unit_id`, ni detectar duplicados o definir el reemplazo entre revisiones. Una futura colección/snapshot de `ActiveCandidateMembership` agrupará entries, impondrá esa unicidad y será el contexto de duplicados, replacement, consistencia y atomicidad; esta subsección no define su clase, secuencia, algoritmo ni formato físico. Membership no determina curriculum order y no incorpora posición, sequence, ordinal ni coordenadas de hierarchy.

La declaración atómica no verifica existencia o bytes de artifact, revision física, digest contra archivo, parseabilidad, manifest ni enumeración de source: declared active membership != physical source integrity demonstrated. Una capa futura de source integrity comprobará que la representación física corresponde a las memberships declaradas. Active membership tampoco equivale a authoritative prerequisite compatibility y no ejecuta ni reinterpreta slices 25–29.

Machine-readable aquí significa value object tipado, frozen, invariantes deterministas y factory pura; no JSON persistido, manifest, DB row, API resource ni filesystem file. La futura factory no accede a filesystem, environment, DB, network, clock, random, file hashes, artifact loading ni source enumeration. A1-U1 permanece pending / non-member y no recibe una membership. Loader continúa BLOCKED: aún faltan colección/snapshot, unicidad/replacement, representación y adquisición de source, source/artifact integrity, consistencia de snapshot y loader.

### Publication y active source membership

Active source membership es el conjunto explícitamente declarado de revisiones admitidas que forman un snapshot productivo. No se deriva de enumerar el filesystem: artifact físicamente presente no equivale a active source member.

Cada declaración de membership identificará como mínimo:

- `unit_id`;
- `candidate_revision`;
- `content_digest`;
- referencia inequívoca al admission record correspondiente.

Admission record y membership declaration son hechos separados: el primero autoriza publication y el segundo declara que ya ocurrió. No se introducen más estados. Una candidate pending o rejected puede conservarse como artifact o historial, pero nunca pertenecer al active snapshot. Puede existir historial de varias revisiones, pero habrá como máximo una revisión activa por `unit_id` dentro de un snapshot.

Una lectura productiva observará un snapshot estable, con identificador o revisión propio y lista explícita de members. Una ejecución no podrá mezclar parcialmente dos publicaciones. El mecanismo físico de atomicidad queda fuera de este contrato.

La futura source podrá entregar candidates activos de múltiples levels y units. No calculará target scope, orden ni completitud: slices 16, 17 y 25 conservan esas responsabilidades.

```text
candidate source membership
!= curriculum ordering authority
```

Filesystem order, filenames, member order, input `Sequence` y orden lexical de `unit_id` nunca definirán precedencia curricular. Esta autoridad permanece exclusivamente en `AuthoritativeCurriculumHierarchy` y `CurriculumUnitPosition`. A su vez, authority de hierarchy no certifica admission, publication, revision ni identidad de candidate payload.

### Active candidate source snapshot v1

`ActiveCandidateSourceSnapshot` es la unidad lógica, completa, inmutable e identificada por revisión que declara la totalidad de `ActiveCandidateMembershipCollection` activa para una revisión concreta de la source. Es estado de source activo lógico, no un evento ni una prueba de persistencia física.

Se mantienen obligatoriamente las fronteras:

```text
logical collection
!= active source snapshot
!= publication event

active source snapshot declared
!= physical publication completed
!= physical source representation
!= source integrity proof
!= loader
!= curriculum order
!= authoritative curricular compatibility
```

La representación lógica v1 contiene exactamente:

- `snapshot_revision: str`;
- `collection: ActiveCandidateMembershipCollection`.

No contiene `snapshot_id`, `content_digest`, `source_id`, `created_at`, `published_at`, `snapshot_schema_version`, `memberships` duplicadas, status, findings, historial, memberships reemplazadas, event log, `PublicationRecord`, candidate, `AdmissionRecord`, `AdmissionGateVerification` ni metadata curricular.

`snapshot_revision` es un string machine-readable, obligatorio, no vacío ni exclusivamente whitespace, suministrado por el caller y preservado literalmente. No se aplica trim, lowercase, SemVer, UUID automático, timestamp ni generación aleatoria. Es una revisión del conjunto activo completo, no un identificador estable de una entidad snapshot con múltiples revisiones; v1 no define esa entidad y por ello no introduce `snapshot_id`.

Se distingue explícitamente:

```text
candidate_revision
!= snapshot_revision
```

`candidate_revision` identifica la revisión de una unit candidata; `snapshot_revision`, la revisión del conjunto activo completo. Ninguna se deriva de la otra, del digest ni del orden curricular.

El snapshot compone una `ActiveCandidateMembershipCollection` ya conforme y no vuelve a exponer o recalcular `memberships`. Por ello hereda exclusivamente de la collection la validez de vacío, la preservación de orden representacional, la preservación de objetos, la unicidad por `identity.unit_id` y la unicidad global de `admission_id`. Ese orden no define orden curricular.

Un snapshot con collection vacía es estructuralmente válido. No demuestra utilidad, completitud curricular, publicación física ni preparación del loader.

El snapshot será un value object frozen. Si cambia una membership activa, S1 permanece intacto y se construye S2; no existen métodos `add`, `remove`, `replace` ni `update`. Replacement es una transición entre estados y no pertenece a este value object. Tampoco se almacenan snapshots previos ni historia de replacement.

La igualdad v1 es estructural: misma `snapshot_revision` y misma `collection` estructural producen snapshots iguales. Una misma `snapshot_revision` con collection distinta produce objetos estructuralmente distintos que pueden construirse localmente. Reutilizar una `snapshot_revision` con contenido distinto es un conflicto global de source/publication, pero un value object aislado no puede demostrarlo: esa garantía pertenece a una futura registry, historia, source state o capa de persistencia.

No se añade `content_digest` del snapshot. Definirlo exigiría decidir canonical serialization, preimage, schema serializable y representación física; esas responsabilidades permanecen fuera de este contrato lógico y no se adelantan mediante hashing.

El snapshot no verifica admission gates, no deriva `CandidatePayloadIdentity`, no valida `PedagogicalUnitCandidate`, no reconstruye linkage con `AdmissionRecord` y no declara `ActiveCandidateMembership`. Consume únicamente la collection ya conforme.

La atomicidad lógica significa que un consumidor recibe el snapshot como una unidad completa e inmutable, sin observar una collection parcial. La composición e inmutabilidad del value object satisfacen esta propiedad. La atomicidad física —persistir o cambiar una revisión completa de source de forma indivisible— pertenece a futuras capas de publisher, storage y source representation.

Un evento de publicación permanece conceptualmente distinto del snapshot y solo requerirá un `PublicationRecord` si aparece una necesidad real de auditoría o de registrar transiciones. La existencia del snapshot lógico no prueba que haya sido representado, publicado o puesto a disposición físicamente.

Una futura capacidad de source integrity deberá poder contrastar la representación física definida a continuación con `snapshot_revision`, la collection declarada, los candidates o artifacts adquiridos y las identities/digests ya contratados en las memberships. La representación física no duplica ni revalida las invariantes lógicas.

El loader permanece bloqueado hasta disponer como mínimo de: implementación de este snapshot, representación física explícita, lectura o publicación física atómica, adquisición de candidates/artifacts, source integrity y correspondencia demostrada entre snapshot y candidates adquiridos. La compatibilidad curricular autoritativa continúa siendo responsabilidad posterior al loader.

A1-U1 permanece `pending / non-member`; esta definición no la convierte en membership ni en snapshot productivo real.

La implementación futura prevista será un frozen dataclass interno, coherente con los value objects actuales, con una factory conceptual equivalente a:

```text
build_active_candidate_source_snapshot(
    collection: ActiveCandidateMembershipCollection,
    *,
    snapshot_revision: str,
) -> ActiveCandidateSourceSnapshot
```

La factory validará únicamente que `snapshot_revision` sea un `str` real no vacío ni whitespace-only y que `collection` sea una `ActiveCandidateMembershipCollection`; las violaciones estructurales producen `ValueError`. No crea `ValidationReport`, `ValidationFinding`, status ni framework genérico de validación.

La cobertura futura mínima comprobará shape exacto, frozen, revision válida preservada literalmente, rechazo de revision non-string/vacía/whitespace-only, collection de tipo incorrecto, preservación de collection por identidad, collection vacía válida, orden heredado, igualdad estructural, ausencia de falsa garantía global para misma revision con collection distinta, ausencia de campos extra, recálculos e I/O.

### Active candidate source snapshot manifest and atomic physical publication v1

`ActiveCandidateSourceSnapshotManifestV1` es el documento físico serializado derivado de un `ActiveCandidateSourceSnapshot` lógico. No es un nuevo domain value object, no duplica el snapshot en memoria y no constituye por sí mismo un evento de publicación, una prueba de source integrity, adquisición de candidates/artifacts, loader readiness, orden curricular ni compatibilidad curricular autoritativa.

Se mantienen obligatoriamente las fronteras:

```text
ActiveCandidateSourceSnapshot
!= ActiveCandidateSourceSnapshotManifestV1 document

manifest document exists
!= manifest atomically published

manifest atomically published
!= source integrity passed
!= candidate/artifact acquisition complete
!= loader ready
```

El formato físico v1 es exactamente un único documento JSON codificado en UTF-8 sin BOM. No se usa YAML, TOML ni JSON Schema externo. Su shape semántico exacto es:

```json
{
  "manifest_schema_version": "1.0",
  "snapshot_revision": "...",
  "memberships": [
    {
      "identity": {
        "unit_id": "...",
        "candidate_revision": "...",
        "payload_schema_version": "...",
        "content_digest": "..."
      },
      "admission_id": "..."
    }
  ]
}
```

No se añaden otros campos: no `snapshot_id`, source ID, timestamp, publication ID, manifest digest, status, findings, count, history, paths/locators de artifacts, admission record serializado, candidate payload ni metadata curricular.

`manifest_schema_version` tiene inicialmente el literal `"1.0"` y pertenece exclusivamente al formato físico. Se distingue de `CandidatePayloadIdentity.payload_schema_version` y no se incorpora a `ActiveCandidateSourceSnapshot`. Un cambio incompatible de este documento requerirá otra `manifest_schema_version`; v1 no define una política SemVer general.

`snapshot_revision` se copia literalmente desde `snapshot.snapshot_revision`, sin normalizar, derivar, trim, usar filename ni usar path como identidad. El revision string opaco no se emplea como componente de path. Cada entry de `memberships` copia, en este orden estructural, `identity.unit_id`, `identity.candidate_revision`, `identity.payload_schema_version`, `identity.content_digest` y `admission_id` desde `snapshot.collection.memberships`.

La serialización no recalcula identity, digest, admission, unicidad por unit, unicidad de admission ID ni compatibilidad curricular. El array `memberships` preserva exactamente el orden representacional existente; no define curriculum order. Una collection vacía se representa exactamente como `"memberships": []` y es físicamente válida, sin demostrar utilidad, completitud ni loader readiness.

Para el mismo snapshot lógico, la serialización v1 produce los mismos bytes. Normativamente es equivalente a serializar el documento construido en el orden indicado mediante `json.dumps(document, ensure_ascii=False, separators=(",", ":"), sort_keys=False, allow_nan=False).encode("utf-8") + b"\n"`: UTF-8 sin BOM, Unicode no escapado a ASCII, sin whitespace JSON no significativo, sin NaN/Infinity y exactamente un newline final. Esta notación fija una representación implementable; no es código ejecutable ni impone interoperabilidad byte-for-byte a implementaciones que no sigan expresamente este contrato v1.

El orden contractual de construcción de keys es obligatorio para estabilidad de representación y auditoría: top level `manifest_schema_version`, `snapshot_revision`, `memberships`; cada membership `identity`, `admission_id`; cada identity `unit_id`, `candidate_revision`, `payload_schema_version`, `content_digest`. `sort_keys=False` preserva este orden construido y el array `memberships` conserva exactamente su orden representacional. Los bytes deterministas no son canonical cryptographic preimage; no se añade digest, hash, firma ni protocolo de canonical hashing del manifest.

La futura operación mínima de publicación es conceptualmente:

```text
publish_active_candidate_source_snapshot_manifest(
    snapshot: ActiveCandidateSourceSnapshot,
    *,
    manifest_path: Path,
) -> None
```

`manifest_path` es un `Path` absoluto, explícito y caller-provided. La ubicación física procede exclusivamente de ese path recibido: no se acepta path relativo, vacío o no representable, no se fija environment variable, source root global, revision directories, artifact directories, cloud path ni múltiples sources. `snapshot_revision` nunca participa en la construcción de `manifest_path`.

La implementación validará como mínimo que su parent existe y es directorio, y que el target es inexistente o un archivo regular, nunca symlink ni directorio. No diseña hardening de host adversarial completo ni sigue deliberadamente symlinks del target. V1 asume filesystem local POSIX/Linux, un único publisher local controlado y directorio de publicación bajo control de la aplicación u operador; la manipulación adversarial concurrente del parent queda fuera de scope. No se añaden locks, `openat2`, framework de dirfd ni sandboxing.

La operación publica atómicamente únicamente el documento manifest activo, no candidates/artifacts ni admission records físicos. Deberá realizar conceptualmente, y en este orden:

1. serializar el documento completo en memoria;
2. crear un temporal en el mismo directorio que `manifest_path`;
3. escribir todos los bytes;
4. flush;
5. ejecutar `fsync` sobre el archivo temporal;
6. cerrar el temporal;
7. ejecutar `os.replace(temp_path, manifest_path)`;
8. ejecutar `fsync` sobre el directorio padre.

El temporal en el mismo directorio es obligatorio para preservar la semántica de reemplazo atómico del filesystem local; no se usa un temporal global que pueda pertenecer a otro filesystem. La **physical atomic visibility** significa que durante `os.replace` un lector observa el documento anterior completo o el nuevo completo, nunca una combinación parcial. Un consumidor abrirá una vez el manifest activo y leerá ese descriptor completo; no construirá una lectura de snapshot a partir de varias aperturas o enumeración de filesystem.

La atomicidad v1 se limita a la visibilidad y persistencia local del manifest bajo las garantías del filesystem local soportado. No afirma atomicidad de artifacts, admission records, source bundle, red, object storage ni múltiples publishers. V1 asume un único publisher local; no añade locks, compare-and-swap, registry, history, last-writer coordination ni rollback automático.

Si falla antes de `os.replace`, el manifest activo anterior debe permanecer intacto y el temporal no publicado puede limpiarse best-effort. Si falla `os.replace`, no se afirma publication. Si falla el `fsync` del directorio después de un replace exitoso, el documento nuevo puede ya ser visible pero su persistencia durable no queda confirmada; la implementación deberá reportar esa frontera explícitamente y no restaurará automáticamente el manifest anterior.

Una publicación exitosa no prueba que los digests declarados coincidan con bytes físicos, que existan candidates/artifacts, que `admission_id` resuelva a un record físico, que no haya reuse histórico de `snapshot_revision` con distinto contenido ni que los artifacts no declarados hayan sido inspeccionados. Esas garantías pertenecen a acquisition, source integrity, registry/history y loader posteriores.

La cobertura futura mínima incluirá: shape exacto y ausencia de campos extra; bytes deterministas, newline final, literals, vacío y orden; publicación inicial y reemplazo S1 → S2; lectura por descriptor anterior/nuevo sin mezcla parcial; fallos de write/replace que conservan S1; frontera de `fsync` posterior al replace; cleanup del temporal no publicado; paths target inválidos; y ausencia de acceso a candidate, admission, acquisition, source integrity, currículo o I/O ajeno a la publicación local.

### Local active candidate source acquisition v1

`Local active candidate source acquisition v1` es la capacidad física que adquiere, sin verificar todavía, los candidates explícitamente asociados a un manifest activo. Recibe un manifest físico, reconstruye el snapshot lógico que declara y adquiere los documentos candidate correspondientes. No publica, no modifica paths, no descubre candidates y no establece source integrity.

Se mantienen obligatoriamente las separaciones:

```text
manifest parsed
!= manifest integrity proven

candidate parsed
!= candidate identity verified
!= candidate digest verified
!= source integrity proof
!= loader readiness

acquired
!= verified
```

V1 se limita a filesystem local POSIX/Linux controlado. Acquisition significa leer bytes desde paths absolutos, explícitos y caller-provided, abriendo cada path una sola vez y leyéndolo completamente desde ese descriptor. No significa copiar archivos, descargar, enumerar directorios, usar glob, descubrir candidates, resolver locators, inferir layouts, ni usar red, HTTP, S3, CDN, object storage o base de datos.

La futura capacidad conceptual es equivalente a `acquire_active_candidate_source(...)`. Recibe `manifest_path: Path` y una secuencia explícita de bindings. Un binding mínimo contiene exactamente `unit_id: str` y `candidate_path: Path`; puede representarse mediante un value object pequeño si mejora la claridad, sin crear una abstracción general de filesystem. `unit_id` es exclusivamente la clave de asociación con una membership declarada:

```text
binding unit_id
!= candidate identity proof
```

`manifest_path` y cada `candidate_path` son `Path` absolutos, explícitos y caller-provided. Deben existir, ser archivos regulares, no ser symlinks ni directorios. No se acepta path relativo y no se usa `resolve()` para convertirlo silenciosamente en absoluto. Ningún path se deriva de `unit_id`, `candidate_revision`, `snapshot_revision` ni convenciones de filename.

Los bindings son una allowlist exacta: sus `unit_id` deben corresponder uno a uno con las memberships declaradas por el manifest. Binding ausente, duplicado para un `unit_id` o adicional para una unit no declarada hace fallar la adquisición. Los archivos adicionales fuera de esa allowlist no se enumeran, no se inspeccionan y no afectan el resultado.

La adquisición abre `manifest_path` una sola vez, lee todos sus bytes desde ese descriptor y lo interpreta como UTF-8 sin BOM. Debe rechazar BOM, JSON malformado, `manifest_schema_version` distinto de `"1.0"`, shape o tipos inválidos, campos desconocidos y duplicados estructurales incompatibles. Debe además rechazar cualquier key JSON duplicada en cualquier objeto y nivel del documento antes de construir value objects de dominio; una técnica equivalente a detectar `object_pairs` durante el parsing satisface esta regla. Por ejemplo, `{"unit_id":"a","unit_id":"b"}` es inválido y no se acepta aplicando silenciosamente la última key. El documento físico debe seguir exactamente `ActiveCandidateSourceSnapshotManifestV1`: top-level object con sus campos contractuales, array `memberships`, identity object y `admission_id`. Su orden representacional se preserva.

El parsing reconstruye el estado lógico en esta dirección:

```text
CandidatePayloadIdentity
-> ActiveCandidateMembership
-> ActiveCandidateMembershipCollection
-> ActiveCandidateSourceSnapshot
```

Debe usar los value objects e invariantes existentes para collection y snapshot, sin duplicar manualmente reglas que ya pertenecen a ellos, salvo la validación necesaria para interpretar el documento físico. El `snapshot_revision` se copia literalmente desde el manifest, permanece opaco, no construye paths, no se deriva de filename ni implica chronological order, integrity o autenticidad.

Después de leer, decodificar, parsear sin keys duplicadas, validar schema/shape y reconstruir el snapshot, acquisition vuelve a serializar ese snapshot con `serialize_active_candidate_source_snapshot_manifest(...)` o una semántica exactamente equivalente al manifest v1. Los bytes reconstruidos deben ser idénticos byte a byte a los bytes adquiridos; si no lo son, existe un manifest acquisition failure por nonconformance de physical format. Esta comprobación exige UTF-8 sin BOM, `ensure_ascii=False`, separators compactos, `sort_keys=False`, `allow_nan=False`, key order contractual y exactamente un newline final. Por ello se rechaza JSON semánticamente equivalente con orden de keys distinto, whitespace adicional, newline final ausente o adicional, o Unicode escapado de forma distinta. Se mantiene:

```text
byte-conformant manifest
!= source integrity proof
```

La igualdad de bytes acredita solo que el archivo es una representación física conforme de `ActiveCandidateSourceSnapshotManifestV1`; no añade manifest digest, hash, firma ni prueba de source integrity.

Para cada membership, en el orden representacional del manifest, la adquisición localiza su binding exacto por `unit_id`, valida el `candidate_path`, abre ese path una sola vez y lee todos sus bytes. Los bytes candidate deben ser UTF-8 válido sin BOM; el parsing JSON rechaza cualquier key duplicada en cualquier objeto o nivel antes de validar `PedagogicalUnitCandidate`. Después se parsea el candidate mediante el modelo vigente. No se exige a candidate JSON separators compactos, key order específico, newline final único, bytes canónicos ni raw-file digest: documentos físicamente distintos pueden representar el mismo payload canónico. Se mantiene:

```text
candidate file format parseable
!= candidate identity verified
!= candidate digest verified
```

La adquisición conserva los bytes físicos leídos, el candidate parseado, la membership declarada, el path absoluto y el orden del manifest. No recalcula `CandidatePayloadIdentity`, no compara digest, no compara identity completa y no ejecuta admission verification.

El resultado v1 es una evidencia estructuralmente inmutable/frozen **acquired / unverified**, por ejemplo `ActiveCandidateSourceAcquisition`, que conserva el snapshot reconstruido y entries adquiridas en orden del manifest. Cada entry conserva conceptualmente membership, `candidate_path`, `candidate_bytes` y `PedagogicalUnitCandidate`. `candidate_path` conserva la referencia física declarada y `candidate_bytes` son evidencia física adquirida inmutable. Un `PedagogicalUnitCandidate` parseado puede conservarse por conveniencia de consumo de B38, pero su presencia no hace profundamente inmutable toda la evidencia: el resultado estructuralmente frozen no equivale a deep immutability de cada modelo mutable anidado. No contiene `verified`, `integrity_status`, `trusted`, `loadable`, `authoritative`, status curricular ni una afirmación global de source completeness.

Un manifest con `memberships=[]` y bindings vacíos produce una adquisición estructuralmente válida. No demuestra utilidad curricular, curriculum completeness, source integrity global ni loader readiness. La operación es all-or-nothing: si falla lectura o parsing de manifest, binding, path, lectura candidate, JSON o validación Pydantic, falla la operación completa. No omite candidates defectuosos ni devuelve resultados parciales; puede fallar de forma determinista según el orden representacional del manifest. V1 no introduce aún un framework genérico de findings.

`CandidatePayloadIdentity.content_digest` no es SHA-256 de los bytes raw del archivo candidate. Es SHA-256 de los bytes canónicos del admission payload v1 de siete campos. Por ello:

```text
candidate raw bytes
!= canonical candidate payload bytes

raw-byte hash
!= CandidatePayloadIdentity.content_digest
```

Dos documentos JSON físicamente distintos pueden producir el mismo digest si representan el mismo payload canónico. Slice 38 no verifica ese digest. La capacidad posterior de candidate integrity verificará sobre los bytes y objeto ya adquiridos, sin releer filesystem, una secuencia conceptual equivalente a:

```text
candidate bytes
-> JSON/Pydantic
-> canonical admission payload
-> canonical bytes
-> SHA-256
-> CandidatePayloadIdentity
-> comparación con manifest identity
```

`candidate_revision` no forma parte intrínseca de `PedagogicalUnitCandidate`. La adquisición no intenta derivarla de candidate bytes, filename ni path; únicamente preserva la revisión declarada por la membership del manifest. Una integrity proof posterior podrá usar esa revisión declarada para derivar y comparar la identity completa. V1 no añade envelope ni sidecar. Asimismo, B38 preserva literalmente `payload_schema_version` desde la identity declarada del manifest, pero no deriva `CandidatePayloadIdentity` ni valida que la versión sea compatible con la canonicalización o el digest. Una `payload_schema_version` no soportada no se convierte automáticamente en acquisition failure si candidate JSON puede parsearse como `PedagogicalUnitCandidate` vigente: permanece metadata declarada / unverified. La candidate-integrity proof posterior comprobará primero si esa versión está soportada; una versión no soportada será integrity verification failure y solo una versión soportada podrá derivar y comparar `CandidatePayloadIdentity`. B38 no crea migraciones ni múltiples schemas físicos.

`required_resource_ids` es un inventario lógico de IDs. No es locator, path, recurso adquirido, digest, physical identity ni artifact verificado. No existe todavía contrato de path, locator, revision, digest, media type, size o acquisition para recursos externos. Por ello slice 38 no los adquiere: un candidate con `required_resource_ids` no vacío puede adquirirse estructuralmente, pero no queda plenamente loadable.

`admission_id` se preserva desde el manifest y participa en las invariantes estructurales existentes; no provoca acquisition de un `AdmissionRecord` físico. Se mantiene:

```text
membership was previously constructed from admission proof
!= physical source later proves that admission again
```

La política sobre un `AdmissionRecord` físico queda pendiente y deberá resolverse antes del loader; v1 no adopta silenciosamente una prueba física de admission ni una exención permanente de ella.

La adquisición conserva los bytes que leyó. La future candidate-integrity capability verificará los `candidate_bytes` adquiridos o una reconstrucción fresca obtenida exclusivamente de esos bytes; no confiará en un `PedagogicalUnitCandidate` que pudo mutarse externamente. Un loader posterior consumirá evidencia ya adquirida/verificada, sin reabrir candidate paths. Se evita conceptualmente:

```text
verify file state A
-> file changes
-> loader reopens state B
```

V1 no afirma que resuelva toda carrera de filesystem ni añade locks, sandboxing, `openat2` o hardening de host adversarial.

Las familias conceptuales de error de acquisition son:

1. manifest: lectura, UTF-8/BOM, JSON malformado, schema no soportado, shape o tipos inválidos;
2. binding: ausente, duplicado, inesperado o path inválido;
3. candidate: path/lectura, JSON malformado o fallo de validación `PedagogicalUnitCandidate`.

No son errores de slice 38 el digest mismatch, identity mismatch, resource digest mismatch ni admission proof mismatch; pertenecen a verificación posterior. Por tanto:

```text
acquisition failure
!= integrity failure
```

La adquisición demuestra una totalidad limitada: todo member declarado tiene exactamente un binding, todo path permitido fue leído y todo documento candidate se parseó, sin bindings adicionales dentro de la allowlist suministrada. No demuestra ausencia de archivos arbitrarios, candidate identity correctness, digest correctness, resource completeness, admission provenance ni curriculum completeness. No se usa `source complete` sin ese calificador.

`LOADER = BLOCKED`. Antes del loader se requerirá como mínimo candidate integrity sobre la evidencia adquirida, una política resuelta para `required_resource_ids` y recursos externos, una frontera resuelta de admission y un resultado verificado consumible sin relectura de filesystem. A1-U1 permanece `pending / non-member`; no se incorpora ni se usa como fixture productiva de source activa.

La cobertura futura mínima de slice 38 comprobará: manifest v1 válido, vacío y en orden; JSON malformado, UTF-8 inválido, BOM, schema no soportado, fields desconocidos/ausentes, keys JSON duplicadas y memberships incompatibles; manifest semánticamente equivalente pero byte-no-conforme rechazado, incluidos key order incorrecto, whitespace adicional, newline final incorrecto y Unicode escaping distinto; bindings exactos, missing/duplicate/unexpected y ausencia de enumeración; paths absolutos, relativos rechazados, inexistentes, directorios, symlinks y targets no regulares cuando sea práctico; candidates válidos, UTF-8 inválido, BOM, keys JSON duplicadas, JSON malformado, fallo Pydantic, preservación de bytes y lectura única cuando sea comprobable; candidate JSON no canónico por whitespace/key order permitido si es JSON/Pydantic válido; `payload_schema_version` declarada no soportada adquirible y preservada como unverified sin derivar identity; resultado estructuralmente frozen, bytes preservados y mutación del candidate model sin alteración de esos bytes; resultado en orden de manifest, vacío válido, all-or-nothing y semántica acquired/unverified; ausencia de digest verification, resource acquisition, `AdmissionRecord` acquisition y loader. No requiere GitHub ni red.

Esta definición no introduce `CandidatePayloadDocumentV1`, envelope, sidecar, raw-file digest, CAS, source root, artifact registry, package manager, signed manifest, Merkle tree, transaction de base de datos ni framework de acquisition remoto. El candidate físico v1 puede ser JSON interpretable directamente como `PedagogicalUnitCandidate`; su formato físico no se confunde con el preimage canónico del `content_digest`.

### Candidate integrity verification from acquired evidence v1

`Candidate integrity verification from acquired evidence v1` consume exclusivamente una `ActiveCandidateSourceAcquisition` conforme producida por la acquisition local v1. Su garantía positiva se denomina **candidate payload integrity verified** y significa exactamente que, para cada entry adquirida, los `candidate_bytes` preservados reconstruyen un `PedagogicalUnitCandidate` válido cuya `CandidatePayloadIdentity` derivada coincide estructuralmente con la identity declarada por la membership bajo la `candidate_revision` declarada:

```text
candidate_bytes adquiridos
-> nueva reconstrucción de PedagogicalUnitCandidate
-> derive_candidate_payload_identity(
       candidate,
       candidate_revision=membership.identity.candidate_revision,
   )
-> derived_identity == membership.identity
```

Se mantienen obligatoriamente las fronteras:

```text
candidate payload integrity verified
!= raw-file byte identity
!= candidate_revision provenance
!= admission provenance
!= resource integrity
!= active source integrity
!= loader readiness
!= curricular compatibility
!= aprendizaje/mastery
```

La autoridad de B39 es `candidate_bytes`, no `AcquiredActiveCandidateSourceEntry.candidate`: ese modelo Pydantic es mutable y solo fue conservado por B38 como conveniencia. B39 reconstruye el candidate exclusivamente desde los bytes ya adquiridos; no reabre `candidate_path`, no relee filesystem ni manifest físico, no vuelve a adquirir bindings y no usa el candidate mutable como evidencia. `candidate_path` puede conservarse solo como metadata de procedencia local. B38 ya acreditó acquisition y parsing físico inicial; si la reconstrucción desde los bytes preservados deja de producir un `PedagogicalUnitCandidate` válido, B39 produce candidate-integrity verification failure, no acquisition failure.

B39 reutiliza sin redefinir `CandidatePayloadIdentity` —`unit_id`, `candidate_revision`, `payload_schema_version`, `content_digest`— y `derive_candidate_payload_identity(candidate, *, candidate_revision)`. La única `PAYLOAD_SCHEMA_VERSION` soportada hoy es `"1.0"`. La canonicalización reutilizada es exclusivamente la de B31 sobre `specification`, `candidate_unit`, `evaluation_plans`, `feedback_plans`, `lesson_capability_plans`, `skill_coverage` y `required_resource_ids`; no se crea segundo canonicalizer ni serialización alternativa. `content_digest` continúa siendo SHA-256 del payload lógico canónico B31, no de los candidate raw bytes: JSON físicamente distinto que reconstruye el mismo estado lógico Pydantic puede producir el mismo digest.

El orden de verificación es obligatorio:

1. tomar `membership.identity.payload_schema_version`;
2. comprobar que B31 la soporte;
3. si no está soportada, fallar explícitamente como candidate-integrity verification failure;
4. solo entonces reconstruir desde bytes, derivar y comparar identidad.

Una versión no soportada fue adquirible en B38 como metadata declarada / unverified, pero no puede derivarse bajo canonicalización desconocida en B39. No es acquisition failure ni identity mismatch.

`candidate_revision` no forma parte intrínseca de `PedagogicalUnitCandidate`: es metadata externa de `membership.identity` y se entrega literalmente a la factory. B39 demuestra que el candidate lógico reconstruido desde bytes coincide con la identity declarada **bajo** esa revisión; no demuestra que la revisión esté codificada en bytes, su provenance física, autenticidad ni unicidad global. Esta limitación no bloquea la verificación. Análogamente, `binding.unit_id` fue solo la key de asociación B38; la prueba de unidad procede de `derived_identity.unit_id`, derivado de `candidate.specification.unit_id` desde los bytes. La igualdad completa detecta un candidate asociado físicamente a una membership de otra unidad.

La verificación positiva exige únicamente `derived_identity == membership.identity`; no admite comparación parcial ni digest aislado. Sus dimensiones son: `unit_id` derivado del candidate, `payload_schema_version` soportada, `content_digest` derivado del payload canónico y `candidate_revision` externa declarada y pasada a la factory.

Los resultados v1 son dos value objects frozen mínimos:

- `CandidatePayloadIntegrityVerification`: `membership`, `candidate_path`, `candidate_bytes`, `derived_identity`;
- `ActiveCandidateSourceCandidateIntegrityVerification`: `snapshot`, `entries`.

No se conserva un `PedagogicalUnitCandidate` mutable como evidencia positiva persistente y no se añaden `verified=True`, status, findings, trust, loadability, authority, resource completeness ni evidence de admission. La API pública conceptual única es `verify_active_candidate_source_candidate_integrity(acquisition)`: consume toda la acquisition, verifica entries en el orden del manifest y devuelve el agregado solo si todas pasan. Una primitive individual puede ser privada.

B39 es all-or-nothing y fail-fast es suficiente. Payload schema no soportada, reconstrucción/validación inválida desde `candidate_bytes` o identity mismatch impiden devolver aggregate positivo; no se retornan resultados parciales, success + failures ni findings collection. Acquisition vacía produce verificación vacía estructuralmente válida, sin afirmar source integrity, utilidad, curriculum completeness ni loader readiness.

La estructura exterior y cada entry verification son frozen; `candidate_bytes`, `derived_identity`, snapshot y membership son la evidencia estable posterior. Esto no exige deep-immutable Pydantic. La cadena de consumo queda fijada así:

```text
B38: filesystem -> acquired physical evidence
B39: acquired candidate_bytes -> candidate payload integrity verification
etapas posteriores: consumen esa evidencia/verificación sin reabrir filesystem
```

Por ello B39 debe poder operar aunque `candidate_path` haya desaparecido, cambiado o dejado de ser accesible tras B38. No introduce locks, `openat2` ni sandbox.

`admission_id` se preserva por la membership, pero B39 no adquiere `AdmissionRecord`, no reejecuta admission gates y no acredita reviewer, decisión ni admission provenance. `required_resource_ids` participa como valor lógico en el digest canónico, pero B39 no resuelve IDs, abre recursos, verifica existencia, calcula hashes ni acredita resource completeness/integrity. Por tanto, digest que cubre `required_resource_ids` no implica que esos recursos físicos existan o sean íntegros.

Después de B39 solo puede afirmarse candidate payload integrity verified. Admission provenance, integridad/completitud física de recursos y demás evidencia externa siguen fuera antes de poder afirmar active source integrity. `LOADER = BLOCKED`; B39 no define loader ni produce objeto `loadable` o `loader-ready`. A1-U1 permanece `pending / non-member` y B39 no la admite, publica, declara membership ni modifica contenido.

Los errores mínimos coherentes con los servicios existentes son `ValueError` o equivalente simple para payload schema no soportada, reconstrucción/validación de candidate desde bytes e identity mismatch. No se crea exception hierarchy ni se denominan estos errores source-integrity, admission o resource-integrity failures.

La cobertura futura mínima incluirá: candidate adquirido válido con schema `"1.0"`, equality exacta y agregado positivo; mutación posterior de `entry.candidate` sin afectar bytes ni B39; ausencia de apertura/read de paths y operación tras borrar o cambiar `candidate_path`; versión no soportada rechazada antes de derivar; unit lógica distinta pese al binding; cambios canónicos que producen mismatch y JSON raw distinto pero semánticamente equivalente que verifica; revisión declarada transmitida literalmente sin afirmar provenance; `required_resource_ids` con efecto lógico en digest y sin I/O de recursos; `admission_id` preservado sin lookup; orden del manifest, all-or-nothing, vacío válido y shapes frozen; ausencia de manifest reread, raw hash, red, resources, admission rerun y loader. No se multiplicarán tests cuando una comprobación material cubra varias garantías.

Esta capacidad no introduce raw-file digest, canonicalizer nuevo, `CandidatePayloadDocumentV1`, envelope, sidecar, modelo candidate profundamente inmutable, framework genérico de verification/findings/status, exception hierarchy, source root, filesystem layer, resource verification, admission verification, active-source-integrity aggregate, loader ni red. La frontera posterior es únicamente integrar candidate payload integrity verificada con las demás pruebas necesarias antes de afirmar active source integrity y habilitar un loader.

### Source integrity y familias de error

Un active member declarado cuyo payload no existe, no puede leerse o parsearse, o no satisface el schema produce acquisition failure. Si sus `candidate_bytes` adquiridos no reconstruyen una identity que coincida con la membership declarada bajo su revision declarada, produce candidate payload integrity verification failure. Ninguno se degrada silenciosamente a una candidate ausente del scope.

Un artifact no declarado como active member será ignorado por la fuente productiva. Esto permite conservar drafts, experiments, rejected candidates y backups sin publicarlos. Una misma revisión declarada más de una vez es source integrity failure; no existe silent dedupe.

Se mantienen separadas:

1. **acquisition failure**: lectura, parsing o schema físico;
2. **candidate payload integrity verification failure**: payload schema no soportada, reconstrucción desde bytes o identity declarada no coincidente;
3. **candidate local validation finding**: hallazgo determinista sobre un payload candidate;
4. **authoritative curricular validation finding**: hallazgo contextual producido posteriormente por las slices autoritativas.

```text
declared payload unreadable
!= candidate locally invalid
!= prerequisite not prepared
!= authoritative curricular incompatibility
```

### Relación con la validación autoritativa

La secuencia conceptual es:

```text
candidate payload
-> local validation
-> human review
-> admission
-> publication / active source membership
-> authoritative prerequisite validation flow
```

La validación autoritativa no es requisito de admission: exigirla produciría circularidad porque necesita precisamente el conjunto publicado. Una futura adquisición entregará una `Sequence[PedagogicalUnitCandidate]` correspondiente a un snapshot activo y esa secuencia podrá suministrarse, sin inferir orden curricular, a `derive_authoritative_prerequisite_validation_flow(...)`.

Admission y publication pertenecen al proceso de construcción curricular; no representan learner state, evidencia del estudiante, progreso ni mastery.

### Invariantes normativas v1

- filesystem presence no implica membership;
- parseable no implica locally valid;
- local passed no implica admitted;
- human-review document presence no implica admission;
- `pending_human_decisions != []` impide admission;
- rejected impide active membership;
- todo active member referencia exactamente contenido admitido y su digest debe coincidir;
- todo cambio del payload canónico requiere nueva admission;
- existe como máximo una revisión activa por unit en un snapshot;
- membership no define orden curricular;
- hierarchy authority no define candidate admission;
- artifacts no declarados se ignoran;
- members declarados ausentes o malformed producen acquisition failure;
- no existe silent dedupe;
- una lectura observa un único snapshot estable;
- la source no calcula scope, orden ni completitud curricular.

### Estado transitorio de A1-U1 y decisiones físicas pendientes

El artifact actual A1-U1 permanece pending y non-member mientras conserve `validation_report.status="pending"`, coverage/review `pending_approval`, decisiones humanas pendientes y ausencia de admission record y membership declaration. No está rejected. Para publicarse deberá resolver pendientes, fijar el payload final, superar validación local recalculada, recibir revisión humana final y obtener admission y membership explícitas.

El manifest físico del snapshot y su mecanismo de publicación atómica quedan resueltos por `ActiveCandidateSourceSnapshotManifestV1`. También quedan para preflight técnico posterior:

- formato físico de admission record;
- namespace operativo de `reviewer_id`;
- acquisition y source integrity de candidates/artifacts.

Estas decisiones físicas no alteran la semántica contractual anterior y no autorizan todavía modelos, loaders, parsers, publishers, DB, endpoints ni servicios productivos.

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
