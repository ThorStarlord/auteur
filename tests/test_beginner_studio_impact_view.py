"""Studio impact view is read-only and grounded in existing artifacts."""
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_impact_view_is_not_story_mutation():
    source = (BROWSER / "studio.js").read_text(encoding="utf-8")
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    assert "/api/beginner/studio/impact" in source
    assert 'state.view = "impact"' in source
    assert "Hypothetical dependency paths only" in source
    assert "Nothing has been revised or accepted" in source
    assert 'value="impact"' in html
    assert "Registered artifact ID" in html
