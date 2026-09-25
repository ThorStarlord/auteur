from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_status_records_current_beginner_package_and_human_evidence() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    design = (ROOT / "docs/design/2026-09-beginner-story-development-continuation.md").read_text(
        encoding="utf-8"
    )

    assert "CURRENT_MAIN_BEGINNER_COHERENCE_RECONCILIATION" in status
    assert "Beginner Narrative-Architecture Coherence" in status
    assert "L3" in status
    assert "human" in status.lower()
    assert "Structure → Realization" in design
    assert "canonical" in design.lower()
