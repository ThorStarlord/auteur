"""Regression tests for Version 1.0 Layer-3 realization debt closure."""

from pathlib import Path

from auteur.narrative_realization.orchestrator.scene_inspector import SceneInspector
from auteur.narrative_realization.schema import ArcBeatRealization, SceneOutline, SceneStatus


LEGACY_XFAIL_REASON = (
    "SceneOutline schema requires goal field; "
    "Layer 3 narrative_realization documented as Partial"
)


def test_inspector_arc_beat_coverage_uses_current_scene_contract() -> None:
    """Inspector must read the canonical SceneOutline realizes_arc_beats field."""
    scene = SceneOutline(
        id="scene_01_01",
        chapter_id="chapter_01",
        status=SceneStatus.DRAFT,
        realizes_arc_beats=[ArcBeatRealization(beat_id="beat_truth", degree="partial")],
    )
    inspector = SceneInspector()
    inspector.add_scene(scene)

    report = inspector.show_arc_beat_coverage()

    assert "beat_truth" in report
    assert "realized in 1 scene" in report


def test_legacy_scene_outline_xfail_workaround_is_removed() -> None:
    """V1 must not grandfather the blanket Layer-3 Partial xfail workaround."""
    tests_dir = Path(__file__).parent
    debt_files = (
        tests_dir / "test_realization_cli.py",
        tests_dir / "test_realization_knowledge.py",
        tests_dir / "test_realization_temporal.py",
    )

    remaining = [
        path.name
        for path in debt_files
        if LEGACY_XFAIL_REASON in path.read_text(encoding="utf-8-sig")
    ]

    assert remaining == [], f"legacy Layer-3 xfail workaround remains in: {remaining}"
