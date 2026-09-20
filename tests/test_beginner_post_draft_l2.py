import json
from pathlib import Path

from auteur.beginner.continuation import build_chapter_plan
from auteur.beginner.post_draft import (
    accept_latest_chapter,
    prepare_revision_handoff,
    project_chapter_outcome,
    project_draft_review,
)


def test_chapter_one_acceptance_closes_into_contextual_chapter_two_plan(tmp_path: Path) -> None:
    chapter_one = tmp_path / "chapters" / "01"
    chapter_one.mkdir(parents=True)
    (chapter_one / "outline.yaml").write_text(
        "chapter_index: 1\nexpected_state:\n  trust: none\n", encoding="utf-8"
    )
    (chapter_one / "draft_v1.md").write_text("Scene one", encoding="utf-8")
    (chapter_one / "validation_v1.json").write_text(
        json.dumps({"findings": [{"severity": "ERROR", "message": "continuity"}]}), encoding="utf-8"
    )

    review = project_draft_review(tmp_path, 1)
    handoff = prepare_revision_handoff(
        tmp_path, 1, command_id="l2-revision", decision=review.recommended_next_action, route="retry"
    )
    (chapter_one / "draft_v2.md").write_text("Scene one revised", encoding="utf-8")
    calls: list[int] = []

    def owner(root: Path, index: int) -> object:
        calls.append(index)
        (root / "chapters" / "01" / "final.md").write_text("Scene one revised", encoding="utf-8")
        (root / "bible.json").write_text(
            json.dumps({"events": [{"chapter_index": 1, "summary": "trust changed", "deltas": {"trust": "partial"}}]}),
            encoding="utf-8",
        )
        return {"accepted": True}

    accepted = accept_latest_chapter(tmp_path, 1, command_id="l2-accept", owner=owner)
    replay = accept_latest_chapter(tmp_path, 1, command_id="l2-accept", owner=owner)
    outcome = project_chapter_outcome(tmp_path, 1)
    plan = build_chapter_plan(tmp_path, 2)

    assert review.production_status.value == "revision_required"
    assert handoff.route == "retry"
    assert accepted.reconciled is False
    assert replay.reconciled is True
    assert calls == [1]
    assert outcome["accepted_expression"] == "final.md"
    assert plan.context["accepted_prior_state"][0]["deltas"]["trust"] == "partial"
    assert plan.divergences[0]["field"] == "trust"
