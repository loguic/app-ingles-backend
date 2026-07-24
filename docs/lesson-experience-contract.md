# Contrato Profesional de Experiencia de Lección

## Estado del documento

- Bloque: B116.
- Estado: diseño en progreso.
- Fuente de verdad para backend, frontend y contenido pedagógico.
- Ninguna decisión de este documento modifica todavía código ni contenido activo.

## Propósito

Definir la experiencia pedagógica profesional que deberá vivir el estudiante al abrir, recorrer y completar una lección de LOGUIC English.

## Problema confirmado

La infraestructura técnica actual incorpora conversación, pronunciación, grabación, ejercicios y progreso, pero el contrato público de `Lesson` y su presentación siguen organizados mediante una estructura tradicional basada en objetivo, vocabulario, gramática, ejemplos y ejercicios.

## Principios obligatorios

- La lección parte de una misión comunicativa y de Skills medibles.
- La conversación, la comprensión auditiva y la práctica oral dirigen la experiencia.
- Vocabulario, gramática y traducción funcionan como apoyo contextual.
- El aprendizaje debe producir evidencia observable.
- Las capacidades técnicas existentes se reutilizan cuando aportan valor.
- La migración será gradual, compatible, probada y reversible.
- Ninguna automatización sobrescribirá contenido activo sin aprobación humana.

## Flujo pedagógico objetivo aprobado

La lección se organizará mediante esta secuencia:

1. **Misión comunicativa:** situación real, Skills implicadas y resultado observable.
2. **Encuentro inicial:** contacto breve y natural con el inglés en contexto.
3. **Comprensión guiada:** comprobación de intención e información relevante.
4. **Lenguaje útil en contexto:** vocabulario, patrones, significado, traducción opcional y pronunciación como apoyo.
5. **Escucha y producción guiada:** escuchar, grabar, comparar y repetir con apoyo gradual.
6. **Respuesta asistida:** participación con sugerencias, elecciones, pistas y traducción opcional.
7. **Conversación aplicada:** realización de la misión con menos apoyo.
8. **Retroalimentación y repetición adaptativa:** refuerzo únicamente de las dificultades detectadas.
9. **Evidencia observable:** demostración vinculada a las Skills trabajadas.
10. **Cierre y siguiente acción:** estado de misión, evidencia, aspectos por reforzar y práctica recomendada.

### Regla arquitectónica

El flujo principal deja de ser:

`Vocabulario → Gramática → Ejemplos → Ejercicios`

La experiencia objetivo será:

`Misión → Contexto → Comprensión → Producción → Conversación → Retroalimentación → Evidencia`

Vocabulario, gramática, traducciones, frases de referencia y ejercicios continuarán existiendo cuando aporten valor, pero como recursos subordinados al propósito comunicativo.

## Contrato público de lección v2 aprobado

### Separación entre autoría y ejecución

LOGUIC English mantendrá dos contratos diferentes:

1. `PedagogicalUnitCandidate` será el contrato interno de autoría, validación y aprobación.
2. `LessonExperience` será el contrato público preparado para ejecutar la experiencia en Flutter.

La aplicación cliente no recibirá toda la complejidad interna del Constructor Pedagógico.

### Estructura objetivo de `Lesson`

El contrato público evolucionará gradualmente hacia esta estructura:

- `id`: identificador estable.
- `title`: título visible.
- `experience`: experiencia pedagógica profesional.
- `conversations`: actividades conversacionales reutilizables.
- `exercises`: evidencias o actividades reutilizables.
- campos heredados temporales durante la migración.

### Responsabilidades iniciales de `LessonExperience`

#### `mission`

Define:

- identificador estable;
- título visible;
- situación comunicativa;
- resultado observable;
- criterios de éxito.

#### `skill_ids`

Referencia las Skills medibles trabajadas por la lección.

Estas referencias permitirán progreso, analítica, retroalimentación y repaso adaptativo sin exponer toda la matriz interna de cobertura.

#### `stages`

Declara la secuencia pedagógica explícita de la lección.

Tipos iniciales:

- `encounter`;
- `comprehension`;
- `language_support`;
- `guided_production`;
- `assisted_response`;
- `applied_conversation`;
- `adaptive_feedback`;
- `evidence`;
- `closure`.

Cada etapa deberá contener:

- identificador estable;
- tipo;
- instrucción para el estudiante;
- referencias a actividades;
- condición de finalización;
- carácter obligatorio o adaptativo.

Flutter ejecutará la secuencia aprobada y no decidirá autónomamente el orden pedagógico.

#### `language_support`

Contendrá recursos subordinados a la misión:

- vocabulario contextual;
- patrones lingüísticos;
- significado o traducción opcional;
- pronunciación;
- frases de referencia cuando aporten valor.

#### `evidence`

Declarará evidencias observables vinculadas a Skills, actividades y condiciones de logro.

Podrá representar:

- conversación completada;
- comprensión auditiva;
- respuesta contextual;
- producción oral;
- ejercicio aplicado.

#### `completion`

Definirá el estado pedagógico de la misión:

- pendiente;
- practicada;
- completada;
- necesita refuerzo.

La finalización no dependerá únicamente de recorrer pantallas.

### Compatibilidad gradual

- `Lesson` conservará temporalmente sus campos heredados.
- Se añadirá `experience` sin romper el contenido vigente.
- El contenido nuevo deberá utilizar el contrato v2.
- Flutter priorizará `experience`.
- El contenido antiguo podrá utilizar un adaptador temporal.
- Los campos heredados solo se retirarán después de completar la migración y sus pruebas.
- `Example` no se ampliará durante esta transición.

### Validaciones mínimas futuras

Una lección v2 deberá garantizar:

- misión presente y no vacía;
- al menos una Skill;
- etapas ordenadas y con identificadores únicos;
- referencias a actividades existentes;
- evidencias vinculadas a Skills;
- finalización basada en evidencia;
- conversación o producción aplicada;
- ausencia de etapas sin propósito pedagógico;
- separación entre candidato y contenido activo hasta la aprobación.

## Responsabilidades de las entidades

### `PedagogicalUnitSpecification`

Define qué unidad debe construirse: resultado observable, Skills, alcances, restricciones, evidencias exigidas y criterios de aceptación.

No contiene componentes de interfaz ni progreso de usuarios.

### `PedagogicalUnitCandidate`

Representa una propuesta completa todavía no publicada.

Incluye especificación, contenido candidato, matriz de cobertura, recursos, validaciones, decisiones humanas pendientes y resumen de cambios.

No será consumido directamente por Flutter.

### `Skill`

Representa una capacidad concreta, estable y medible del estudiante.

No equivale a una lección, actividad, herramienta, agente ni categoría genérica.

### `SkillCoverage`

Demuestra durante la autoría dónde se introduce, practica, aplica, evalúa y consolida cada Skill.

Será principalmente una estructura interna de construcción y validación.

### `Lesson`

Actúa como contenedor público estable.

Contendrá identidad, título, `LessonExperience`, actividades reutilizables y compatibilidad temporal con campos heredados.

No determinará el orden pedagógico mediante campos sueltos.

### `LessonExperience`

Orquesta la experiencia pedagógica completa.

Define misión, Skills, etapas, apoyos lingüísticos, evidencias y política de finalización.

No contiene lógica técnica de audio, navegación de grafos ni persistencia.

### `Mission`

Describe la situación comunicativa y lo que el estudiante deberá demostrar.

Contiene identificador, título, situación, resultado observable y criterios de éxito.

### `LessonStage`

Representa una etapa ejecutable del flujo.

Contiene identificador, tipo, instrucción, referencias a actividades, obligatoriedad y condición de finalización.

No duplica conversaciones ni ejercicios.

### `LanguageSupport`

Proporciona expresiones, vocabulario, patrones, significado, traducción opcional, pronunciación y pistas cuando una etapa lo requiera.

No dirige la lección ni se muestra obligatoriamente al inicio.

### `Conversation`

Representa una actividad conversacional ejecutable con turnos, interlocutores, elecciones, transiciones, audio y modos de interacción.

No decide por sí misma qué Skill demuestra, cuándo se utiliza ni si completa la misión.

### `Exercise`

Representa una comprobación o actividad evaluable concreta.

Puede vincularse a Skills, pero no será la única forma válida de evidencia.

### `EvidenceDefinition`

Declara qué acción observable cuenta como evidencia de una Skill.

Referencia Skills, actividad, tipo de evidencia, condición de logro y obligatoriedad.

No almacena resultados de un usuario concreto.

### `CompletionPolicy`

Define las condiciones para considerar una misión pendiente, practicada, completada o necesitada de refuerzo.

No depende únicamente de recorrer todas las etapas.

### Progreso e intentos

Almacenan las acciones reales del usuario: intentos, respuestas, conversaciones, evidencias, dificultades y estado de Skills.

Permanecen separados de la definición estática de la lección.

### Regla preventiva sobre `Example`

Hasta resolver formalmente su destino:

- no se ampliará;
- no recibirá nuevas responsabilidades;
- no se incorporará a `LessonExperience`;
- no fundamentará etapas nuevas;
- permanecerá únicamente como estructura heredada compatible.

## Decisión aprobada sobre `Example`

### Retirada del diseño v2

`Example` no formará parte de `LessonExperience` ni se utilizará para diseñar contenido nuevo.

La sección visible `Ejemplos` desaparecerá del flujo pedagógico principal.

### Compatibilidad heredada

Durante la migración:

- el backend continuará aceptando temporalmente `Lesson.examples`;
- Flutter conservará compatibilidad con las lecciones antiguas;
- `Example` no recibirá campos ni responsabilidades nuevas;
- el Constructor Pedagógico no generará contenido nuevo basado en `examples`.

### Sustitución profesional

Las expresiones que ayuden a completar una misión se representarán mediante `LanguageSupportItem`.

Un apoyo lingüístico podrá incluir:

- tipo y propósito contextual;
- texto en inglés;
- significado o traducción opcional;
- pronunciaciones regionales;
- pista de uso;
- referencia a una misión o etapa.

### Adaptación temporal

Un adaptador podrá transformar un `Example` heredado en un `LanguageSupportItem` de tipo `reference_expression`.

La transformación deberá conservar:

- identificador estable;
- texto inglés;
- traducción;
- pronunciaciones;
- recursos de audio.

No se modificarán identificadores silenciosamente.

### Contenido nuevo

Después de implementar el contrato v2:

- ninguna lección nueva utilizará `examples`;
- los apoyos lingüísticos estarán vinculados a una misión o etapa;
- una lección podrá no necesitar frases de referencia;
- vocabulario, patrones y traducciones permanecerán subordinados al propósito comunicativo.

### Retirada definitiva

`Example` solo podrá eliminarse cuando:

- todo el contenido activo esté migrado;
- Flutter ya no dependa de `LessonExample`;
- no existan referencias internas pendientes;
- audios y pronunciaciones estén preservados;
- las pruebas de contrato backend–frontend estén superadas;
- la migración sea reversible;
- la retirada quede documentada y versionada.

## Evidencias de aprendizaje y finalización

### `EvidenceDefinition`

Cada definición estática de evidencia deberá contener:

- `id`: identificador estable;
- `skill_ids`: Skills que puede demostrar;
- `stage_id`: etapa pedagógica relacionada;
- `activity_id`: actividad que produce la evidencia;
- `evidence_type`: tipo observable;
- `measurement_mode`: forma de medición;
- `success_condition`: condición explícita de logro;
- `required`: obligatoriedad para completar la misión.

Tipos iniciales:

- `comprehension_result`;
- `contextual_response`;
- `conversation_completion`;
- `guided_production`;
- `exercise_result`.

Modos iniciales de medición:

- `completion`;
- `binary`;
- `score`.

No se introducirán ponderaciones arbitrarias sin evidencia o datos reales que las justifiquen.

### `EvidenceRecord`

El resultado real del estudiante permanecerá separado de la definición estática.

Un registro podrá almacenar:

- usuario;
- evidencia;
- intento relacionado;
- estado de logro;
- puntuación opcional;
- fecha;
- metadatos de origen.

### Reglas de interpretación

- Completar una conversación demuestra aplicación recorrida, no fluidez.
- Elegir una respuesta contextual correcta puede demostrar comprensión o selección, no producción libre.
- Grabar y escuchar la propia voz demuestra práctica, no pronunciación correcta.
- Un ejercicio correcto demuestra únicamente las Skills declaradas para ese ejercicio.
- No se afirmará dominio de pronunciación o fluidez sin una evaluación válida.
- El `mastery_score` actual, basado únicamente en ejercicios, queda clasificado como cálculo heredado y no como dominio definitivo v2.

### `CompletionPolicy`

La política de finalización deberá declarar:

- `required_evidence_ids`;
- condición de misión practicada;
- condición de misión completada;
- regla de refuerzo;
- posibilidad de reintento.

Estados iniciales:

- `pending`: no iniciada o con práctica esencial pendiente;
- `practiced`: práctica recorrida, pero faltan evidencias obligatorias;
- `completed`: evidencias obligatorias logradas;
- `needs_reinforcement`: evidencia insuficiente o fallida.

### Regla profesional de finalización

Una misión no se completará únicamente por:

- abrir todas las secciones;
- escuchar todos los audios;
- grabar una vez;
- terminar una ruta conversacional;
- recorrer todas las etapas.

La misión se completará cuando se hayan obtenido las evidencias obligatorias declaradas por su política de finalización.

## Estrategia aprobada de sustitución paralela

### Decisión arquitectónica

El flujo heredado no se transformará progresivamente en la experiencia v2.

Se construirá un núcleo nuevo y aislado basado en `LessonExperience`, mientras el sistema actual permanecerá congelado únicamente para compatibilidad.

### Sistema heredado congelado

Permanecerán temporalmente operativos:

- `LessonExample`;
- `Lesson.vocabulary`;
- `Lesson.grammar`;
- `Lesson.examples`;
- `LessonDetailCard`;
- finalización local basada en ejercicios.

Estos componentes no recibirán nuevas capacidades pedagógicas.

Solo podrán modificarse para corregir errores confirmados o mantener compatibilidad durante la transición.

### Núcleo v2 independiente

La nueva arquitectura se implementará mediante entidades separadas:

- `LessonExperience`;
- `Mission`;
- `LessonStage`;
- `LanguageSupportItem`;
- `EvidenceDefinition`;
- `CompletionPolicy`.

El contrato nuevo no heredará el orden ni las responsabilidades del flujo tradicional.

### Renderizador Flutter independiente

Flutter incorporará un renderizador nuevo para la experiencia profesional.

La selección será explícita:

- `experience` presente: ejecutar el flujo v2;
- `experience` ausente: utilizar temporalmente el renderizador heredado.

Ambos recorridos permanecerán separados durante la migración.

### Capacidades reutilizables

El núcleo v2 podrá reutilizar:

- Skills y cobertura pedagógica;
- conversaciones guiadas y ramificadas;
- ejercicios;
- pronunciaciones;
- reproducción y grabación;
- audios;
- identificadores estables;
- persistencia de intentos;
- validadores deterministas después de generalizarlos.

La reutilización de una capacidad técnica no implicará conservar su ubicación o responsabilidad heredada.

### Sustitución mediante una lección piloto

La primera lección v2 se construirá como candidata aislada.

No sustituirá el contenido activo hasta superar:

- validación backend;
- contrato API;
- deserialización Flutter;
- pruebas del renderizador v2;
- recorrido pedagógico completo;
- persistencia de evidencias;
- regresión del flujo heredado;
- revisión pedagógica humana.

### Retirada controlada

`Example`, los campos heredados y `LessonDetailCard` solo podrán retirarse cuando:

- ninguna lección activa dependa de ellos;
- Flutter ejecute todas las lecciones mediante el contrato v2;
- audios, identificadores y progreso estén preservados;
- las migraciones sean reversibles;
- la suite completa sea correcta;
- la retirada esté aprobada, documentada y versionada.

### Regla preventiva

No se modificará una entidad provisional para convertirla en el núcleo definitivo cuando resulte más seguro construir el reemplazo profesional en paralelo.

## Auditoría arquitectónica de impacto

### Causa raíz

El problema no se limita a la entidad `Example`.

El contrato público y el renderizador vigente organizan la lección mediante una secuencia tradicional fija:

`Objetivo → Vocabulario → Gramática → Ejemplos → Conversación → Ejercicios`.

Además, la finalización actual depende exclusivamente de haber respondido todos los ejercicios.

La experiencia pedagógica profesional, las evidencias y la política de finalización no fueron definidas antes de reforzar esta estructura con funcionalidades y pruebas.

### Impacto confirmado en backend

#### Componentes que pueden conservarse

- conversaciones guiadas y ramificadas;
- validación de grafos conversacionales;
- ejercicios vinculados a Skills;
- pronunciaciones y recursos de audio;
- persistencia de progreso e intentos;
- identificadores estables;
- separación entre candidato y contenido activo;
- estructura general de validadores deterministas.

#### Componentes que deberán adaptarse

- `PedagogicalUnitCandidate`;
- `ContentLimits`;
- validación de referencias internas;
- validación de identificadores;
- validación de integridad textual;
- inventario y validación de audios;
- `SkillCoverage`;
- pruebas asociadas al contrato candidato.

#### Componentes que deberán sustituirse progresivamente

- campos públicos `vocabulary`, `grammar` y `examples`;
- límites específicos de cantidad de ejemplos;
- uso de `Example` como actividad de práctica;
- cálculo heredado de dominio basado únicamente en ejercicios.

### Impacto confirmado en Flutter

#### Componentes que pueden conservarse

- `LessonPronunciation`;
- `PronunciationAudioController`;
- reproducción de audios;
- grabación y escucha de la voz;
- `LessonConversationCard`;
- `LessonExerciseCard`;
- servicios de API ampliables;
- controladores técnicos independientes de `Example`.

#### Componentes que deberán adaptarse

- modelo `Lesson`;
- deserialización del contrato;
- coordinación del progreso;
- persistencia y lectura de evidencias;
- pruebas y datos de prueba;
- selección entre flujo heredado y experiencia v2.

#### Componentes que deberán sustituirse progresivamente

- orden fijo de `LessonDetailCard`;
- sección principal `Ejemplos`;
- presentación inicial obligatoria de vocabulario y gramática;
- finalización local basada solamente en ejercicios;
- mensajes de progreso dependientes del número de ejercicios.

### Contenido y recursos

La migración deberá preservar:

- identificadores válidos;
- textos;
- traducciones cuando aporten apoyo;
- IPA;
- variantes regionales;
- archivos de audio;
- referencias conversacionales;
- progreso ya registrado.

Ningún identificador o recurso podrá cambiar silenciosamente.

### Deuda técnica creada por el modelo provisional

La estructura heredada está protegida actualmente por:

- modelos backend y Flutter;
- contenido activo;
- validadores;
- pruebas de contrato;
- pruebas de interfaz;
- cálculo de progreso;
- documentación previa.

Por ello, una sustitución directa sin compatibilidad generaría regresiones y trabajo duplicado.

### Principales factores de coste

El coste real de la corrección dependerá de:

- número de lecciones activas que deban migrarse;
- cantidad de pruebas acopladas al contrato heredado;
- cambios necesarios en persistencia y progreso;
- diseño e implementación del renderizador v2;
- construcción de adaptadores temporales;
- validación pedagógica de cada lección;
- preservación de audios e identificadores;
- pruebas verticales backend–Flutter.

No se estimará esfuerzo ni duración sin completar primero el diseño, el inventario y la lección piloto.

### Puertas arquitectónicas obligatorias

Antes de implementar cualquier nueva capacidad central deberá existir:

1. contrato profesional aprobado;
2. responsabilidades de entidades definidas;
3. mapa de impacto;
4. estrategia de compatibilidad;
5. criterios de aceptación;
6. pruebas de contrato previstas;
7. mecanismo de reversión;
8. aprobación humana antes de modificar contenido activo.

### Estado de la auditoría

Hasta este punto se ha confirmado:

- el alcance transversal del problema;
- qué infraestructura es reutilizable;
- qué componentes deben adaptarse;
- qué componentes deben sustituirse;
- la conveniencia de construir `LessonExperience` en paralelo;
- la necesidad de mantener congelado el flujo heredado.

No se ha modificado código, contenido activo, persistencia ni contratos de API.

## Automatización controlada

### Propósito

La automatización reducirá trabajo repetitivo y errores mecánicos sin sustituir las decisiones pedagógicas, arquitectónicas ni humanas.

### Capacidades permitidas

Los agentes, herramientas y scripts podrán:

- generar paquetes candidatos aislados;
- construir estructuras a partir de especificaciones aprobadas;
- comprobar identificadores y referencias;
- validar contratos y límites;
- comprobar textos, pronunciaciones y audios;
- generar pruebas deterministas;
- producir informes de cobertura;
- preparar propuestas de migración;
- generar diferencias revisables;
- actualizar documentación mediante precondiciones verificables.

### Acciones prohibidas

La automatización no podrá:

- sobrescribir directamente `content_tree.json`;
- publicar contenido candidato;
- decidir qué Skills debe enseñar una unidad;
- modificar criterios pedagógicos aprobados;
- declarar dominio sin evidencias válidas;
- eliminar campos heredados;
- cambiar identificadores silenciosamente;
- reemplazar recursos de audio sin revisión;
- aprobar sus propios resultados;
- realizar commits o publicaciones no autorizadas.

### Flujo obligatorio

Toda generación o migración seguirá esta secuencia:

1. especificación aprobada;
2. candidato aislado;
3. validaciones automáticas;
4. pruebas;
5. informe de hallazgos;
6. diferencia revisable;
7. revisión humana;
8. aprobación explícita;
9. copia o mecanismo de reversión;
10. integración controlada;
11. validación vertical;
12. documentación y trazabilidad Git.

### Separación terminológica

`Skill` continuará significando exclusivamente una habilidad pedagógica medible del estudiante.

Los agentes, herramientas, constructores y validadores generan, relacionan o comprueban Skills, pero no se denominarán `skills`.

### Diseño determinista

Los scripts de modificación deberán:

- utilizar `python3`;
- comprobar precondiciones mediante `assert`;
- operar sobre ubicaciones explícitas;
- rechazar estados Git inesperados;
- evitar reemplazos ambiguos;
- producir resultados revisables;
- comprobar formato y espacios excesivos;
- permitir restauración o reversión;
- detenerse ante cualquier inconsistencia.

### Separación candidato–activo

Los archivos candidatos permanecerán separados del contenido activo hasta su aprobación.

Una validación correcta no equivale a publicación automática.

### Revisión humana obligatoria

La revisión humana deberá confirmar como mínimo:

- coherencia con la misión;
- utilidad pedagógica;
- correspondencia con las Skills;
- calidad y naturalidad del lenguaje;
- suficiencia de las evidencias;
- ausencia de afirmaciones de dominio no justificadas;
- impacto técnico de la integración.

### Regla preventiva

La automatización se introducirá después de aprobar el contrato profesional y sus validaciones, nunca para compensar un diseño incompleto.

## Riesgos y medidas preventivas

### Coexistencia prolongada de dos arquitecturas

Riesgo:

El flujo heredado y el contrato v2 podrían coexistir indefinidamente, duplicando mantenimiento y pruebas.

Medidas:

- congelar el flujo heredado;
- prohibir nuevas lecciones heredadas;
- mantener un inventario de migración;
- revisar el avance al cerrar cada bloque;
- definir condiciones verificables para retirar el legado.

### Divergencia entre backend y Flutter

Riesgo:

El backend podría evolucionar sin que Flutter interprete correctamente el contrato.

Medidas:

- versión explícita del contrato;
- pruebas con cargas JSON reales;
- pruebas de serialización y deserialización;
- fixtures sincronizados;
- validación vertical;
- rechazo de versiones no soportadas.

### Permanencia del adaptador temporal

Riesgo:

El adaptador heredado podría convertirse en parte permanente de la arquitectura y acumular decisiones pedagógicas.

Medidas:

- limitarlo a traducción de datos compatibles;
- impedir que decida etapas, evidencias o finalización;
- identificarlo como temporal;
- probarlo aisladamente;
- documentar su retirada;
- impedir su uso para contenido nuevo.

### Pérdida de identificadores, audios o progreso

Riesgo:

Una migración incorrecta podría romper referencias persistidas o recursos existentes.

Medidas:

- inventariar identificadores y recursos;
- mantener un mapa explícito de origen y destino;
- prohibir cambios silenciosos;
- comprobar automáticamente los audios;
- respaldar antes de integrar;
- exigir migración reversible;
- probar con progreso existente.

### Afirmaciones de aprendizaje no medido

Riesgo:

Completar actividades podría confundirse con dominio de conversación, pronunciación o fluidez.

Medidas:

- separar práctica, aplicación, evidencia y dominio;
- exigir `EvidenceDefinition`;
- declarar el modo real de medición;
- no inferir pronunciación desde una grabación;
- no inferir fluidez desde una ruta completada;
- clasificar el dominio actual basado en ejercicios como cálculo heredado.

### Sobreingeniería del motor de etapas

Riesgo:

Soportar variantes futuras no confirmadas podría retrasar el producto y crear abstracciones innecesarias.

Medidas:

- implementar únicamente etapas aprobadas;
- validar el diseño mediante una lección piloto;
- no crear extensiones sin un caso real;
- mantener contratos ampliables sin capacidades especulativas;
- justificar cada nueva abstracción.

### Nuevo acoplamiento de los validadores

Riesgo:

Los validadores podrían volver a depender rígidamente de entidades concretas.

Medidas:

- separar reglas comunes y específicas;
- reutilizar validaciones de texto, pronunciación, identificadores y referencias;
- mantener códigos de hallazgo estables;
- probar validadores aisladamente;
- evitar un servicio central con condicionales crecientes.

### Pruebas que protejan el diseño descartado

Riesgo:

Una suite correcta podría conservar comportamientos heredados que ya no representan la arquitectura objetivo.

Medidas:

- clasificar pruebas como heredadas, de compatibilidad o v2;
- mantener pruebas antiguas mientras exista contenido heredado;
- crear pruebas desde criterios pedagógicos aprobados;
- verificar comportamientos y no solo campos;
- retirar pruebas junto con el componente correspondiente.

### Publicación accidental de candidatos

Riesgo:

Un candidato técnicamente válido podría sustituir contenido activo sin revisión pedagógica.

Medidas:

- separar físicamente candidatos y contenido activo;
- impedir escritura directa sobre `content_tree.json`;
- exigir un diff revisable;
- requerir aprobación humana explícita;
- utilizar un proceso separado de promoción;
- registrar validaciones y aprobación.

### Autoridad excesiva de la automatización

Riesgo:

Un agente o herramienta podría tomar decisiones pedagógicas o arquitectónicas no autorizadas.

Medidas:

- limitar permisos por función;
- producir propuestas y no publicaciones automáticas;
- usar herramientas deterministas para operaciones críticas;
- exigir revisión humana;
- registrar entradas, resultados y hallazgos;
- detenerse ante precondiciones incumplidas.

### Reversión no comprobada

Riesgo:

Mantener una copia no garantiza que el sistema pueda restaurarse correctamente.

Medidas:

- probar la restauración antes de publicar;
- conservar contratos anteriores durante la transición;
- validar el rollback backend–Flutter;
- separar migraciones irreversibles de nuevas funcionalidades;
- mantener commits pequeños y trazables.

### Cierre incompleto

Riesgo:

El núcleo v2 podría integrarse sin documentación, validación vertical o estado Git limpio.

Medidas:

Ningún bloque relacionado podrá cerrarse sin:

- contrato aprobado;
- riesgos documentados;
- pruebas previstas y ejecutadas;
- validación backend–Flutter;
- revisión pedagógica;
- documentación actualizada;
- mecanismo de reversión comprobado;
- Git y GitHub limpios y sincronizados.

## Documentación técnica didáctica

La documentación del proyecto deberá servir simultáneamente como referencia profesional y como material de aprendizaje.

Cada concepto nuevo deberá explicar:

- qué es;
- qué problema resuelve;
- por qué se utiliza;
- dónde se encuentra en el sistema;
- cómo se relaciona con otros componentes;
- un ejemplo aplicado al proyecto;
- alternativas relevantes;
- riesgos, límites y carácter temporal cuando corresponda.

Se documentarán progresivamente:

- contratos y esquemas;
- clases y responsabilidades;
- patrones de diseño realmente aplicados;
- Skills pedagógicas;
- agentes, herramientas y constructores;
- validadores deterministas;
- adaptadores y migraciones;
- APIs y persistencia;
- MCP cuando exista un caso de uso aprobado;
- automatización e inteligencia artificial;
- arquitectura backend–Flutter;
- pruebas y trazabilidad Git.

No se utilizarán como equivalentes los términos clase, patrón, contrato, Skill, agente y herramienta.

### Manual técnico

Comenzará como documentación modular versionada junto con cada capacidad.

Después de validar la primera lección v2 se consolidarán:

- arquitectura;
- instalación y ejecución;
- componentes;
- contratos;
- flujos;
- persistencia;
- pruebas;
- solución de problemas;
- decisiones y migraciones.

### Manual de usuario

Su índice podrá prepararse durante el desarrollo, pero sus instrucciones y capturas se crearán a partir de una experiencia real y estable.

La primera versión se elaborará después de validar la lección piloto v2 y se comprobará mediante un recorrido realizado únicamente con el manual.

## Criterios de aceptación

B116 será aceptable únicamente cuando:

1. el contrato de `LessonExperience` y sus entidades esté definido;
2. el flujo pedagógico profesional esté aprobado;
3. las responsabilidades estén separadas;
4. `Skill` conserve su significado pedagógico medible;
5. `Example` esté clasificado como legado congelado;
6. la sustitución paralela esté definida;
7. la finalización se base en evidencias;
8. práctica, aplicación, evidencia y dominio estén diferenciados;
9. no se atribuyan capacidades que el sistema todavía no mide;
10. el impacto backend–Flutter esté auditado;
11. estén identificados los componentes que se conservan, adaptan y sustituyen;
12. identificadores, audios, pronunciaciones y progreso estén protegidos;
13. exista separación entre especificación, candidato y contenido activo;
14. la automatización tenga autoridad limitada;
15. los riesgos y medidas preventivas estén documentados;
16. la documentación técnica tenga función didáctica;
17. el documento no tenga contradicciones ni secciones pendientes;
18. `git diff --check` finalice correctamente;
19. no se haya implementado prematuramente el contrato v2.

## Definition of Done

B116 solo podrá cerrarse cuando:

- el contrato profesional esté completo;
- las responsabilidades estén definidas;
- la decisión sobre `Example` esté registrada;
- las evidencias y la finalización estén definidas;
- la sustitución paralela esté aprobada;
- la auditoría de impacto esté completa;
- la automatización y sus límites estén documentados;
- los riesgos y criterios de aceptación estén registrados;
- la estrategia de manual técnico y manual de usuario esté definida;
- el documento haya sido revisado y validado;
- la bitácora esté actualizada;
- se realice commit y push;
- el repositorio quede limpio y sincronizado;
- no se haya modificado código ni contenido activo.
