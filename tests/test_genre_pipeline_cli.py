from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auteur.blueprint import Genre
from auteur.cli import parse_args
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.genre_pipeline.runtime import GenrePipelineResult


@pytest.mark.parametrize(
    ("slug", "default_core", "default_port"),
    [
        ("netorare", "classic_humiliation", 8765),
        ("mystery", "howdunit", 8766),
        ("gentlefemdom", "sensual_dominance", 8767),
    ],
)
def test_cli_parser_uses_registry_defaults(slug, default_core, default_port, tmp_path):
    args = parse_args([slug, "init", str(tmp_path)])

    assert args.core == default_core
    assert args.port == default_port
    assert args.mode is None
    assert args.provider is None


@pytest.mark.parametrize("slug", ["netorare", "mystery", "gentlefemdom"])
def test_cli_parser_accepts_visible_mode_override(slug, tmp_path):
    args = parse_args([slug, "init", str(tmp_path), "--mode", "noir"])

    assert args.mode == "noir"


def test_generic_command_runs_registry_backed_runtime_and_formats_result(tmp_path, capsys):
    from auteur.genre_pipeline.cli import GenrePipelineCommand

    result = GenrePipelineResult(
        genre="mystery",
        core_id="howdunit",
        session_file=tmp_path / ".auteur" / "genre_sessions" / "mystery" / "session.json",
        identity_file=tmp_path / "story_identity.yaml",
        warnings=("Review the clue density.",),
        browser_opened=True,
    )
    runtime = Mock()
    runtime.run.return_value = result
    runtime_factory = Mock(return_value=runtime)

    command = GenrePipelineCommand(
        project_path=tmp_path,
        spec=get_genre_pipeline(Genre.MYSTERY),
        core_id="howdunit",
        mode="procedural",
        provider="anthropic",
        runtime_factory=runtime_factory,
    )

    assert command.run() == 0
    runtime_factory.assert_called_once()
    kwargs = runtime_factory.call_args.kwargs
    assert kwargs["spec"].slug == "mystery"
    assert kwargs["mode"] == "procedural"
    assert kwargs["port"] == 8766
    captured = capsys.readouterr()
    assert "story_identity.yaml" in captured.out
    assert "Review the clue density." in captured.err
    assert "deprecated" in captured.err
    assert "no LLM call" in captured.err


@pytest.mark.parametrize(
    ("module_name", "handler_name", "genre"),
    [
        ("auteur.cli_netorare", "handle_netorare_init", Genre.NETORARE),
        ("auteur.cli_mystery", "handle_mystery_init", Genre.MYSTERY),
        ("auteur.cli_gentlefemdom", "handle_gentlefemdom_init", Genre.GENTLEFEMDOM),
    ],
)
def test_compatibility_handlers_dispatch_through_generic_command(
    module_name, handler_name, genre, tmp_path
):
    module = __import__(module_name, fromlist=[handler_name])
    spec = get_genre_pipeline(genre)

    with patch(f"{module_name}.GenrePipelineCommand") as command_type:
        command_type.return_value.run.return_value = 0
        result = getattr(module, handler_name)(
            tmp_path,
            core_id=spec.default_core_id,
            mode=spec.identity_profile_factory(spec.default_core_id).default_mode,
        )

    assert result == 0
    assert command_type.call_args.kwargs["spec"] == spec


def test_compatibility_cli_modules_do_not_import_legacy_runtime_infrastructure():
    root = Path(__file__).parents[1] / "src" / "auteur"

    for filename in ("cli_netorare.py", "cli_mystery.py", "cli_gentlefemdom.py"):
        source = (root / filename).read_text(encoding="utf-8")
        assert "auteur.netorare.browser.server" not in source
        assert "auteur.netorare.session" not in source
        assert "NETORARE_" not in source
        assert "IdentityGenerator" not in source


@pytest.mark.parametrize(
    ("slug", "handler_name", "mode"),
    [
        ("netorare", "handle_netorare_init", "tragic"),
        ("mystery", "handle_mystery_init", "procedural"),
        ("gentlefemdom", "handle_gentlefemdom_init", "intimate"),
    ],
)
def test_public_cli_dispatches_each_command_to_compatibility_handler(
    slug, handler_name, mode, tmp_path
):
    import auteur.cli as cli

    with patch.object(cli, handler_name, return_value=0) as handler:
        result = cli.main([slug, "init", str(tmp_path), "--mode", mode])

    assert result == 0
    assert handler.call_args.kwargs["mode"] == mode
