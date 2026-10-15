import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(
  new URL('../src/auteur/beginner/browser/app.js', import.meta.url), 'utf8'
);

// Run the real browser script with init deferred. Expose only the polling seam
// inside this test VM; production code does not export or own a test API.
const initMarker = '  if (document.readyState === "loading") {';
assert.equal(source.split(initMarker).length, 2, 'browser init marker must be unique');
const instrumented = source.replace(initMarker,
  '  window.__pollTest = { state, scheduleQuickDraftPoll, showWorkspace, ' +
  'checkQuickDraftResult };\n' + initMarker);

function fixture() {
  const elements = new Map();
  const timeouts = new Map();
  const requests = [];
  let nextTimer = 0;
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      hidden: true, textContent: '', innerHTML: '', value: '', disabled: false,
      scrollIntoView() {},
    });
    return elements.get(id);
  }
  element('home-surface').hidden = false;
  const document = {
    readyState: 'loading', hidden: false,
    getElementById: element,
    addEventListener() {},
  };
  const window = {
    setTimeout(callback) {
      const id = ++nextTimer;
      timeouts.set(id, callback);
      return id;
    },
    clearTimeout(id) { timeouts.delete(id); },
  };
  const fetch = (url) => new Promise((resolve, reject) => {
    requests.push({ url, resolve, reject });
  });
  vm.runInNewContext(instrumented, { window, document, fetch });
  const control = window.__pollTest;
  control.state.quickDraftPending = true;
  control.state.quickDraftSessionId = 'session-a';
  function tick() {
    const item = timeouts.entries().next().value;
    assert.ok(item, 'a polling timer should be scheduled');
    timeouts.delete(item[0]);
    item[1]();
  }
  return { control, document, element, requests, timeouts, tick };
}

function readyResponse() {
  return {
    ok: true,
    json: async () => ({
      session_id: 'session-a',
      draft: { status: 'draft_ready', accepted: false },
      draft_text: 'Unaccepted Working prose',
      scaffold: { inputs: { premise: 'Premise', first_scene_intent: 'Opening' } },
    }),
  };
}

function pendingResponse() {
  return {
    ok: true,
    json: async () => ({
      session_id: 'session-a',
      draft: { status: 'awaiting_host_agent', accepted: false },
      draft_text: null,
      scaffold: { inputs: { premise: 'Premise', first_scene_intent: 'Opening' } },
    }),
  };
}

async function settleMicrotasks() {
  for (let n = 0; n < 8; n += 1) await Promise.resolve();
}

test('in-flight poll cannot render a hidden Quick Draft after workspace navigation', async () => {
  const f = fixture();
  f.control.scheduleQuickDraftPoll();
  f.tick();
  assert.equal(f.requests.length, 1);
  f.control.showWorkspace();
  assert.equal(f.element('home-surface').hidden, true);
  f.requests[0].resolve(readyResponse());
  await settleMicrotasks();
  assert.equal(f.element('quick-draft-result').hidden, true);
  assert.equal(f.control.state.quickDraftPending, false);
  assert.equal(f.timeouts.size, 0);
});

test('manual Check for scene confirms when the host-agent response is still pending', async () => {
  const f = fixture();
  const manualCheck = f.control.checkQuickDraftResult();
  assert.equal(f.requests.length, 1);
  f.requests[0].resolve(pendingResponse());
  await manualCheck;
  assert.match(f.element('quick-draft-handoff-status').textContent, /still waiting/i);
  assert.equal(f.control.state.quickDraftPending, true);
});

test('manual Check for scene response cannot render after workspace navigation', async () => {
  const f = fixture();
  const manualCheck = f.control.checkQuickDraftResult();
  assert.equal(f.requests.length, 1);
  f.control.showWorkspace();
  f.requests[0].resolve(pendingResponse());
  await manualCheck;
  assert.equal(f.element('home-surface').hidden, true);
  assert.equal(f.element('quick-draft-result').hidden, true);
});

test('late poll failure cannot overwrite a newer manual Check for scene result', async () => {
  const f = fixture();
  f.control.scheduleQuickDraftPoll();
  f.tick();
  const manualCheck = f.control.checkQuickDraftResult();
  assert.equal(f.requests.length, 2);
  f.requests[1].resolve(readyResponse());
  await manualCheck;
  assert.equal(f.element('quick-draft-editor').value, 'Unaccepted Working prose');
  f.requests[0].reject(new Error('stale network failure'));
  await settleMicrotasks();
  assert.equal(f.element('quick-draft-handoff-status').textContent, '');
  assert.equal(f.timeouts.size, 0);
});

test('hidden-tab responses are ignored and a visible retry can render Working prose', async () => {
  const f = fixture();
  f.control.scheduleQuickDraftPoll();
  f.tick();
  f.document.hidden = true;
  f.requests[0].resolve(readyResponse());
  await settleMicrotasks();
  assert.equal(f.element('quick-draft-result').hidden, true);
  f.document.hidden = false;
  f.control.scheduleQuickDraftPoll();
  f.tick();
  f.requests[1].resolve(readyResponse());
  await settleMicrotasks();
  assert.equal(f.element('quick-draft-editor').value, 'Unaccepted Working prose');
  assert.equal(f.control.state.quickDraftPending, false);
  assert.equal(f.timeouts.size, 0);
});
