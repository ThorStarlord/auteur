from unittest.mock import Mock, patch

from auteur.blueprint import Genre
from auteur.cli_netorare import NetorareCommand, handle_netorare_init
from auteur.genre_pipeline.registry import get_genre_pipeline


def test_netorare_command_is_registry_backed(tmp_path):
    spec = get_genre_pipeline(Genre.NETORARE)

    command = NetorareCommand(tmp_path)

    assert command.spec is spec
    assert command.core_id == spec.default_core_id
    assert command.port == spec.default_port
    assert command.session_file == (
        tmp_path / ".auteur" / "genre_sessions" / "netorare" / "session.json"
    )


def test_netorare_command_preserves_public_overrides(tmp_path):
    command = NetorareCommand(
        tmp_path,
        core_id="horror",
        provider="openai",
        port=9900,
        timeout=12,
        debug=True,
        mode="tragic",
    )

    assert command.core_id == "horror"
    assert command.provider == "openai"
    assert command.port == 9900
    assert command.timeout == 12
    assert command.debug is True
    assert command.mode == "tragic"


def test_handle_netorare_init_delegates_to_generic_command(tmp_path):
    with patch("auteur.cli_netorare.GenrePipelineCommand") as command_type:
        command_type.return_value.run.return_value = 0

        result = handle_netorare_init(tmp_path, core_id="mystery", mode="noir")

    assert result == 0
    assert command_type.call_args.kwargs["spec"] is get_genre_pipeline(Genre.NETORARE)
    assert command_type.call_args.kwargs["core_id"] == "mystery"
    assert command_type.call_args.kwargs["mode"] == "noir"
