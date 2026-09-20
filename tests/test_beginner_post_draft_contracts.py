import json
from pathlib import Path

from auteur.beginner.post_draft import (
    ChapterProductionStatus,
    DraftReviewProjection,
    project_draft_review,
)


def _chapter(tmp_path: Path) -> Path:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    return chapter


def test_candidate_draft_is_not_an_accepted_chapter(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.production_status is ChapterProductionStatus.CANDIDATE_DRAFT
    assert projection.source_draft == "draft_v1.md"
    assert projection.accepted is False


def test_final_is_the_only_artifact_that_projects_as_accepted(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    (chapter / "final.md").write_text("accepted", encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.production_status is ChapterProductionStatus.ACCEPTED
    assert projection.accepted is True


def test_latest_draft_and_matching_validation_are_selected(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("old", encoding="utf-8")
    (chapter / "draft_v2.md").write_text("new", encoding="utf-8")
    (chapter / "validation_v1.json").write_text(json.dumps({"findings": [{"severity": "ERROR", "message": "old"}]}), encoding="utf-8")
    (chapter / "validation_v2.json").write_text(json.dumps({"findings": [{"severity": "WARNING", "message": "new"}]}), encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.draft_version == 2
    assert projection.review_artifact == "validation_v2.json"
    assert projection.blocking_findings == []
    assert projection.warnings == ["new"]


def test_malformed_review_artifact_is_explicitly_unavailable(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    (chapter / "validation_v1.json").write_text("not json", encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.review_available is False
    assert "invalid" in projection.review_error.lower()


def test_upstream_fingerprint_makes_review_stale(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (tmp_path / "blueprint.yaml").write_text("version: 2", encoding="utf-8")
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    (chapter / "draft_v1.meta.json").write_text(json.dumps({"upstream_fingerprint": "old"}), encoding="utf-8")

    projection = project_draft_review(tmp_path, 1)

    assert projection.production_status is ChapterProductionStatus.STALE
    assert projection.stale is True


def test_projection_does_not_call_a_provider(tmp_path: Path) -> None:
    _chapter(tmp_path)
    projection = project_draft_review(tmp_path, 1)
    assert isinstance(projection, DraftReviewProjection)
