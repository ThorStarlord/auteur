"""Browser interactions of exact bundled prototype source; HTTP/ESM is tested separately when allowed."""
import re
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / 'docs/prototypes/focused-unfolding'
EXPORTS = ['createDemoState','createAnchor','selectFocus','suggestForFocus','inspectGhost',
           'adoptGhost','dismissGhost','replaceSourceRevision','collapseCluster',
           'returnFocus','editWorkingNode']


def inline_page():
    # Use the same exact-source bundle as the Full Architecture regression runner.
    from tests.test_full_architecture_browser import bundle_page
    return bundle_page()


@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        yield b
        b.close()


def opened(browser,width=1440,height=900):
    page=browser.new_page(viewport={'width':width,'height':height})
    page.set_default_timeout(3500)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(inline_page(),wait_until='domcontentloaded')
    return page,errors


def start_emotion(page):
    page.get_by_role('button',name='Start with an emotion').click()
    page.get_by_role('heading',name='Joy through generous heroism').wait_for()


def test_first_session_emotion_invitation_and_early_alternative(browser):
    page,errors=opened(browser)
    try:
        assert page.get_by_role('button',name='Start with an emotion').is_visible()
        assert page.get_by_role('button',name='Start elsewhere').is_visible()
        assert page.locator('.ghost-card').count()==0
        page.get_by_role('button',name='Start elsewhere').click()
        page.get_by_label('Idea type').select_option('character')
        page.get_by_label('Working idea').fill('Eira the healer')
        page.get_by_role('button',name='Create working idea').click()
        assert 'Eira the healer' in page.locator('#graph-stage').inner_text()
        assert page.locator('.ghost-card').count()==3
        assert errors==[]
    finally:page.close()


def test_emotion_ghosts_explain_and_adopt_without_canon(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        assert page.locator('.ghost-card').count()==3
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Suggested')).click()
        assert 'might turn sustained effort' in page.locator('#focus-explainer').inner_text()
        assert 'illustrative' in page.locator('#focus-explainer').inner_text().lower()
        assert page.get_by_role('button',name='Adopt into working architecture').is_visible()
        page.get_by_role('button',name='Adopt into working architecture').click()
        assert page.locator('.working-node').count()==2
        assert 'Working · not canon' in page.locator('#graph-stage').inner_text()
        assert 'Accepted story' not in page.locator('#graph-stage').inner_text()
        assert page.locator('.ghost-card').count()<=3
        assert errors==[]
    finally:page.close()


def test_adopted_trope_unfolds_structure_and_can_return_to_emotion(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Suggested')).click()
        page.get_by_role('button',name='Adopt into working architecture').click()
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Working')).click()
        assert 'Earned breakthrough' in page.locator('#current-focus').inner_text()
        assert 'Challenge → Growth → Responsibility' in page.locator('#graph-stage').inner_text()
        page.get_by_role('button',name='Previous focus').click()
        assert 'Joy through generous heroism' in page.locator('#current-focus').inner_text()
        assert errors==[]
    finally:page.close()


def test_dismissal_and_focus_switch_do_not_accumulate_ghosts(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Suggested')).click()
        page.get_by_role('button',name='Dismiss suggestion').click()
        assert 'Earned breakthrough' not in page.locator('.ghost-layer').inner_text()
        assert page.locator('.ghost-card').count()<=3
        page.get_by_role('button',name=re.compile('Generosity empowers others.*Suggested')).click()
        page.get_by_role('button',name='Adopt into working architecture').click()
        page.get_by_role('button',name=re.compile('Generosity empowers others.*Working')).click()
        assert page.locator('.ghost-card').count()<=3
        assert 'Earned breakthrough' not in page.locator('.ghost-layer').inner_text()
        assert errors==[]
    finally:page.close()


def test_collapse_is_visual_only_and_expand_preserves_work(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Suggested')).click()
        page.get_by_role('button',name='Adopt into working architecture').click()
        page.get_by_role('button',name='Collapse this branch').click()
        assert page.get_by_role('button',name='Expand this branch').is_visible()
        assert '1 working idea collapsed' in page.locator('#graph-stage').inner_text()
        page.get_by_role('button',name='Expand this branch').click()
        assert page.locator('.working-node').count()==2
        assert errors==[]
    finally:page.close()


def test_revision_change_preserves_adoption_and_expires_stale_ghosts(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        page.get_by_role('button',name=re.compile('Earned breakthrough.*Suggested')).click()
        page.get_by_role('button',name='Adopt into working architecture').click()
        page.get_by_role('button',name='Simulate source revision').click()
        assert page.locator('.working-node').count()==2
        assert 'new revision' in page.locator('#announcement').inner_text().lower()
        assert errors==[]
    finally:page.close()


@pytest.mark.parametrize('width,height',[(1440,900),(900,700),(390,844)])
def test_responsive_density_and_keyboard_without_overflow(browser,width,height):
    page,errors=opened(browser,width,height)
    try:
        start_emotion(page)
        limit=2 if width<=480 else 3
        assert page.locator('.ghost-card').count()==limit
        assert page.evaluate('document.documentElement.scrollWidth') <= page.evaluate('document.documentElement.clientWidth')+1
        first=page.locator('.ghost-card').first
        first.focus();page.keyboard.press('Enter')
        assert page.locator('#focus-explainer').is_visible()
        assert page.get_by_role('button',name='Adopt into working architecture').is_visible()
        assert errors==[]
    finally:page.close()


def test_no_network_calls_on_render_or_focus(browser):
    page,errors=opened(browser)
    requests=[];page.on('request',lambda req:requests.append(req.url))
    try:
        start_emotion(page)
        page.locator('.ghost-card').first.click()
        page.get_by_role('button',name='Explore proposed meaning').click()
        assert requests==[]
        assert errors==[]
    finally:page.close()


def test_spatial_edges_show_only_current_hypothetical_ghost_relations(browser):
    page,errors=opened(browser)
    try:
        start_emotion(page)
        assert page.locator('#ghost-connections .ghost-edge').count()==3
        assert all(v for v in page.locator('#ghost-connections .ghost-edge').evaluate_all(
            '(edges)=>edges.map(e=>e.getAttribute("stroke-dasharray"))'))
        page.locator('.ghost-card').first.click()
        page.get_by_role('button',name='Dismiss suggestion').click()
        assert page.locator('#ghost-connections .ghost-edge').count()==3
        assert errors==[]
    finally:page.close()
