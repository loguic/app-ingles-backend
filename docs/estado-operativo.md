# Estado operativo — LOGUIC English

Actualizado: 2026-08-06
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Horizonte pedagógico: 3 meses como meta y 6 meses como máximo.
- Todo bloque nuevo debe partir de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B178 — Sistematización profesional del método de trabajo

Estado: último bloque completamente cerrado.

Capacidades completadas:

- checkpoint operativo compacto y validable;
- detección de estado desactualizado y límite de tamaño;
- generación de resumen operativo corto;
- orquestación sobre `block_close.py`;
- interrupción temprana ante contexto operativo inválido.

Validación final:

- pruebas específicas: 8 passed;
- suite backend: 923 passed;
- `git diff --check`: limpio;
- commit técnico: `c08196d`.

## Bloque activo

### B179 — Diagnóstico conversacional persistente y consultable

Hito A — modelos persistentes y migración Alembic: cerrado técnicamente mediante validación directa de respaldo.

Hito S1 — contrato ejecutable de seguridad DevSecOps: cerrado técnicamente.

Capacidades completadas:

- persistencia de las siete entidades diagnósticas principales;
- propiedad exclusiva actividad–producción;
- coincidencia relacional de sesión, actividad, `prompt_id` y producción;
- integridad observación–evaluación–producción;
- perfiles iniciales históricos y acumulativos;
- producción obligatoria para las ocho dimensiones dependientes;
- revisión Alembic `3c4f1a2b7d90` con `upgrade` y `downgrade` validados aisladamente.
- puerta preventiva fail-closed con entorno e identidad explícitos;
- evidencias verificables de backup, restauración, ensayo y rollback;
- producción rechazada incondicionalmente en S1.

Validación final directa en Kitty:

- pruebas específicas: 14 passed in 1.13s;
- regresión relacionada: 7 passed in 0.31s;
- suite backend: 937 passed in 2.91s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión final de Codex: sin defectos accionables;
- commit técnico: `40a30b3`.

Validación de S1:

- pruebas específicas: 17 passed;
- regresión de ingeniería: 27 passed;
- suite backend: 954 passed in 2.89s;
- revisión de Codex: sin defectos accionables;
- `operational_state.py validate` y `git diff --check`: correctos;
- commit técnico: `0472093`.

Límites vigentes:

- sin servicio transaccional;
- sin API ni Flutter;
- sin progreso ni mastery;
- conversión Pydantic–tablas normalizadas pendiente del Hito B.

## Deuda operativa separada

El cierre mediante `block_workflow.py` no terminó correctamente. La herramienta puede perder la salida final o dejar procesos hijos al interrumpirse; esta deuda permanece separada de B179.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` requiere resolver la deuda de interrupción antes de considerarse fiable para cierres desatendidos.

## Método operativo vigente

Cada hito pasa por definición, implementación técnica, validación específica, regresión relacionada, suite completa y cierre documental. Los commits y la publicación permanecen bajo confirmación humana.

## Fronteras obligatorias

- producción ≠ evaluación técnica;
- evaluación técnica ≠ observación diagnóstica;
- observación diagnóstica ≠ decisión pedagógica;
- perfil inicial ≠ progreso;
- progreso ≠ mastery.

## Próximo objetivo

B179 Hito S2 — diseñar el adaptador PostgreSQL seguro para backup y restauración aislada, sin aplicarlo todavía a datos reales.

El diseño debe conservar el núcleo común sin red ni ejecución y preparar adaptadores específicos antes de cualquier propagación transversal.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/conversational-diagnostic-contract.md`;
- `docs/devsecops-gate.md`;
- `docs/roadmap.md`;
- `docs/bitacora.md`.
