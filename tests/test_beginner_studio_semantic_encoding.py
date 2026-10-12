"""Architecture category and relationship semantics must not rely only on color."""
from pathlib import Path
import re
BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"

def test_typed_semantic_nodes_and_legend_with_explicit_proposal_status():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    css = (BROWSER / "studio.css").read_text(encoding="utf-8")
    assert 'id="architecture-legend"' in html
    for word in ("Emotions", "Genres", "Tropes", "Structure", "Dashed = proposed"):
        assert word in html
    for kind in ('reader_experience', 'genre', 'trope', 'engine', 'structure'):
        assert f'[data-kind="{kind}"]' in css or f'["{kind}"' in css
    assert 'button.dataset.kind = item.category;' in js
    assert 'item.category + " · Proposed"' in js
    assert '.node.candidate[aria-pressed="true"]' in css
    assert 'edge.function || "Related"' in js
    assert 'edge.kind.replace(/_/g, " ")' in js
    assert 'title.textContent = (edge.function || "Related")' in js
    assert 'button.addEventListener("click", function () { visitFacet("overview", null, other.id); });' in js
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'\$\("([^"]+)"\)', js)) <= set(ids)
