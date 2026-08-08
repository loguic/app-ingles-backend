import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest

import scripts.engineering.isolated_postgresql_pytest as wrapper
from scripts.engineering.postgresql_devsecops_adapter import (
    AdapterError,
    ManagedWorkspace,
)


class FakeCluster:
    def __init__(self, workspace, binaries, runner, port):
        self.workspace = workspace
        self.binaries = binaries
        self.runner = runner
        self.port = port
        self.events = binaries.events

    def initialize(self):
        self.events.append("initialize")

    def start(self):
        self.events.append("start")

    def stop(self):
        self.events.append("stop")
        return True


def test_main_forwards_every_argument_after_separator(monkeypatch):
    observed = []
    monkeypatch.setattr(
        wrapper,
        "run_isolated_pytest",
        lambda arguments: observed.extend(arguments) or 0,
    )

    assert wrapper.main(
        ["--", "tests/test_example.py", "-q", "-k", "focused"]
    ) == 0
    assert observed == ["tests/test_example.py", "-q", "-k", "focused"]


def managed_workspace(tmp_path: Path) -> ManagedWorkspace:
    root = Path(
        tempfile.mkdtemp(
            prefix="loguic-pg-s2-wrapper-",
            dir=tempfile.gettempdir(),
        )
    )
    (root / ".loguic-devsecops-managed").write_text(
        "managed-by-loguic-s2\n",
        encoding="utf-8",
    )
    paths = {}
    for name in ("data", "socket", "backups", "evidence"):
        path = root / name
        path.mkdir()
        paths[name] = path
    return ManagedWorkspace(
        root=root,
        authorized_parent=Path(tempfile.gettempdir()),
        **paths,
    )


def run_wrapper(tmp_path, *, pytest_args=("-q",), returncode=0, **overrides):
    workspace = managed_workspace(tmp_path)
    events = []
    observed = {}

    def create_database(_cluster, database):
        events.append(("create_database", database))

    def run_alembic(_cluster, database, action, revision, root):
        events.append(("alembic", database, action, revision, root))

    def run_process(command, **kwargs):
        events.append("pytest")
        observed.update(command=command, kwargs=kwargs)
        return subprocess.CompletedProcess(command, returncode)

    def cleanup(target):
        events.append(("cleanup", target))
        wrapper.cleanup_workspace(target)

    kwargs = {
        "port": 55439,
        "repository_root": Path("/repository"),
        "workspace_factory": lambda _parent: workspace,
        "workspace_cleanup": cleanup,
        "binaries_discoverer": lambda **_kwargs: SimpleNamespace(events=events),
        "cluster_factory": FakeCluster,
        "database_creator": create_database,
        "alembic_runner": run_alembic,
        "process_runner": run_process,
    }
    kwargs.update(overrides)
    result = wrapper.run_isolated_pytest(pytest_args, **kwargs)
    return result, events, observed, workspace


def test_preserves_pytest_arguments_and_injects_only_temporary_url(tmp_path):
    result, events, observed, workspace = run_wrapper(
        tmp_path,
        pytest_args=("tests/test_example.py", "-q", "-k", "focused"),
    )

    assert result == 0
    assert observed["command"][-4:] == [
        "tests/test_example.py",
        "-q",
        "-k",
        "focused",
    ]
    database_url = observed["kwargs"]["env"]["DATABASE_URL"]
    assert parse_qs(urlparse(database_url).query)["host"] == [
        str(workspace.socket.resolve())
    ]
    assert "localhost" not in database_url
    assert "app_ingles_db" not in database_url
    assert observed["kwargs"]["shell"] is False
    assert events.index("pytest") > next(
        index for index, event in enumerate(events) if isinstance(event, tuple) and event[0] == "alembic"
    )


def test_inherited_database_url_is_never_used_as_destination(tmp_path, monkeypatch):
    inherited = "postgresql+psycopg://user:secret@localhost:5432/app_ingles_db"
    monkeypatch.setenv("DATABASE_URL", inherited)

    _, _, observed, _ = run_wrapper(tmp_path)

    injected = observed["kwargs"]["env"]["DATABASE_URL"]
    assert injected != inherited
    assert "localhost:5432" not in injected
    assert "app_ingles_db" not in injected


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"port": 5432}, "port"),
        ({"database": "app_ingles_db"}, "development database"),
    ],
)
def test_rejects_forbidden_target_before_workspace_creation(
    tmp_path,
    overrides,
    message,
):
    created = []
    with pytest.raises(AdapterError, match=message):
        wrapper.run_isolated_pytest(
            ("-q",),
            repository_root=Path("/repository"),
            workspace_factory=lambda _parent: created.append(True),
            binaries_discoverer=lambda **_kwargs: SimpleNamespace(),
            **overrides,
        )
    assert created == []


def test_rejects_socket_outside_workspace_before_alembic_or_pytest(tmp_path):
    workspace = managed_workspace(tmp_path)
    outside = tmp_path / "outside-socket"
    outside.mkdir()
    unsafe = ManagedWorkspace(
        root=workspace.root,
        data=workspace.data,
        socket=outside,
        backups=workspace.backups,
        evidence=workspace.evidence,
        authorized_parent=workspace.authorized_parent,
    )
    events = []
    with pytest.raises(AdapterError, match="socket"):
        wrapper.run_isolated_pytest(
            ("-q",),
            port=55439,
            repository_root=Path("/repository"),
            workspace_factory=lambda _parent: unsafe,
            workspace_cleanup=lambda target: (
                events.append("cleanup"),
                wrapper.cleanup_workspace(target),
            ),
            binaries_discoverer=lambda **_kwargs: SimpleNamespace(),
            alembic_runner=lambda *_args: events.append("alembic"),
            process_runner=lambda *_args, **_kwargs: events.append("pytest"),
        )
    assert events == ["cleanup"]


@pytest.mark.parametrize("returncode", [0, 1, 5])
def test_propagates_pytest_exit_code_and_cleans_up(tmp_path, returncode):
    result, events, _, workspace = run_wrapper(tmp_path, returncode=returncode)
    assert result == returncode
    assert "stop" in events
    assert ("cleanup", workspace) in events


def test_cleanup_occurs_when_pytest_raises(tmp_path):
    def fail(*_args, **_kwargs):
        raise RuntimeError("pytest process failed")

    workspace = managed_workspace(tmp_path)
    events = []
    with pytest.raises(RuntimeError, match="pytest process failed"):
        wrapper.run_isolated_pytest(
            ("-q",),
            port=55439,
            repository_root=Path("/repository"),
            workspace_factory=lambda _parent: workspace,
            workspace_cleanup=lambda target: (
                events.append(("cleanup", target)),
                wrapper.cleanup_workspace(target),
            ),
            binaries_discoverer=lambda **_kwargs: SimpleNamespace(events=events),
            cluster_factory=FakeCluster,
            database_creator=lambda *_args: None,
            alembic_runner=lambda *_args: None,
            process_runner=fail,
        )
    assert "stop" in events
    assert ("cleanup", workspace) in events


def test_cleanup_occurs_on_keyboard_interrupt(tmp_path):
    def interrupt(*_args, **_kwargs):
        raise KeyboardInterrupt

    workspace = managed_workspace(tmp_path)
    events = []
    with pytest.raises(KeyboardInterrupt):
        wrapper.run_isolated_pytest(
            ("-q",),
            port=55439,
            repository_root=Path("/repository"),
            workspace_factory=lambda _parent: workspace,
            workspace_cleanup=lambda target: (
                events.append(("cleanup", target)),
                wrapper.cleanup_workspace(target),
            ),
            binaries_discoverer=lambda **_kwargs: SimpleNamespace(events=events),
            cluster_factory=FakeCluster,
            database_creator=lambda *_args: None,
            alembic_runner=lambda *_args: None,
            process_runner=interrupt,
        )
    assert "stop" in events
    assert ("cleanup", workspace) in events


def test_wrapper_does_not_change_or_call_historical_s2_rehearsal():
    source = Path(wrapper.__file__).read_text(encoding="utf-8")
    assert "run_isolated_rehearsal" not in source
    assert '"upgrade", "head"' in source
