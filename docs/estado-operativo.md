# Estado operativo — LOGUIC English

Actualizado: 2026-08-05
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Horizonte pedagógico: 3 meses como meta y 6 meses como máximo.
- Todo bloque nuevo debe partir de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B178 — Sistematización profesional del método de trabajo

Estado: implementación técnica y documentación completadas; pendiente publicación final.

Capacidades completadas:

- checkpoint operativo compacto y validable;
- detección de estado desactualizado;
- límite automático de tamaño del checkpoint;
- generación de resumen operativo corto;
- validación frente al último commit Git;
- orquestador único sobre `block_close.py`;
- interrupción del flujo antes de ejecutar validaciones si el estado es inválido;
- delegación transparente de argumentos al cierre técnico existente.

Validación final:

- pruebas específicas de automatización: 8 passed;
- suite backend completa: 923 passed;
- `git diff --check`: limpio;
- commit técnico: `c08196d`.

## Bloque activo

Ninguno.

B178 queda pendiente únicamente de publicación y verificación final de Git.

## Automatización disponible

- `scripts/engineering/block_close.py` automatiza validaciones y staging técnico controlado.
- Debe extenderse o reutilizarse antes de crear herramientas duplicadas.
- No automatiza todavía diseño, documentación, commits ni push.

## Método operativo vigente

Cada bloque utiliza tres puertas:

1. Definición: capacidad, alcance, evidencia y límites.
2. Ejecución automatizada: cambio, pruebas específicas y validación de formato.
3. Cierre: suite completa, documentación, commits, push y Git limpio.

Reglas:

- una confirmación humana por hito significativo;
- inspección manual solo cuando falta información real o aparece un error inesperado;
- no repetir búsquedas o validaciones con resultados todavía vigentes;
- una sola acción o comando por paso;
- detener el avance si el método vuelve a degradarse.

## Fronteras obligatorias

- producción ≠ evaluación técnica;
- evaluación técnica ≠ observación diagnóstica;
- observación diagnóstica ≠ decisión pedagógica;
- perfil inicial ≠ progreso;
- progreso ≠ mastery;
- score técnico ≠ juicio humano;
- contexto motivador ≠ clasificación personal.

## Próximo objetivo

Definir el siguiente bloque pedagógico desde una capacidad observable del estudiante, utilizando el nuevo flujo:

1. validar el checkpoint;
2. recuperar el resumen operativo;
3. ejecutar el incremento mediante un hito técnico agrupado;
4. cerrar con validación, documentación y Git limpio.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/conversational-diagnostic-contract.md`;
- `docs/roadmap.md`;
- `docs/bitacora.md`;
- `scripts/engineering/block_close.py`.
