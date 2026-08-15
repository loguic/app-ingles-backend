"""Represent curriculum hierarchy provenance issued by the official provider.

Representa la procedencia de una jerarquía curricular emitida por el proveedor oficial.
"""

from dataclasses import dataclass

from app.schemas.content import ContentTreeResponse


@dataclass(frozen=True, init=False)
class AuthoritativeCurriculumHierarchy:
    """Carry a hierarchy issued by the contractually authoritative provider.

    Conserva una jerarquía emitida por el proveedor autoritativo contractual.
    """

    hierarchy: ContentTreeResponse

    def __init__(self, hierarchy: ContentTreeResponse) -> None:
        """Prevent ordinary callers from asserting authoritative provenance."""
        raise TypeError(
            "AuthoritativeCurriculumHierarchy must be issued by the "
            "authoritative curriculum provider"
        )


def _issue_authoritative_curriculum_hierarchy(
    hierarchy: ContentTreeResponse,
) -> AuthoritativeCurriculumHierarchy:
    """Issue authoritative provenance for the official provider only.

    Emite procedencia autoritativa únicamente para el proveedor oficial.
    """
    authority = object.__new__(AuthoritativeCurriculumHierarchy)
    object.__setattr__(authority, "hierarchy", hierarchy)
    return authority
