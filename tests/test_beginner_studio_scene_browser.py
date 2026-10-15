"""Studio scene writing uses existing Quick Draft API without silent canon."""
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_scene_editor_explicitly_requests_generation_from_existing_endpoint():
    js = (HERE / "studio.js").read_text(encoding="utf-8")
    html = (HERE / "studio.html").read_text(encoding="utf-8")
    assert "/api/beginner/quick-draft" in js
    assert "awaiting_host_agent" in js
    assert "scene-premise" in html and "scene-intent" in html
    assert "Copy candidate into working scene" in html
    assert "Review discoveries in guided Quick Draft" in html
    assert "Quick Draft status" in js
    assert "Nothing accepted" in js
