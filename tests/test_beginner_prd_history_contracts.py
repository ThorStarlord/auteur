"""Regression contracts for accepted prose, review evidence, and author consent."""

import hashlib
import json
from pathlib import Path

import pytest

from auteur.beginner.post_draft import (
    ChapterProductionStatus,
    accept_latest_chapter,
    project_chapter_outcome,
    project_draft_review,
    project_next_chapter_context,
)


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }


@pytest.mark.parametrize("directory", ["02", "2"])
def test_final_only_chapter_remains_readable_without_new_acceptance(
    tmp_path: Path, directory: str,
) -> None:
    _write(tmp_path, f"chapters/{directory}/final.md", "The kept chapter.")
    before = _snapshot(tmp_path)

    review = project_draft_review(tmp_path, 2)

    assert review.draft_text == "The kept chapter."
    assert review.accepted is True
    assert review.production_status is ChapterProductionStatus.ACCEPTED
    assert review.source_draft is None
    assert review.draft_version is None
    assert review.revision_options == []
    assert review.creative_discoveries == []
    assert review.reconciliation_available is False
    assert _snapshot(tmp_path) == before


def test_outcome_points_to_the_actual_unpadded_accepted_file(tmp_path: Path) -> None:
    _write(tmp_path, "chapters/2/final.md", "Kept history.")
    before = _snapshot(tmp_path)

    outcome = project_chapter_outcome(tmp_path, 2)

    assert outcome["source_refs"] == ["chapters/2/final.md"]
    assert (tmp_path / outcome["source_refs"][0]).read_text() == "Kept history."
    assert _snapshot(tmp_path) == before


def test_prior_chapters_are_numeric_and_exclude_current_future_and_working_prose(
    tmp_path: Path,
) -> None:
    for index in [1, 2, 10, 11, 12]:
        _write(tmp_path, f"chapters/{index}/final.md", f"Kept {index}")
    _write(tmp_path, "chapters/3/draft_v1.md", "Working, not kept.")
    _write(tmp_path, "chapters/2/draft_v2.md", "Unaccepted replacement.")
    _write(tmp_path, "bible.json", '{"events": [], "notes": "preserve existing state"}')
    before = _snapshot(tmp_path)

    context = project_next_chapter_context(tmp_path, 11)

    assert context["prior_accepted_chapters"] == [1, 2, 10]
    assert [ref["path"] for ref in context["prior_chapter_refs"]] == [
        "chapters/1/final.md", "chapters/2/final.md", "chapters/10/final.md",
    ]
    assert context["realized_state"]["notes"] == "preserve existing state"
    assert _snapshot(tmp_path) == before


def test_history_uses_the_existing_padded_owner_precedence_once(tmp_path: Path) -> None:
    _write(tmp_path, "chapters/2/final.md", "Legacy path.")
    _write(tmp_path, "chapters/02/final.md", "Preferred path.")

    context = project_next_chapter_context(tmp_path, 3)

    assert context["prior_accepted_chapters"] == [2]
    assert context["prior_chapter_refs"] == [
        {"chapter_index": 2, "path": "chapters/02/final.md"},
    ]
    assert project_chapter_outcome(tmp_path, 2)["source_refs"] == [
        context["prior_chapter_refs"][0]["path"],
    ]


def test_history_ignores_nonfiles_and_unaddressable_chapter_directories(tmp_path: Path) -> None:
    _write(tmp_path, "chapters/00/final.md", "Not a positive Chapter.")
    _write(tmp_path, "chapters/001/final.md", "Unsupported alias.")
    _write(tmp_path, "chapters/notes/final.md", "Not a Chapter.")
    (tmp_path / "chapters/01/final.md").mkdir(parents=True)
    _write(tmp_path, "chapters/2/final.md", "Kept.")

    assert project_next_chapter_context(tmp_path, 3)["prior_accepted_chapters"] == [2]


@pytest.mark.parametrize("status", ["started", "complete"])
@pytest.mark.parametrize("change", ["bytes", "version"])
def test_replayed_acceptance_never_transfers_consent_to_a_changed_draft(
    tmp_path: Path, status: str, change: str,
) -> None:
    draft = _write(tmp_path, "chapters/01/draft_v1.md", "Original")
    _write(tmp_path, "chapters/01/final.md", "Original")
    _write(tmp_path, ".auteur/beginner/acceptance/1-keep.json", json.dumps({
        "status": status, "chapter_index": 1, "command_id": "keep",
        "candidate": draft.name,
        "candidate_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
        "authority_result": {"accepted": True},
    }))
    if change == "bytes":
        draft.write_text("Changed without a new keep action.", encoding="utf-8")
    else:
        _write(tmp_path, "chapters/01/draft_v2.md", "Original")
    before = _snapshot(tmp_path)
    calls = []

    def owner(root: Path, index: int) -> None:
        calls.append(index)

    with pytest.raises(ValueError, match="different draft"):
        accept_latest_chapter(tmp_path, 1, command_id="keep", owner=owner)

    assert calls == []
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("final_text", [None, "A different accepted version"])
def test_completed_receipt_does_not_claim_missing_or_replaced_output_is_current(
    tmp_path: Path, final_text: str | None,
) -> None:
    draft = _write(tmp_path, "chapters/01/draft_v1.md", "Original")
    _write(tmp_path, ".auteur/beginner/acceptance/1-keep.json", json.dumps({
        "status": "complete", "chapter_index": 1, "command_id": "keep",
        "candidate": draft.name,
        "candidate_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
    }))
    if final_text is not None:
        _write(tmp_path, "chapters/01/final.md", final_text)
    before = _snapshot(tmp_path)

    with pytest.raises(ValueError, match="accepted chapter no longer matches"):
        accept_latest_chapter(tmp_path, 1, command_id="keep")

    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("metadata", [
    "{broken", "null", "[]", '{"candidate_sha256": null}',
    '{"candidate_sha256": ""}', '{"candidate_sha256": []}',
])
def test_invalid_review_metadata_never_presents_unverified_findings_as_current(
    tmp_path: Path, metadata: str,
) -> None:
    _write(tmp_path, "chapters/01/draft_v1.md", "The unchanged draft.")
    _write(tmp_path, "chapters/01/draft_v1.meta.json", metadata)
    _write(tmp_path, "chapters/01/validation_v1.json", json.dumps({"findings": [
        {"severity": "ERROR", "message": "Unverified blocker"},
        {"severity": "WARNING", "message": "Unverified warning"},
    ]}))
    before = _snapshot(tmp_path)

    review = project_draft_review(tmp_path, 1)

    assert review.review_available is False
    assert review.review_stale is True
    assert review.blocking_findings == []
    assert review.warnings == []
    assert "metadata" in review.review_error.lower()
    assert _snapshot(tmp_path) == before


def test_missing_metadata_keeps_legacy_review_behavior(tmp_path: Path) -> None:
    _write(tmp_path, "chapters/01/draft_v1.md", "Legacy draft.")
    _write(tmp_path, "chapters/01/validation_v1.json", '{"findings": []}')

    review = project_draft_review(tmp_path, 1)

    assert review.review_available is True
    assert review.review_stale is False
    assert review.accepted is False


def test_valid_fingerprint_preserves_current_review_findings(tmp_path: Path) -> None:
    draft = _write(tmp_path, "chapters/01/draft_v1.md", "Current draft.")
    _write(tmp_path, "chapters/01/draft_v1.meta.json", json.dumps({
        "candidate_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
    }))
    _write(tmp_path, "chapters/01/validation_v1.json", json.dumps({"findings": [
        {"severity": "WARNING", "message": "A current observation"},
    ]}))

    review = project_draft_review(tmp_path, 1)

    assert review.review_available is True
    assert review.review_stale is False
    assert review.warnings == ["A current observation"]


def test_new_keep_decision_can_accept_a_changed_draft(tmp_path: Path) -> None:
    draft = _write(tmp_path, "chapters/01/draft_v1.md", "Original")
    calls = []

    def owner(root: Path, index: int) -> dict[str, bool]:
        calls.append(index)
        (root / "chapters/01/final.md").write_bytes(draft.read_bytes())
        return {"accepted": True}

    accept_latest_chapter(tmp_path, 1, command_id="keep-1", owner=owner)
    draft.write_text("Deliberately revised.", encoding="utf-8")
    accept_latest_chapter(tmp_path, 1, command_id="keep-2", owner=owner)

    assert calls == [1, 1]
    assert project_draft_review(tmp_path, 1).accepted is True
    assert (tmp_path / "chapters/01/final.md").read_text() == "Deliberately revised."
