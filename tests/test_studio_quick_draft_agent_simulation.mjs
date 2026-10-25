import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

// Exercise actual Studio action bodies without starting a provider or changing a story.
const code = readFileSync(new URL('../src/auteur/beginner/browser/studio.js', import.meta.url), 'utf8');
function section(start, end) {
  const first = code.indexOf(start);
  const last = code.indexOf(end, first + start.length);
  assert.ok(first >= 0 && last > first, `Missing Studio action: ${start}`);
  return code.slice(first, last);
}
const actions = [
  section('function copyRealization()', 'function inspectRealizationPurpose()'),
  section('function generateScene()', 'function useGenerated()'),
  section('$("use-vision-as-premise").addEventListener', '$("use-scene-as-intent").addEventListener'),
  section('$("use-scene-as-intent").addEventListener', '$("save-scene").addEventListener'),
].join('\n');

function simulatedAuthor(vision = "Each storm renews the town's promise to care for everyone.") {
  const elements = new Map();
  const $ = key => {
    if (!elements.has(key)) elements.set(key, {
      value: '', textContent: '', disabled: false, handlers: {},
      addEventListener(type, callback) { this.handlers[type] = callback; },
    });
    return elements.get(key);
  };
  const scene = {
    id: 'assembly_scene', kind: 'scene', title: 'Storm assembly',
    description: 'Neighbors decide which repairs should be made before nightfall.',
    architecture_refs: ['reciprocal_care'],
  };
  const state = {
    items: [{id: 'story-vision', kind: 'note', title: 'Story Vision', content: vision}],
    positions: {}, selected: null, selectedRealization: scene.id,
    realizationRequestSha: 'a'.repeat(64), view: 'realization_candidates',
  };
  const remote = {ready: true, failed: false};
  const posts = [], notices = [];
  const selected = () => state.items.find(i => i.id === state.selected);
  const captureScene = () => {
    const item = selected();
    item.content = $('scene-text').value;
    item.scene_premise = $('scene-premise').value;
    item.scene_intent = $('scene-intent').value;
  };
  const context = {
    $, state, remote, selected, captureScene,
    realizationElement: id => id === scene.id ? scene : null,
    visionItem: () => state.items.find(x => x.id === 'story-vision'),
    id: () => 'copied-scene', availablePosition: () => ({x: 80, y: 90}),
    render() {}, queueSave: async () => {}, scheduleSave() {}, rememberFocus() {},
    status: x => notices.push(x),
    fetch: async (path, init) => {
      posts.push({path, body: JSON.parse(init.body)});
      return {ok: true, json: async () => ({
        session_id: 'simulation-session', draft: {status: 'awaiting_host_agent'},
      })};
    },
    apiJson: response => response.json(),
    draftStatus(projection) { $('generation-status').textContent = projection.draft.status; },
  };
  const keys = Object.keys(context);
  const handlers = new Function(...keys, `${actions}\nreturn {copyRealization, generateScene};`)(
    ...Object.values(context)
  );
  const click = key => {
    const callback = $(key).handlers.click;
    assert.equal(typeof callback, 'function');
    return callback();
  };
  const copy = () => {
    handlers.copyRealization();
    const item = selected();
    assert.equal(item.kind, 'scene');
    $('scene-text').value = item.content;
    $('scene-intent').value = item.scene_intent || '';
    $('scene-premise').value = item.scene_premise || '';
    return item;
  };
  return {state, remote, $, posts, notices, selected, handlers, click, copy};
}

// Agent-authored scenario, not empirical author preference or human UX evidence.
test('simulated author copies focused scene, edits inputs, explicitly requests Quick Draft', async () => {
  const f = simulatedAuthor();
  const item = f.copy();
  assert.equal(item.scene_intent, 'Neighbors decide which repairs should be made before nightfall.');
  assert.match(item.content, /Architecture refs: reciprocal_care/);
  assert.equal(f.posts.length, 0);
  f.click('use-scene-as-intent');
  assert.match(f.$('generation-status').textContent, /provenance footer/);
  assert.equal(f.$('scene-intent').value, item.scene_intent);
  f.handlers.generateScene();
  assert.match(f.$('generation-status').textContent, /premise and a scene intent/);
  assert.equal(f.posts.length, 0);
  f.click('use-vision-as-premise');
  assert.equal(f.$('scene-premise').value, f.state.items[0].content);
  assert.equal(f.posts.length, 0);
  f.$('scene-premise').value = 'The town decides how to share limited shelter.';
  f.$('scene-intent').value = 'A caretaker refuses to abandon a stranger.';
  f.click('use-vision-as-premise');
  assert.equal(f.$('scene-premise').value, 'The town decides how to share limited shelter.');
  f.handlers.generateScene();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(f.posts, [{
    path: '/api/beginner/quick-draft',
    body: {premise: 'The town decides how to share limited shelter.',
      first_scene: 'A caretaker refuses to abandon a stranger.'},
  }]);
  assert.equal(item.quick_draft_session_id, 'simulation-session');
  assert.equal(f.$('generation-status').textContent, 'awaiting_host_agent');
  assert.equal(f.state.items.filter(x => x.kind === 'scene').length, 1);
});

test('simulated vague or long Story Vision never silently becomes a premise', () => {
  for (const vision of ['', 'A'.repeat(4001)]) {
    const f = simulatedAuthor(vision);
    f.copy();
    f.click('use-vision-as-premise');
    assert.equal(f.$('scene-premise').value, '');
    assert.equal(f.posts.length, 0);
    assert.match(f.$('generation-status').textContent, /No saved Story Vision|longer than/);
  }
});

test('simulated long scene notes refuse truncation without destroying existing intent', () => {
  const f = simulatedAuthor();
  const item = f.copy();
  f.$('scene-text').value = 'B'.repeat(4001);
  f.click('use-scene-as-intent');
  assert.equal(f.$('scene-intent').value, item.scene_intent);
  assert.match(f.$('generation-status').textContent, /longer than/);
  assert.equal(f.posts.length, 0);
});

test('simulated stale Realization can be copied without hiding its stale source', () => {
  const f = simulatedAuthor();
  f.state.realizationStale = true;
  const copied = f.copy();
  assert.equal(copied.scene_intent,
    'Neighbors decide which repairs should be made before nightfall.');
  assert.equal(f.state.items.length, 2);
  assert.match(f.notices.at(-1), /Source is STALE relative to current creative materials/);
  assert.equal(f.posts.length, 0);
});
