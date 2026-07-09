import pytest
from pathlib import Path
import yaml
from auteur.cli import main
from auteur.blueprint import StoryBlueprint
from auteur.genre_builder.builder import build_custom_genre_contract
from auteur.genre_builder.parser import parse_genre_brief


CUSTOM_OTHER_BRIEF = """# Genre
Project Other

# Emotional Promise
The reader should feel restorative closure.

# Core Truth
Cruel endings break this custom project contract.

# Required Tropes
- restorative ending

# Optional Tropes
- civic repair

# Forbidden Mismatches
- tragic ending

# Common Failures
- mistaking despair for depth

# Scope
minimum_viable_length: novella
default_length: novel
narrative_runway: medium
recommended_complexity: focused
mechanical_load: medium
worldbuilding_load: medium
cast_load: medium

# Setup Requirements
- establish why restoration matters
"""

def test_cli_identity_workflow(tmp_path: Path):
    identity_yaml_path = tmp_path / "story_identity.yaml"
    blueprint_yaml_path = tmp_path / "blueprint.yaml"
    
    identity_data = {
        "title": "A Song of Bronze",
        "core_answer": "A tragic political drama about the bronze age collapse.",
        "central_engine": {
            "want": "The king wants to preserve the trade routes at any cost.",
            "resistance": "The Sea Peoples disrupt the shipping lanes and burn the ports.",
            "conflict": "Sacrificing minor cities protects the capital but destroys the empire's legitimacy.",
            "stakes": "The complete collapse of late bronze age civilization.",
            "change": "The king changes from a proud god-ruler to an exhausted survivor sitting in ashes.",
        }
    }
    
    # Write the identity YAML
    identity_yaml_path.write_text(yaml.safe_dump(identity_data), encoding="utf-8")
    
    # 1. Test identity validate
    exit_code_validate = main(["identity", "validate", str(identity_yaml_path)])
    assert exit_code_validate == 0
    # Verify artifact was written
    validation_artifact = tmp_path / "identity" / "validation_report.json"
    assert validation_artifact.exists()
    import json
    report = json.loads(validation_artifact.read_text(encoding="utf-8"))
    assert "diagnostics" in report
    
    # 2. Test identity compile
    exit_code_compile = main(["identity", "compile", str(identity_yaml_path), "--output", str(blueprint_yaml_path)])
    assert exit_code_compile == 0
    assert blueprint_yaml_path.exists()
    
    # Verify compiled blueprint parses cleanly
    blueprint = StoryBlueprint.from_yaml(blueprint_yaml_path)
    assert blueprint.identity.title == "A Song of Bronze"
    assert blueprint.story_engine.main_thread.want.author_text.startswith("The king wants")

    # Clean up blueprint
    blueprint_yaml_path.unlink()
    
    # 3. Test blueprint seed
    exit_code_seed = main(["blueprint", "seed", str(identity_yaml_path), "--output", str(blueprint_yaml_path)])
    assert exit_code_seed == 0
    assert blueprint_yaml_path.exists()
    
    blueprint_2 = StoryBlueprint.from_yaml(blueprint_yaml_path)
    assert blueprint_2.identity.title == "A Song of Bronze"
    assert blueprint_2.story_engine.main_thread.want.author_text.startswith("The king wants")


def test_identity_validate_project_uses_project_local_genre_contract(tmp_path: Path):
    project = tmp_path / "project"
    custom_dir = project / "genres" / "custom"
    custom_dir.mkdir(parents=True)
    custom = build_custom_genre_contract(parse_genre_brief(CUSTOM_OTHER_BRIEF)).model_copy(
        update={"custom_genre_id": "other"}
    )
    (custom_dir / "other.yaml").write_text(
        yaml.safe_dump(custom.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    identity_path = tmp_path / "story_identity.yaml"
    identity_path.write_text(
        yaml.safe_dump(
            {
                "title": "The Failed Restoration",
                "core_answer": "A tragic story that violates the project-local custom contract.",
                "target_experience": {
                    "primary": "dread",
                    "progression": "hope -> collapse",
                    "avoid": [],
                },
                "story_type": {
                    "medium": "novel",
                    "mode": "tragic",
                    "genre": "other",
                    "subgenres": [],
                    "target_audience": "adult",
                    "length_class": None,
                },
                "central_engine": {
                    "want": "The mayor wants to restore the city.",
                    "resistance": "The old council sabotages every repair.",
                    "conflict": "Every compromise saves a building and loses a neighbor.",
                    "stakes": "The city either heals or becomes a monument to betrayal.",
                    "change": "The mayor becomes a cynic who abandons restoration.",
                },
                "not_this": [],
                "open_questions": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert main(["identity", "validate", str(identity_path), "--project", str(project)]) == 1
