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

Incluye bloqueo prioritario, capacidad objetivo, apoyo recomendado, contextos relevantes, método inicial, primera experiencia, criterio de revisión y resumen de evidencia.

Sus estados permitidos son `provisional` y `confirmed`. No representa certificación MCER, fluidez, diagnóstico psicológico ni mastery.

### InitialConversationalProfileEvidence

Vincula el Perfil Conversacional Inicial con cada observación utilizada para generarlo.

La relación conserva trazabilidad, pero no convierte una observación aislada en una decisión pedagógica completa.
## Límites de la Etapa A

La Etapa A define exclusivamente contratos puros e invariantes internos.

Todavía no incluye validaciones cruzadas entre objetos, generación del perfil, persistencia, migraciones, API, contenido piloto ni integración Flutter.

## Validación confirmada

- 67 pruebas específicas superadas;
- 806 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `6d4a52b`.
