"""Studio source evidence is projected without becoming editable working notes."""
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_studio_has_separate_derived_evidence_inspector():
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    assert "/api/beginner/studio/graph" in js
    assert "source-detail" in html and "source-ref" in html
    assert 'node.className = "node derived"' in js
    assert "state.derivedPositions" in js
    assert "renderInspector()" in js
    assert "Working notes are unchanged" in js
