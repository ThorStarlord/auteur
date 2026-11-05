"""Real Chromium DOM interaction tests using the repository's recorded candidate.

The isolated environment may prohibit local HTTP navigation; scripts are loaded
into a blank Chromium page so this test is *not* evidence of served Studio use.
"""
from pathlib import Path
import json
import re
import shutil
import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/prototypes/hybrid-architecture-revision'
EVIDENCE = ROOT / 'docs/qualification-evidence/agent-first-ontology-20261103'


def _source_bundle():
    sources = []
    for name in ('studio_architecture_revision_compare.mjs', 'studio_architecture_revision_view.mjs'):
        source = (ROOT / 'src/auteur/beginner/browser' / name).read_text(encoding='utf-8')
        source = re.sub(r'^import .*?;\s*$', '', source, flags=re.MULTILINE)
        source = re.sub(r'^export \{[^}]*\};\s*$', '', source, flags=re.MULTILINE)
        source = source.replace('export function ', 'function ').replace('export const ', 'const ')
        sources.append(source)
    sources.append('window.__startReview=(comparison)=>mountRevisionReview(document.getElementById("review-root"),{comparison});')
    return '\n'.join(sources)


def test_hybrid_review_semantic_summary_comparison_focus_and_narrow_screen():
    before = json.loads((EVIDENCE / 'rich-vision-candidate.json').read_text(encoding='utf-8'))
    after = json.loads(json.dumps(before))
    node = next(n for n in after['nodes'] if n['id'] == 'memory_economy')
    node['summary'] = 'Wonder from personal cost'
    edge = next(e for e in after['links'] if e['id'] == 'engine_drives_cost')
    old_target = edge['target']
    edge['target'] = 'wonder_promise'
    if old_target == edge['target']:
        pytest.skip('Recorded fixture no longer provides the expected redirect case')
    target = next(t for t in after['emotion_targets'] if t['id'] == 'wonder')
    target['intended_effect'] = 'Beautiful wonder'
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception:
            chrome = shutil.which('chromium') or shutil.which('chromium-browser')
            if not chrome:
                pytest.skip('Chromium browser unavailable')
            browser = playwright.chromium.launch(executable_path=chrome, headless=True,
                                                  args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1100, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<main><div id="review-root"></div></main>')
        page.add_style_tag(content=(BASE / 'styles.css').read_text(encoding='utf-8'))
        page.add_script_tag(content=_source_bundle())
        page.evaluate('([before,after])=>{const comparison=compareArchitectureRevision({before,after,beforeRequestSha:"a".repeat(64),afterRequestSha:"b".repeat(64),expectedPriorSha:"a".repeat(64),requestedChange:"Make wonder dominant"});window.__review=window.__startReview(comparison)}', [before, after])
        assert 'working' in page.locator('#revision-summary').inner_text().lower()
        assert 'Requirements to check' in page.locator('body').inner_text()
        page.locator('[data-mode="compare"]').click()
        assert page.locator('[data-side="before"] .architecture-node').count() > 0
        assert page.locator('[data-side="after"] .architecture-node').count() > 0
        assert 'memory economy' in page.locator('[data-side="before"]').inner_text().lower()
        assert 'memory economy' in page.locator('[data-side="after"]').inner_text().lower()
        page.locator('.change-action[data-change-kind="link"][data-change-id="engine_drives_cost"]').click()
        assert 'focused' in page.locator('#focus-pane').inner_text().lower()
        fields = page.locator('#field-comparison').inner_text()
        assert old_target in fields and 'wonder_promise' in fields
        page.locator('#focus-back').click()
        assert page.locator('[data-side="before"]').count() == 1
        page.set_viewport_size({'width': 390, 'height': 844})
        page.locator('#mobile-side').select_option('after')
        assert page.locator('[data-side="after"]').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
        assert not errors, errors
        browser.close()
