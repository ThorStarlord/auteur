import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mountGraphExperiment} from './app.mjs';

const RICH_SHA = 'c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66';
const candidate = JSON.parse(readFileSync(
  new URL('../../qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json', import.meta.url),
  'utf8',
));
const sparse = JSON.parse(readFileSync(
  new URL('../../qualification-evidence/agent-first-ontology-20261103/sparse-vision-candidate.json', import.meta.url),
  'utf8',
));
const appSource = readFileSync(new URL('./app.mjs', import.meta.url), 'utf8');

class El {
  constructor(tag = '') {
    this.tagName = tag;
    this.id = '';
    this.className = '';
    this.textContent = '';
    this.value = '';
    this.hidden = false;
    this.disabled = false;
    this.children = [];
    this.events = {};
    this.attributes = {};
    this.dataset = {};
    this.style = {};
  }
  append(...items) { for (const item of items) { item.parentNode = this; this.children.push(item); } }
  appendChild(item) { item.parentNode = this; this.children.push(item); return item; }
  replaceChildren(...items) { this.children = []; this.append(...items); }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  getAttribute(key) { return this.attributes[key]; }
  addEventListener(event, handler) { this.events[event] = handler; }
  removeEventListener(event) { delete this.events[event]; }
  focus() { this.focused = true; }
}

function walk(item, visit) {
  if (!item) return;
  visit(item);
  for (const child of item.children || []) walk(child, visit);
}
function all(root, predicate) {
  const result = [];
  walk(root, item => { if (predicate(item)) result.push(item); });
  return result;
}
function byId(root, id) {
  return all(root, item => item.id === id)[0] || null;
}
function byData(root, key, value) {
  return all(root, item => item.dataset && item.dataset[key] === value);
}
function textOf(item) {
  let result = item && typeof item.textContent === 'string' ? item.textContent : '';
  for (const child of (item && item.children) || []) result += ' ' + textOf(child);
  return result;
}
function click(item) {
  assert.ok(item, 'expected a clickable element');
  assert.equal(typeof item.events.click, 'function');
  item.events.click();
}
function setInput(item, value, event = 'input') {
  assert.ok(item, 'expected an input element');
  item.value = value;
  item.events[event]();
}
function mount(fixture = candidate, variant = 'B1') {
  const root = new El('main');
  const document = {createElement: tag => new El(tag)};
  const copied = [];
  const api = mountGraphExperiment(root, {
    candidate: fixture,
    requestSha: fixture === sparse ? 'b'.repeat(64) : RICH_SHA,
    variant,
    document,
    fixtureLabel: fixture === sparse ? 'Recorded sparse candidate' : 'Recorded rich candidate',
    onCopy: value => copied.push(value),
  });
  return {root, api, copied};
}

test('B1 declares source authority and exposes the real source-bound index', () => {
  const {root} = mount();
  const source = textOf(byId(root, 'source-status'));
  assert.match(source, new RegExp(RICH_SHA));
  assert.match(source, /working proposal/i);
  assert.match(textOf(byId(root, 'variant-label')), /B1/);
  assert.match(textOf(byId(root, 'fixture-label')), /Recorded rich candidate/);
  const engine = all(root, item => item.dataset
    && item.dataset.anchorKind === 'node' && item.dataset.anchorId === 'memory_economy')[0];
  assert.ok(engine);
  assert.equal(engine.dataset.sourceRef, 'nodes/3');
  assert.match(engine.textContent, /Memory economy/);
  assert.match(engine.textContent, /working proposal/);
});

test('B1 selects an entity, inspects a recorded relation and returns', () => {
  const {root} = mount();
  const engine = all(root, item => item.dataset
    && item.dataset.anchorKind === 'node' && item.dataset.anchorId === 'memory_economy')[0];
  click(engine);
  assert.equal(byId(root, 'focus-title').textContent, 'Memory economy');
  assert.match(byId(root, 'focus-source').textContent, /nodes\/3/);
  const relation = all(root, item => item.dataset
    && item.dataset.relationId === 'engine_drives_cost')[0];
  assert.ok(relation);
  click(relation);
  assert.ok(byId(root, 'relation-detail'), 'relation detail exists');
  assert.match(textOf(byId(root, 'relation-detail')), /links\/3/);
  assert.match(textOf(byId(root, 'relation-detail')), /personal loss/i);
  click(byId(root, 'back-to-entity'));
  assert.equal(byId(root, 'focus-title').textContent, 'Memory economy');
  assert.equal(byId(root, 'relation-detail'), null);
});

test('B1 missing relation stays explicit and the draft is prepared_not_executed', () => {
  const {root, copied} = mount();
  const engine = all(root, item => item.dataset
    && item.dataset.anchorKind === 'node' && item.dataset.anchorId === 'memory_economy')[0];
  click(engine);
  const wonder = all(root, item => item.dataset
    && item.dataset.anchorKind === 'emotion_target' && item.dataset.anchorId === 'wonder')[0];
  assert.ok(wonder);
  click(wonder);
  assert.match(textOf(byId(root, 'relation-empty')), /No recorded relation/i);
  assert.equal(byId(root, 'operation-select').value, 'ask_relation');
  setInput(byId(root, 'author-intention'),
    'How might the memory economy shape wonder without asserting a link?');
  click(byId(root, 'prepare-draft'));
  assert.match(byId(root, 'draft-status').textContent, /prepared_not_executed/);
  assert.match(byId(root, 'draft-status').textContent, /not sent/i);
  const output = byId(root, 'draft-output');
  assert.ok(output);
  assert.match(output.value, /How might the memory economy shape wonder/);
  assert.match(output.value, new RegExp(RICH_SHA));
  assert.match(output.value, /nodes\/3/);
  assert.match(output.value, /emotion_targets\/0/);
  assert.match(output.value, /No recorded relation/i);
  assert.match(textOf(byId(root, 'draft-warnings')), /author-declared/i);
  click(byId(root, 'copy-draft'));
  assert.equal(copied[0], output.value);
});

test('B1 stale source invalidates the draft and disables preparation', () => {
  const {root} = mount();
  const engine = all(root, item => item.dataset
    && item.dataset.anchorKind === 'node' && item.dataset.anchorId === 'memory_economy')[0];
  click(engine);
  setInput(byId(root, 'author-intention'), 'Is this engine supported?');
  click(byId(root, 'prepare-draft'));
  assert.ok(byId(root, 'draft-output'));
  click(byId(root, 'simulate-stale'));
  assert.match(textOf(byId(root, 'source-status')), /STALE SOURCE/);
  assert.match(byId(root, 'draft-status').textContent, /Source changed|stale/i);
  assert.equal(byId(root, 'prepare-draft').disabled, true);
  assert.equal(byId(root, 'draft-output'), null);
  click(byId(root, 'simulate-stale'));
  assert.equal(byId(root, 'prepare-draft').disabled, false);
  assert.match(textOf(byId(root, 'source-status')), new RegExp(RICH_SHA));
});

test('B1 sparse fixture shows no invented genre and keeps unknown relations explicit', () => {
  const {root} = mount(sparse);
  assert.match(textOf(byId(root, 'fixture-label')), /Recorded sparse candidate/);
  const genreContract = all(root, item => item.dataset
    && item.dataset.anchorKind === 'genre_contract');
  assert.equal(genreContract.length, 0);
  const engine = all(root, item => item.dataset
    && item.dataset.anchorKind === 'node' && item.dataset.anchorId === 'repair_engine')[0];
  const trust = all(root, item => item.dataset
    && item.dataset.anchorKind === 'emotion_target' && item.dataset.anchorId === 'trust')[0];
  click(engine);
  click(trust);
  assert.match(textOf(byId(root, 'relation-empty')), /No recorded relation/i);
});

test('B1 source never uses innerHTML, fetch or localStorage', () => {
  assert.doesNotMatch(appSource, /innerHTML|outerHTML|insertAdjacentHTML|document\.write/);
  assert.doesNotMatch(appSource, /\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage/);
  assert.match(appSource, /textContent/);
});
