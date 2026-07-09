"""Tests: CLI dispatcher registers and invokes all three genres."""

import pytest
from pathlib import Path
from unittest.mock import patch
from auteur.cli import parse_args
from auteur.blueprint import Genre


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
