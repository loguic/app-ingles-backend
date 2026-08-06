# Puerta DevSecOps preventiva

## Propósito

La puerta impide que una operación potencialmente destructiva avance sin evidencia verificable de recuperación. S1 define únicamente un contrato ejecutable de seguridad: valida un plan JSON local y falla de forma cerrada ante cualquier evidencia ausente, inválida, incoherente, vencida o ilegible.

## Plan de seguridad

El plan declara:

- un entorno explícito: `test`, `development`, `staging` o `production`;
- una identidad no secreta del objetivo, su huella y las revisiones actual y objetivo;
- el artefacto de backup, su fecha y su SHA-256 declarado;
- una evidencia separada de restauración, su resultado, fecha y SHA-256 restaurado;
- un ensayo de migración aislado, con revisiones inicial y final y resultados de upgrade y downgrade;
- una revisión de retorno y un procedimiento explícito de rollback.

No existe entorno implícito. Aunque `production` forma parte del vocabulario contractual, S1 lo rechaza siempre y no ofrece bypass, flag ni token de autorización.

## Controles implementados

- existencia, legibilidad, carácter regular y tamaño no vacío del backup;
- coincidencia entre el SHA-256 calculado y el declarado;
- restauración satisfactoria vinculada al SHA-256 exacto del backup;
- evidencia de restauración separada y con antigüedad máxima configurable;
- coherencia temporal entre backup, restauración y ensayo;
- ensayo aislado identificado con upgrade y downgrade satisfactorios;
- coincidencia entre revisiones del objetivo, ensayo y rollback;
- procedimiento de rollback no vacío;
- mensajes fail-closed que no exponen secretos ni URLs de conexión.

## Límites de S1

La puerta:

- no conecta a bases de datos;
- no ejecuta Alembic;
- no crea ni restaura backups;
- no inicia procesos externos;
- no accede a red;
- no autoriza producción;
- no sustituye todavía una prueba real de restauración.

## Validación técnica

- 17 pruebas específicas;
- 27 pruebas de regresión de ingeniería;
- suite backend completa: 954 passed in 2.89s;
- revisión de Codex sin defectos accionables;
- `operational_state.py validate` válido;
- `git diff --check` limpio;
- commit técnico `0472093`.

## Estrategia transversal

LOGUIC English será el proyecto piloto. El núcleo común se extraerá posteriormente a un repositorio independiente y versionado. Cada proyecto tendrá un adaptador propio para su base de datos, backups, migraciones, pruebas y entornos; los scripts no se copiarán manualmente entre repositorios.

La propagación solo comenzará después de validar backup y restauración reales en un entorno aislado. Los proyectos futuros previstos incluyen CNAPP-Lite, AutoRadar ES, AgencyForge y otros.

## Siguiente hito

S2 diseñará un adaptador PostgreSQL seguro para backup y restauración aislada, sin aplicarlo todavía a datos reales.

La deuda de `block_workflow.py`, cuya interrupción puede perder la salida final o dejar procesos hijos activos, permanece separada y fuera de este hito.
