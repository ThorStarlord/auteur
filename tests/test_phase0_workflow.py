from pathlib import Path

from auteur.cli import main


EXAMPLE_IDENTITY = Path(__file__).parent.parent / "examples" / "story_identity.yaml"


def test_example_story_identity_seeds_blueprint_and_diagnoses_cleanly(tmp_path: Path):
    blueprint_path = tmp_path / "blueprint.yaml"

    assert main(["identity", "validate", str(EXAMPLE_IDENTITY)]) == 0
    assert main(["blueprint", "seed", str(EXAMPLE_IDENTITY), "--output", str(blueprint_path)]) == 0
    assert main(["structure", "diagnose", str(blueprint_path)]) == 0
