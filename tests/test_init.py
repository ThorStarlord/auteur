"""Tests for the auteur init enhancements: pre-init validation and --force."""

import json

import yaml

from auteur.cli import main

SAMPLE_YAML = "examples/sample_blueprint.yaml"


def test_cli_init_rejects_malformed_blueprint_with_clear_error(tmp_path, capsys):
    """A malformed blueprint should produce a readable error message
    and not create any directory artifacts."""
    target = tmp_path / "novel"
    bad_bp = tmp_path / "bad.yaml"
    bad_bp.write_text(
        "identity:\n  title: Broken\n  author_intent: Test\n",
        encoding="utf-8",
    )

    rc = main(["init", str(target), "--from", str(bad_bp)])

    assert rc == 1
    assert not target.exists()
    err = capsys.readouterr().err
    assert "ValidationError" not in err
    assert any(w in err.lower() for w in ["blueprint", "invalid", "malformed"])



def test_cli_init_force_reinitializes_existing_project(tmp_path, capsys):
    """--force re-initializes an existing auteur project, wiping old state."""
    target = tmp_path / "novel"
    main(["init", str(target), "--from", SAMPLE_YAML])

    bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    bible["characters"]["Stale"] = {"location": "Nowhere"}
    (target / "bible.json").write_text(json.dumps(bible), encoding="utf-8")

    rc = main(["init", str(target), "--from", SAMPLE_YAML, "--force"])

    assert rc == 0
    new_bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    assert "Stale" not in new_bible["characters"]


def test_cli_init_force_refuses_non_auteur_directory(tmp_path, capsys):
    """--force refuses directories without both blueprint.yaml and bible.json."""
    target = tmp_path / "random_dir"
    target.mkdir()
    (target / "notes.txt").write_text("not a project", encoding="utf-8")

    rc = main(["init", str(target), "--from", SAMPLE_YAML, "--force"])

    assert rc == 1
    assert not (target / "blueprint.yaml").exists()
    err = capsys.readouterr().err
    assert "auteur project" in err.lower()
