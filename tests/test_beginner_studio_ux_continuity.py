"""Navigation continuity: focus is presentation state, never accepted story state."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_cross_section_trace_has_source_linked_navigation_and_return():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    inspector = js.split("function renderInspector()", 1)[1].split("function choose(", 1)[0]
    for text in (
        'jump("Explore emotion: "', 'jump("Explore composition: "',
        'jump("Explore trope function: "', 'jump("Explore narrative engine", "structure"',
        'jump("Explore structural pattern", "structure"', 'visitFacet("genres", null, other.id)',
    ):
        assert text in inspector
    assert 'function renderFacetInspector(entry)' in js
    assert 'Genre-level emotional targets (not a claim that this individual trope' in js
    assert 'function renderPhaseInspector(phase)' in js


def test_focus_restoration_does_not_serialize_facet_as_story_content():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    snapshot = js.split("function snapshot()", 1)[1].split("function queueSave()", 1)[0]
    assert "facet" not in snapshot and "selectedPhase" not in snapshot
    assert "function rememberFocus()" in js and "function restoreFocus()" in js
    assert 'phase: state.selectedPhase, search: $("find-nodes").value' in js
    assert 'state.lastWorkingSelection = state.selected;' in js
    assert 'if (!state.selected && state.items.some(' in js
    assert 'state.facetHistory.push({facet:state.architectureFacet' in js
    assert 'scope:state.architectureFocus, center:state.architectureCenter, phase:state.selectedPhase' in js
    assert '$("find-nodes").value = old.search || "";' in js
    assert 'if (state.selectedCandidate && !candidateNode(state.selectedCandidate))' in js
    assert 'state.facetHistory = state.facetHistory.filter(function (old)' in js


def test_http_studio_assets_expose_architecture_controls_without_duplicate_ids(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        url = f"http://127.0.0.1:{server.port}"
        with urlopen(url + "/studio.html") as response:
            assert response.status == 200
            html = response.read().decode("utf-8")
        with urlopen(url + "/studio.js") as response:
            assert response.status == 200
            script = response.read().decode("utf-8")
        for name in ("architecture-work-area", "architecture-facet-panel", "architecture-facet-back",
                     "vision-preview", "genre-timeline", "timeline-phases", "architecture-legend"):
            assert f'id="{name}"' in html
        ids = re.findall(r'\bid="([^"]+)"', html)
        assert len(ids) == len(set(ids))
        assert set(re.findall(r'\$\("([^"]+)"\)', script)) <= set(ids)
        assert 'SOURCE-LINKED PROPOSAL / NOT ACCEPTED' in script
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
