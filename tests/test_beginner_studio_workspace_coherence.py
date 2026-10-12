"""Studio keeps action bars and inspector content scoped to the visible workspace."""
from pathlib import Path
import re

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_hidden_workflow_sections_override_flex_display():
    css = (BROWSER / "studio.css").read_text(encoding="utf-8")
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert re.search(r"\[hidden\]\s*\{\s*display\s*:\s*none\s*!important", css)
    assert 'id="realization-tools" class="architecture-actions" hidden' in html
    assert '$("architecture-tools").hidden = !designing;' in js
    assert '$("realization-tools").hidden = designing;' in js


def test_inspector_does_not_fall_through_to_hidden_story_vision():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    inspector = js.split("function renderInspector()", 1)[1].split("function choose(", 1)[0]
    assert 'state.workspace === "architecture" && state.view === "architecture"' in inspector
    assert 'state.workspace === "realization" ? selected() : null' in inspector
    assert 'if (item && !visibleWorking(item)) item = null;' in inspector
    assert 'if (proposal && !candidateVisible(proposal)) proposal = null;' in inspector
    assert 'if (source && (!visibleDerived(source) || !matches(source))) source = null;' in inspector
    assert '$("source-detail").hidden = !source && !proposal && !concrete;' in inspector


def test_explicit_working_item_creation_moves_to_realization_workspace():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    for name, end in [("function copyCandidate()", "function loadRemote()"),
                      ("function newItem(kind)", "function changedRelationVisible(")]:
        code = js.split(name, 1)[1].split(end, 1)[0]
        assert 'state.workspace = "realization"; state.lastRealizationView = "create";' in code
