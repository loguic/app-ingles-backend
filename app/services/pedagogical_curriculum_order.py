"""Expose the canonical CEFR v1 curriculum order.

Expone el orden curricular canónico CEFR v1.
"""


CEFR_LEVEL_ORDER: tuple[str, ...] = (
    "A1",
    "A2",
    "B1",
    "B2",
    "C1",
    "C2",
)


def cefr_level_index(level: str) -> int:
    """Return the canonical CEFR v1 index for one level.

    Devuelve el índice canónico CEFR v1 de un nivel.
    """
    return CEFR_LEVEL_ORDER.index(level)
