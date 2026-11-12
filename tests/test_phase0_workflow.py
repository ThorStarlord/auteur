import shutil
from pathlib import Path

from auteur.cli import main


EXAMPLE_IDENTITY = Path(__file__).parent.parent / "examples" / "story_identity.yaml"


def test_example_story_identity_seeds_blueprint_and_diagnoses_cleanly(tmp_path: Path):
    blueprint_path = tmp_path / "blueprint.yaml"
    # `identity validate` writes its report beside the file it validates. Run the workflow on a
    # copy so the committed example directory is never rewritten.
    identity = tmp_path / "story_identity.yaml"
    shutil.copy(EXAMPLE_IDENTITY, identity)

    assert main(["identity", "validate", str(identity)]) == 0
    assert main(["blueprint", "seed", str(identity), "--output", str(blueprint_path)]) == 0
    assert main(["structure", "diagnose", str(blueprint_path)]) == 0


def test_example_workflow_leaves_committed_example_directory_untouched(tmp_path: Path):
    report = EXAMPLE_IDENTITY.parent / "identity" / "validation_report.json"
    before = report.read_bytes()

    test_example_story_identity_seeds_blueprint_and_diagnoses_cleanly(tmp_path)

    assert report.read_bytes() == before
