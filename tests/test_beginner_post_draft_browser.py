from pathlib import Path


def test_browser_surface_has_one_primary_next_action() -> None:
    browser = Path("src/auteur/beginner/browser/index.html").read_text(encoding="utf-8")
    app = Path("src/auteur/beginner/browser/app.js").read_text(encoding="utf-8")
    assert "Recommended next step" in browser
    assert "accept-latest-draft" in app
    assert "final.md" not in app
