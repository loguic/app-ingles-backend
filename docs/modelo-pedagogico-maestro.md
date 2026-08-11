# Modelo Pedagógico Maestro de LOGUIC English

## Propósito

Este documento define el puerto de llegada pedagógico de LOGUIC English y gobierna las decisiones futuras de producto, contenido, arquitectura e implementación.

LOGUIC English no se construirá como una colección de funcionalidades técnicas ni como un curso tradicional organizado principalmente alrededor de explicaciones gramaticales, ejercicios aislados o lecciones completadas.

Su núcleo diferencial será un sistema de aprendizaje conversacional que convierta teorías y métodos pedagógicos seleccionados en experiencias prácticas, progresivas, medibles y transferibles.

## Puerto de llegada

LOGUIC English será un entrenador pedagógico de fluidez conversacional.

Su objetivo será ayudar al estudiante a desarrollar conversación funcional, espontánea, inteligible y transferible mediante práctica oral frecuente, comprensión auditiva, construcción directa en inglés, feedback útil, repetición adaptativa y conversaciones nuevas.

El estudiante no completará el recorrido por tiempo transcurrido ni por acumulación de puntos. Deberá demostrar capacidades conversacionales observables.

## Fluidez conversacional funcional

El estudiante alcanza fluidez conversacional funcional cuando puede mantener conversaciones nuevas sin depender constantemente de traducciones, guiones o ayudas de la aplicación.

Deberá poder:

- comprender la intención principal del interlocutor;
- iniciar respuestas con una demora razonable;
- construir frases directamente en inglés;
- enlazar y ampliar ideas;
- formular preguntas espontáneas;
- reaccionar a información inesperada;
- reformular cuando no conoce una palabra;
- pedir aclaraciones y reparar malentendidos;
- continuar después de errores o bloqueos;
- mantener una pronunciación suficientemente inteligible;
- transferir estas capacidades a situaciones cotidianas y profesionales reales.

Fluidez funcional no significa hablar como una persona nativa, eliminar completamente el acento, conocer todas las reglas gramaticales, comprender cada palabra ni hablar sin cometer errores.

## Horizonte de aprendizaje

El recorrido principal tendrá un horizonte intensivo orientativo de tres a seis meses:

- tres meses para estudiantes constantes, con dedicación intensiva y un punto de partida favorable;
- hasta seis meses para un recorrido sostenible o para estudiantes que necesiten mayor consolidación.

Estos plazos no constituyen una garantía automática. El avance dependerá de la práctica realizada y del desempeño demostrado.

## Núcleo pedagógico

Las teorías, métodos y técnicas de aprendizaje serán el núcleo diferencial de LOGUIC English.

La tecnología, la inteligencia artificial, los modelos acústicos, el reconocimiento de voz, los contratos backend y la interfaz estarán subordinados al aprendizaje observable del estudiante.

Ninguna solución técnica se considerará valiosa únicamente por aumentar la sofisticación del sistema.

## Naturaleza del contenido prototípico

El contenido construido durante el desarrollo de infraestructura puede servir para demostrar contratos, contenido estructurado, runtime, producción, evaluación, persistencia y otras capacidades técnicas sin convertirse automáticamente en contenido pedagógico canónico.

En particular, la `a1-u1-l1` actual es un prototipo/candidato histórico y no la futura puerta de entrada A1 definitiva. Su valor técnico y pedagógico experimental se preserva, pero no autoriza a tratarla como fundamento canónico de la progresión A1 ni a describirla retrospectivamente como una L1 definitiva fallida.

## Separación de estados pedagógicos

La regla permanente es:

`EXPUESTO != ENSEÑADO != PRACTICADO != EVIDENCIADO != DOMINADO`

- **Expuesto:** el estudiante ha encontrado una forma, significado o capacidad en contenido, audio o interacción; su aparición no demuestra comprensión.
- **Enseñado:** la capacidad fue presentada con intención pedagógica, explicación o andamiaje suficiente para hacerla comprensible.
- **Practicado:** el estudiante tuvo oportunidades reales de recuperar o producir la capacidad con una progresión de apoyo definida.
- **Evidenciado:** existe desempeño observable y trazable bajo criterios explícitos; una evidencia aislada no implica dominio estable.
- **Dominado:** la capacidad se demuestra de forma suficientemente consistente, transferible y retenida en contextos pertinentes.

Ningún estado se inferirá automáticamente a partir del anterior. La mera aparición de lenguaje no equivale a aprendizaje adquirido.

## Flujo de construcción pedagógica escalable

El curso no se redactará manualmente lección por lección. Su flujo canónico será:

Modelo pedagógico maestro → capacidad observable → Constructor Pedagógico con IA → mapa de prerrequisitos → candidato pedagógico → validadores deterministas → puerta humana de calidad → runtime → evidencia humana → retroalimentación al sistema.

Las responsabilidades quedan separadas:

- la IA construye candidatos pedagógicos;
- los validadores deterministas comprueban invariantes y contratos;
- la revisión humana actúa como puerta de calidad antes de la incorporación canónica;
- la evidencia humana contrasta el diseño y su ejecución con la realidad y retroalimenta el sistema.

### Regla anti-parche

Un fallo o carencia descubierto mediante evidencia humana deberá alimentar primero las reglas, los prerrequisitos, los validadores o los criterios del sistema cuando sea generalizable. No se resolverá automáticamente parcheando una lección aislada para hacer superar una validación concreta.

## Futura entrada A1

La futura A1 L1 será la puerta de entrada pedagógica de LOGUIC English y un patrón de calidad para la progresión posterior. Deberá diseñarse minuciosamente para una persona con conocimiento muy bajo o nulo, buscando comprensión, confianza, éxito observable temprano, motivación para continuar y progresión real. Este principio no define todavía sus actividades, vocabulario, diálogos ni estructura detallada.

## Regla permanente de control del rumbo

Antes de comenzar cualquier bloque futuro deberá definirse explícitamente:

1. la fase pedagógica a la que pertenece;
2. el problema concreto del estudiante que resuelve;
3. la capacidad conversacional que desarrollará;
4. el principio o método pedagógico utilizado;
5. la experiencia práctica que realizará el estudiante;
6. la evidencia observable de aprendizaje;
7. la prueba de transferencia a una situación nueva;
8. su contribución directa a la fluidez funcional.

Una propuesta deberá aplazarse cuando su justificación sea solamente mejorar la arquitectura, completar otro contrato, preparar una posibilidad futura o aumentar la sofisticación técnica.

La secuencia obligatoria será:

Puerto de llegada → fase → problema real → método pedagógico → experiencia del estudiante → evidencia → transferencia → implementación técnica.

## Sistema operativo de desarrollo

LOGUIC English se desarrollará mediante macrobloques pedagógicos completos y demostrables, no mediante una sucesión indefinida de cambios técnicos aislados.

Cada macrobloque deberá entregar una capacidad observable del estudiante. Podrá incluir conjuntamente contenido, backend, frontend, audio, evaluación, pruebas y documentación cuando todos esos elementos sean necesarios para completar la misma experiencia pedagógica.

Las tareas internas, como schemas, servicios, persistencia, API o componentes Flutter, no se considerarán por sí solas un resultado de producto.

### Tres puertas humanas

Cada macrobloque deberá atravesar tres puntos obligatorios de aprobación.

#### Puerta 1 — Definición de la capacidad

Antes de modificar código deberán quedar aprobados:

- el problema concreto del estudiante;
- la fase pedagógica;
- la capacidad conversacional objetivo;
- el principio o método aplicado;
- la experiencia que realizará el estudiante;
- la evidencia observable;
- la prueba de transferencia;
- el alcance y las exclusiones;
- los criterios de aceptación.

#### Puerta 2 — Plan de implementación

Después de inspeccionar únicamente lo necesario deberán quedar definidos:

- las capacidades existentes que se reutilizarán;
- los cambios técnicos necesarios;
- los archivos o módulos afectados;
- las pruebas requeridas;
- los riesgos;
- la estrategia de reversión;
- la documentación que deberá actualizarse.

La implementación no comenzará mientras el plan no permita visualizar una capacidad completa y no una colección de parches.

#### Puerta 3 — Cierre

Un macrobloque solo podrá cerrarse cuando incluya:

- demostración funcional de la capacidad;
- prueba de la experiencia del estudiante;
- evidencia de transferencia;
- pruebas específicas;
- regresión necesaria;
- documentación actualizada;
- revisión limpia del diff;
- Git limpio y sincronizado cuando corresponda;
- comprobación de su contribución al puerto de llegada.

### Reparto de responsabilidades

El sistema de trabajo seguirá esta separación:

- el usuario aprueba el producto, las prioridades, la experiencia y los resultados;
- ChatGPT estructura el modelo pedagógico, el alcance, la arquitectura y los criterios;
- Codex podrá ejecutar posteriormente inspecciones técnicas, implementación, pruebas y preparación del diff;
- las pruebas verifican el comportamiento técnico;
- Git y GitHub conservan trazabilidad, reversión y publicación.

La secuencia de control será:

Humano dirige → ChatGPT estructura → Codex ejecuta → pruebas verifican → Git registra.

Codex no decidirá autónomamente el rumbo pedagógico, los métodos de aprendizaje ni los criterios de fluidez.

### Condiciones previas para incorporar Codex

Codex no se incorporará al flujo hasta disponer de:

- este Modelo Pedagógico Maestro consolidado;
- un roadmap reorganizado por capacidades;
- un archivo `AGENTS.md` con reglas del repositorio;
- una plantilla canónica de macrobloque;
- comandos oficiales de validación y cierre;
- límites claros de escritura, red, commits y push.

La configuración inicial deberá ser conservadora:

- escritura limitada al repositorio;
- acceso de red deshabilitado salvo necesidad aprobada;
- operaciones delicadas sujetas a aprobación;
- commits y push manuales;
- sin ejecución paralela de múltiples agentes;
- sin MCP hasta que exista una necesidad demostrada.

### Regla de tamaño

Un bloque podrá ser más extenso cuando entregue una única capacidad pedagógica coherente.

No deberá ampliarse cuando mezcle capacidades independientes, aumente riesgos innecesarios o impida validar y revertir los cambios de manera controlada.

## Recorrido pedagógico principal

El recorrido principal de LOGUIC English se organiza en cuatro fases basadas en capacidades demostradas, no en semanas rígidas ni en lecciones completadas.

### Fase 1 — Desbloqueo mental

Objetivo: reducir la traducción mental desde el español y enseñar al estudiante a construir respuestas simples directamente en inglés.

El estudiante deberá aprender a:

- comprender intenciones comunicativas sencillas;
- iniciar respuestas sin recibir una frase completa en español;
- construir frases mediante patrones básicos del inglés;
- priorizar inicialmente una respuesta simple, rápida y comprensible;
- ampliar una frase con información adicional;
- reutilizar patrones en situaciones diferentes;
- mantener intercambios breves con ayuda reducida.

La fase se supera mediante una conversación nueva en la que el estudiante comprende, inicia, responde, amplía y reacciona a una variación inesperada con ayuda mínima.

### Fase 2 — Automatización

Objetivo: automatizar patrones lingüísticos frecuentes para recuperarlos y combinarlos rápidamente durante una conversación.

El estudiante deberá:

- recuperar vocabulario y estructuras frecuentes con menor demora;
- transformar patrones para distintas personas, tiempos e intenciones;
- formular preguntas espontáneas;
- enlazar ideas mediante conectores;
- reformular sin comenzar completamente desde cero;
- utilizar los patrones dentro de conversaciones nuevas.

La automatización solo se considera adquirida cuando existe recuperación rápida, variación y transferencia conversacional.

### Fase 3 — Continuidad conversacional

Objetivo: mantener intercambios conectados, reaccionar a información nueva y recuperarse de bloqueos sin abandonar el inglés.

El estudiante deberá:

- mantener un tema durante varios intercambios;
- relacionar sus respuestas con lo dicho anteriormente;
- ampliar ideas con razones, detalles y ejemplos;
- formular preguntas de seguimiento;
- pedir repetición o aclaración;
- ganar tiempo mientras organiza una idea;
- reformular cuando desconoce una palabra;
- reparar malentendidos;
- conservar una pronunciación suficientemente inteligible.

La fase se supera mediante una conversación nueva de aproximadamente cinco a diez minutos, con ayuda reducida y al menos una dificultad controlada.

### Fase 4 — Transferencia y fluidez funcional

Objetivo: trasladar las capacidades conversacionales a situaciones nuevas y reales.

El estudiante deberá:

- adaptarse a interlocutores, velocidades y contextos diferentes;
- comprender el mensaje principal aunque pierda algunas palabras;
- combinar patrones aprendidos en respuestas nuevas;
- improvisar con el vocabulario disponible;
- sostener conversaciones cotidianas y profesionales relevantes;
- recuperar la continuidad después de errores o malentendidos;
- mantener inteligibilidad durante habla espontánea.

La demostración final incluirá varias conversaciones no memorizadas, incluida una conversación cotidiana, otra personal o profesional y una transferencia inesperada.

## Diagnóstico conversacional inicial

LOGUIC English comenzará con un diagnóstico basado en desempeño y no principalmente con un examen de gramática.

El diagnóstico observará:

1. comprensión auditiva;
2. tiempo de inicio de respuesta;
3. construcción directa en inglés;
4. continuidad;
5. recuperación lingüística;
6. inteligibilidad;
7. necesidad de apoyo;
8. transferencia.

Su resultado será un Plan Conversacional Inicial con:

- bloqueo prioritario;
- capacidad objetivo;
- método pedagógico asignado;
- nivel de apoyo inicial;
- criterio de revisión.

El nivel CEFR podrá mantenerse como referencia general, pero no determinará por sí solo el entrenamiento.

## Ciclo diario de entrenamiento

Cada sesión seguirá este ciclo:

1. activación;
2. construcción guiada;
3. producción oral;
4. corrección prioritaria;
5. variación;
6. conversación;
7. transferencia;
8. revisión del desempeño.

La sesión deberá terminar con una conducta conversacional que el estudiante pueda realizar mejor que al comenzar.

### Intensidad

Plan intensivo:

- 45 a 60 minutos diarios;
- seis días por semana;
- 20 a 30 minutos reales hablando.

Plan sostenible:

- 25 a 35 minutos diarios;
- seis días por semana;
- 10 a 18 minutos reales hablando.

Se medirá tiempo útil de aprendizaje y no únicamente tiempo con la aplicación abierta.

## Método pedagógico 1 — Construcción directa en inglés

### Problema

El estudiante piensa primero en español, traduce palabra por palabra, duda sobre el orden y se bloquea antes de hablar.

### Principio

El estudiante construirá significado directamente mediante patrones productivos del inglés, comenzando con estructuras simples como Persona + Verbo.

Persona + Verbo será un andamio inicial y no una regla absoluta para todas las estructuras del inglés.

### Mecanismo

Intención comunicativa → Persona → Acción → Información adicional → Producción oral.

Las ayudas se retirarán progresivamente:

1. persona y verbo visibles;
2. ayudas parciales;
3. solo intención comunicativa;
4. pregunta inesperada;
5. transferencia a otro contexto.

### Experiencia

Situación real → intención comunicativa → construcción mínima → respuesta oral → corrección prioritaria → variación → conversación nueva.

### Criterio de superación

El estudiante puede producir oralmente una frase simple y comprensible desde una intención comunicativa, ampliarla y reutilizar su estructura en una conversación nueva con ayuda mínima.

La repetición de una frase memorizada no demuestra aprendizaje suficiente.

## Principio pedagógico 2 — Pronunciación funcional transversal

La pronunciación comenzará en la Fase 1 y continuará durante todo el recorrido.

LOGUIC English priorizará:

- inteligibilidad;
- percepción auditiva;
- contrastes de alto valor comunicativo;
- uso dentro de palabras, frases y conversaciones;
- correcciones breves que no destruyan la continuidad.

No será obligatorio conocer todas las reglas fonéticas ni eliminar completamente el acento.

### Mapa Sonoro Funcional

Cada ancla seguirá este ciclo:

Escuchar → distinguir → comprender la articulación → producir → recibir feedback → usar en una frase → transferir a conversación.

La selección de nuevas anclas considerará:

- riesgo comunicativo;
- dificultad para hispanohablantes;
- frecuencia;
- relevancia personal;
- percepción entrenable;
- aplicación inmediata;
- transferencia.

### Ancla Vocal 1 — /iː/–/ɪ/–/e/

La primera ancla distinguirá tres categorías sonoras inglesas mediante referencias como:

- /iː/: sheep;
- /ɪ/: ship;
- /e/: bed.

No se enseñará que las letras E e I se intercambian. Se entrenarán sonidos diferentes mediante escucha, anclas articulatorias, producción, feedback y conversación.

El estudiante supera esta ancla cuando distingue y produce los tres sonidos de manera suficientemente clara para evitar confusiones frecuentes y conserva la diferencia dentro de frases nuevas.

## Conversación continua

Conversación continua es un intercambio conectado en el que el estudiante comprende, responde, reacciona y mantiene el tema durante varias intervenciones sin recibir una frase completa para repetir.

Su progresión será:

1. tres o cuatro intercambios con ayuda visible;
2. cinco a siete intercambios con ayudas parciales;
3. ocho a doce intercambios con preguntas inesperadas;
4. conversación de tres a cinco minutos con ayuda mínima;
5. conversación de diez a veinte minutos en contextos nuevos.

La fluidez incluye estrategias de reparación, como pedir repetición, ganar tiempo, reformular o explicar una palabra desconocida.
