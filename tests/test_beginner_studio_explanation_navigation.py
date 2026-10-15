"""Studio explanatory heroes are read-only projections with explicitly served assets.

Run against the full Auteur checkout that contains the Studio UX branch.
"""
from pathlib import Path
import re
from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer

BROWSER = Path(__file__).resolve().parents[1] / 'src/auteur/beginner/browser'
SERVER = Path(__file__).resolve().parents[1] / 'src/auteur/beginner/server.py'


def source(path):
    return path.read_text(encoding='utf-8')


def test_dedicated_heroes_share_single_source_scoped_adapter():
    html=source(BROWSER/'studio.html')
    js=source(BROWSER/'studio.js')
    assert 'id="studio-explanatory-hero"' in html
    assert 'id="studio-semantic-trail"' in html
    assert 'id="studio-semantic-arrival"' in html
    assert html.index('/studio_explanations.js') < html.index('/studio_explanation_views.js') < html.index('/studio.js')
    assert 'projector.project(state.architecture,state.architectureRequestSha,null)' in js and 'var projector = window.AuteurStudioExplanations' in js
    assert 'window.AuteurStudioExplanationViews' in js
    assert 'function visitFacet(facet, key, nodeId, semanticLink)' in js
    assert 'function restoreFacetHistory(index)' in js
    assert 'state.explanationInspectRequested' in js
    assert 'state.explanationArrival' in js
    assert '"viewport").hidden = state.view === "genre_timeline" || explanationActive()' in js


def test_navigation_cannot_create_accepted_story_actions_or_data_mutation():
    js=source(BROWSER/'studio.js')
    route=js.split('function renderStudioExplanation()',1)[1].split('function render()',1)[0]
    assert 'visitFacet(' in route and 'linksFor(' in route
    assert 'scheduleSave(' not in route and 'queueSave(' not in route
    assert 'requestArchitecture(' not in route and 'applyReviewedArchitecture(' not in route
    assert 'copyCandidate(' not in route and 'generateScene(' not in route
    assert 'semanticLink.requestSha' in js or 'link.requestSha' in route
    assert 'source unavailable' in route.lower() or 'source changed' in route.lower()


def test_browser_assets_are_explicitly_allowlisted():
    source_text=source(SERVER)
    for name in ('studio_explanations.js', 'studio_explanation_views.js', 'studio_author_intent.js', 'studio_agent_handoff.js'):
        assert f'"/{name}": "{name}"' in source_text
        assert f'src="/{name}"' in source(BROWSER/'studio.html')


def test_http_assets_and_dom_are_available_without_extra_public_routes(tmp_path):
    server=BeginnerWorkspaceServer(tmp_path,port=0)
    thread=server.start_in_thread()
    try:
        base=f'http://127.0.0.1:{server.port}'
        for path in ('/studio.html','/studio.js','/studio.css','/studio_explanations.js','/studio_explanation_views.js'):
            with urlopen(base+path) as response:
                assert response.status==200
                if path.endswith('.js'):
                    assert 'javascript' in response.headers.get('Content-Type','').lower()
        with urlopen(base+'/studio.html') as response: html=response.read().decode('utf-8')
        ids=re.findall(r'\bid="([^"]+)"',html)
        assert len(ids)==len(set(ids))
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def test_semantic_arrival_and_back_trail_remain_visible_on_emotions_and_timeline():
    """A cross-facet semantic link must not lose its meaning when its target has no hero."""
    js=source(BROWSER/'studio.js')
    assert 'trail.hidden = state.workspace !== "architecture" || !state.facetHistory.length;' in js
    assert 'arrival.hidden = state.workspace !== "architecture" || !state.explanationArrival;' in js
    assert 'if (state.workspace !== "architecture") return;' in js
    assert '"architecture-facet-back").hidden = state.workspace === "architecture"' in js
    assert 'if (presenter) presenter(host,projection,key,onNavigate,onInspect);' in js
