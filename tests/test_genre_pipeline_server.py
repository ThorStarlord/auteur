import json
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from auteur.blueprint import Genre
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.genre_pipeline.server import GenrePipelineServer
from auteur.genre_pipeline.session import GenreSessionStore
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


@contextmanager
def running_server(store):
    server = GenrePipelineServer(store, port=0)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def get_json(server, path: str):
    with urlopen(f"http://127.0.0.1:{server.port}{path}") as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def post_json(server, path: str, payload: dict):
    request = Request(
        f"http://127.0.0.1:{server.port}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_root_serves_generic_real_browser_and_pipeline_has_nine_phases(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("sensual_dominance")

    with running_server(store) as server:
        with urlopen(f"http://127.0.0.1:{server.port}/") as response:
            html = response.read().decode("utf-8")
        status, descriptor = get_json(server, "/pipeline")

    assert "mockOptions" not in html
    assert 'request("/pipeline")' in html
    assert "Interactive Genre Pipeline" in html
    assert status == 200
    assert descriptor["browser_title"] == spec.browser_title
    assert len(descriptor["phases"]) == 9


def test_gentlefemdom_partial_update_uses_registered_validator_without_unknown_core(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("sensual_dominance")

    with running_server(store) as server:
        status, body = post_json(
            server,
            "/session/update",
            {"phase": 1, "choices": {"emotional_core": "sensual_dominance"}},
        )

    assert status == 200
    assert body["is_valid"] is True
    assert not any("Unknown core" in error for error in body["errors"])


def test_invalid_update_returns_422_without_persisting(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("howdunit")

    with running_server(store) as server:
        with pytest.raises(HTTPError) as error:
            post_json(
                server,
                "/session/update",
                {"phase": 7, "choices": {"clue_distribution": "not-real"}},
            )
        payload = json.loads(error.value.read().decode("utf-8"))

    assert error.value.code == 422
    assert "invalid option" in payload["errors"][0]
    assert 7 not in store.load().choices


def test_settings_update_mode_and_working_title(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("cozy")

    with running_server(store) as server:
        status, body = post_json(
            server,
            "/session/settings",
            {"mode": "intimate", "working_title": "The Garden Club Case"},
        )

    assert status == 200
    assert body["session"]["mode"] == "intimate"
    assert body["session"]["working_title"] == "The Garden Club Case"


def test_completion_rejects_missing_fields_and_accepts_complete_choices(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("howdunit")

    with running_server(store) as server:
        with pytest.raises(HTTPError) as error:
            post_json(server, "/session/complete", {})
        assert error.value.code == 422

        for phase, choices in complete_choices(spec, "howdunit").items():
            post_json(server, "/session/update", {"phase": phase, "choices": choices})
        status, body = post_json(server, "/session/complete", {})

    assert status == 200
    assert body["session"]["status"] == "complete"


def test_warning_choices_are_persisted_and_redisplayed_after_reload(tmp_path):
    spec = get_genre_pipeline(Genre.NETORARE)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("classic_humiliation")

    with running_server(store) as server:
        _, update = post_json(
            server,
            "/session/update",
            {
                "phase": 4,
                "choices": {
                    "want": "want-expose",
                    "resistance": "resistance-inadequacy",
                    "change": "change-accept",
                },
            },
        )
    with running_server(store) as reloaded_server:
        _, validation = get_json(reloaded_server, "/session/validate")
        with urlopen(f"http://127.0.0.1:{reloaded_server.port}/") as response:
            html = response.read().decode("utf-8")

    assert update["warnings"]
    assert validation["warnings"] == update["warnings"]
    assert 'request("/session/validate")' in html


def test_completed_session_rejects_invalid_updates_before_validation(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("howdunit")
    store.mark_complete()

    with running_server(store) as server:
        with pytest.raises(HTTPError) as error:
            post_json(
                server,
                "/session/update",
                {"phase": 4, "choices": {"want": "not-an-option"}},
            )

    assert error.value.code == 409


def test_completed_session_rejects_settings_update_with_409(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("howdunit")
    store.mark_complete()

    with running_server(store) as server:
        with pytest.raises(HTTPError) as error:
            post_json(
                server,
                "/session/settings",
                {"working_title": "Different Title"},
            )

    assert error.value.code == 409


def test_completed_session_rejects_repeated_completion_with_409(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("sensual_dominance")

    with running_server(store) as server:
        for phase, choices in complete_choices(spec, "sensual_dominance").items():
            post_json(server, "/session/update", {"phase": phase, "choices": choices})
        post_json(server, "/session/complete", {})

        with pytest.raises(HTTPError) as error:
            post_json(server, "/session/complete", {})

    assert error.value.code == 409


def test_netorare_horror_full_workflow_with_resistance_inescapable(tmp_path):
    spec = get_genre_pipeline(Genre.NETORARE)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("horror")

    with running_server(store) as server:
        _, descriptor = get_json(server, "/pipeline")
        phase_4 = [p for p in descriptor["phases"] if p["number"] == 4][0]
        resistance_options = [f["options"] for f in phase_4["fields"] if f["id"] == "resistance"]
        assert any(opt["id"] == "resistance-inescapable" for opts in resistance_options for opt in opts)

        horror_choices = complete_choices(spec, "horror")

        for phase, choices in horror_choices.items():
            status, result = post_json(server, "/session/update", {"phase": phase, "choices": choices})
            assert status == 200, f"Phase {phase} update failed: {result}"

        status, validation = get_json(server, "/session/validate")
        assert status == 200
        assert validation["is_valid"], f"Validation failed: {validation['errors']}"

        status, completion = post_json(server, "/session/complete", {})
        assert status == 200
        assert completion["session"]["status"] == "complete"
