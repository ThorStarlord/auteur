"""Interactive source-bound Full Architecture and Review browser journeys.

Uses exact local ES-module contents bundled into Chromium when browser network policy blocks localhost.
"""
from pathlib import Path
import re
import pytest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
FOCUS=ROOT/'docs/prototypes/focused-unfolding'
FULL=ROOT/'docs/prototypes/full-architecture'


def bundle_page():
    html=(FOCUS/'index.html').read_text(encoding='utf8')
    css=(FOCUS/'styles.css').read_text(encoding='utf8')
    files=[FULL/'projection.mjs',FULL/'review.mjs',FOCUS/'model.mjs',FOCUS/'full-view.mjs',FOCUS/'review-view.mjs',FOCUS/'app.mjs']
    scripts=[]
    for path in files:
        code=path.read_text(encoding='utf8')
        code=re.sub(r'^import\s+[^;]+;\s*$', '',code,flags=re.MULTILINE)
        code=re.sub(r'\bexport\s+(?=function|const|class|async\s+function)', '',code)
        scripts.append(code)
    fixture=(FULL/'fixtures/paladin.json').read_text(encoding='utf8')
    script='const paladinFixture='+fixture+';\n'+'\n'.join(scripts)
    return html.replace('<link rel="stylesheet" href="./styles.css">',f'<style>{css}</style>')\
        .replace('<script type="module" src="./app.mjs"></script>','')\
        .replace('</body>','<script>'+script+'</script></body>')

@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        yield b
        b.close()

def opened(browser,width=1440,height=900):
    page=browser.new_page(viewport={'width':width,'height':height})
    page.set_default_timeout(3500)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(bundle_page())
    return page,errors

def start(page):
    page.get_by_role('button',name='Start with an emotion').click()
    page.get_by_role('heading',name='Joy through generous heroism').wait_for()

def full(page):
    page.get_by_role('button',name='Full Architecture',exact=True).click()
    page.get_by_role('heading',name='The full narrative architecture').wait_for()


def test_empty_full_architecture_shows_reviewable_scaffold_not_invented_author_choices(browser):
    page,errors=opened(browser)
    try:
        full(page)
        assert 'No author working ideas yet' in page.locator('#full-architecture').inner_text()
        assert 'Genre morphology not established' in page.locator('#full-architecture').inner_text()
        assert errors==[]
    finally:page.close()


def test_focus_full_roundtrip_preserves_working_focus_and_ghost_limit(browser):
    page,errors=opened(browser)
    try:
        start(page)
        assert page.locator('.ghost-card').count()==3
        full(page)
        assert 'Joy through generous heroism' in page.locator('#full-architecture').inner_text()
        page.get_by_role('button',name='Focused Unfolding',exact=True).click()
        assert 'Joy through generous heroism' in page.locator('#current-focus').inner_text()
        assert page.locator('.ghost-card').count()==3
        assert errors==[]
    finally:page.close()


def test_genre_constellation_separates_candidate_interpretation_from_versioned_pack(browser):
    page,errors=opened(browser)
    try:
        start(page);full(page)
        page.get_by_role('button',name=re.compile('Progression Fantasy')).click()
        detail=page.locator('#full-architecture').inner_text()
        assert 'Genre morphology not established' in detail
        assert 'Candidate interpretation' in detail
        assert 'Earned breakthrough' in detail
        assert 'Challenge and earned growth' in detail
        assert errors==[]
    finally:page.close()


def test_reader_emotions_book_phases_and_unlinked_author_added_are_inspectable(browser):
    page,errors=opened(browser)
    try:
        start(page);full(page)
        for term in ['joy','A fragile promise','Responsibility deepens','Story-specific additions']:
            assert term.lower() in page.locator('#full-architecture').inner_text().lower()
        assert 'Working, not canon' in page.locator('#full-architecture').inner_text()
        assert errors==[]
    finally:page.close()


def test_review_lists_open_author_decisions_and_returns_to_authoring_without_acceptance(browser):
    page,errors=opened(browser)
    try:
        start(page);full(page)
        page.get_by_role('button',name='Review Full Architecture').click()
        assert page.locator('#review-full-architecture').is_visible()
        text=page.locator('#review-full-architecture').inner_text()
        assert 'Working design' in text
        assert 'Book structure' in text
        assert 'not established' in text.lower()
        assert 'canon accepted' not in text.lower()
        page.get_by_role('button',name='Return to architecture').click()
        assert page.locator('#full-architecture').is_visible()
        assert errors==[]
    finally:page.close()

@pytest.mark.parametrize('width,height',[(1440,900),(900,700),(390,844)])
def test_full_is_keyboard_accessible_and_does_not_overflow(browser,width,height):
    page,errors=opened(browser,width,height)
    try:
        start(page);full(page)
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth+1')
        page.get_by_role('button',name='Review Full Architecture').focus()
        page.keyboard.press('Enter')
        assert page.locator('#review-full-architecture').is_visible()
        assert errors==[]
    finally:page.close()


def test_full_and_review_do_not_make_network_requests_or_mutate_work(browser):
    page,errors=opened(browser)
    requests=[];page.on('request',lambda r:requests.append(r.url))
    try:
        start(page);n=page.locator('.working-node').count()
        full(page);page.get_by_role('button',name='Review Full Architecture').click()
        page.get_by_role('button',name='Return to architecture').click()
        page.get_by_role('button',name='Focused Unfolding',exact=True).click()
        assert page.locator('.working-node').count()==n
        assert requests==[] and errors==[]
    finally:page.close()

def test_source_revision_in_full_preserves_adopted_work_and_marks_historical_source_stale(browser):
    page,errors=opened(browser)
    try:
        start(page)
        page.locator('.ghost-card').first.click()
        page.get_by_role('button',name='Adopt into working architecture').click()
        full(page)
        assert 'Needs review' not in page.locator('#full-architecture').inner_text()
        page.locator('#revise-source').click()
        assert 'Needs review' in page.locator('#full-architecture').inner_text()
        assert 'Earned breakthrough' in page.locator('#full-architecture').inner_text()
        assert errors==[]
    finally:page.close()
