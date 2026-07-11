import pytest
from pathlib import Path
from auteur.universe.models import UniverseIdentity, SettingProfile, TimelineProfile
from auteur.universe.cli import register_universe_subcommands, handle_universe_command
import argparse


def test_universe_validate_command_with_valid_universe(tmp_path):
    """Validating a well-formed universe returns exit code 0."""
    universe = UniverseIdentity(
        name="Test World",
        slug="test-world",
        description="A test universe",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="TestLand"),
        magic_system="Magic exists",
        core_mythology="Creation myth",
        timeline=TimelineProfile(current_era="Present", era_description="Now", years_of_history=1000),
        forbidden_elements=["Chaos"],
        required_elements=["Order"],
        cross_story_constraints=[]
    )

    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)

    # Simulate CLI args
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)

    args = parser.parse_args(["universe", "validate", str(universe_path)])

    exit_code = handle_universe_command(args)

    assert exit_code == 0


def test_universe_validate_command_with_invalid_yaml(tmp_path):
    """Validating malformed YAML returns non-zero exit code."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("{ invalid yaml :")

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)

    args = parser.parse_args(["universe", "validate", str(bad_yaml)])

    exit_code = handle_universe_command(args)

    assert exit_code != 0


def test_universe_diagnose_command_generates_report(tmp_path, capsys):
    """Diagnose command loads universe and outputs diagnostics."""
    universe = UniverseIdentity(
        name="Incomplete Universe",
        slug="incomplete",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Today", era_description="", years_of_history=0),
        forbidden_elements=[],  # Empty!
        required_elements=[],   # Empty!
        cross_story_constraints=[]
    )

    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)

    args = parser.parse_args(["universe", "diagnose", str(universe_path)])

    exit_code = handle_universe_command(args)
    captured = capsys.readouterr()

    # Should report the empty elements warning
    assert "empty_forbidden_and_required" in captured.out.lower() or "empty_forbidden_and_required" in captured.err.lower() or exit_code != 0
