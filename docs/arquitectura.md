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
