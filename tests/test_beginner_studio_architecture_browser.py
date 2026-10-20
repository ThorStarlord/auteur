"""Architecture Studio keeps generated candidates, genre phases and author notes distinct."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_architecture_views_and_agent_bridge_have_explicit_user_controls():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for name in (
        "architecture-develop", "architecture-refresh", "architecture-handoff",
        "architecture-complete", "architecture-instruction", "architecture-revise",
        "architecture-scope", "genre-timeline", "timeline-phases", "candidate-copy",
    ):
        assert f'id="{name}"' in html
    assert "/host-agent-response" in js and "/prepare" in js
    assert "AGENT CANDIDATE / NOT ACCEPTED" in js
    assert "working agent proposal" in js
    assert "phase.parallel_with" in js
    assert "scope === state.architectureFocus" in js
    assert "renderTimeline" in js


def test_studio_script_parses_and_references_existing_elements():
    script = (BROWSER / "studio.js").read_text(encoding="utf-8")
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    import re
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    unfolding = (BROWSER / "studio_unfolding_controller.js").read_text(encoding="utf-8")
    ids.update(re.findall(r"\.id\s*=\s*['\"]([^'\"]+)['\"]", unfolding))
    for referenced in re.findall(r'\$\("([^"]+)"\)', script):
        assert referenced in ids, referenced
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is unavailable; DOM IDs still checked")
    check = subprocess.run([node, "--check", str(BROWSER / "studio.js")],
                           text=True, capture_output=True, check=False)
    assert check.returncode == 0, check.stderr


def test_long_story_focus_is_reversible_and_does_not_mutate_story_authority():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert 'id="candidate-focus"' in html
    assert 'id="architecture-clear-focus"' in html
    assert "state.architectureCenter = state.selectedCandidate" in js
    assert "state.architectureCenter = null" in js
    assert "edge.source === center" in js
    assert "node.parent_id === center" in js
    assert "render(); fit(); rememberFocus();" in js


def test_parallel_genre_interactions_have_distinct_directed_graph_paths():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert 'createElementNS(svgNS, "path")' in js
    assert 'setAttribute("marker-end", "url(#architecture-genre-arrow)")' in js
    assert 'data-genre-interaction-id' in js
    assert "var pair = genreInteractions.filter" in js
    assert "var canonicalFrom = edge.source_genre_id < edge.target_genre_id ? from : to;" in js
    assert "pairIndex - (pair.length - 1) / 2" in js
