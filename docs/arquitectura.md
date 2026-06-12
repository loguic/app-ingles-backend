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
