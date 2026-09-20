import json
from pathlib import Path

import pytest

from auteur.beginner.post_draft import (
    ChapterProductionStatus,
    accept_latest_chapter,
    prepare_revision_handoff,
    project_draft_review,
)


def _chapter(root: Path, index: int = 1) -> Path:
    chapter = root / "chapters" / f"{index:02d}"
    chapter.mkdir(parents=True, exist_ok=True)
    return chapter


def test_review_selects_latest_matching_evidence_and_preserves_candidate_authority(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("old", encoding="utf-8")
    (chapter / "draft_v2.md").write_text("new", encoding="utf-8")
    (chapter / "validation_v2.json").write_text(
        json.dumps({"findings": [{"severity": "WARNING", "message": "check continuity"}]}),
        encoding="utf-8",
    )

    review = project_draft_review(tmp_path, 1)

    assert review.production_status is ChapterProductionStatus.CANDIDATE_DRAFT
    assert review.source_draft == "draft_v2.md"
    assert review.review_artifact == "validation_v2.json"
    assert review.warnings == ["check continuity"]
    assert not (chapter / "final.md").exists()


def test_review_marks_blocking_findings_as_revision_required(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    (chapter / "validation_v1.json").write_text(
        json.dumps({"findings": [{"severity": "ERROR", "message": "continuity break"}]}),
        encoding="utf-8",
    )

    review = project_draft_review(tmp_path, 1)

    assert review.production_status is ChapterProductionStatus.REVISION_REQUIRED
    assert review.blocking_findings == ["continuity break"]


def test_acceptance_delegates_once_and_reconciles_replay(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    calls: list[int] = []

    def owner(root: Path, index: int) -> object:
        calls.append(index)
        (root / "chapters" / "01" / "final.md").write_text("candidate", encoding="utf-8")
        return {"accepted": True}

    first = accept_latest_chapter(tmp_path, 1, command_id="cmd-1", owner=owner)
    replay = accept_latest_chapter(tmp_path, 1, command_id="cmd-1", owner=owner)

    assert first.reconciled is False
    assert replay.reconciled is True
    assert calls == [1]


def test_acceptance_reconciles_owner_crash_without_replaying_authority(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    calls = 0

    def owner(root: Path, index: int) -> object:
        nonlocal calls
        calls += 1
        (root / "chapters" / "01" / "final.md").write_text("candidate", encoding="utf-8")
        raise RuntimeError("crash after authority")

    with pytest.raises(RuntimeError):
        accept_latest_chapter(tmp_path, 1, command_id="cmd-crash", owner=owner)

    replay = accept_latest_chapter(tmp_path, 1, command_id="cmd-crash", owner=owner)

    assert replay.reconciled is True
    assert calls == 1


def test_revision_handoff_is_noncanonical_and_routes_only(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")

    handoff = prepare_revision_handoff(
        tmp_path,
        1,
        command_id="revise-1",
        decision="repair continuity",
        route="retry",
    )

    payload = json.loads(handoff.path.read_text(encoding="utf-8"))
    assert payload["canonical"] is False
    assert payload["source_draft"] == "draft_v1.md"
    assert not (chapter / "final.md").exists()


def test_newer_candidate_after_prior_acceptance_is_not_projected_as_accepted(tmp_path: Path) -> None:
    chapter = _chapter(tmp_path)
    (chapter / "final.md").write_text("accepted v1", encoding="utf-8")
    (chapter / "draft_v1.md").write_text("accepted v1", encoding="utf-8")
    (chapter / "draft_v2.md").write_text("new candidate", encoding="utf-8")
    (chapter / "validation_v2.json").write_text(json.dumps({"findings": []}), encoding="utf-8")

    review = project_draft_review(tmp_path, 1)

    assert review.accepted is False
    assert review.production_status is ChapterProductionStatus.CANDIDATE_DRAFT
    assert review.source_draft == "draft_v2.md"
