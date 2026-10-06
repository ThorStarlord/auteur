"""Read-only PRD re-entry contract, with real temporary story files."""
import hashlib
import json

from auteur.beginner import book_orientation as orientation


def chapter(root, index, prose="Kept prose.", *, draft=None, padded=True):
    path = root / "chapters" / (f"{index:02d}" if padded else str(index))
    path.mkdir(parents=True, exist_ok=True)
    if prose is not None:
        (path / "final.md").write_text(prose, encoding="utf-8")
    if draft is not None:
        (path / "draft_v2.md").write_text(draft, encoding="utf-8")
    return path


def receipt(root, index, prose, **overrides):
    path = root / ".auteur/beginner/reconciliation" / f"{index}-decision.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {
        "canonical": False, "chapter_index": index, "chapter_accepted": True,
        "candidate_sha256": hashlib.sha256(prose.encode()).hexdigest(),
        "status": "proposal_ready", "decision": "keep_and_reconcile",
        "proposal_items": [{"label": "Sister Beatrice", "value": "She matters going forward.",
                            "status": "proposed", "canonical": False,
                            "target_owner": "realization"}],
    }
    value.update(overrides)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_empty_book_has_a_working_first_chapter(tmp_path):
    result = orientation.project_book_orientation(tmp_path)
    assert result.current_chapter == 1
    assert result.current_chapter_state == "Working"
    assert result.next_story_action == "Write Chapter 1"
    assert result.recent_changes == ()
    assert snapshot(tmp_path) == {}


def test_completed_book_does_not_invent_an_extra_chapter(tmp_path):
    for index in range(1, 7):
        chapter(tmp_path, index)
    result = orientation.project_book_orientation(tmp_path, planned_chapters=6)
    assert result.current_chapter == 6
    assert result.current_chapter_state == "Kept"
    assert result.next_story_action == "Review your Book"
    assert result.next_action_chapter is None


def test_unaccepted_revision_does_not_erase_history(tmp_path):
    chapter(tmp_path, 1, "Old accepted history", draft="Working revision")
    result = orientation.project_book_orientation(tmp_path, planned_chapters=2)
    assert result.current_chapter == 1
    assert result.current_chapter_state == "Working"
    assert result.next_story_action == "Continue Chapter 1"
    assert result.recent_changes[0].state == "Kept"


def test_first_gap_and_numeric_order_not_lexical_order(tmp_path):
    chapter(tmp_path, 10, padded=False)
    chapter(tmp_path, 2, padded=False)
    result = orientation.project_book_orientation(tmp_path, planned_chapters=10)
    assert result.current_chapter == 1
    assert [item.chapter_index for item in result.recent_changes] == [10, 2]


def test_accepted_changes_use_only_real_accepted_chapters(tmp_path):
    chapter(tmp_path, 1)
    events = [
        {"chapter_index": 1, "summary": "Mara is Nia's sister."},
        {"chapter_index": 2, "summary": "An unaccepted future event."},
        {"chapter_index": True, "summary": "Invalid boolean chapter."},
    ]
    (tmp_path / "bible.json").write_text(json.dumps({"events": events}))
    result = orientation.project_book_orientation(tmp_path, planned_chapters=3)
    assert [item.summary for item in result.recent_changes] == ["Mara is Nia's sister."]
    assert result.recent_changes[0].source_ref == "bible.json#/events/0"


def test_compatible_pending_update_is_suggested_not_blocking(tmp_path):
    chapter(tmp_path, 1, "Beatrice appeared.")
    receipt(tmp_path, 1, "Beatrice appeared.")
    before = snapshot(tmp_path)
    result = orientation.project_book_orientation(tmp_path, planned_chapters=3)
    assert len(result.pending_updates) == 1
    assert result.pending_updates[0].state == "Suggested"
    assert result.pending_updates[0].summary == "Sister Beatrice: She matters going forward."
    assert not result.pending_updates[0].blocking
    assert result.current_chapter == 2
    assert result.next_story_action == "Write Chapter 2"
    assert snapshot(tmp_path) == before


def test_stale_receipt_is_attention_not_current_suggestion(tmp_path):
    chapter(tmp_path, 1, "Explicitly revised history.")
    receipt(tmp_path, 1, "Earlier accepted history.")
    result = orientation.project_book_orientation(tmp_path)
    assert result.pending_updates == ()
    assert result.needs_attention[0].state == "Needs attention"
    assert "changed" in result.needs_attention[0].summary.lower()
    assert not result.needs_attention[0].blocking


def test_intentional_divergence_and_resolved_items_are_not_pending(tmp_path):
    chapter(tmp_path, 1)
    receipt(tmp_path, 1, "Kept prose.", status="acknowledged_intentional_divergence")
    assert orientation.project_book_orientation(tmp_path).pending_updates == ()
    receipt(tmp_path, 1, "Kept prose.", proposal_items=[{
        "label": "Already handled", "status": "accepted", "canonical": False}])
    assert orientation.project_book_orientation(tmp_path).pending_updates == ()


def test_corrupt_evidence_is_visible_without_disabling_writing(tmp_path):
    (tmp_path / "bible.json").write_text("not json")
    chapter(tmp_path, 1)
    path = receipt(tmp_path, 1, "Kept prose.")
    path.write_text("{broken")
    result = orientation.project_book_orientation(tmp_path)
    assert len(result.needs_attention) == 2
    assert all(not item.blocking for item in result.needs_attention)
    assert result.next_story_action == "Write Chapter 2"


def test_duplicate_receipts_do_not_duplicate_updates(tmp_path):
    chapter(tmp_path, 1)
    path = receipt(tmp_path, 1, "Kept prose.")
    path.with_name("1-retry.json").write_bytes(path.read_bytes())
    assert len(orientation.project_book_orientation(tmp_path).pending_updates) == 1


def test_recent_history_is_bounded_and_remains_retrievable(tmp_path):
    for index in range(1, 9):
        chapter(tmp_path, index)
    result = orientation.project_book_orientation(tmp_path, planned_chapters=9)
    assert len(result.recent_changes) == 5
    assert len(result.accepted_chapter_refs) == 8
    assert result.recent_changes[0].chapter_index == 8


def test_non_json_mapping_has_a_visible_evidence_warning(tmp_path):
    (tmp_path / "bible.json").write_text("[]")
    result = orientation.project_book_orientation(tmp_path)
    assert result.needs_attention


def test_working_chapter_beyond_old_plan_is_not_lost(tmp_path):
    chapter(tmp_path, 1)
    chapter(tmp_path, 2)
    chapter(tmp_path, 4, prose=None, draft="New working Chapter")
    result = orientation.project_book_orientation(tmp_path, planned_chapters=2)
    assert result.current_chapter == 4
    assert result.next_story_action == "Continue Chapter 4"
