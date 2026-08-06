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

## S2 — adaptador PostgreSQL aislado

S2 implementó un adaptador que crea un clúster PostgreSQL temporal bajo `/tmp`, escucha exclusivamente mediante socket Unix y usa un puerto dinámico distinto de `5432`. No utiliza el servicio PostgreSQL del sistema ni hereda la `DATABASE_URL` real. Las conexiones SQLAlchemy y Alembic declaran explícitamente Psycopg 3 mediante `postgresql+psycopg://`; las herramientas PostgreSQL reciben parámetros separados.

El flujo validado es:

1. crear una base fuente aislada y datos deterministas;
2. generar un backup custom y comprobar su SHA-256;
3. restaurar en una base temporal distinta;
4. verificar esquema y datos de control;
5. ejecutar Alembic desde la revisión inicial hasta `3c4f1a2b7d90`;
6. volver mediante downgrade y comprobar la revisión inicial;
7. generar evidencia compatible con S1;
8. detener PostgreSQL y limpiar únicamente el workspace marcado.

Codex preparó y revisó el código y las pruebas sin conservar una terminal de infraestructura como evidencia final. La integración real se ejecutó directamente en Kitty para mantener observabilidad externa completa.

Validación confirmada:

- integración real aislada: 1 passed in 2.47s;
- `INTEGRATION_EXIT_CODE=0`;
- suite backend: 967 passed in 5.56s;
- ningún proceso PostgreSQL, socket o clúster temporal residual;
- `operational_state.py validate` correcto;
- `git diff --check` limpio;
- commit técnico `d0efe1e`.

S2 demuestra backup, restauración y reversibilidad en infraestructura temporal controlada. No autoriza migraciones sobre desarrollo, staging o producción reales y no elimina los riesgos propios de datos, volumen, permisos o configuración de esos entornos.

## Siguiente hito

B179 continúa con el Hito B de persistencia transaccional e historial consultable. Cualquier futura ejecución DevSecOps sobre entornos reales requerirá una puerta adicional y autorización explícita.

La deuda de `block_workflow.py`, cuya interrupción puede perder la salida final o dejar procesos hijos activos, permanece separada y fuera de este hito.
