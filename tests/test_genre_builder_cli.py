from __future__ import annotations

import yaml

from auteur.cli import main


BRIEF = """# Genre
Cozy Political Fantasy

# Emotional Promise
The reader should feel that broken civic trust can be repaired through courage and cleverness.

# Core Truth
Communities can heal when power is made accountable.

# Required Tropes
- intimate political stakes
- community web

# Optional Tropes
- magical bureaucracy

# Forbidden Mismatches
- nihilistic ending

# Common Failures
- politics becomes exposition instead of pressure

# Scope
minimum_viable_length: novella
default_length: novel
narrative_runway: medium
recommended_complexity: focused
mechanical_load: medium
worldbuilding_load: medium
cast_load: medium

# Setup Requirements
- show the community wound
"""


def test_genre_build_validate_explain_install_and_list_custom(tmp_path, capsys) -> None:
    brief = tmp_path / "brief.md"
    brief.write_text(BRIEF, encoding="utf-8")
    output = tmp_path / "cozy_political_fantasy.yaml"
    guide = tmp_path / "guide.md"
    project = tmp_path / "project"
    project.mkdir()

    assert main(["genre", "build", str(brief), "--output", str(output)]) == 0
    payload = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert payload["custom_genre_id"] == "cozy_political_fantasy"

    assert main(["genre", "validate", str(output)]) == 0
    assert main(["genre", "explain", str(output), "--output", str(guide)]) == 0
    assert "Genre Contract" in guide.read_text(encoding="utf-8")

    assert main(["genre", "install", str(output), "--project", str(project)]) == 0
    installed = project / "genres" / "custom" / "cozy_political_fantasy.yaml"
    assert installed.exists()

    assert main(["genre", "list-custom", str(project)]) == 0
    captured = capsys.readouterr()
    assert "cozy_political_fantasy" in captured.out


def test_genre_install_refuses_invalid_contract(tmp_path) -> None:
    contract = tmp_path / "bad.yaml"
    contract.write_text(
        yaml.safe_dump(
            {
                "custom_genre_id": "../bad",
                "base_genre": "other",
                "contract": {},
            }
        ),
        encoding="utf-8",
    )
    project = tmp_path / "project"
    project.mkdir()

    assert main(["genre", "install", str(contract), "--project", str(project)]) != 0
    assert not (project / "genres").exists()
