# Paquetes candidatos pedagógicos

Este directorio almacena paquetes `PedagogicalUnitCandidate` aislados del contenido activo.

## Reglas obligatorias

- Los candidatos no son consumidos por la API ni por Flutter.
- Ningún archivo de este directorio puede sustituir automáticamente `content/content_tree.json`.
- Cada candidato debe representar un `PedagogicalUnitCandidate` completo y validable.
- La especificación pedagógica debe estar aprobada antes de generar el candidato.
- Las validaciones deterministas deben ejecutarse antes de la revisión humana.
- El informe almacenado debe reflejar resultados reales, no estados inventados.
- Las decisiones pendientes deben declararse en `pending_human_decisions`.
- La integración requiere un diff revisable y aprobación humana explícita.
- La promoción al contenido activo pertenece a un proceso posterior y separado.
- Un candidato puede rechazarse completamente sin modificar el contenido vigente.

## Convención inicial

La primera candidata v2 se almacenará en:

`content/candidates/a1-u1/pedagogical-unit-candidate-v2.json`

La presencia de un archivo en este directorio no significa que haya sido aprobado ni publicado.
