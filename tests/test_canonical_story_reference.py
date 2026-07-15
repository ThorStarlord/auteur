from pathlib import Path


ROOT = Path("examples/canonical_story")


def test_canonical_story_reference_contains_the_living_workflow():
    required = [
        "README.md", "story_identity.yaml", "blueprint.md", "external_edit.md",
        "expected_review.md", "expected_publication.md",
        "chapter_01/scene_01/realization.yaml",
        "chapter_01/scene_01/expression.md",
        "chapter_01/scene_02/realization.yaml",
        "chapter_01/scene_02/expression.md",
        "chapter_01/scene_03/realization.yaml",
        "chapter_01/scene_03/expression.md",
        "chapter_01/scene_04/realization.yaml",
        "chapter_01/scene_04/expression.md",
        "chapter_01/scene_05/realization.yaml",
        "chapter_01/scene_05/expression.md",
        "reasoning/README.md", "reconciliation/README.md",
    ]
    assert all((ROOT / path).is_file() for path in required)
