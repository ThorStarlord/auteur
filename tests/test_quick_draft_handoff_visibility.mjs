import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Source-loaded UI behavior checks. These are NOT an end-to-end running Auteur
// project, a host-agent invocation, or an acceptance/creative-quality gate.
const surfaces = [
  {
    label: 'Studio',
    js: '../src/auteur/beginner/browser/studio.js',
    html: '../src/auteur/beginner/browser/studio.html',
    end: '  function draftStatus(projection) {',
  },
  {
    label: 'Beginner',
    js: '../src/auteur/beginner/browser/app.js',
    html: '../src/auteur/beginner/browser/index.html',
    end: '  function renderQuickDraftProjection(projection) {',
  },
];

function prepare(surface) {
  const source = readFileSync(new URL(surface.js, import.meta.url), 'utf8');
  const html = readFileSync(new URL(surface.html, import.meta.url), 'utf8');
  for (const id of ['quick-draft-handoff', 'quick-draft-handoff-file',
                    'quick-draft-handoff-sha']) {
    assert.equal(html.split(`id="${id}"`).length - 1, 1,
      `${surface.label} must provide exactly one ${id}`);
  }
  const begin = source.indexOf('  function renderQuickDraftHandoff(projection) {');
  const end = source.indexOf(surface.end, begin + 1);
  assert.ok(begin >= 0 && end > begin, `${surface.label} request renderer missing`);
  const controls = new Map();
  const $ = id => {
    if (!controls.has(id)) controls.set(id, { hidden: true, textContent: '' });
    return controls.get(id);
  };
  const render = new Function('$',
    source.slice(begin, end) + '\nreturn renderQuickDraftHandoff;',
  )($);
  return { render, $, source };
}

function projection(status = 'awaiting_host_agent', overrides = {}) {
  return {
    session_id: 'quick-20261025T120001000000Z-123abcde',
    draft: {
      status,
      backend_request: {
        file: 'host_agent_request.json',
        request_sha256: 'a'.repeat(64),
      },
    },
    ...overrides,
  };
}

for (const surface of surfaces) {
  test(`${surface.label}: pending request exposes exact project-relative source and SHA`, () => {
    const t = prepare(surface);
    t.render(projection());
    assert.equal(t.$('quick-draft-handoff').hidden, false);
    assert.equal(t.$('quick-draft-handoff-file').textContent,
      '.auteur/quick_draft/quick-20261025T120001000000Z-123abcde/host_agent_request.json');
    assert.equal(t.$('quick-draft-handoff-sha').textContent, 'a'.repeat(64));
  });

  test(`${surface.label}: completed and missing requests do not show stale metadata`, () => {
    const t = prepare(surface);
    t.render(projection());
    t.render(projection('draft_ready'));
    assert.equal(t.$('quick-draft-handoff').hidden, true);
    assert.equal(t.$('quick-draft-handoff-file').textContent, '');
    assert.equal(t.$('quick-draft-handoff-sha').textContent, '');
    t.render(projection('awaiting_host_agent', { draft: { status: 'awaiting_host_agent' } }));
    assert.equal(t.$('quick-draft-handoff').hidden, true);
  });

  test(`${surface.label}: invalid request data cannot become a displayed path`, () => {
    const t = prepare(surface);
    const malicious = projection();
    malicious.draft.backend_request.file = '../private-secret.env';
    t.render(malicious);
    assert.equal(t.$('quick-draft-handoff').hidden, true);
    malicious.draft.backend_request.file = 'host_agent_request.json';
    malicious.session_id = '../../outside';
    t.render(malicious);
    assert.equal(t.$('quick-draft-handoff').hidden, true);
    malicious.session_id = 'quick-legitimate';
    malicious.draft.backend_request.request_sha256 = 'not-a-fingerprint';
    t.render(malicious);
    assert.equal(t.$('quick-draft-handoff').hidden, true);
    assert.equal(t.$('quick-draft-handoff-file').textContent, '');
  });
}

test('each authoring surface calls request detail rendering from the existing projection', () => {
  for (const surface of surfaces) {
    const source = readFileSync(new URL(surface.js, import.meta.url), 'utf8');
    const after = source.slice(source.indexOf(surface.end),
      source.indexOf(surface.end) + 700);
    assert.match(after, /renderQuickDraftHandoff\(projection\);/);
  }
});
