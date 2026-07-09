from __future__ import annotations

import yaml

from auteur.cli import main


def _project_with_draft(tmp_path):
    project = tmp_path / "project"
    chapter_dir = project / "chapters" / "03"
    chapter_dir.mkdir(parents=True)
    draft = chapter_dir / "draft_v2.md"
    draft.write_text("The tower stood as a testament to old fear.\n", encoding="utf-8")
    return project, draft


def test_edit_review_writes_versioned_artifacts(tmp_path) -> None:
    project, _ = _project_with_draft(tmp_path)

    exit_code = main(["edit", "review", str(project), "3", "--passes", "aiisms"])

    artifact_dir = project / "editing" / "chapter_03" / "draft_v2"
    assert exit_code == 0
    assert (artifact_dir / "edit_report.json").exists()
    assert (artifact_dir / "patch_proposals.yaml").exists()
    assert (artifact_dir / "review.md").exists()


def test_edit_accept_and_reject_update_single_chapter_patch(tmp_path) -> None:
    project, _ = _project_with_draft(tmp_path)
    assert main(["edit", "review", str(project), "3", "--passes", "aiisms"]) == 0

    assert main(["edit", "accept", str(project), "3", "patch_001"]) == 0
    patch_path = project / "editing" / "chapter_03" / "draft_v2" / "patch_proposals.yaml"
    assert yaml.safe_load(patch_path.read_text(encoding="utf-8"))["patches"][0]["status"] == "accepted"

    assert main(["edit", "reject", str(project), "3", "patch_001"]) == 0
    assert yaml.safe_load(patch_path.read_text(encoding="utf-8"))["patches"][0]["status"] == "rejected"


def test_edit_apply_writes_revised_draft_without_overwriting_source(tmp_path) -> None:
    project, draft = _project_with_draft(tmp_path)
    original = draft.read_text(encoding="utf-8")
    assert main(["edit", "review", str(project), "3", "--passes", "aiisms"]) == 0
    assert main(["edit", "accept", str(project), "3", "patch_001"]) == 0

    exit_code = main(["edit", "apply", str(project), "3", "--patch", "patch_001"])

    revised = project / "editing" / "chapter_03" / "draft_v2" / "revised_draft.md"
    patch_path = project / "editing" / "chapter_03" / "draft_v2" / "patch_proposals.yaml"
    assert exit_code == 0
    assert revised.read_text(encoding="utf-8") == "The tower still carried old fear.\n"
    assert draft.read_text(encoding="utf-8") == original
    assert yaml.safe_load(patch_path.read_text(encoding="utf-8"))["patches"][0]["status"] == "applied"


def test_stale_edit_apply_exits_nonzero_and_does_not_write_revised_draft(tmp_path) -> None:
    project, draft = _project_with_draft(tmp_path)
    assert main(["edit", "review", str(project), "3", "--passes", "aiisms"]) == 0
    assert main(["edit", "accept", str(project), "3", "patch_001"]) == 0
    draft.write_text("The tower refused the old boast.\n", encoding="utf-8")

    exit_code = main(["edit", "apply", str(project), "3", "--patch", "patch_001"])

    artifact_dir = project / "editing" / "chapter_03" / "draft_v2"
    assert exit_code != 0
    assert not (artifact_dir / "revised_draft.md").exists()
    assert yaml.safe_load((artifact_dir / "patch_proposals.yaml").read_text(encoding="utf-8"))[
        "patches"
    ][0]["status"] == "stale"
