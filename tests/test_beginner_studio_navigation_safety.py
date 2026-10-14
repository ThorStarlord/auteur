"""Development-default Studio retains a safe route to guided legacy authorship.

The browser execution gate (#360) must still confirm navigation under real
HTTP/failure conditions; this test anchors the relevant source contract.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_guided_quick_draft_always_uses_legacy_route():
    script = (ROOT / "studio.js").read_text(encoding="utf-8")
    page = (ROOT / "studio.html").read_text(encoding="utf-8")
    assert '"/beginner.html?quick_draft="' in script
    assert 'href="/beginner.html"' in page
    assert 'id="legacy-home"' in page
    assert 'id="open-quick-draft"' in page


def test_unsaved_changes_block_unflushed_navigation():
    script = (ROOT / "studio.js").read_text(encoding="utf-8")
    assert "function hasUnsavedChanges()" in script
    assert "function leaveForLegacy(href)" in script
    assert "remote.savedSnapshot !== JSON.stringify(snapshot())" in script
    assert 'addEventListener("beforeunload"' in script
    assert 'event.preventDefault()' in script
    assert 'Promise.resolve(remote.queue)' in script
    assert "window.location.assign(href)" in script
