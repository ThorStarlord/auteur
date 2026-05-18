import pytest
from pathlib import Path
import yaml
from auteur.cli import main
from auteur.blueprint import StoryBlueprint

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
