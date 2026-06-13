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
