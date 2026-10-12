"""Four source-linked Architecture perspectives supplement the primary graph."""
from pathlib import Path
import re
BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"

def test_source_scoped_facets_and_relationship_exploration():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    css = (BROWSER / "studio.css").read_text(encoding="utf-8")
    for value in ("overview", "emotions", "genres", "tropes", "structure", "timeline"):
        assert f'data-architecture-facet="{value}"' in html
    for key in ("architecture-facet-panel", "architecture-facet-list",
                "architecture-facet-back", "architecture-work-area"):
        assert f'id="{key}"' in html
    assert "function architectureFacetEntries(facet)" in js
    assert "function renderFacetInspector(entry)" in js
    assert 'state.facetSelection = typeof saved.facetSelection' in js
    for source in ("emotion_targets", "complex_emotions", "genre_contracts",
                   "trope_functions", "structural_pattern", "structural_function"):
        assert source in js
    assert "locally scoped" in js and "NOT ACCEPTED" in js
    assert "not a claim that this individual trope" in js
    assert ".architecture-facet-panel" in css
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'\$\("([^"]+)"\)', js)) <= set(ids)
