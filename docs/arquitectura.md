# Arquitectura del proyecto app-ingles-backend

## Visión general

Backend modular para una aplicación de aprendizaje de inglés por niveles.

## Stack actual

- FastAPI: framework principal de API.
- PostgreSQL: base de datos relacional.
- SQLAlchemy: ORM para comunicación con la base de datos.
- psycopg: driver PostgreSQL.
- pytest: pruebas automatizadas.

## Estructura funcional actual

- Health check.
- Niveles A1-C2.
- Árbol de contenido.
- Lecciones.
- Ejercicios.
- Progreso de usuario.
- Estadísticas de progreso.

## Idea arquitectónica futura

El sistema debe evolucionar desde lecciones simples hacia habilidades medibles:

Nivel → Unidad → Lección → Ejercicio → Intento → Progreso → Habilidad → Recomendación

## Hallazgos de arquitectura — B38

La arquitectura actual del backend está organizada de forma modular:

- `app/main.py` crea la aplicación FastAPI y conecta el router principal.
- `app/api/v1/router.py` centraliza los endpoints bajo el prefijo `/api/v1`.
- `app/api/v1/endpoints/` separa los módulos por dominio funcional.
- `app/services/` contiene lógica de negocio.
- `app/schemas/` define los modelos de entrada y salida con Pydantic.
- `app/db/` contiene configuración y modelos de base de datos.

### Puntos positivos

- Separación clara entre endpoints, servicios, schemas y base de datos.
- Uso correcto de `Depends(get_db)` para inyectar sesiones de base de datos.
- Pruebas automatizadas activas con pytest.
- Documentación inicial dentro de `docs/`.

### Mejoras futuras detectadas

- Evitar que endpoints llamen directamente a otros endpoints internos.
- Optimizar `content_service.py` para no leer el archivo JSON en cada búsqueda.
- Agregar pruebas para casos 404.
- Evolucionar los schemas de progreso hacia `ProgressCreate` y `ProgressRead`.
- Usar `Field(default_factory=list)` en listas de schemas Pydantic.
- Diseñar entidades pedagógicas futuras: `Skill`, `Attempt` y `Mastery`.

## Diseño pedagógico — B40 Skill

Una `Skill` representa una habilidad concreta que el estudiante debe desarrollar.

No equivale a una lección completa. Una lección puede trabajar varias habilidades, y una habilidad puede aparecer en varias lecciones.

### Ejemplos de Skills

- `a1_greetings_basic`: saludos básicos.
- `a1_introduce_yourself`: presentarse de forma simple.
- `a1_verb_to_be_basic`: uso básico del verbo to be.
- `a1_basic_farewells`: despedidas básicas.

### Campos propuestos

- `id`: identificador único de la habilidad.
- `name`: nombre visible de la habilidad.
- `level`: nivel asociado, por ejemplo A1.
- `category`: tipo de habilidad.
- `description`: explicación breve de la habilidad.

### Categorías iniciales

- vocabulary
- grammar
- listening
- speaking
- reading
- writing
- pronunciation

### Decisión inicial

La entidad `Skill` se diseñará primero a nivel documental. Luego se convertirá en schema, modelo de base de datos y endpoint cuando el diseño esté claro.

## Diseño pedagógico — B41 Relación Exercise-Skill

Un `Exercise` representa una actividad concreta que el estudiante debe resolver.

Una `Skill` representa la habilidad pedagógica que ese ejercicio entrena o evalúa.

### Relación propuesta

La relación entre `Exercise` y `Skill` será de muchos a muchos:

- Un ejercicio puede entrenar una o varias habilidades.
- Una habilidad puede aparecer en varios ejercicios.

### Ejemplo

El ejercicio `a1-u1-l1-q1` puede estar relacionado con:

- `a1_greetings_basic`
- `a1_vocabulary_greetings`

### Justificación pedagógica

Esta relación permite medir el progreso del estudiante no solo por ejercicios correctos o incorrectos, sino por habilidades específicas.

Ejemplo:

- El estudiante puede fallar varios ejercicios relacionados con `a1_greetings_basic`.
- El sistema podrá detectar que necesita reforzar saludos básicos.
- Más adelante, esta información permitirá calcular dominio y recomendar repasos.

### Decisión inicial

La relación `Exercise-Skill` se documenta primero como diseño conceptual.

En bloques posteriores podrá implementarse como:

- lista de `skill_ids` dentro de cada ejercicio en el JSON;
- tabla relacional `exercise_skills` en PostgreSQL;
- endpoint para consultar habilidades asociadas a ejercicios.

## Diseño técnico — B42 Registro de intentos reales

El registro de progreso debe evolucionar desde una respuesta aislada hacia un intento con contexto pedagógico.

### Campos mínimos del intento

- `user_id`: usuario que realiza el intento.
- `level_id`: nivel asociado al ejercicio.
- `unit_id`: unidad asociada al ejercicio.
- `lesson_id`: lección asociada al ejercicio.
- `exercise_id`: ejercicio respondido.
- `selected_index`: opción elegida por el usuario.
- `correct`: resultado de la evaluación.
- `created_at`: fecha y hora del intento.

### Decisión inicial

En B42 se añadirá contexto de contenido al progreso: `level_id`, `unit_id` y `lesson_id`.

La asociación con `skill_id` se dejará para una fase posterior, después de implementar la relación `Exercise-Skill`.

## Diseño técnico — B43 Dominio por habilidad

Para calcular el dominio por habilidad, cada ejercicio debe indicar qué habilidades entrena o evalúa.

### Cambio inicial

Se agrega el campo `skill_ids` a los ejercicios de tipo `ExerciseMCQ`.

Ejemplo:

- `a1-u1-l1-q1` entrena:
  - `a1_greetings_basic`
  - `a1_vocabulary_greetings`

### Fórmula inicial de dominio

El dominio por habilidad se calculará inicialmente como:

`mastery_score = aciertos relacionados con la skill / intentos relacionados con la skill`

### Decisión inicial

En B43 primero se crea la base de datos pedagógica mínima: ejercicios asociados a habilidades.

El cálculo completo de dominio podrá implementarse después usando los intentos guardados en `user_progress`.
