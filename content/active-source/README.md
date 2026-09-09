# Active candidate source manifests

Este directorio conserva manifests durables `ActiveCandidateSourceSnapshotManifestV1`
que declaran snapshots completos de membership activa.

- Cada manifest se publica en una ruta relativa al repositorio autorizada por el
  operador; la capa operativa resuelve `repository_root / relative_path` y
  rechaza rutas absolutas o escapes fuera del repositorio antes de invocar el
  publicador canónico con un `Path` absoluto.
- El manifest declara memberships e identidades ya admitidas; no contiene
  candidates, recursos físicos, bindings, evaluación B52 ni configuración del
  loader.
- Publicar un manifest declara membership durable, pero no activa contenido,
  no modifica `content/content_tree.json` y no reanuda B181.
