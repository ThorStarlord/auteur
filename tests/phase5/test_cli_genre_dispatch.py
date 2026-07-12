"""Tests: CLI dispatcher registers and invokes all three genres."""

import pytest
from pathlib import Path
from unittest.mock import patch
from auteur.cli import parse_args
from auteur.blueprint import Genre
from auteur.genre_pipeline.models import GenrePipelineSpec
from auteur.genre_pipeline import registry as pipeline_registry


class TestCLIGenreDispatch:
    """Verify all three genres are registered and dispatchable via CLI."""

    def test_cli_has_gentlefemdom_subcommand(self):
        """CLI parser accepts 'auteur gentlefemdom init'."""
        args = parse_args(["gentlefemdom", "init", "test_project"])
        assert args.command == "gentlefemdom"
        assert args.gentlefemdom_command == "init"

    def test_cli_has_mystery_subcommand(self):
        """CLI parser accepts 'auteur mystery init'."""
        args = parse_args(["mystery", "init", "test_project"])
        assert args.command == "mystery"
        assert args.mystery_command == "init"

    def test_cli_has_netorare_subcommand(self):
        """CLI parser accepts 'auteur netorare init'."""
        args = parse_args(["netorare", "init", "test_project"])
        assert args.command == "netorare"
        assert args.netorare_command == "init"

    def test_gentlefemdom_init_accepts_core_parameter(self):
        """'auteur gentlefemdom init --core sensual_dominance' parses."""
        args = parse_args(["gentlefemdom", "init", "test_project", "--core", "sensual_dominance"])
        assert args.core == "sensual_dominance"

    def test_all_core_ids_accepted_for_gentlefemdom(self):
        """Gentlefemdom accepts all three core IDs."""
        for core in ["sensual_dominance", "tender_surrender", "romantic_authority"]:
            args = parse_args(["gentlefemdom", "init", "test_project", "--core", core])
            assert args.core == core

    def test_registered_fourth_genre_dispatches_through_shared_command(self, monkeypatch):
        spec = GenrePipelineSpec(
            genre=Genre.OTHER, slug="other", core_ids=("core",),
            default_core_id="core", default_port=8780, browser_title="Other",
            template_factory=lambda _: object(), validate_choices=lambda *_: (True, [], []),
            contract_loader=lambda: None, identity_profile_factory=lambda _: None,
        )
        monkeypatch.setattr(pipeline_registry, "_SPECS", {spec.genre: spec})
        with patch("auteur.genre_pipeline.cli.GenrePipelineCommand.run", return_value=17) as run:
            from auteur.cli import main
            assert main(["other", "init", "project"]) == 17
        run.assert_called_once()

    def test_spec_rejects_slug_mismatch(self):
        with pytest.raises(ValueError, match="slug"):
            GenrePipelineSpec(
                genre=Genre.OTHER, slug="wrong", core_ids=("core",), default_core_id="core",
                default_port=8780, browser_title="Other", template_factory=lambda _: object(),
                validate_choices=lambda *_: (True, [], []), contract_loader=lambda: None,
                identity_profile_factory=lambda _: None,
            )

    def test_command_rejects_invalid_port_before_runtime_creation(self):
        from auteur.genre_pipeline.cli import GenrePipelineCommand
        spec = pipeline_registry.get_genre_pipeline(Genre.NETORARE)
        with pytest.raises(ValueError, match="port"):
            GenrePipelineCommand(Path("project"), spec, spec.default_core_id, port=65536)
