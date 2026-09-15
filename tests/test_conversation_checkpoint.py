from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from scripts.engineering import conversation_checkpoint
from scripts.engineering.git_close import close_git_changes
from scripts.engineering.operational_state import ROOT_GIT_BASELINE


def run_git(root: Path, *args: str) -> str:
    """Run Git inside one isolated test repository.

    Ejecuta Git dentro de un repositorio aislado de prueba.
    """
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def state_document(
    updated_at: str,
    git_baseline: str = ROOT_GIT_BASELINE,
    recognized_paths: tuple[str, ...] = (
        "tracked.txt",
        "new file.txt",
        "renamed file.txt",
        "staged.txt",
        "untracked.txt",
        "docs/estado-operativo.md",
    ),
    active_content: str = "Contenido Bloque activo.",
    next_content: str = "Contenido Próximo objetivo.",
) -> str:
    """Build the smallest valid canonical operational state.

    Construye el estado operativo canónico válido más pequeño.
    """
    sections = (
        "Dirección vigente",
        "Último bloque cerrado",
        "Bloque activo",
        "Automatización disponible",
        "Método operativo vigente",
        "Fronteras obligatorias",
        "Próximo objetivo",
        "Archivos clave",
    )
    lines = [
        "# Estado operativo — LOGUIC English",
        "",
        f"Actualizado: {updated_at}",
        f"Baseline Git previa a este checkpoint: {git_baseline}",
        "",
    ]
    for section in sections:
        content = f"Contenido {section}."
        if section == "Bloque activo":
            content = active_content
        elif section == "Próximo objetivo":
            content = next_content
        lines.extend([f"## {section}", "", content])
        if section == "Archivos clave":
            lines.extend(f"- `{path}`;" for path in recognized_paths)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def create_repository(tmp_path: Path) -> tuple[Path, Path]:
    """Create an isolated repository with canonical state and one commit.

    Crea un repositorio aislado con estado canónico y un commit.
    """
    root = tmp_path / "repository"
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds")
        ),
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("original\n", encoding="utf-8")
    (root / "staged.txt").write_text("base\n", encoding="utf-8")
    run_git(root.parent, "init", "-q", str(root))
    run_git(root, "config", "user.name", "Checkpoint Test")
    run_git(root, "config", "user.email", "checkpoint@example.invalid")
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "initial checkpoint")
    run_git(root, "branch", "upstream-fixture")
    run_git(root, "branch", "--set-upstream-to=upstream-fixture")
    return root, state_path


def build(root: Path, state_path: Path, command: str = "prepare") -> str:
    """Build one checkpoint against the isolated repository.

    Construye un checkpoint sobre el repositorio aislado.
    """
    return conversation_checkpoint.build_checkpoint(
        command,
        root=root,
        state_path=state_path,
    )


def build_format(
    root: Path,
    state_path: Path,
    *,
    command: str = "prepare",
    output_format: str,
) -> str:
    return conversation_checkpoint.build_checkpoint(
        command,
        root=root,
        state_path=state_path,
        output_format=output_format,
    )


def parse_compact(output: str) -> dict[str, str]:
    assert output.count("\n") == 1
    pairs = parse_qsl(
        output.rstrip("\n"),
        keep_blank_values=True,
        strict_parsing=True,
    )
    assert len(pairs) == len(dict(pairs))
    return dict(pairs)


def test_prepare_clean_repository_with_valid_upstream(tmp_path: Path) -> None:
    """Describe a clean repository with a resolvable upstream.

    Describe un repositorio limpio con upstream resoluble.
    """
    root, state_path = create_repository(tmp_path)

    output = build(root, state_path)

    assert "- Working tree: clean" in output
    assert "- Upstream: `upstream-fixture`" in output
    assert "- Local relation: ahead 0, behind 0" in output
    assert "- Autoridad semántica: `docs/estado-operativo.md`." in output
    assert "- Autoridad Git viva: inspección read-only de Git." in output
    assert f"- Baseline Git semántica: `{ROOT_GIT_BASELINE}`." in output
    assert "the only source of truth" not in output
    assert "were not rerun" in output
    assert f"- HEAD: `{run_git(root, 'rev-parse', 'HEAD')}`" in output


@pytest.mark.parametrize("command", ["prepare", "resume"])
def test_compact_checkpoint_reports_validated_facts(
    tmp_path: Path,
    command: str,
) -> None:
    root, state_path = create_repository(tmp_path)
    head = run_git(root, "rev-parse", "HEAD")

    output = build_format(
        root,
        state_path,
        command=command,
        output_format="compact",
    )
    fields = parse_compact(output)

    assert fields == {
        "CHECKPOINT_FORMAT": "compact-v1",
        "CHECKPOINT_STATUS": "PASS",
        "COMMAND": command,
        "HEAD": head,
        "BRANCH": "master",
        "UPSTREAM": "upstream-fixture",
        "AHEAD": "0",
        "BEHIND": "0",
        "TREE": "CLEAN",
        "BASELINE": ROOT_GIT_BASELINE,
        "DIRTY": "0",
        "ACTIVE_BLOCK": "Contenido Bloque activo.",
        "ACTIVE_BLOCK_TRUNCATED": "false",
        "ACTIVE_BLOCK_LENGTH": str(len("Contenido Bloque activo.")),
        "NEXT": "Contenido Próximo objetivo.",
        "NEXT_TRUNCATED": "false",
        "NEXT_LENGTH": str(len("Contenido Próximo objetivo.")),
    }


@pytest.mark.parametrize("command", ["prepare", "resume"])
def test_json_checkpoint_reports_same_essential_facts_as_markdown(
    tmp_path: Path,
    command: str,
) -> None:
    root, state_path = create_repository(tmp_path)
    head = run_git(root, "rev-parse", "HEAD")

    markdown = build(root, state_path, command=command)
    payload = json.loads(
        build_format(root, state_path, command=command, output_format="json")
    )
    compact = parse_compact(
        build_format(root, state_path, command=command, output_format="compact")
    )

    assert payload == {
        "active_block": "Contenido Bloque activo.",
        "ahead": 0,
        "baseline": ROOT_GIT_BASELINE,
        "behind": 0,
        "branch": "master",
        "checkpoint_status": "PASS",
        "command": command,
        "dirty_count": 0,
        "head": head,
        "next": "Contenido Próximo objetivo.",
        "tree": "CLEAN",
        "upstream": "upstream-fixture",
    }
    assert compact["CHECKPOINT_STATUS"] == payload["checkpoint_status"]
    assert compact["COMMAND"] == payload["command"]
    assert compact["HEAD"] == payload["head"]
    assert compact["BRANCH"] == payload["branch"]
    assert compact["UPSTREAM"] == payload["upstream"]
    assert int(compact["AHEAD"]) == payload["ahead"]
    assert int(compact["BEHIND"]) == payload["behind"]
    assert compact["TREE"] == payload["tree"]
    assert compact["BASELINE"] == payload["baseline"]
    assert int(compact["DIRTY"]) == payload["dirty_count"]
    assert compact["ACTIVE_BLOCK"] == payload["active_block"]
    assert compact["NEXT"] == payload["next"]
    assert f"- Command: `{payload['command']}`." in markdown
    assert f"- HEAD: `{payload['head']}`" in markdown
    assert f"- Branch: `{payload['branch']}`" in markdown
    assert f"- Upstream: `{payload['upstream']}`" in markdown
    assert "- Local relation: ahead 0, behind 0" in markdown
    assert f"- Baseline Git semántica: `{payload['baseline']}`." in markdown
    assert payload["active_block"] in markdown
    assert payload["next"] in markdown
    assert "- Working tree: clean" in markdown


def test_json_preserves_complete_semantic_sections_and_compact_metadata(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)
    head = run_git(root, "rev-parse", "HEAD")
    active = '### Active | "quoted" \\ path\nUnicode: áβ\n' + "a" * 260
    next_objective = 'Next | "quoted" \\ path\nUnicode: ñλ\n' + "n" * 260
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            head,
            active_content=active,
            next_content=next_objective,
        ),
        encoding="utf-8",
    )

    markdown = build(root, state_path, command="resume")
    payload = json.loads(
        build_format(root, state_path, command="resume", output_format="json")
    )
    compact = parse_compact(
        build_format(root, state_path, command="resume", output_format="compact")
    )

    assert payload["active_block"] == active
    assert payload["next"] == next_objective
    assert active in markdown
    assert next_objective in markdown
    assert compact["ACTIVE_BLOCK_TRUNCATED"] == "true"
    assert compact["ACTIVE_BLOCK_LENGTH"] == str(len(active))
    assert compact["ACTIVE_BLOCK"].endswith("…")
    assert compact["NEXT_TRUNCATED"] == "true"
    assert compact["NEXT_LENGTH"] == str(len(next_objective))
    assert compact["NEXT"].endswith("…")


def test_compact_encoding_round_trips_delimiters_and_control_characters() -> None:
    special = 'value | "quoted" \\ backslash\nUnicode: áβ'
    facts: dict[str, object] = {
        "checkpoint_status": "PASS",
        "command": "resume",
        "head": "a" * 40,
        "branch": special,
        "upstream": special,
        "ahead": 1,
        "behind": 2,
        "tree": "DIRTY",
        "baseline": "b" * 40,
        "dirty_count": 3,
        "active_block": special,
        "next": special,
    }

    fields = parse_compact(conversation_checkpoint.render_compact_checkpoint(facts))

    assert fields["BRANCH"] == special
    assert fields["UPSTREAM"] == special
    assert fields["ACTIVE_BLOCK"] == "value | \"quoted\" \\ backslash Unicode: áβ"
    assert fields["NEXT"] == "value | \"quoted\" \\ backslash Unicode: áβ"
    assert fields["ACTIVE_BLOCK_TRUNCATED"] == "false"
    assert fields["NEXT_TRUNCATED"] == "false"


@pytest.mark.parametrize("output_format", ["markdown", "compact", "json"])
def test_checkpoint_formats_report_dirty_count_read_only(
    tmp_path: Path,
    output_format: str,
) -> None:
    root, state_path = create_repository(tmp_path)
    before_state = state_path.read_text(encoding="utf-8")
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    before_status = run_git(root, "status", "--porcelain=v1")

    output = build_format(root, state_path, output_format=output_format)

    if output_format == "compact":
        fields = parse_compact(output)
        assert fields["CHECKPOINT_STATUS"] == "PASS"
        assert fields["TREE"] == "DIRTY"
        assert fields["DIRTY"] == "1"
    elif output_format == "json":
        payload = json.loads(output)
        assert payload["checkpoint_status"] == "PASS"
        assert payload["tree"] == "DIRTY"
        assert payload["dirty_count"] == 1
    else:
        assert "- Working tree: 1 Git status record(s)" in output
    assert state_path.read_text(encoding="utf-8") == before_state
    assert run_git(root, "status", "--porcelain=v1") == before_status


def test_compact_and_json_fail_closed_before_pass_output(tmp_path: Path) -> None:
    root, state_path = create_repository(tmp_path)
    state_path.write_text("invalid\n", encoding="utf-8")

    for output_format in ("compact", "json"):
        with pytest.raises(ValueError, match="title is invalid"):
            build_format(root, state_path, output_format=output_format)


def test_compact_and_json_fail_closed_for_git_validation(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            "a" * 40,
        ),
        encoding="utf-8",
    )

    for output_format in ("compact", "json"):
        with pytest.raises(ValueError, match="prior Git baseline is incompatible"):
            build_format(root, state_path, output_format=output_format)


@pytest.mark.parametrize("output_format", ["markdown", "compact", "json"])
def test_missing_upstream_fails_closed(
    tmp_path: Path,
    output_format: str,
) -> None:
    root, state_path = create_repository(tmp_path)
    run_git(root, "branch", "--unset-upstream")

    with pytest.raises(ValueError, match="upstream is missing or cannot be resolved"):
        build_format(root, state_path, output_format=output_format)


@pytest.mark.parametrize("output_format", ["markdown", "compact", "json"])
def test_unresolvable_upstream_fails_closed(
    tmp_path: Path,
    output_format: str,
) -> None:
    root, state_path = create_repository(tmp_path)
    run_git(root, "config", "branch.master.remote", "origin")
    run_git(root, "config", "branch.master.merge", "refs/heads/missing")

    with pytest.raises(ValueError, match="upstream is missing or cannot be resolved"):
        build_format(root, state_path, output_format=output_format)


def test_markdown_default_and_explicit_format_are_compatible(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)

    assert build(root, state_path) == build_format(
        root,
        state_path,
        output_format="markdown",
    )


def test_cli_accepts_explicit_checkpoint_formats() -> None:
    parser = conversation_checkpoint.build_parser()

    assert parser.parse_args(["resume"]).output_format == "markdown"
    assert parser.parse_args(["resume", "--format", "compact"]).output_format == "compact"
    assert parser.parse_args(["prepare", "--format", "json"]).output_format == "json"


def test_cli_failure_is_nonzero_without_pass_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        conversation_checkpoint,
        "build_checkpoint",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("Git upstream is missing or cannot be resolved")
        ),
    )
    monkeypatch.setattr(
        conversation_checkpoint.sys,
        "argv",
        ["conversation_checkpoint.py", "resume", "--format", "compact"],
    )

    with pytest.raises(SystemExit) as captured:
        conversation_checkpoint.main()

    output = capsys.readouterr()
    assert captured.value.code == 2
    assert output.out == ""
    assert "upstream is missing or cannot be resolved" in output.err
    assert "CHECKPOINT_STATUS=PASS" not in output.err


def test_prepare_accepts_dirty_state_with_baseline_equal_to_head(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)
    head = run_git(root, "rev-parse", "HEAD")
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            head,
        ),
        encoding="utf-8",
    )

    output = build(root, state_path)

    assert f"- HEAD: `{head}`" in output
    assert f"- Baseline Git semántica: `{head}`." in output
    assert "- Working tree: 1 Git status record(s)" in output


def test_prepare_accepts_clean_checkpoint_with_parent_baseline(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)
    prior_head = run_git(root, "rev-parse", "HEAD")
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            prior_head,
        ),
        encoding="utf-8",
    )
    run_git(root, "add", "docs/estado-operativo.md")
    run_git(root, "commit", "-q", "-m", "close checkpoint")
    current_head = run_git(root, "rev-parse", "HEAD")

    output = build(root, state_path, command="resume")

    assert current_head != prior_head
    assert f"- HEAD: `{current_head}`" in output
    assert f"- Baseline Git semántica: `{prior_head}`." in output
    assert "- Working tree: clean" in output


def test_git_close_then_prepare_accepts_non_circular_checkpoint(
    tmp_path: Path,
) -> None:
    root, state_path = create_repository(tmp_path)
    remote = tmp_path / "remote.git"
    run_git(tmp_path, "init", "--bare", "-q", str(remote))
    run_git(root, "remote", "add", "origin", str(remote))
    run_git(root, "push", "-q", "-u", "origin", "master")
    prior_head = run_git(root, "rev-parse", "HEAD")
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            prior_head,
        ),
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("closed\n", encoding="utf-8")

    preclose = build(root, state_path)
    assert f"- Baseline Git semántica: `{prior_head}`." in preclose
    commit = close_git_changes(
        branch="master",
        upstream="origin/master",
        message="close checkpoint fixture",
        files=["docs/estado-operativo.md", "tracked.txt"],
        root=root,
    )

    postclose = build(root, state_path)

    assert commit != prior_head
    assert f"- HEAD: `{commit}`" in postclose
    assert f"- Baseline Git semántica: `{prior_head}`." in postclose
    assert "- Working tree: clean" in postclose
    assert "- Local relation: ahead 0, behind 0" in postclose


def test_reports_staged_change(tmp_path: Path) -> None:
    """Report a staged path without showing its content.

    Informa una ruta staged sin mostrar su contenido.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("secret staged content\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")

    output = build(root, state_path)

    assert '`M ` `"tracked.txt"`' in output
    assert "secret staged content" not in output


def test_reports_unstaged_change(tmp_path: Path) -> None:
    """Report an unstaged path using its porcelain status.

    Informa una ruta unstaged mediante su estado porcelain.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

    output = build(root, state_path)

    assert '` M` `"tracked.txt"`' in output


def test_reports_untracked_path(tmp_path: Path) -> None:
    """Report an untracked path without reading its content.

    Informa una ruta untracked sin leer su contenido.
    """
    root, state_path = create_repository(tmp_path)
    (root / "new file.txt").write_text("private\n", encoding="utf-8")

    output = build(root, state_path)

    assert '`??` `"new file.txt"`' in output
    assert "private" not in output


def test_reports_combined_states_and_rename(tmp_path: Path) -> None:
    """Report staged, unstaged, untracked and renamed paths together.

    Informa conjuntamente rutas staged, unstaged, untracked y renombradas.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "mv", "staged.txt", "renamed file.txt")
    (root / "tracked.txt").write_text("unstaged\n", encoding="utf-8")
    (root / "untracked.txt").write_text("new\n", encoding="utf-8")

    output = build(root, state_path)

    assert '`R ` `"renamed file.txt" (from "staged.txt")`' in output
    assert '` M` `"tracked.txt"`' in output
    assert '`??` `"untracked.txt"`' in output


def test_allows_documented_dirty_path(tmp_path: Path) -> None:
    """Allow a tracked change named exactly by canonical state.

    Permite un cambio tracked nombrado exactamente por el estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

    assert "Working tree: 1 Git status record" in build(root, state_path)


def test_allows_documented_untracked_path(tmp_path: Path) -> None:
    """Allow an untracked path named exactly by canonical state.

    Permite una ruta untracked nombrada exactamente por el estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    (root / "untracked.txt").write_text("new\n", encoding="utf-8")

    assert '`??` `"untracked.txt"`' in build(root, state_path)


@pytest.mark.parametrize("output_format", ["markdown", "compact", "json"])
@pytest.mark.parametrize("untracked", [False, True])
def test_rejects_undocumented_dirty_or_untracked_path(
    tmp_path: Path,
    untracked: bool,
    output_format: str,
) -> None:
    """Reject tracked and untracked paths absent from canonical state.

    Rechaza rutas tracked y untracked ausentes del estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    path = root / ("unknown.txt" if untracked else "tracked.txt")
    if not untracked:
        state_path.write_text(
            state_document(
                datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                run_git(root, "rev-parse", "HEAD"),
                (),
            ),
            encoding="utf-8",
        )
        run_git(root, "add", "docs/estado-operativo.md")
        run_git(root, "commit", "-q", "-m", "remove recognized paths")
    path.write_text("changed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Operational state omits local paths"):
        build_format(root, state_path, output_format=output_format)


def test_rejects_all_undocumented_paths_in_one_error(tmp_path: Path) -> None:
    """Report every omitted path deterministically in one failure.

    Informa determinísticamente todas las rutas omitidas en un único fallo.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (root / "unknown.txt").write_text("new\n", encoding="utf-8")

    with pytest.raises(ValueError) as captured:
        build(root, state_path)

    assert '"unknown.txt"' in str(captured.value)
    assert '"tracked.txt"' not in str(captured.value)


def test_rename_requires_documented_source_and_destination(tmp_path: Path) -> None:
    """Require exact recognition of both paths in a rename.

    Exige reconocimiento exacto de ambas rutas de un rename.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "mv", "tracked.txt", "renamed file.txt")

    assert '`R ` `"renamed file.txt" (from "tracked.txt")`' in build(
        root,
        state_path,
    )


def test_rename_rejects_undocumented_destination(tmp_path: Path) -> None:
    """Reject a rename when its destination is absent from canonical state.

    Rechaza un rename cuyo destino está ausente del estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "mv", "tracked.txt", "unknown-name.txt")

    with pytest.raises(ValueError, match='"unknown-name.txt"'):
        build(root, state_path)


@pytest.mark.parametrize(
    "path",
    [
        "name`with-backtick.txt",
        "name\nwith-newline.txt",
        "name\x01with-control.txt",
        "name\u0085with-next-line.txt",
        "name\u2028with-line-separator.txt",
        "name\u2029with-paragraph-separator.txt",
    ],
)
def test_git_paths_use_reversible_json_representation(path: str) -> None:
    """Escape Markdown-sensitive and control characters in Git paths.

    Escapa caracteres de rutas Git sensibles a Markdown o de control.
    """
    rendered = conversation_checkpoint._format_git_path(path)

    assert conversation_checkpoint.json.loads(rendered) == path
    assert "\n" not in rendered
    assert "\x01" not in rendered
    assert "\u0085" not in rendered
    assert "\u2028" not in rendered
    assert "\u2029" not in rendered
    if "`" in path:
        assert "`" not in rendered
        assert "\\u0060" in rendered


def test_rename_paths_share_safe_json_representation() -> None:
    """Render both rename paths without literal line or control breaks.

    Renderiza ambas rutas de rename sin saltos ni controles literales.
    """
    change = conversation_checkpoint.GitChange(
        status="R ",
        path="new`name\n.txt",
        original_path="old\x02name.txt",
    )

    rendered = conversation_checkpoint._format_change(change)

    assert "\n" not in rendered
    assert "\x02" not in rendered
    assert '"new\\u0060name\\n.txt"' in rendered
    assert '"old\\u0002name.txt"' in rendered


def test_reports_local_ahead_and_behind_against_upstream(tmp_path: Path) -> None:
    """Calculate ahead and behind only from local references.

    Calcula ahead y behind únicamente desde referencias locales.
    """
    root, state_path = create_repository(tmp_path)

    output = build(root, state_path)

    assert "- Upstream: `upstream-fixture`" in output
    assert "- Local relation: ahead 0, behind 0" in output


def test_json_reports_resolved_ahead_and_behind_counts(tmp_path: Path) -> None:
    ahead_root, ahead_state = create_repository(tmp_path / "ahead")
    prior_head = run_git(ahead_root, "rev-parse", "HEAD")
    ahead_state.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds"),
            prior_head,
        ),
        encoding="utf-8",
    )
    run_git(ahead_root, "add", "docs/estado-operativo.md")
    run_git(ahead_root, "commit", "-q", "-m", "ahead checkpoint")

    ahead_payload = json.loads(
        build_format(ahead_root, ahead_state, output_format="json")
    )

    assert ahead_payload["ahead"] == 1
    assert ahead_payload["behind"] == 0

    behind_root, behind_state = create_repository(tmp_path / "behind")
    run_git(behind_root, "checkout", "-q", "upstream-fixture")
    (behind_root / "upstream.txt").write_text("upstream\n", encoding="utf-8")
    run_git(behind_root, "add", "upstream.txt")
    run_git(behind_root, "commit", "-q", "-m", "advance upstream")
    run_git(behind_root, "checkout", "-q", "master")

    behind_payload = json.loads(
        build_format(behind_root, behind_state, output_format="json")
    )

    assert behind_payload["ahead"] == 0
    assert behind_payload["behind"] == 1


def test_detached_head_without_upstream_fails_closed(tmp_path: Path) -> None:
    """Reject detached HEAD when no resolvable upstream exists.

    Rechaza detached HEAD cuando no existe un upstream resoluble.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "checkout", "-q", "--detach", "HEAD")

    with pytest.raises(ValueError, match="upstream is missing or cannot be resolved"):
        build(root, state_path, command="resume")


def test_fail_closed_for_invalid_operational_state(tmp_path: Path) -> None:
    """Reject invalid canonical state before inspecting Git.

    Rechaza estado canónico inválido antes de inspeccionar Git.
    """
    root, state_path = create_repository(tmp_path)
    state_path.write_text("invalid\n", encoding="utf-8")

    with pytest.raises(ValueError, match="title is invalid"):
        build(root, state_path)


def test_fail_closed_for_state_older_than_latest_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reject a canonical state demonstrably older than Git.

    Rechaza un estado canónico demostrablemente anterior a Git.
    """
    root, state_path = create_repository(tmp_path)
    report_at = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
    (root / "tracked.txt").write_text("newer\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")
    run_git(root, "commit", "-q", "-m", "newer than state")
    state_path.write_text(
        state_document(
            report_at.isoformat(),
            run_git(root, "rev-parse", "HEAD"),
        ),
        encoding="utf-8",
    )
    validate_state = conversation_checkpoint.validate_operational_state
    monkeypatch.setattr(
        conversation_checkpoint,
        "validate_operational_state",
        lambda path: validate_state(
            path,
            now=report_at,
        ),
    )

    with pytest.raises(ValueError, match="older than the Git baseline"):
        build(root, state_path)
