import json

import pytest
from pydantic import ValidationError

from auteur.blueprint import Genre, StoryMode
from auteur.genre_pipeline.models import GenreSession, GenreSessionStatus
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.genre_pipeline.session import GenreSessionError, GenreSessionStore


def test_session_store_writes_versioned_state_under_dot_auteur(tmp_path):
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    store = GenreSessionStore.for_project(tmp_path, spec)

    session = store.create("sensual_dominance")

    assert store.session_file == tmp_path / ".auteur" / "genre_sessions" / "gentlefemdom" / "session.json"
    assert session.schema_version == 1
    assert session.genre == Genre.GENTLEFEMDOM
    assert session.mode == StoryMode.INTIMATE
    assert session.working_title == "Untitled: Sensual Dominance"
    assert store.load() == session
    assert not store.session_file.with_suffix(".tmp").exists()
    assert json.loads(store.session_file.read_text(encoding="utf-8"))["genre"] == "gentlefemdom"


def test_session_model_rejects_extra_fields():
    with pytest.raises(ValidationError):
        GenreSession.model_validate(
            {
                "schema_version": 1,
                "id": "session-id",
                "genre": "mystery",
                "core_id": "howdunit",
                "mode": "procedural",
                "working_title": "Title",
                "choices": {},
                "status": "incomplete",
                "created_at": "2026-07-10T00:00:00Z",
                "updated_at": "2026-07-10T00:00:00Z",
                "generated_analysis": {},
            }
        )


def test_session_model_rejects_blank_working_title():
    with pytest.raises(ValidationError, match="working_title"):
        GenreSession.model_validate(
            {
                "schema_version": 1,
                "id": "session-id",
                "genre": "mystery",
                "core_id": "howdunit",
                "mode": "procedural",
                "working_title": "   ",
                "choices": {},
                "status": "incomplete",
                "created_at": "2026-07-10T00:00:00Z",
                "updated_at": "2026-07-10T00:00:00Z",
            }
        )


def test_session_store_refuses_existing_and_legacy_sessions(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("howdunit")

    with pytest.raises(GenreSessionError, match="already exists"):
        store.create("howdunit")

    other_project = tmp_path / "legacy"
    legacy_file = other_project / "netorare" / "session.json"
    legacy_file.parent.mkdir(parents=True)
    legacy_file.write_text("{}", encoding="utf-8")

    with pytest.raises(GenreSessionError, match="Legacy genre session"):
        GenreSessionStore.for_project(other_project, spec).create("howdunit")


def test_completed_session_rejects_further_mutation(tmp_path):
    spec = get_genre_pipeline(Genre.NETORARE)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("classic_humiliation")
    store.mark_complete()

    assert store.load().status == GenreSessionStatus.COMPLETE
    with pytest.raises(GenreSessionError, match="completed"):
        store.update_choices(4, {"want": "want-dignity"})
    with pytest.raises(GenreSessionError, match="completed"):
        store.update_settings(mode=StoryMode.NOIR)


def test_session_settings_and_choices_round_trip(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)
    store = GenreSessionStore.for_project(tmp_path, spec)
    store.create("cozy")

    store.update_settings(mode=StoryMode.INTIMATE, working_title="The Garden Club Case")
    store.update_choices(4, {"want": "want-restore-harmony"})

    session = store.load()
    assert session.mode == StoryMode.INTIMATE
    assert session.working_title == "The Garden Club Case"
    assert session.choices[4] == {"want": "want-restore-harmony"}


def test_session_creation_rejects_unknown_core_and_invalid_mode(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)

    with pytest.raises(GenreSessionError, match="Unknown core_id"):
        GenreSessionStore.for_project(tmp_path / "core", spec).create("not-a-core")

    with pytest.raises(GenreSessionError, match="Invalid story mode"):
        GenreSessionStore.for_project(tmp_path / "mode", spec).create(
            "howdunit", mode="not-a-mode"
        )
