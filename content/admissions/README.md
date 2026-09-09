# Admission records

Este directorio conserva documentos `AdmissionRecordDocumentV1` versionados y
separados de candidates, membership y contenido activo.

- `admission_id` es caller-provided, estable y opaco; no es un path ni un
  orden curricular.
- `reviewer_id` identifica al reviewer humano que tomó la decisión.
- Cada record vive bajo `content/admissions/<unit_id>/` en una ruta relativa
  declarada explícitamente para esa decisión.
- La capa operativa resuelve `repository_root / relative_path` y rechaza rutas
  absolutas o cualquier escape fuera de la raíz del repositorio antes de pasar
  el `Path` absoluto al publicador existente.
- Admission no implica membership, snapshot, activation, loader ni cambio de
  `content/content_tree.json`.
