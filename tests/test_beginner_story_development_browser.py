from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_browser_exposes_story_development_continuation_surface() -> None:
    html = (ROOT / "src/auteur/beginner/browser/index.html").read_text(encoding="utf-8")
    app = (ROOT / "src/auteur/beginner/browser/app.js").read_text(encoding="utf-8")

    assert 'id="continuation-panel"' in html
    assert "renderContinuation" in app
    assert "prepare-draft-handoff" in app
    assert "derived plans" in html
