from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_status_records_current_beginner_package_and_human_evidence() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    design = (ROOT / "docs/design/2026-09-beginner-story-development-continuation.md").read_text(
        encoding="utf-8"
    )

    assert "BEGINNER NARRATIVE-ARCHITECTURE COHERENCE" in status
    assert "L3" in status
    assert "human" in status.lower()
    assert "Structure → Realization" in design
    assert "canonical" in design.lower()
