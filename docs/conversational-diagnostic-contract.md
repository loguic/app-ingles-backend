# Contrato del diagnóstico conversacional

## Propósito

Este documento define los contratos puros de B177 para representar un diagnóstico conversacional contextual y su punto de entrada pedagógico personalizado.

El diagnóstico contempla cuatro perfiles orientativos: 6–8 años, 9–12 años, 13–17 años y adultos.

La edad adapta la experiencia, pero no determina automáticamente la capacidad lingüística.

## Separación de responsabilidades

```text
sesión
≠ contexto autorizado
≠ actividad
≠ producción
≠ evaluación técnica
≠ apoyo utilizado
≠ observación diagnóstica
≠ perfil inicial
≠ progreso
≠ mastery
```

Una relación de trazabilidad no implica equivalencia entre estos objetos.
## Contratos

### ConversationalDiagnosticSession

Representa una ejecución trazable del diagnóstico.

Incluye identificadores de sesión y usuario, perfil de edad, estado, fecha de inicio y fecha de finalización opcional.

Estados permitidos: `in_progress`, `provisional`, `completed` y `cancelled`.

Protege la coherencia temporal entre el estado y las fechas de inicio y finalización.

### ConversationalDiagnosticContext

Conserva únicamente el contexto autorizado necesario para personalizar la experiencia.

Incluye lenguas habituales, contacto previo con el inglés, intereses generales, objetivos de aprendizaje, nivel de autonomía, presencia opcional del adulto responsable y autorización de audio.

Las listas deben contener valores únicos y no vacíos. Este contrato no incorpora datos personales innecesarios.
### ConversationalDiagnosticActivity

Declara una actividad dentro de una sesión diagnóstica.

Incluye etapa, intención comunicativa, modalidad, evidencia esperada, ayudas disponibles, variante de transferencia y orden de ejecución.

Una actividad de transferencia debe declarar su variante. Las demás actividades no pueden definirla.

### DiagnosticSupportUsage

Registra un apoyo realmente utilizado durante una respuesta diagnóstica.

Incluye sesión, actividad, producción, tipo e intensidad del apoyo, orden, momento de aplicación y retirada posterior.

La ausencia de ayuda se representa mediante `support_type="none"` y `support_level="none"`.
### ConversationalDiagnosticObservation

Describe una conducta observada y trazable dentro de una actividad diagnóstica.

Puede relacionarse con una producción y con resultados técnicos, pero conserva separada la interpretación diagnóstica.

Las dimensiones permitidas son comprensión auditiva, inicio de respuesta, construcción directa en inglés, producción oral, continuidad, recuperación lingüística, inteligibilidad, necesidad de apoyo, transferencia y contexto motivador.

### InitialConversationalProfile

Representa una hipótesis pedagógica inicial, trazable y revisable.

Incluye bloqueo prioritario, capacidad objetivo, apoyo recomendado, contextos relevantes, método inicial, primera lección, criterio de revisión y resumen de evidencia.

Sus estados permitidos son `provisional` y `confirmed`. No representa certificación MCER, fluidez, diagnóstico psicológico ni mastery.

### InitialConversationalProfileEvidence

Vincula el Perfil Conversacional Inicial con cada observación utilizada para generarlo.

La relación conserva trazabilidad, pero no convierte una observación aislada en una decisión pedagógica completa.
## Etapa A — contratos puros

La Etapa A definió los contratos puros y sus invariantes internos.

Validación confirmada:

- 67 pruebas específicas superadas;
- 806 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `6d4a52b`.

## Etapa B — validaciones cruzadas

La Etapa B valida las relaciones entre:

- sesión y contexto autorizado;
- actividad, contexto y modalidad;
- actividad y producción mediante `prompt_id`;
- producción y observación;
- producción y evaluaciones técnicas;
- apoyos disponibles, utilizados y retirados;
- observación y nivel real de apoyo;
- actividades y secuencia diagnóstica;
- perfil inicial, sesión y evidencias;
- producción y propiedad exclusiva de una actividad.

Una producción puede respaldar varias observaciones de la misma actividad, pero no puede reutilizarse entre actividades diferentes.

Las evaluaciones técnicas conservan su trazabilidad hacia la producción observada, pero no se convierten automáticamente en una decisión pedagógica.

## Etapa C — generación del Perfil Conversacional Inicial

La Etapa C añadió una generación determinista, trazable y revisable del Perfil Conversacional Inicial.

La generación:

- deriva el estado `provisional` o `confirmed` desde el estado de la sesión;
- exige un único bloqueo prioritario explícito;
- conserva los contextos relevantes autorizados;
- separa las observaciones diagnósticas del plan pedagógico;
- vincula todas las observaciones utilizadas mediante evidencias trazables;
- valida que la primera lección exista y contenga `LessonExperience`;
- exige evidencia diagnóstica completa para un perfil confirmado;
- permite evidencia incompleta para un perfil provisional revisable.

El método recomendado permanece limitado a `direct-english-construction`.

La generación no deriva automáticamente MCER, fluidez, mastery, progreso ni diagnóstico psicológico.

Validación confirmada:

- pruebas específicas del diagnóstico superadas;
- 915 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `d0004fd`.

## B179 — Hito A: persistencia relacional

El Hito A persiste las siete entidades principales del diagnóstico:

- `ConversationalDiagnosticSession`;
- `ConversationalDiagnosticContext`;
- `ConversationalDiagnosticActivity`;
- `ConversationalDiagnosticSupportUsage`;
- `ConversationalDiagnosticObservation`;
- `InitialConversationalProfile`;
- `InitialConversationalProfileEvidence`.

Dos tablas normalizadas adicionales protegen la trazabilidad cruzada:

- `conversational_diagnostic_activity_productions` asigna cada producción a una única actividad y exige coincidencia de sesión, actividad, `prompt_id` y producción;
- `conversational_diagnostic_observation_evaluations` vincula observaciones y evaluaciones técnicas de la misma producción, sin identificadores JSON sin integridad relacional.

Los perfiles se conservan como historial acumulativo y revisable, sin sobrescritura destructiva. La restricción `ck_diagnostic_observation_required_production` exige producción para `response_initiation`, `direct_english_construction`, `oral_production`, `continuity`, `linguistic_retrieval`, `intelligibility`, `support_need` y `transfer`.

La revisión Alembic `3c4f1a2b7d90` dispone de `upgrade` y `downgrade`, ambos validados en una base aislada.

## B179 — Hito B: persistencia transaccional incremental

`ConversationalDiagnosticSessionSetup` agrega sesión, contexto y actividades usando los contratos Pydantic existentes. `save_conversational_diagnostic_session_setup` valida el agregado antes del primer `add`, rechaza identificadores existentes sin idempotencia ni sobrescritura, ejecuta tres `flush`, un único `commit` y rollback ante errores esperados o inesperados.

`get_conversational_diagnostic_session_setup` reconstruye el agregado desde SQLAlchemy a Pydantic, ordena actividades por `sequence_order` y `activity_id`, y no ejecuta commit ni depende de lazy loading. Los errores públicos distinguen sesión existente, referencia ausente, invariante inválido y fallo general de persistencia.

Validación confirmada: 16 pruebas específicas, 190 pruebas de regresión diagnóstica, suite backend de 983 pruebas y commit técnico `56a3d42`.

El segundo incremento amplía el agregado con `production_supports=[]`, conservando compatibilidad con configuraciones del primer incremento. `ConversationalDiagnosticActivityProductionSetup` referencia una producción preexistente y sus usos de apoyo; `ConversationalDiagnosticProductionSupportsBatch` agrupa asociaciones nuevas para enriquecer una sesión ya persistida.

`save_conversational_diagnostic_session_setup` puede crear la configuración, la propiedad actividad–producción y sus apoyos en una única transacción: conserva los tres `flush` de configuración y añade dos para asociaciones y apoyos. `save_conversational_diagnostic_production_supports(batch, db)` usa estos dos últimos al enriquecer una sesión. Ambas rutas ejecutan exactamente un commit y rollback integral, sin sobrescritura ni idempotencia implícita.

`LearnerProduction` debe existir previamente y solo se consulta. La validación reconstruye desde persistencia su `prompt_id` y modalidad, exige compatibilidad de sesión y actividad, protege la propiedad exclusiva y reutiliza las reglas canónicas de apoyos disponibles, utilizados y retirados, incluido el historial previo. La recuperación es explícita, estable y no usa lazy loading ni commit.

Validación confirmada: 41 pruebas específicas en 0.72 s, 190 de regresión diagnóstica en 1.29 s, suite backend de 1008 pruebas en 5.60 s, revisión sin defectos accionables y commit técnico `719aa74`. No se modificaron modelos ni migraciones.

## Límites vigentes

Hito B continúa activo. Todavía no persiste observaciones, enlaces con evaluaciones, perfiles, evidencias de perfil ni el historial completo consultable. No incluye API, Flutter, progreso o mastery. El siguiente incremento incorporará observaciones diagnósticas y sus referencias a evaluaciones técnicas preexistentes.

## Validación confirmada de la Etapa B

- 71 pruebas específicas superadas;
- 879 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `e4e287c`.
