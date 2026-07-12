import json
from pathlib import Path

import pytest

from auteur.project import Project
from auteur.blueprint import StoryBlueprint


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_init_creates_directory_with_blueprint_and_bible(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)

    project = Project.init(proj_dir, blueprint)

    assert proj_dir.is_dir()
    assert (proj_dir / "blueprint.yaml").exists()
    assert (proj_dir / "bible.json").exists()
    assert (proj_dir / "chapters").is_dir()
    assert not (proj_dir / "structure").exists()
    bible_data = json.loads((proj_dir / "bible.json").read_text(encoding="utf-8"))
    assert bible_data["characters"] == {}


def test_init_refuses_to_overwrite_existing(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    Project.init(proj_dir, blueprint)

    with pytest.raises(FileExistsError):
        Project.init(proj_dir, blueprint)


def test_load_round_trips_blueprint_and_bible(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    Project.init(proj_dir, blueprint)

    project = Project.load(proj_dir)

    assert project.blueprint.identity.title == "The Shattered Crown"
    assert project.bible.data["characters"] == {}


def test_chapter_dir_paths_are_zero_padded(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert project.chapter_dir(1).name == "01"
    assert project.chapter_dir(45).name == "45"


def test_structure_diagnostics_dir_creates_standard_path(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))

    diagnostics_dir = project.structure_diagnostics_dir()

    assert diagnostics_dir == tmp_path / "n" / "structure" / "diagnostics"
    assert diagnostics_dir.is_dir()


def test_structure_proposals_dir_creates_standard_path_without_changing_chapter_paths(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))

    proposals_dir = project.structure_proposals_dir()

    assert proposals_dir == tmp_path / "n" / "structure" / "proposals"
    assert proposals_dir.is_dir()
    assert project.chapter_dir(1) == tmp_path / "n" / "chapters" / "01"


def test_next_draft_version_starts_at_one(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert project.next_draft_version(1) == 1


def test_next_draft_version_after_writes(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    project.write_draft(1, 1, "first")
    project.write_draft(1, 2, "second")
    assert project.next_draft_version(1) == 3


def test_write_outline_and_draft_and_validation(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))

    out_path = project.write_outline(1, {"scope": "chapter", "scenes": []})
    draft_path = project.write_draft(1, 1, "Once upon a time...")
    val_path = project.write_validation(1, 1, {"passed": True, "findings": []})

    assert out_path.read_text(encoding="utf-8").startswith("scope:")
    assert draft_path.read_text(encoding="utf-8") == "Once upon a time..."
    assert json.loads(val_path.read_text(encoding="utf-8"))["passed"] is True


def test_write_final_and_has_final(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert not project.has_final(1)
    project.write_final(1, "the chapter prose")
    assert project.has_final(1)
    assert (project.chapter_dir(1) / "final.md").read_text(encoding="utf-8") == "the chapter prose"


def test_write_draft_refuses_to_overwrite_existing_version(tmp_path):
    project = Project.init(tmp_path / "project", StoryBlueprint.from_yaml(SAMPLE_YAML))
    project.write_draft(1, 1, "first")

    with pytest.raises(FileExistsError, match="already exists"):
        project.write_draft(1, 1, "replacement")
