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

## Límites vigentes

Todavía no se incluyen persistencia, migraciones, API, contenido piloto ni integración Flutter.

## Validación confirmada de la Etapa B

- 71 pruebas específicas superadas;
- 879 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `e4e287c`.
