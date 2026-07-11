from unittest.mock import patch

from auteur.blueprint import Genre
from auteur.cli_mystery import MysteryCommand, handle_mystery_init
from auteur.genre_pipeline.registry import get_genre_pipeline


def test_mystery_command_is_registry_backed(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)

    command = MysteryCommand(tmp_path)

    assert command.spec is spec
    assert command.core_id == spec.default_core_id
    assert command.port == spec.default_port
    assert command.session_file == (
        tmp_path / ".auteur" / "genre_sessions" / "mystery" / "session.json"
    )


def test_mystery_command_supports_all_registered_cores(tmp_path):
    spec = get_genre_pipeline(Genre.MYSTERY)

    for core_id in spec.core_ids:
        assert MysteryCommand(tmp_path / core_id, core_id=core_id).core_id == core_id


def test_handle_mystery_init_delegates_to_generic_command(tmp_path):
    with patch("auteur.cli_mystery.GenrePipelineCommand") as command_type:
        command_type.return_value.run.return_value = 0

        result = handle_mystery_init(tmp_path, core_id="cozy", mode="comic")

    assert result == 0
    assert command_type.call_args.kwargs["spec"] is get_genre_pipeline(Genre.MYSTERY)
    assert command_type.call_args.kwargs["core_id"] == "cozy"
    assert command_type.call_args.kwargs["mode"] == "comic"
