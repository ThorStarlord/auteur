from __future__ import annotations

from pathlib import Path

from auteur.editing.passes.aiisms import run_aiism_pass


def test_aiism_detector_finds_known_phrase_and_patch_suggestion() -> None:
    text = "The ruined tower stood as a testament to forgotten power.\n"

    findings, patches = run_aiism_pass(text, source_file=Path("chapters/03/draft_v2.md"))

    assert len(findings) == 1
    assert findings[0].evidence == "stood as a testament to"
    assert findings[0].location.start_line == 1
    assert patches[0].original == "stood as a testament to"
    assert patches[0].replacement == "still carried"
    assert patches[0].status.value == "proposed"


def test_aiism_detector_allows_findings_without_safe_patch_suggestions() -> None:
    text = "A whisper of regret moved through the hall.\n"

    findings, patches = run_aiism_pass(text, source_file=Path("chapters/03/draft_v2.md"))

    assert [finding.evidence for finding in findings] == ["a whisper of"]
    assert patches == []


def test_aiism_detector_returns_no_findings_for_clean_prose() -> None:
    findings, patches = run_aiism_pass(
        "Rain ticked on the skylight while Mara counted the exits.\n",
        source_file=Path("chapters/03/draft_v2.md"),
    )

    assert findings == []
    assert patches == []


def test_aiism_detector_uses_stable_ids_and_distinct_line_ranges() -> None:
    text = (
        "The arch stood as a testament to old kings.\n"
        "Mara waited.\n"
        "The tower stood as a testament to bad decisions.\n"
    )

    findings, patches = run_aiism_pass(text, source_file=Path("chapters/03/draft_v2.md"))

    assert [finding.id for finding in findings] == ["finding_001", "finding_002"]
    assert [finding.location.start_line for finding in findings] == [1, 3]
    assert [patch.id for patch in patches] == ["patch_001", "patch_002"]
