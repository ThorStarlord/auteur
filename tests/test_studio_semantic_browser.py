"""Real Chromium DOM/event interactions against the exact bundled source (not HTTP/ESM qualification).

Local browser navigation is blocked by policy in this execution environment. The test
preserves the JS/CSS source and JSON fixtures but adapts ES module imports to inline IIFEs.
"""
import json
import re
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1] / 'docs/prototypes/studio-explanations'


def inline_document():
    html=(ROOT/'index.html').read_text()
    css=(ROOT/'styles.css').read_text()
    html=html.replace('<link rel="stylesheet" href="./styles.css">',f'<style>{css}</style>')
    html=html.replace('<script type="module" src="./app.mjs"></script>','')
    modules=[
        ('model.mjs','__model',['normalizeEvidence','entriesForPerspective','connectionsForSelection']),
        ('semantic-links.mjs','__semantic',['deriveSemanticLinks','linksForFocus','preferredPerspective']),
        ('navigation-state.mjs','__routes',['visitRoute','returnRoute','reconcileRoute','serializeFixtureRoute','parseFixtureRoute']),
        ('views/anatomy.mjs','__anatomy',['renderAnatomy']),
        ('views/comparison.mjs','__comparison',['renderComparison']),
        ('views/mechanism.mjs','__mechanism',['renderMechanism'])
    ]
    script=''
    for filename,var,exports in modules:
        src=(ROOT/filename).read_text()
        src=re.sub(r'^import .*?;\s*$', '', src, flags=re.MULTILINE)
        src=re.sub(r'\bexport (function|const)\b',r'\1',src)
        script+=f'const {var}=(()=>{{\n{src}\nreturn {{{",".join(exports)}}};\n}})();\n'
    fixtures={n:json.loads((ROOT/'fixtures'/f'{n}.json').read_text()) for n in ('paladin','hybrid')}
    fixtures['genre-evidence']=json.loads((ROOT/'fixtures/genre-evidence.json').read_text())
    script+='const __views={anatomy:__anatomy,comparison:__comparison,mechanism:__mechanism};\n'
    script+='const __fixtures='+json.dumps(fixtures)+';\n'
    script+='window.fetch = async (path)=>({ok:true,json:async()=>__fixtures[path.includes("genre-evidence")?"genre-evidence":(path.includes("hybrid")?"hybrid":"paladin")]});\n'
    script+='const {normalizeEvidence,entriesForPerspective,connectionsForSelection}=__model;\n'
    script+='const {deriveSemanticLinks,linksForFocus,preferredPerspective}=__semantic;\n'
    script+='const {visitRoute,returnRoute,reconcileRoute,serializeFixtureRoute,parseFixtureRoute}=__routes;\n'
    app=(ROOT/'app.mjs').read_text()
    app=re.sub(r'^import .*?;\s*$', '',app,flags=re.MULTILINE)
    app=app.replace('await import(files[mode])','await Promise.resolve(__views[mode])')
    script+=app
    return html.replace('</body>','<script>'+script+'</script></body>')


@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        yield browser
        browser.close()


def page_with_source(browser, width=1440,height=900):
    page=browser.new_page(viewport={'width':width,'height':height})
    errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
    page.set_content(inline_document(),wait_until='domcontentloaded')
    page.locator('h2.stage-heading').wait_for()
    return page,errors


def test_paladin_genre_to_trope_to_mechanism_and_exact_back(browser):
    page,errors=page_with_source(browser)
    try:
        page.get_by_role('tab',name='Genre anatomy').click()
        page.get_by_role('link',name=re.compile('Progression Fantasy uses Earned breakthrough',re.I)).click()
        assert 'Convention' in page.locator('.stage-heading').inner_text() or 'genre' in page.locator('.stage-heading').inner_text()
        assert 'From' in page.locator('#arrival-context').inner_text()
        assert page.locator('#detail-panel').is_hidden()
        page.get_by_role('link',name=re.compile('Earned breakthrough illustrates Challenge',re.I)).click()
        assert page.locator('.stage-heading').inner_text()=='What makes the story move?'
        assert 'illustrates' in page.locator('#arrival-context').inner_text()
        assert 'Hypothesis' in page.locator('#arrival-context').inner_text()
        page.locator('#semantic-return').click()
        assert page.get_by_text('Where does the genre end',exact=False).is_visible()
        page.locator('#semantic-return').click()
        assert page.get_by_text('What makes a genre work?',exact=True).is_visible()
        assert 'Progression Fantasy' in page.locator('#explanation-main').inner_text()
        assert errors==[]
    finally:page.close()


def test_multi_genre_roles_and_no_unfounded_emotion_shortcut(browser):
    page,errors=page_with_source(browser)
    try:
        page.get_by_role('tab',name='Convention & invention').click()
        assert page.get_by_role('link',name=re.compile('Progression Fantasy anatomy')).count()==1
        assert page.get_by_role('link',name=re.compile('Heroic Fantasy anatomy')).count()==1
        assert page.locator('#explanation-main .semantic-link').filter(has_text='Joy').count()==0
        page.get_by_role('link',name=re.compile('Heroic Fantasy anatomy')).click()
        assert page.locator('#arrival-context').is_visible()
        assert page.locator('#arrival-context').inner_text().find('Heroic Fantasy')>=0
        assert errors==[]
    finally:page.close()


@pytest.mark.parametrize('width,height',[(1440,900),(900,700),(390,844)])
def test_all_views_without_horizontal_page_overflow_or_console_errors(browser,width,height):
    page,errors=page_with_source(browser,width,height)
    try:
        for tab in ('Story map','Genre anatomy','Convention & invention','Mechanism map'):
            page.get_by_role('tab',name=tab).click()
            assert page.locator('h2.stage-heading').is_visible()
            assert page.locator('#detail-panel').is_hidden()
            documentWidth=page.evaluate('document.documentElement.scrollWidth')
            viewportWidth=page.evaluate('document.documentElement.clientWidth')
            assert documentWidth<=viewportWidth+1,(tab,width,documentWidth,viewportWidth)
        assert errors==[]
    finally:page.close()


def test_public_hash_only_contains_fixture_identifiers_and_no_made_up_back(browser):
    page,errors=page_with_source(browser)
    try:
        assert page.locator('#semantic-return').is_hidden()
        page.get_by_role('tab',name='Genre anatomy').click()
        fragment=page.evaluate('location.hash')
        assert 'story=paladin' in fragment
        assert 'view=anatomy' in fragment
        assert 'generous paladin' not in fragment.lower()
        assert page.locator('#semantic-return').is_hidden()
        assert errors==[]
    finally:page.close()


def test_browser_back_forward_restores_semantic_link_and_focus(browser):
    page,errors=page_with_source(browser)
    try:
        page.get_by_role('tab',name='Genre anatomy').click()
        src=page.get_by_role('link',name=re.compile('Progression Fantasy uses Earned breakthrough',re.I))
        link_ref=src.get_attribute('data-nav-focus')
        src.focus();page.keyboard.press('Enter')
        assert page.locator('#arrival-context').is_visible()
        page.go_back(wait_until='domcontentloaded')
        assert page.get_by_text('What makes a genre work?',exact=True).is_visible()
        assert page.evaluate('document.activeElement.dataset.navFocus')==link_ref
        page.go_forward(wait_until='domcontentloaded')
        assert page.locator('#arrival-context').is_visible()
        assert 'Earned breakthrough' in page.locator('#arrival-context').inner_text()
        assert errors==[]
    finally:page.close()


def test_unavailable_hash_does_not_select_title_similar_fallback(browser):
    page,errors=page_with_source(browser)
    try:
        page.evaluate("window.history.pushState({route:{storyId:'paladin',perspective:'comparison',focus:{kind:'item',id:'retired'},viaLinkId:null,trail:[]}},'', '#story=paladin&view=comparison&kind=item&key=retired')")
        page.evaluate('window.dispatchEvent(new PopStateEvent("popstate",{state:window.history.state}))')
        assert page.locator('#navigation-unavailable').is_visible()
        assert 'unavailable' in page.locator('#navigation-unavailable').inner_text().lower()
        assert page.locator('.stage-heading').inner_text()=='The story at a glance'
        assert errors==[]
    finally:page.close()


def test_change_fixture_clears_semantic_history(browser):
    page,errors=page_with_source(browser)
    try:
        page.get_by_role('tab',name='Genre anatomy').click()
        page.get_by_role('link',name=re.compile('Progression Fantasy uses Earned breakthrough',re.I)).click()
        assert page.locator('#semantic-return').is_visible()
        page.locator('#story-select').select_option('hybrid')
        assert page.locator('#semantic-return').is_hidden()
        assert page.locator('.stage-heading').inner_text()=='The story at a glance'
        assert 'story=hybrid' in page.evaluate('location.hash')
        assert errors==[]
    finally:page.close()
