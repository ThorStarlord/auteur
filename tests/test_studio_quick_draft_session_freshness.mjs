import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Narrow DOM-stubbed author simulation of actual Studio session/read handlers.
// This checks action contracts, not a served Auteur application or a host model.
const code = readFileSync(new URL('../src/auteur/beginner/browser/studio.js', import.meta.url), 'utf8');
function take(start, end) {
  const from = code.indexOf(start);
  const to = code.indexOf(end, from + start.length);
  assert.ok(from !== -1 && to > from, `Cannot find source boundary ${start}`);
  return code.slice(from, to);
}
const functions = take('function draftStatus(', 'function generateScene()');
const inputListener = take('["scene-premise", "scene-intent"].forEach', '$("use-vision-as-premise").addEventListener');

function scenario() {
  const elements = new Map(), requests = [];
  const item = { id: 'working-scene', kind: 'scene', quick_draft_session_id: 'session-1' };
  const $ = id => {
    if (!elements.has(id)) elements.set(id, {
      value: '', hidden: false, textContent: '', href: '',
      handlers: {}, addEventListener(name, callback) { this.handlers[name] = callback; },
    });
    return elements.get(id);
  };
  const selected = () => item;
  const fetch = url => new Promise(resolve => requests.push({ url, resolve }));
  const apiJson = response => response.json();
  const built = new Function('$', 'selected', 'fetch', 'apiJson',
    `${functions}\n${inputListener}\nreturn { draftStatus, refreshDraft };`)(
      $, selected, fetch, apiJson);
  return { $, item, requests, ...built };
}
const projection = (session, premise, intent) => ({
  session_id: session, draft: { status: 'awaiting_host_agent' },
  draft_text: 'Previously generated working prose.',
  scaffold: { inputs: { premise, first_scene_intent: intent } },
});
const flush = () => new Promise(resolve => setImmediate(resolve));

test('historical Quick Draft remains visible but is identified as using older inputs', () => {
  const f = scenario();
  f.$('scene-premise').value = 'Current premise';
  f.$('scene-intent').value = 'Current scene request';
  f.draftStatus(projection('session-1', 'Old premise', 'Old scene request'));
  assert.match(f.$('generation-status').textContent, /earlier scene inputs/);
  assert.equal(f.$('generated-prose').value, 'Previously generated working prose.');
  assert.equal(f.$('generation-result').hidden, false);
  assert.equal(f.$('open-quick-draft').href, '/beginner.html?quick_draft=session-1');
  f.draftStatus(projection('session-1', 'Current premise', 'Current scene request'));
  assert.doesNotMatch(f.$('generation-status').textContent, /earlier scene inputs/);
});

test('late refresh response cannot replace a newer linked Quick Draft', async () => {
  const f = scenario();
  f.$('generation-status').textContent = 'Fresh session has been linked';
  f.refreshDraft();
  assert.deepEqual(f.requests.map(x => x.url), ['/api/beginner/quick-draft/session-1']);
  f.item.quick_draft_session_id = 'session-2';
  f.requests[0].resolve({ json: async () => projection('session-1', '', '') });
  await flush();
  assert.equal(f.$('generation-status').textContent, 'Fresh session has been linked');

  f.refreshDraft();
  assert.equal(f.requests.length, 2);
  f.requests[1].resolve({ json: async () => projection('session-2', '', '') });
  await flush();
  assert.match(f.$('generation-status').textContent, /Request staged for the active coding agent/);
});

test('editing linked scene inputs displays a noncanonical freshness warning', () => {
  const f = scenario();
  f.$('scene-premise').handlers.input();
  assert.match(f.$('generation-status').textContent, /linked Quick Draft/);
  f.item.quick_draft_session_id = '';
  f.$('generation-status').textContent = '';
  f.$('scene-intent').handlers.input();
  assert.equal(f.$('generation-status').textContent, '');
});
