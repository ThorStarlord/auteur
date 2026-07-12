from pathlib import Path

import pytest
import yaml

from auteur.blueprint import Genre
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.genre_pipeline.runtime import GenrePipelineRuntime, GenrePipelineRuntimeError
from auteur.genre_pipeline.templates import build_pipeline_descriptor


def complete_choices(spec, core_id: str) -> dict[int, dict[str, str]]:
    descriptor = build_pipeline_descriptor(spec, core_id)
    choices = {
        phase.number: {field.id: field.options[0].id for field in phase.fields}
        for phase in descriptor.phases
        if phase.fields
    }
    if core_id == "paranoia":
        choices[8]["truth_ambiguity"] = "ambiguous"
    return choices


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        self.terminated = True
        self.returncode = -9


def test_runtime_launches_generic_server_and_writes_validated_identity(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    launched: list[tuple[list[str], dict]] = []
    process = FakeProcess()

    def process_factory(command, **kwargs):
        launched.append((command, kwargs))
        return process

    runtime = GenrePipelineRuntime(
        project_path=tmp_path,
        spec=spec,
        core_id="sensual_dominance",
        process_factory=process_factory,
        browser_opener=lambda _url: True,
        server_probe=lambda _url: True,
        port_checker=lambda _port: None,
        timeout=2,
    )

    def complete_during_wait(_seconds):
        if runtime.store.load().status.value == "incomplete":
            for phase, choices in complete_choices(spec, "sensual_dominance").items():
                runtime.store.update_choices(phase, choices)
            runtime.store.mark_complete()

    runtime.sleep = complete_during_wait
    result = runtime.run()

    command, kwargs = launched[0]
    assert command[1:4] == ["-m", "auteur.genre_pipeline.server", "--project"]
    assert "NETORARE_SESSION_FILE" not in kwargs.get("env", {})
    assert result.identity_file == tmp_path / "story_identity.yaml"
    assert result.session_file == runtime.store.session_file
    assert process.terminated is True

    identity_data = yaml.safe_load(result.identity_file.read_text(encoding="utf-8"))
    assert identity_data["story_type"]["genre"] == "gentlefemdom"
    assert identity_data["story_type"]["mode"] == "intimate"
    assert identity_data["title"] == "Untitled: Sensual Dominance"


def test_runtime_refuses_to_overwrite_canonical_identity_before_creating_session(tmp_path):
    identity_file = tmp_path / "story_identity.yaml"
    identity_file.write_text("title: Existing\n", encoding="utf-8")
    spec = get_genre_pipeline(Genre.MYSTERY)
    runtime = GenrePipelineRuntime(tmp_path, spec, "howdunit")

    with pytest.raises(GenrePipelineRuntimeError, match="already exists"):
        runtime.run()

    assert identity_file.read_text(encoding="utf-8") == "title: Existing\n"
    assert not runtime.store.session_file.exists()


def test_runtime_fails_if_server_exits_before_completion(tmp_path):
    spec = get_genre_pipeline(Genre.NETORARE)
    process = FakeProcess()
    process.returncode = 3
    runtime = GenrePipelineRuntime(
        tmp_path,
        spec,
        "classic_humiliation",
        process_factory=lambda *_args, **_kwargs: process,
        browser_opener=lambda _url: True,
        server_probe=lambda _url: False,
        port_checker=lambda _port: None,
    )

    with pytest.raises(GenrePipelineRuntimeError, match="server exited"):
        runtime.run()

    assert not (tmp_path / "story_identity.yaml").exists()


def test_runtime_waits_for_server_readiness_before_opening_browser(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    process = FakeProcess()
    events: list[str] = []
    runtime = None

    def probe(_url):
        events.append("probe")
        return events.count("probe") >= 2

    def open_browser(_url):
        events.append("browser")
        assert runtime is not None
        for phase, choices in complete_choices(spec, "howdunit").items():
            runtime.store.update_choices(phase, choices)
        runtime.store.mark_complete()
        return True

    runtime = GenrePipelineRuntime(
        tmp_path,
        spec,
        "howdunit",
        process_factory=lambda *_args, **_kwargs: process,
        browser_opener=open_browser,
        server_probe=probe,
        port_checker=lambda _port: None,
        timeout=2,
    )
    runtime.sleep = lambda _seconds: None

    result = runtime.run()

    assert events == ["probe", "probe", "browser"]
    assert result.identity_file.exists()


def test_runtime_rejects_occupied_port_before_creating_session(tmp_path):
    import socket

    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)

    # Find an available port, then occupy it
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    occupied_port = listener.getsockname()[1]

    try:
        runtime = GenrePipelineRuntime(
            tmp_path,
            spec,
            "sensual_dominance",
            port=occupied_port,
        )
        with pytest.raises(GenrePipelineRuntimeError, match="already in use"):
            runtime.run()

        assert not runtime.store.session_file.exists()
    finally:
        listener.close()


def test_runtime_resume_requires_an_existing_incomplete_session(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    launched = []
    runtime = GenrePipelineRuntime(
        tmp_path,
        spec,
        spec.default_core_id,
        resume=True,
        process_factory=lambda *args, **kwargs: launched.append((args, kwargs)),
        port_checker=lambda _port: None,
    )

    with pytest.raises(GenrePipelineRuntimeError, match="session not found"):
        runtime.run()

    assert not launched


def test_runtime_no_browser_reports_url_after_completion(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    process = FakeProcess()
    runtime = GenrePipelineRuntime(
        tmp_path,
        spec,
        "sensual_dominance",
        process_factory=lambda *_args, **_kwargs: process,
        browser_opener=lambda _url: (_ for _ in ()).throw(AssertionError("browser should not open")),
        no_browser=True,
        server_probe=lambda _url: True,
        port_checker=lambda _port: None,
        timeout=2,
    )

    def complete_during_wait(_seconds):
        if runtime.store.load().status.value == "incomplete":
            for phase, choices in complete_choices(spec, "sensual_dominance").items():
                runtime.store.update_choices(phase, choices)
            runtime.store.mark_complete()

    runtime.sleep = complete_during_wait
    result = runtime.run()

    assert result.browser_opened is False
    assert result.url == f"http://127.0.0.1:{runtime.port}/?session={runtime.store.load().id}"
