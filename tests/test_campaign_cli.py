from __future__ import annotations

import json
from pathlib import Path

from auteur.cli import main, parse_args


def test_campaign_commands_are_parseable() -> None:
    args = parse_args(["campaign", "inspect", "--project", ".", "--json"])
    assert args.command == "campaign"
    assert args.campaign_command == "inspect"
    assert args.json is True


def test_campaign_cli_golden_path_is_local_and_explicit(tmp_path: Path, capsys) -> None:
    assert main(["campaign", "init", "--project", str(tmp_path), "--campaign-id", "c1", "--project-id", "p1"]) == 0
    capsys.readouterr()
    assert main(["campaign", "validate", "--project", str(tmp_path), "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["valid"] is True

    assert main(["campaign", "handoff", "--project", str(tmp_path), "--operation", "inspect"]) == 0
    handoff_output = json.loads(capsys.readouterr().out)
    assert handoff_output["authority"] == "read_only"
