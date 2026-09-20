import json
from pathlib import Path

from auteur.beginner.post_draft import project_draft_review


def test_alignment_reports_planned_and_observed_scene_counts(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "02"
    chapter.mkdir(parents=True)
    (chapter / "outline.yaml").write_text(
        "chapter_index: 2\nchapter_summary: pressure\nscenes:\n  - id: one\n  - id: two\n",
        encoding="utf-8",
    )
    (chapter / "draft_v1.md").write_text("Scene one\n", encoding="utf-8")
    (chapter / "validation_v1.json").write_text(json.dumps({"findings": []}), encoding="utf-8")

    projection = project_draft_review(tmp_path, 2)

    assert projection.plan_alignment["planned_scene_count"] == 2
    assert projection.plan_alignment["observed_scene_count"] == 1
    assert projection.recommended_next_action


def test_missing_plan_remains_unknown_instead_of_guessing(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.plan_alignment["status"] == "unknown"
    assert projection.plan_alignment["reason"] == "chapter plan unavailable"
