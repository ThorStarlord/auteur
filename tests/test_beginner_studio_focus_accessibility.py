"""Studio supports keyboard and nonspatial search/focus without changing canon."""
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_accessible_outline_search_and_keyboard_pan():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert 'id="outline-list"' in html
    assert 'id="find-nodes"' in html
    assert 'id="group"' in html
    assert "renderOutline()" in js
    assert 'addEventListener("keydown"' in js
    assert "matches(" in js


def test_working_groups_are_only_working_item_metadata():
    from auteur.beginner.studio_store import CanvasItem
    note = CanvasItem(id="first", title="Idea", group="Act 1")
    assert note.group == "Act 1"
    assert not hasattr(note, "accepted")
