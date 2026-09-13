import json
from types import SimpleNamespace

import pytest

from auteur.cli import main, parse_args
from auteur.story_design_packs import cli as design_cli


def test_design_pack_commands_parse_and_run(capsys):
    args = parse_args(["design", "pack", "compose", "--pack", "superhero", "--pack", "anti_hero"])
    assert args.command == "design"
    assert args.design_pack_command == "compose"
    assert main(["design", "pack", "list", "--json"]) == 0
    assert '"pack_id": "superhero"' in capsys.readouterr().out


def test_legacy_tutor_command_remains_derived(capsys):
    assert main(["design", "tutor", "recommend", "--pack", "superhero", "--decision", "power origin"]) == 0
    output = capsys.readouterr().out
    assert "DERIVED / NOT CANON" in output
    assert "Recommended:" in output


def test_story_discovery_accepts_optional_design_pack_priors():
    args = parse_args([
        "story-discovery", "run", "a premise", "--design-pack", "superhero",
        "--design-pack", "hard_determinism",
    ])
    assert args.design_packs == ["superhero", "hard_determinism"]


def test_root_tutor_next_parses_and_is_explicitly_noncanonical(capsys):
    args = parse_args([
        "tutor", "next", "--pack", "superhero", "--decision", "power origin"
    ])
    assert args.command == "tutor"
    assert args.tutor_command == "next"

    assert main([
        "tutor", "next", "--pack", "superhero", "--decision", "power origin"
    ]) == 0
    output = capsys.readouterr().out
    assert "Decision Card" in output
    assert "DERIVED / NOT CANON" in output
    assert "Recommended:" in output


def test_root_tutor_depth_changes_presentation_not_semantic_identity(capsys):
    assert main([
        "tutor", "next", "--pack", "superhero", "--decision", "power origin",
        "--depth", "teach", "--json",
    ]) == 0
    teach = json.loads(capsys.readouterr().out)

    assert main([
        "tutor", "explain", "--pack", "superhero", "--decision", "power origin", "--json",
    ]) == 0
    explain = json.loads(capsys.readouterr().out)

    assert teach["card_id"] == explain["card_id"]
    assert teach["recommendation"] == explain["recommendation"]
    assert teach["evidence"] == explain["evidence"]
    assert teach["depth"] == "teach"
    assert explain["depth"] == "explain"


def test_root_tutor_persist_show_explain_choose_preserves_canonical_files(tmp_path, capsys):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    identity.write_bytes(b"accepted identity\n")
    blueprint.write_bytes(b"accepted blueprint\n")
    before = (identity.read_bytes(), blueprint.read_bytes())

    common = [
        "--pack", "superhero",
        "--decision", "power origin",
        "--premise", "a reluctant hero",
        "--project", str(tmp_path),
        "--source", "identity=story_identity.yaml",
    ]
    assert main(["tutor", "next", *common, "--json"]) == 0
    created = json.loads(capsys.readouterr().out)
    session_id = created["session_id"]
    assert created["card"]["authority_status"] == "DERIVED / NOT CANON"

    assert main(["tutor", "show", session_id, "--project", str(tmp_path), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["status"] == "active"
    assert shown["authority_status"] == "LOCAL / NONCANONICAL"

    assert main(["tutor", "explain", *common, "--json"]) == 0
    explained = json.loads(capsys.readouterr().out)
    assert explained["session_id"] == session_id
    assert explained["card"]["card_id"] == created["card"]["card_id"]
    assert explained["card"]["depth"] == "explain"

    assert main([
        "tutor", "choose", session_id, "choose",
        "--value", "keep the origin costly",
        "--project", str(tmp_path), "--json",
    ]) == 0
    chosen = json.loads(capsys.readouterr().out)
    assert chosen["status"] == "resolved"
    assert chosen["response_action"] == "choose"
    assert chosen["response_value"] == "keep the origin costly"
    assert chosen["authority_status"] == "LOCAL / NONCANONICAL"
    assert chosen["card"]["authority_status"] == "DERIVED / NOT CANON"
    assert (identity.read_bytes(), blueprint.read_bytes()) == before


def test_root_tutor_source_change_marks_stale_and_blocks_all_actions(tmp_path, capsys):
    source = tmp_path / "story_identity.yaml"
    source.write_text("identity: v1\n", encoding="utf-8")

    assert main([
        "tutor", "next", "--pack", "superhero", "--decision", "power origin",
        "--project", str(tmp_path), "--source", "identity=story_identity.yaml", "--json",
    ]) == 0
    session_id = json.loads(capsys.readouterr().out)["session_id"]

    source.write_text("identity: v2\n", encoding="utf-8")
    assert main(["tutor", "show", session_id, "--project", str(tmp_path), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["status"] == "stale"

    for action in ("choose", "keep_unresolved", "reject_finding", "request_alternatives"):
        assert main([
            "tutor", "choose", session_id, action, "--project", str(tmp_path)
        ]) == 2
        error = capsys.readouterr().err
        assert "stale Tutor session" in error


def test_root_tutor_rejects_unresolvable_or_malformed_sources(tmp_path, capsys):
    assert main([
        "tutor", "next", "--pack", "superhero", "--project", str(tmp_path),
    ]) == 2
    assert "require at least one --source" in capsys.readouterr().err

    assert main([
        "tutor", "next", "--pack", "superhero", "--project", str(tmp_path),
        "--source", "story_identity.yaml",
    ]) == 2
    assert "NAME=PATH" in capsys.readouterr().err

    assert main([
        "tutor", "next", "--pack", "superhero", "--project", str(tmp_path),
        "--source", "identity=missing.yaml",
    ]) == 2
    assert "does not exist" in capsys.readouterr().err


def test_root_tutor_rejects_source_outside_project(tmp_path, capsys):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.yaml"
    outside.write_text("outside: true\n", encoding="utf-8")
    try:
        assert main([
            "tutor", "next", "--pack", "superhero", "--project", str(tmp_path),
            "--source", f"outside={outside}",
        ]) == 2
        assert "inside the selected project" in capsys.readouterr().err
    finally:
        outside.unlink(missing_ok=True)


def test_root_tutor_reports_no_decision_instead_of_fabricating(monkeypatch, capsys):
    monkeypatch.setattr(
        design_cli,
        "compose_packs",
        lambda _pack_ids: SimpleNamespace(applicable_design_priors=[]),
    )
    assert main(["tutor", "next", "--pack", "superhero", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {"status": "no_decision", "card": None}


def test_root_tutor_parser_rejects_unknown_response_action():
    with pytest.raises(SystemExit):
        parse_args(["tutor", "choose", "0123456789abcdef", "rewrite_canon"])
