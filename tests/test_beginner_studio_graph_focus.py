"""Architecture is the default focal work surface, with compact saved Story Vision."""
from pathlib import Path
import re
BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"

def test_graph_first_layout_and_optional_vision():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    css = (BROWSER / "studio.css").read_text(encoding="utf-8")
    for name in ("architecture-context", "architecture-context-summary", "vision-preview",
                 "vision-text", "vision-save", "working-group-control"):
        assert f'id="{name}"' in html
    assert 'state.workspace = "architecture"; state.lastRealizationView' in js
    assert 'state.view = "architecture"; state.workspace = "architecture"' in js
    assert 'if (visionItem() && visionItem().content.trim()) $("vision-disclosure").open = false;' in js
    assert 'state.architecture && state.architecture.summary' in js
    assert '$("working-group-control").hidden = designing;' in js
    assert '.vision-preview' in css and '.architecture-context' in css

def test_emotional_report_is_below_graph_and_timeline_is_alternative():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert html.index('id="viewport"') < html.index('id="emotional-design"')
    assert 'id="genre-timeline"' in html
    assert '$("viewport").hidden = state.view === "genre_timeline";' in js
    assert '$("genre-timeline").hidden = state.view !== "genre_timeline";' in js
    assert 'if (state.workspace === "architecture") requestArchitecture("");' in js
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'\$\("([^"]+)"\)', js)) <= set(ids)
