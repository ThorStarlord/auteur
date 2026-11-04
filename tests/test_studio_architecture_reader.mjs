import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const root = new URL('../src/auteur/beginner/browser/', import.meta.url);
const source = readFileSync(new URL('studio_architecture_reader.js', root), 'utf8');
const plain = value => JSON.parse(JSON.stringify(value));

function load() {
  const sandbox = {window: {}};
  runInNewContext(source, sandbox);
  return sandbox.window.AuteurStudioArchitectureReader;
}

function element(tag) {
  return {
    tag, children: [], textContent: '', className: '', attrs: {},
    append(...items) { this.children.push(...items); },
    appendChild(item) { this.children.push(item); return item; },
    replaceChildren(...items) { this.children = items; },
    setAttribute(key, value) { this.attrs[key] = value; },
  };
}

function documentStub() {
  return {createElement: element};
}

function textOf(node) {
  if (!node || typeof node !== 'object') return '';
  return (node.textContent || '') + (node.children || []).map(textOf).join(' ');
}

const sample = {
  schema_version: 2,
  summary: 'Wonder survives dread through a costly promise.',
  nodes: [
    {id: 'wonder-engine', title: 'Wonder engine', category: 'engine',
     summary: 'Discovery keeps widening the possible world.'},
    {id: 'wonder-genre', title: 'Wonder', category: 'genre',
     summary: 'Wonder governs the opening.'},
    {id: 'dread-genre', title: 'Dread', category: 'genre',
     summary: 'Dread pressures wonder.'},
  ],
  links: [
    {id: 'wonder-cost', source: 'wonder-engine', target: 'dread-genre',
     function: 'makes discovery costly'},
  ],
  emotion_targets: [
    {id: 'awe', emotion: 'joy', role: 'primary',
     intended_effect: 'Awe at a larger world.',
     eliciting_condition: 'Discovery reveals more than expected.',
     aesthetic_strategy: 'Scale and delayed revelation.',
     provenance: 'agent_proposed'},
    {id: 'fear', emotion: 'fear', role: 'supporting',
     intended_effect: 'Fear of the cost.',
     eliciting_condition: 'A discovery endangers someone.',
     aesthetic_strategy: 'Intimate sensory contrast.',
     provenance: 'author_declared'},
  ],
  complex_emotions: [
    {id: 'tragic-wonder', title: 'Tragic wonder',
     basic_emotions: ['joy', 'sadness'], context: 'Beauty carries loss.'},
  ],
  genre_contracts: [
    {genre_node_id: 'wonder-genre', role: 'governing',
     emotion_target_ids: ['awe'], complex_emotion_ids: ['tragic-wonder'],
     trope_functions: ['The forbidden discovery'],
     narrative_engine: 'Discovery widens the world.',
     structural_pattern: 'Discovery, awe, consequence.',
     aesthetic_strategies: ['Vast scale.'],
     payoff_expectations: ['Wonder survives loss.']},
    {genre_node_id: 'dread-genre', role: 'supporting',
     emotion_target_ids: ['fear'], complex_emotion_ids: [],
     trope_functions: ['The cost of knowledge'],
     narrative_engine: 'Knowledge makes the world dangerous.',
     structural_pattern: 'Discovery, threat, choice.',
     aesthetic_strategies: ['Intimate menace.'],
     payoff_expectations: ['Fear becomes meaningful.']},
  ],
  genre_interactions: [
    {id: 'wonder-dread', source_genre_id: 'dread-genre',
     target_genre_id: 'wonder-genre', kind: 'constrains',
     mechanism: 'Dread keeps wonder from becoming escape.'},
  ],
  phases: [
    {id: 'middle', title: 'Middle', order: 1,
     narrative_function: 'Turn wonder into risk.',
     reader_experience: 'Uneasy awe.',
     transition: 'A discovery costs a memory.',
     parallel_with: []},
    {id: 'opening', title: 'Opening', order: 0,
     narrative_function: 'Establish wonder.',
     reader_experience: 'Open awe.',
     transition: 'The first cost appears.'},
  ],
  open_questions: ['How much wonder should survive the ending?'],
};

test('reader projects a complete, readable working proposal', () => {
  const api = load();
  const p = api.project(sample);
  assert.equal(p.status, 'ready');
  assert.equal(p.authority, 'working_proposal');
  assert.match(p.authorityLabel, /working proposal/i);
  assert.equal(p.summary, sample.summary);
  assert.deepEqual(plain(p.emotions.map(item => item.role)), ['primary', 'supporting']);
  assert.equal(p.emotions[0].label, 'joy');
  assert.equal(p.emotions[0].intendedEffect, 'Awe at a larger world.');
  assert.equal(p.complexEmotions[0].title, 'Tragic wonder');
  assert.equal(p.genres[0].title, 'Wonder');
  assert.equal(p.genres[0].role, 'governing');
  assert.deepEqual(plain(p.genres[0].tropeFunctions), ['The forbidden discovery']);
  assert.deepEqual(plain(p.tropes.map(item => item.text)), [
    'The forbidden discovery', 'The cost of knowledge',
  ]);
  assert.deepEqual(plain(p.structure.map(item => item.id)), ['opening', 'middle']);
  assert.equal(p.structure[0].narrativeFunction, 'Establish wonder.');
  assert.ok(p.mechanisms.some(item => item.id === 'wonder-engine'));
  assert.ok(p.relationships.some(item => item.id === 'wonder-cost'));
  assert.ok(p.relationships.some(item => item.id === 'wonder-dread'));
  assert.equal(p.relationships.find(item => item.id === 'wonder-cost').from, 'Wonder engine');
  assert.deepEqual(plain(p.uncertainties), sample.open_questions);
});

test('reader exposes a truthful empty state without inventing design', () => {
  const api = load();
  for (const value of [null, undefined, {}, {schema_version: 2}]) {
    const p = api.project(value);
    assert.equal(p.status, 'empty');
    assert.match(p.summary, /no working architecture/i);
    assert.deepEqual(plain(p.emotions), []);
    assert.deepEqual(plain(p.genres), []);
    assert.deepEqual(plain(p.tropes), []);
    assert.deepEqual(plain(p.structure), []);
    assert.deepEqual(plain(p.mechanisms), []);
    assert.deepEqual(plain(p.relationships), []);
    assert.deepEqual(plain(p.uncertainties), []);
  }
});

test('reader tolerates malformed optional fields without crashing', () => {
  const api = load();
  const p = api.project({
    schema_version: 2,
    summary: 'Sparse proposal.',
    nodes: [{id: 'engine', title: 'Engine', category: 'engine'}, null, {id: 4}],
    emotion_targets: [{id: 'awe', emotion: 'joy'}],
    phases: [{id: 'phase', title: 'Phase', order: 'not a number'}],
    open_questions: [null, 'A real question'],
  });
  assert.equal(p.status, 'ready');
  assert.equal(p.emotions.length, 1);
  assert.equal(p.structure.length, 1);
  assert.equal(p.structure[0].order, 0);
  assert.deepEqual(plain(p.uncertainties), ['A real question']);
});

test('reader renders text-first sections and never injects HTML', () => {
  const api = load();
  const hostile = {
    ...sample,
    summary: '<img src=x onerror=alert(1)>',
    open_questions: ['<script>alert(2)</script>'],
  };
  const projection = api.project(hostile);
  const container = element('section');
  const document = documentStub();
  api.render(container, projection, document);
  const text = textOf(container);
  assert.match(text, /Your narrative architecture/);
  assert.match(text, /Emotional promise/);
  assert.match(text, /Genres and their work/);
  assert.match(text, /Functional tropes/);
  assert.match(text, /Structure/);
  assert.match(text, /Narrative mechanisms/);
  assert.match(text, /Relationships/);
  assert.match(text, /Open questions/);
  assert.match(text, /Working proposal/);
  assert.match(text, /<img src=x onerror=alert\(1\)>/);
  assert.match(text, /<script>alert\(2\)<\/script>/);
  assert.doesNotMatch(source, /innerHTML|outerHTML|insertAdjacentHTML|document\.write/);
  assert.doesNotMatch(source, /\bfetch\s*\(|XMLHttpRequest|accept_story|acceptStoryIdentity/);
});

test('reader render handles an empty projection with an honest message', () => {
  const api = load();
  const container = element('section');
  api.render(container, api.project(null), documentStub());
  const text = textOf(container);
  assert.match(text, /No working architecture/);
  assert.doesNotMatch(text, /undefined/);
});
