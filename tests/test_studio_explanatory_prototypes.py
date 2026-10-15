"""Static and served-browser contracts for source-honest explanatory prototypes."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'docs/prototypes/studio-explanations'


def source(filename):
    return (ROOT / filename).read_text(encoding='utf-8')


def test_shell_has_one_main_hero_no_empty_reserved_inspector_and_keyboard_tabs():
    page = source('index.html')
    assert page.count('id="explanation-main"') == 1
    assert 'id="detail-panel"' in page and re.search(r'id="detail-panel"[^>]*hidden', page)
    assert 'id="story-select"' in page and 'id="view-tabs"' in page
    assert 'id="provenance-summary"' in page
    assert 'id="back-overview"' in page
    for tab in ('overview', 'anatomy', 'comparison', 'mechanism'):
        assert f'data-perspective="{tab}"' in page
    assert 'role="tablist"' in page and 'role="tabpanel"' in page
    ids = re.findall(r'\bid="([^"]+)"', page)
    assert len(ids) == len(set(ids))


def test_shared_shell_loads_same_fixture_and_never_writes_story():
    app = source('app.mjs')
    assert "fetch('./fixtures/" in app
    assert 'normalizeEvidence' in app and 'entriesForPerspective' in app
    assert 'connectionsForSelection' in app
    assert 'localStorage' not in app and 'CanvasStore' not in app
    assert 'story-select' in app and 'explanation-main' in app
    assert 'replaceChildren' in app and 'textContent' in app
    assert 'aria-selected' in app


def test_shell_styles_have_focus_and_small_screen_priority():
    css = source('styles.css')
    assert ':focus-visible' in css
    assert re.search(r'@media\s*\(max-width:\s*650px\)', css)
    assert '.hero-stage' in css and '.detail-panel[hidden]' in css
    assert 'overflow-wrap' in css


def test_genre_anatomy_explains_promise_engine_conflict_payoff_with_coverage():
    anatomy = source('views/anatomy.mjs')
    for semantic in ('READER PROMISE', 'GENRE ENGINE', 'TYPICAL PRESSURE', 'POSSIBLE PAYOFF', 'SOURCE COVERAGE'):
        assert semantic in anatomy
    assert 'renderAnatomy' in anatomy
    assert 'source_ref' in anatomy and 'coverage_note' in anatomy
    assert 'inference_only' in anatomy and 'legacy_contract' in anatomy
    assert 'genre.engine_steps' in anatomy
    assert 'onNavigate' in anatomy and 'onInspect' in anatomy


def test_comparison_keeps_convention_and_story_treatment_distinct():
    js = source('views/comparison.mjs')
    assert 'renderComparison' in js
    for label in ('GENRE KNOWLEDGE', 'THIS STORY PROPOSES', 'HOW THEY MEET', 'Not classified by a versioned pack'):
        assert label in js
    assert 'genre_links' in js and 'story_treatment' in js
    assert 'coverage' in js and 'rule_strength' in js
    assert 'original in literature' in js
    assert 'onNavigate' in js and 'onInspect' in js


def test_mechanism_map_only_uses_declared_edges_and_shows_uncertainty():
    js = source('views/mechanism.mjs')
    assert 'renderMechanism' in js
    assert 'connectionsForSelection(model' in js
    for label in ('HYPOTHESIS · NOT PROVEN', 'SOURCE-BACKED RELATION', 'No supported relationship is recorded'):
        assert label in js
    assert 'document.createElement(\'ol\')' in js
    assert 'source_ref' in js and 'support_status' in js
    assert 'onNavigate' in js and 'onInspect' in js
    assert 'model.items.find' in js


def test_switching_explanation_item_does_not_automatically_open_inspector():
    app = source('app.mjs')
    assert 'function setFocus(ref)' in app
    focus = app.split('function setFocus(ref)', 1)[1].split('function inspect(id)', 1)[0]
    assert "$('detail-panel').hidden=true" in focus
    assert 'inspect(' not in focus
    assert 'function inspect(id)' in app
    for view in ('comparison', 'mechanism'):
        text = source(f'views/{view}.mjs')
        assert 'onFocus' in text
        assert 'onFocus({kind:' in text


def test_exploratory_semantic_history_can_return_without_losing_view():
    page = source('index.html')
    app = source('app.mjs')
    assert 'id="semantic-return"' in page
    assert 'returnRoute(current())' in app
    assert "window.history.back()" in app
    assert "$('semantic-return').addEventListener('click'" in app
    assert 'visitRoute(' in app


def test_semantic_navigation_uses_one_route_owner_and_provenance_context():
    page = source('index.html')
    app = source('app.mjs')
    assert 'id="arrival-context"' in page
    assert 'id="semantic-trail"' in page
    assert 'id="semantic-return"' in page
    assert 'id="navigation-unavailable"' in page
    assert "from './semantic-links.mjs'" in app
    assert "from './navigation-state.mjs'" in app
    assert 'function navigateByLink(' in app
    assert 'window.addEventListener(\'popstate\'' in app
    assert 'window.history.pushState(' in app
    assert 'window.history.replaceState(' in app
    assert 'state.selectionHistory' not in app
    assert 'state.history.push(' not in app


def test_contextual_nav_affordances_are_visible_without_inspector():
    html = source('index.html')
    css = source('styles.css')
    assert 'id="arrival-context"' in html and 'hidden' in html.split('id="arrival-context"', 1)[1].split('>', 1)[0]
    assert '.semantic-link:focus-visible' in css
    assert '@media(max-width:650px)' in css
    assert 'prefers-reduced-motion' in css
    assert 'dataset.linkId' in source('app.mjs')


def test_cross_view_links_use_semantic_targets_not_generic_inspector():
    for name in ('anatomy', 'comparison', 'mechanism'):
        js = source(f'views/{name}.mjs')
        assert 'onNavigate(' in js
        assert 'href' in js
        assert 'sourceRef' in js or 'source_ref' in js
    assert 'preferredPerspective' in source('app.mjs')
