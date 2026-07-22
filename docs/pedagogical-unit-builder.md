# Constructor Pedagógico de Unidades

## Propósito

Diseñar, generar y validar unidades pedagógicas completas para LOGUIC English a partir de resultados de aprendizaje observables y Skills medibles.

El constructor debe reducir el trabajo fragmentado, mantener coherencia entre lecciones y producir paquetes candidatos compatibles con los contratos existentes del backend y frontend.

Su finalidad no es generar contenido masivo sin control, sino acelerar la construcción profesional de A1 a C2 mediante especificaciones aprobadas, validaciones deterministas, revisión humana y trazabilidad en Git.

## Principios obligatorios

- Seguir el roadmap aprobado y no abrir capacidades ajenas al bloque activo.
- Diseñar primero la unidad completa antes de generar lecciones aisladas.
- Partir de resultados de aprendizaje observables y Skills medibles.
- Cada contenido debe introducir, practicar, aplicar o evaluar una habilidad concreta.
- Mantener progresión pedagógica entre lecciones y evitar repeticiones sin propósito.
- Reutilizar los contratos existentes del backend y frontend.
- Generar primero un paquete candidato; nunca sobrescribir contenido activo sin aprobación.
- Aplicar validaciones deterministas antes de cualquier revisión humana.
- Mantener identificadores estables, trazabilidad y reversión sencilla.
- No permitir que agentes o IA omitan pruebas, validaciones o aprobación humana.
- Priorizar aprendizaje demostrable sobre cantidad de contenido.
- Evitar sobreingeniería: agentes y MCP solo se incorporarán cuando resuelvan una necesidad confirmada.

## Contrato de entrada

Cada construcción deberá recibir una especificación de unidad versionable y validable con estos campos:

- `unit_id`: identificador estable, por ejemplo `a1-u1`.
- `level`: nivel CEFR asociado, por ejemplo `A1`.
- `title`: nombre visible de la unidad.
- `learner_outcome`: capacidad observable que el estudiante demostrará al finalizar.
- `prerequisites`: conocimientos o Skills necesarios antes de comenzar.
- `skills`: Skills medibles que la unidad debe introducir, practicar o consolidar.
- `required_evidence`: evidencias mínimas exigidas para demostrar cada Skill.
- `lesson_scope`: límites temáticos y comunicativos de la unidad.
- `language_scope`: vocabulario, funciones comunicativas y gramática permitidos.
- `pronunciation_scope`: sonidos, ritmo, acento o variantes regionales que se practicarán.
- `content_constraints`: límites de dificultad, extensión, repetición y cantidad de contenido.
- `technical_constraints`: contratos, identificadores y capacidades existentes que deben reutilizarse.
- `acceptance_criteria`: condiciones pedagógicas y técnicas que debe superar el paquete candidato.

Ningún campo obligatorio podrá ser completado silenciosamente por un agente. Los datos ausentes deberán bloquear la generación o quedar marcados explícitamente para aprobación humana.

## Contrato de salida

El constructor deberá producir un paquete candidato completo, aislado del contenido activo, que incluya:

- especificación final de la unidad y resultado observable;
- secuencia pedagógica ordenada de lecciones;
- Skills trabajados y nivel de participación en cada lección;
- objetivos, vocabulario, gramática y pronunciación por lección;
- ejemplos con identificadores estables;
- ejercicios vinculados mediante `skill_ids`;
- conversaciones guiadas o ramificadas con grafos válidos;
- evidencias exigidas para demostrar cada Skill;
- matriz de cobertura completa;
- inventario de audios y recursos necesarios;
- informe de validaciones pedagógicas y técnicas;
- lista explícita de decisiones pendientes de aprobación humana;
- diff o propuesta de cambios antes de modificar archivos activos.

El paquete candidato deberá poder ser rechazado completamente sin alterar el contenido vigente. Solo una versión aprobada podrá pasar al flujo de integración, pruebas y revisión visual.

## Papel de los Skills

Un `Skill` representa exclusivamente una habilidad concreta y medible que debe desarrollar el estudiante. Los agentes, herramientas y validadores no se denominarán Skills.

El diseño de cada unidad deberá comenzar por los Skills necesarios para alcanzar el resultado observable. Las lecciones, ejemplos, conversaciones y ejercicios se derivarán de ellos, no al contrario.

Cada Skill deberá:

- tener un identificador estable y una descripción pedagógica clara;
- indicar si se introduce, practica, aplica, evalúa o consolida;
- aparecer en una progresión coherente entre lecciones;
- contar con evidencia observable de aprendizaje;
- vincularse explícitamente con los ejercicios mediante `skill_ids`;
- participar en conversación, escucha, pronunciación u otras prácticas cuando corresponda;
- alimentar el cálculo de dominio, el repaso y la siguiente acción recomendada;
- quedar representado en la matriz de cobertura de la unidad.

El constructor deberá rechazar unidades con Skills declarados pero sin práctica, aplicación o evaluación suficiente.

## Matriz de cobertura

Cada paquete candidato deberá incluir una matriz que relacione los Skills con las lecciones y evidencias de la unidad.

La matriz deberá registrar, como mínimo:

- identificador y descripción del Skill;
- lección donde se introduce;
- actividades donde se practica;
- conversación o contexto donde se aplica;
- ejercicio o evidencia donde se evalúa;
- lección o actividad donde se consolida;
- modalidades implicadas: listening, speaking, reading, writing o pronunciation;
- estado de cobertura: completa, incompleta o pendiente de aprobación.

El constructor deberá detectar automáticamente Skills sin introducción, práctica, aplicación o evaluación. Una unidad con cobertura incompleta no podrá integrarse en el contenido activo salvo excepción pedagógica explícitamente documentada y aprobada.

## Validaciones deterministas

Antes de cualquier revisión mediante agentes o personas, el paquete candidato deberá superar validaciones automáticas reproducibles:

- conformidad con el contrato de entrada y ausencia de campos obligatorios vacíos;
- compatibilidad con los esquemas vigentes del backend y los modelos del frontend;
- identificadores estables, únicos y con formato coherente;
- referencias internas válidas y ausencia de elementos huérfanos;
- integridad de los grafos de conversaciones guiadas y ramificadas;
- ejercicios con opciones válidas, respuesta correcta y `skill_ids`;
- cobertura de introducción, práctica, aplicación y evaluación para cada Skill;
- evidencias obligatorias presentes para todos los resultados de aprendizaje;
- límites de contenido, dificultad y repetición definidos por la especificación;
- detección de duplicados exactos y similitudes por encima del umbral permitido;
- inventario completo de audios y recursos referenciados;
- aislamiento del paquete candidato respecto al contenido activo;
- pruebas contractuales y de regresión aplicables;
- `git diff --check` sin errores antes de la integración.

Un fallo en cualquiera de estas validaciones deberá rechazar el paquete o devolverlo para corrección. Las validaciones deterministas no sustituirán la revisión lingüística, pedagógica ni humana.

## Agente orquestador controlado

La primera automatización inteligente utilizará un único agente orquestador. No se implementará inicialmente una red de agentes especialistas.

Responsabilidades permitidas:

- leer la especificación aprobada de la unidad;
- consultar contratos, Skills, roadmap y contenido vigente;
- proponer la secuencia pedagógica completa;
- generar un paquete candidato aislado;
- relacionar lecciones, actividades, evidencias y Skills;
- solicitar validaciones deterministas;
- corregir el candidato cuando una validación falle;
- producir un informe de decisiones, riesgos y elementos pendientes;
- preparar la propuesta para revisión humana.

Restricciones obligatorias:

- no completar silenciosamente campos obligatorios ausentes;
- no modificar directamente el contenido activo;
- no ejecutar commits, pushes ni despliegues;
- no desactivar, alterar ni omitir validaciones;
- no aprobar su propio paquete candidato;
- no introducir nuevas capacidades fuera del roadmap aprobado;
- no utilizar herramientas externas sin autorización explícita;
- detener el flujo cuando exista una decisión pedagógica ambigua o de alto impacto.

La división en agentes especialistas solo se justificará cuando el agente único presente una limitación medible de calidad, contexto, coste o mantenibilidad.

## Preparación futura para MCP

El constructor se diseñará para que sus consultas y validaciones puedan exponerse posteriormente mediante MCP, pero B105 no implementará todavía un servidor MCP.

Capacidades candidatas para una futura exposición mediante MCP:

- consultar el roadmap y el bloque activo;
- leer contratos pedagógicos y técnicos vigentes;
- consultar el catálogo de Skills;
- obtener contenido activo y paquetes candidatos;
- validar identificadores y referencias;
- comprobar grafos conversacionales;
- calcular la matriz de cobertura;
- detectar duplicados y recursos ausentes;
- ejecutar validadores pedagógicos y contractuales;
- producir informes de integración.

MCP se incorporará únicamente cuando exista una necesidad confirmada de reutilizar estas capacidades desde varios agentes, aplicaciones o herramientas. Su adopción deberá incluir permisos mínimos, operaciones de solo lectura por defecto, aprobación humana para acciones sensibles y registros de auditoría.

## Flujo de aprobación humana

El contenido generado no podrá incorporarse automáticamente al producto. El flujo obligatorio será:

1. aprobar la especificación de entrada de la unidad;
2. generar el paquete candidato en un espacio aislado;
3. superar todas las validaciones deterministas;
4. revisar la progresión pedagógica y la cobertura de Skills;
5. revisar la corrección lingüística, cultural y comunicativa;
6. revisar conversaciones, ejercicios, respuestas y posibles ambigüedades;
7. comprobar los cambios propuestos mediante un diff legible;
8. aprobar explícitamente la integración en el contenido activo;
9. ejecutar pruebas backend, frontend y validación visual;
10. documentar, versionar y confirmar Git limpio.

La aprobación deberá detenerse cuando exista contenido dudoso, cobertura incompleta, una decisión no autorizada o una validación fallida. El rechazo de un paquete candidato no deberá modificar el contenido vigente.

## Criterios de aceptación

El diseño del Constructor Pedagógico será aceptado cuando:

- defina contratos claros de entrada y salida;
- utilice Skills medibles como núcleo de cada unidad;
- exija una matriz de cobertura completa;
- diferencie contenido candidato y contenido activo;
- especifique validaciones deterministas reproducibles;
- limite al agente orquestador mediante permisos y restricciones explícitas;
- mantenga MCP como preparación futura, sin convertirlo en dependencia actual;
- incluya aprobación humana antes de cualquier integración;
- preserve los contratos vigentes de backend y frontend;
- permita rechazar o revertir un paquete sin afectar el producto;
- mantenga trazabilidad documental y compatibilidad con Git;
- pueda aplicarse inicialmente a A1-U1 sin diseñar una solución exclusiva para esa unidad;
- no introduzca capacidades fuera de la Fase 5 ni altere el roadmap aprobado.

## Definition of Done

B105 podrá cerrarse cuando:

- el documento de arquitectura esté completo y revisado;
- los contratos de entrada y salida estén definidos;
- el papel de los Skills y la matriz de cobertura estén aprobados;
- las validaciones deterministas estén enumeradas;
- el agente orquestador tenga responsabilidades y restricciones explícitas;
- la preparación futura para MCP esté documentada sin implementación prematura;
- el flujo de aprobación humana esté definido;
- los criterios de aceptación se hayan verificado;
- el diseño sea aplicable a distintas unidades y niveles;
- se confirme que no contradice el roadmap ni los contratos existentes;
- `git diff --check` no detecte errores;
- la documentación se revise mediante un diff legible;
- B105 quede registrado en la bitácora;
- los commits se publiquen en GitHub;
- el repositorio quede limpio y sincronizado.

El cierre de B105 aprobará únicamente la arquitectura del constructor. La implementación, el agente y la primera especificación de A1-U1 deberán ejecutarse en bloques posteriores separados y trazables.
