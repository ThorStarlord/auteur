from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.cli import main, parse_args
from auteur.story_design_packs.tutor import decision_card_from_diagnostic
from auteur.structure import DiagnosticSeverity, analyze_structure


def _minimal_blueprint_data() -> dict[str, object]:
    return {
        "identity": {
            "title": "Boundary Test Story",
            "author_intent": "Test whether advice remains advice.",
            "length_class": "novel",
            "genre": "literary",
            "medium": "novel",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "quiet pressure",
        },
        "theme": {
            "central_question": "What does truth cost?",
            "thesis": "Truth costs belonging.",
            "motifs": [],
        },
    }


def _non_tutor_snapshot(root: Path) -> dict[str, bytes]:
    snapshot: dict[str, bytes] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts[:2] == (".auteur", "tutor"):
            continue
        snapshot[relative.as_posix()] = path.read_bytes()
    return snapshot


def test_real_structure_diagnostic_becomes_derived_card_without_repair(tmp_path: Path):
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_data = _minimal_blueprint_data()
    blueprint_path.write_text(yaml.safe_dump(blueprint_data), encoding="utf-8")
    before = blueprint_path.read_bytes()

    diagnostics = analyze_structure(StoryBlueprint.model_validate(blueprint_data))
    diagnostic = next(item for item in diagnostics if item.rule == "story_engine.missing")
    card = decision_card_from_diagnostic(
        diagnostic,
        story_context="blueprint.yaml",
    )

    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert card.authority_status == "DERIVED / NOT CANON"
    assert card.source_rule == "story_engine.missing"
    assert "automatic rewrite" in card.beginner_trap
    assert "proposal" in card.downstream_consequences[0]
    assert blueprint_path.read_bytes() == before
    assert sorted(path.name for path in tmp_path.iterdir()) == ["blueprint.yaml"]


def test_root_tutor_only_mutates_local_tutor_workspace(tmp_path: Path, capsys):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    notes = tmp_path / "author_notes.md"
    identity.write_bytes(b"accepted identity\n")
    blueprint.write_bytes(b"accepted blueprint\n")
    notes.write_bytes(b"private author notes\n")
    before = _non_tutor_snapshot(tmp_path)

    common = [
        "--pack",
        "superhero",
        "--decision",
        "power origin",
        "--premise",
        "a reluctant hero",
        "--project",
        str(tmp_path),
        "--source",
        "identity=story_identity.yaml",
        "--source",
        "blueprint=blueprint.yaml",
    ]

    assert main(["tutor", "next", *common, "--json"]) == 0
    created = json.loads(capsys.readouterr().out)
    session_id = created["session_id"]
    assert created["card"]["authority_status"] == "DERIVED / NOT CANON"

    assert main(["tutor", "show", session_id, "--project", str(tmp_path), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["authority_status"] == "LOCAL / NONCANONICAL"

    assert main(["tutor", "explain", *common, "--json"]) == 0
    explained = json.loads(capsys.readouterr().out)
    assert explained["card"]["card_id"] == created["card"]["card_id"]

    assert main(
        [
            "tutor",
            "choose",
            session_id,
            "choose",
            "--value",
            "keep the origin costly",
            "--project",
            str(tmp_path),
            "--json",
        ]
    ) == 0
    resolved = json.loads(capsys.readouterr().out)
    assert resolved["status"] == "resolved"
    assert resolved["authority_status"] == "LOCAL / NONCANONICAL"
    assert resolved["card"]["authority_status"] == "DERIVED / NOT CANON"

    assert _non_tutor_snapshot(tmp_path) == before
    session_files = list((tmp_path / ".auteur" / "tutor" / "sessions").glob("*.json"))
    assert len(session_files) == 1


def test_tutor_cannot_create_story_identity_or_replace_discovery_acceptance(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "tutor",
            "next",
            "--pack",
            "superhero",
            "--decision",
            "power origin",
        ]
    ) == 0
    assert "DERIVED / NOT CANON" in capsys.readouterr().out
    assert not (tmp_path / "story_identity.yaml").exists()

    discovery_accept = parse_args(
        [
            "story-discovery",
            "accept",
            "candidate.yaml",
            "--output",
            "story_identity.yaml",
        ]
    )
    assert discovery_accept.command == "story-discovery"
    assert discovery_accept.story_discovery_command == "accept"
    assert discovery_accept.output == Path("story_identity.yaml")


def test_existing_design_and_genre_pack_surfaces_remain_available(capsys):
    assert main(["design", "pack", "list", "--json"]) == 0
    design_payload = json.loads(capsys.readouterr().out)
    assert any(item["pack_id"] == "superhero" for item in design_payload)

    assert main(["genre", "pack", "list", "--json"]) == 0
    genre_payload = json.loads(capsys.readouterr().out)
    assert genre_payload


def test_stale_root_session_cannot_reenter_authority_path(tmp_path: Path, capsys):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    identity.write_text("identity: v1\n", encoding="utf-8")
    blueprint.write_text("blueprint: accepted\n", encoding="utf-8")
    before_blueprint = blueprint.read_bytes()

    assert main(
        [
            "tutor",
            "next",
            "--pack",
            "superhero",
            "--project",
            str(tmp_path),
            "--source",
            "identity=story_identity.yaml",
            "--json",
        ]
    ) == 0
    session_id = json.loads(capsys.readouterr().out)["session_id"]

    identity.write_text("identity: v2\n", encoding="utf-8")
    for action in ("choose", "keep_unresolved", "reject_finding", "request_alternatives"):
        assert main(
            ["tutor", "choose", session_id, action, "--project", str(tmp_path)]
        ) == 2
        assert "stale Tutor session" in capsys.readouterr().err

    assert blueprint.read_bytes() == before_blueprint
