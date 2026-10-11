"""Realization UI is distinct from the abstract architecture and honors ownership."""
from pathlib import Path
import re
import shutil
import subprocess

import pytest

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_realization_handoff_and_working_graph_controls():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for name in (
        "realization-tools", "realization-develop", "realization-refresh",
        "realization-handoff", "realization-complete", "realization-revise",
        "realization-review", "realization-apply", "realization-copy",
        "realization-inspect", "realization-feedback",
    ):
        assert f'id="{name}"' in html
    assert "function requestRealization" in js
    assert "function applyRealizationProjection" in js
    assert '"/realization"' in js
    assert "realization_candidates" in js


def test_concrete_proposals_explain_architecture_and_cannot_accept_canon():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert "architecture_refs" in js
    assert "STORY REALIZATION PROPOSAL / NOT ACCEPTED" in js
    assert "function inspectRealizationPurpose" in js
    assert "function proposeArchitectureFromRealization" in js
    assert "requestArchitecture(" in js
    assert "Copy as editable story idea" in (
        BROWSER / "studio.html"
    ).read_text(encoding="utf-8")


def test_realization_scripts_have_valid_syntax_and_real_dom_ids():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'\$\("([^"]+)"\)', js)) <= set(ids)
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    checked = subprocess.run([node, "--check", str(BROWSER / "studio.js")],
                             capture_output=True, text=True, check=False)
    assert checked.returncode == 0, checked.stderr


def test_cross_workflow_revision_guard_and_emotional_diff_visibility():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for field in ("emotion_targets", "complex_emotions", "genre_contracts", "genre_interactions"):
        assert field in js
    assert "state.realizationStale" in js
    assert "Concrete proposal is stale" in js
    assert "remote.canvasId !== canvasId" in js
    assert "function applyRealizationReview" in js
    assert "requestArchitecture(" in js
