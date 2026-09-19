from pathlib import Path

BROWSER_DIR = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"
INDEX = BROWSER_DIR / "index.html"
APP = BROWSER_DIR / "app.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_browser_leads_with_interpretation_and_hides_internal_vocabulary() -> None:
    source = _read(APP)
    html = _read(INDEX)
    assert "Continue with this interpretation" in html
    assert "Refine this interpretation" in html
    assert "Why does Auteur see this?" in html
    assert "PRIMARY_ENGINE" not in html
    assert "SETTING_WORLD" not in html
    assert "RELATIONSHIP_THEMATIC" not in html
    assert "Use this lens" not in html
    assert "Narrative Architecture Analysis" not in html
    assert "Realization" not in html
    assert "Expression" not in html
    assert "primary_surface" in source
    assert "discovery" in source
    assert "identity_candidate" in source
