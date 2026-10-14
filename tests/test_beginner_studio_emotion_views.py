"""The v2 emotion-first projection remains a noncanonical architecture UI."""
from __future__ import annotations

import re
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_distinct_workspaces_and_emotional_contract_controls():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for control in (
        "workspace-architecture", "workspace-realization", "emotional-design",
        "emotional-targets", "genre-contract-detail",
    ):
        assert f'id="{control}"' in html
    assert "switchWorkspace" in js
    assert "state.workspace" in js
    assert "state.lastRealizationView" in js
    assert "rememberFocus()" in js


def test_v2_genres_display_mechanisms_and_emotions_not_concrete_plot():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for term in (
        "emotion_target_ids", "complex_emotion_ids", "trope_functions",
        "narrative_engine", "structural_pattern", "payoff_expectations",
        "eliciting_condition", "aesthetic_strategy", "genre_interactions",
        "genre_activations", "basic_emotions",
    ):
        assert term in js
    assert "state.architecture" in js
    assert "AGENT CANDIDATE / NOT ACCEPTED" in js
    assert "copyCandidate" in js


def test_script_references_real_controls_and_no_duplicate_ids():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    unfolding = (BROWSER / "studio_unfolding_controller.js").read_text(encoding="utf-8")
    dynamic_ids = set(re.findall(r"\.id\s*=\s*['\"]([^'\"]+)['\"]", unfolding))
    assert set(re.findall(r'\$\("([^"]+)"\)', js)) <= set(ids) | dynamic_ids
