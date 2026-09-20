from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_status_selects_beginner_story_development_continuation() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    design = (ROOT / "docs/design/2026-09-beginner-story-development-continuation.md").read_text(
        encoding="utf-8"
    )

    assert "BEGINNER STORY DEVELOPMENT CONTINUATION" in status
    assert "L3" in status
    assert "human qualification" in status.lower()
    assert "Structure → Realization" in design
    assert "canonical" in design.lower()
