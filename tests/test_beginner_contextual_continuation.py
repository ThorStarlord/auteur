import json
from pathlib import Path

from auteur.beginner.continuation import (
    ChapterContinuationState,
    build_contextual_chapter_plan,
    build_contextual_scene_plans,
)


def _accepted_chapter(root: Path, index: int) -> Path:
    chapter = root / "chapters" / f"{index:02d}"
    chapter.mkdir(parents=True, exist_ok=True)
    (chapter / "final.md").write_text("accepted", encoding="utf-8")
    return chapter


def test_contextual_plan_uses_accepted_prior_state(tmp_path: Path) -> None:
    _accepted_chapter(tmp_path, 1)
    chapter_two = tmp_path / "chapters" / "02"
    chapter_two.mkdir()
    (chapter_two / "outline.yaml").write_text(
        "chapter_index: 2\nchapter_summary: confront the hidden witness\n",
        encoding="utf-8",
    )
    (tmp_path / "bible.json").write_text(
        json.dumps(
            {
                "events": [
                    {
                        "chapter_index": 1,
                        "summary": "Maya trusts Elias",
                        "deltas": {"trust": "partial"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    plan = build_contextual_chapter_plan(tmp_path, 2)

    assert isinstance(plan.continuation, ChapterContinuationState)
    assert plan.continuation.current_chapter_index == 2
    assert plan.intended_role == "confront the hidden witness"
    assert plan.context["accepted_prior_state"][0]["summary"] == "Maya trusts Elias"
    assert plan.draft_handoff_ready is True


def test_contextual_plan_reports_structure_divergence_without_rewrite(tmp_path: Path) -> None:
    prior = _accepted_chapter(tmp_path, 1)
    (prior / "outline.yaml").write_text(
        "chapter_index: 1\nexpected_state:\n  trust: none\n",
        encoding="utf-8",
    )
    (tmp_path / "bible.json").write_text(
        json.dumps(
            {
                "events": [
                    {
                        "chapter_index": 1,
                        "summary": "trust changed",
                        "deltas": {"trust": "partial"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    plan = build_contextual_chapter_plan(tmp_path, 2)

    assert plan.divergences == (
        {
            "field": "trust",
            "planned": "none",
            "accepted": "partial",
            "recommendation": "adapt the next chapter to the accepted state",
        },
    )
    assert "trust: none" in (prior / "outline.yaml").read_text(encoding="utf-8")


def test_contextual_scene_plans_keep_chapter_ownership(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "03"
    chapter.mkdir(parents=True)
    (chapter / "outline.yaml").write_text(
        "chapter_index: 3\nscenes:\n"
        "  - id: opening\n    purpose: pressure\n"
        "  - id: turn\n    purpose: reveal\n",
        encoding="utf-8",
    )

    scenes = build_contextual_scene_plans(tmp_path, 3)

    assert [(scene.chapter_index, scene.scene_id) for scene in scenes] == [
        (3, "opening"),
        (3, "turn"),
    ]
