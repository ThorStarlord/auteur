from __future__ import annotations

from pathlib import Path

from auteur import cli
from auteur.open_app import open_auteur


class FakeServer:
    instances = []

    def __init__(self, project, *, port, dependencies):
        self.project = Path(project)
        self.port = port
        self.dependencies = dependencies
        self.started = False
        self.__class__.instances.append(self)

    def start(self):
        self.started = True


def test_launcher_reuses_running_auteur_and_only_opens_browser(tmp_path: Path) -> None:
    opened = []

    result = open_auteur(
        project=tmp_path,
        port=8791,
        browser_open=opened.append,
        running_probe=lambda port: port == 8791,
        server_factory=FakeServer,
    )

    assert result == 0
    assert opened == ["http://127.0.0.1:8791/"]
    assert FakeServer.instances == []


def test_launcher_starts_local_server_and_opens_home(tmp_path: Path) -> None:
    FakeServer.instances.clear()
    opened = []

    result = open_auteur(
        project=tmp_path,
        port=9123,
        browser_open=opened.append,
        running_probe=lambda port: False,
        server_factory=FakeServer,
    )

    assert result == 0
    assert opened == ["http://127.0.0.1:9123/"]
    assert len(FakeServer.instances) == 1
    server = FakeServer.instances[0]
    assert server.project == tmp_path.resolve()
    assert server.port == 9123
    assert server.started is True


def test_bare_auteur_and_auteur_open_route_to_application_launcher(monkeypatch) -> None:
    calls = []

    def fake_open_main(argv):
        calls.append(argv)
        return 17

    import auteur.open_app

    monkeypatch.setattr(auteur.open_app, "main", fake_open_main)

    assert cli.main([]) == 17
    assert cli.main(["open", "--no-browser", "--port", "9000"]) == 17
    assert calls == [[], ["--no-browser", "--port", "9000"]]
