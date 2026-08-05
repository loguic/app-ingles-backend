from datetime import date
from pathlib import Path

import pytest

from scripts.engineering.operational_state import (
    render_operational_summary,
    validate_operational_state,
)


def build_state(updated_on: str = "2026-08-05") -> str:
    lines = [
        "# Estado operativo — LOGUIC English",
        "",
        f"Actualizado: {updated_on}",
        "",
    ]
    for section in (
        "Dirección vigente",
        "Último bloque cerrado",
        "Bloque activo",
        "Automatización disponible",
        "Método operativo vigente",
        "Fronteras obligatorias",
        "Próximo objetivo",
        "Archivos clave",
    ):
        lines.extend(
            [
                f"## {section}",
                "",
                f"Contenido de {section}.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def test_validate_compact_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(), encoding="utf-8")

    report = validate_operational_state(
        path,
        today=date(2026, 8, 5),
    )

    assert report.updated_on == date(2026, 8, 5)
    assert report.line_count < 140


def test_reject_stale_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(
        build_state("2026-07-01"),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Operational state is stale",
    ):
        validate_operational_state(
            path,
            today=date(2026, 8, 5),
        )


def test_reject_missing_required_section(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    content = build_state().replace(
        "## Próximo objetivo",
        "## Objetivo eliminado",
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Próximo objetivo",
    ):
        validate_operational_state(
            path,
            today=date(2026, 8, 5),
        )


def test_reject_oversized_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    content = build_state() + ("línea histórica\n" * 150)
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="exceeds 140 lines",
    ):
        validate_operational_state(
            path,
            today=date(2026, 8, 5),
        )


def test_render_short_operational_summary(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(), encoding="utf-8")

    summary = render_operational_summary(path)

    assert "## Último bloque cerrado" in summary
    assert "## Bloque activo" in summary
    assert "## Próximo objetivo" in summary
    assert "## Dirección vigente" not in summary
