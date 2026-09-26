"""Read-only selection of the verified active runtime projection tree."""

from pathlib import Path

from app.schemas.content import ContentTreeResponse
from app.services.pedagogical_runtime_activation_documents import (
    acquire_active_runtime_document_chain,
)


_ACTIVE_RUNTIME_POINTER_RELATIVE_PATH = Path("content/runtime-active.json")


def select_active_runtime_content_tree(
    repository_root: Path,
) -> ContentTreeResponse | None:
    """Return the verified projection tree, or ``None`` when no pointer exists."""

    _validate_repository_root(repository_root)
    pointer_path = repository_root / _ACTIVE_RUNTIME_POINTER_RELATIVE_PATH
    if not pointer_path.exists() and not pointer_path.is_symlink():
        return None
    return acquire_active_runtime_document_chain(
        repository_root
    ).projection_document.content_tree


def _validate_repository_root(repository_root: Path) -> None:
    if not isinstance(repository_root, Path):
        raise ValueError("repository_root must be a Path")
    if not repository_root.is_absolute():
        raise ValueError("repository_root must be absolute")
    if not repository_root.exists() or not repository_root.is_dir():
        raise ValueError("repository_root must be an existing directory")
