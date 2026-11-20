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

test('reader opens with one line per narrative system and keeps the full text one disclosure away', () => {
  const api = load();
  const decided = {...sample, interpretations: [{id: 'reading', interpretation: 'Memory is currency.',
    affects: ['wonder-engine'], consequences: 'Discovery costs memory.', author_decision_required: true}]};
  const container = element('section');
  api.render(container, api.project(decided), documentStub());
  const glanceIndex = container.children.findIndex(child => child.textContent === 'At a glance');
  const glance = textOf(container.children[glanceIndex + 1]);
  assert.match(glance, /Emotional promise: joy \(primary\) · fear \(supporting\)/);
  assert.match(glance, /Narrative engines: Wonder engine/);
  assert.match(glance, /Genres: Wonder \(governing\) · Dread \(supporting\)/);
  assert.match(glance, /How genres interact: Dread constrains Wonder/);
  assert.match(glance, /Development: 2 phases — Opening → Middle/);
  assert.match(glance, /Needs your decision: 1/);
  assert.match(glance, /Open questions: 1/);
  // Every long section lives inside the collapsed "Read the full architecture" disclosure.
  const full = container.children.find(child => child.tag === 'details');
  assert.equal(full.className, 'architecture-reader-full');
  assert.equal(full.open, false);
  assert.equal(full.children[0].tag, 'summary');
  assert.match(full.children[0].textContent, /Read the full architecture/);
  for (const heading of ['Emotional promise', 'Genres and their work', 'Functional tropes', 'Relationships',
    'Readings the agent is using', 'Open questions']) {
    assert.ok(full.children.some(child => child.tag === 'h3' && child.textContent.startsWith(heading)), heading);
    assert.ok(!container.children.some(child => child.tag === 'h3' && child.textContent.startsWith(heading)), heading);
  }
});

test('reader keeps the full architecture open across a re-render', () => {
  const api = load();
  const container = element('section');
  container.querySelector = selector => selector === '.architecture-reader-full[open]' &&
    container.children.find(child => child.tag === 'details' && child.open) || null;
  api.render(container, api.project(sample), documentStub());
  container.children.find(child => child.tag === 'details').open = true;
  api.render(container, api.project(sample), documentStub());
  assert.equal(container.children.find(child => child.tag === 'details').open, true);
});

test('reader render handles an empty projection with an honest message', () => {
  const api = load();
  const container = element('section');
  api.render(container, api.project(null), documentStub());
  const text = textOf(container);
  assert.match(text, /No working architecture/);
  assert.doesNotMatch(text, /undefined/);
});

const premiseStatus = {
  governingObjective: {
    authority: 'author_expressed',
    story_vision: 'An optimistic seventy-Book series about repairing a ruined climate.',
    instruction: null,
    note: 'The author expressed creative objective for this working proposal.',
  },
  premiseStatus: {
    authority: 'working_architecture_not_canon',
    author_expressed: {emotion_targets: ['wonder']},
    accepted: {source: null, commitments: {}},
    provisional_agent_interpretation: {
      summary: true, nodes: ['wonder-engine'], links: ['wonder-cost'],
    },
    unresolved: {open_questions: ['How much wonder should survive the ending?']},
  },
};

test('reader names the author objective and premise status without claiming acceptance', () => {
  const api = load();
  const container = element('section');
  api.render(container, api.project(sample, premiseStatus), documentStub());
  const text = textOf(container);
  assert.match(text, /What this proposal is/);
  assert.match(text, /Author objective:/);
  assert.match(text, /seventy-Book series/);
  assert.match(text, /Author-named: wonder/);
  assert.match(text, /Agent interpretation: 1 mechanisms, 1 relationships/);
  assert.match(text, /Accepted commitments: none yet/);
  assert.match(text, /Unresolved: 1 open question/);
  assert.doesNotMatch(text, /Accepted Story Identity/);
});

test('reader omits the status section when no status is supplied', () => {
  const api = load();
  const p = api.project(sample);
  assert.equal(p.governingObjective, null);
  assert.equal(p.premiseStatus, null);
  const container = element('section');
  api.render(container, p, documentStub());
  assert.doesNotMatch(textOf(container), /What this proposal is/);
});

const withOpportunity = Object.assign({}, sample, {
  opportunities: [{
    id: 'archive-city',
    title: 'The archive becomes a city',
    why_it_matters: 'A late Book could expose the keepers as an institution.',
    scope: 'series',
  }],
});

test('reader surfaces optional opportunities as explicitly not accepted', () => {
  const api = load();
  const p = api.project(withOpportunity);
  assert.equal(p.opportunities.length, 1);
  assert.equal(p.opportunities[0].scope, 'series');
  const container = element('section');
  api.render(container, p, documentStub());
  const text = textOf(container);
  assert.match(text, /Optional opportunities \(not accepted\)/);
  assert.match(text, /The archive becomes a city/);
});

test('reader omits the opportunity section when none is proposed', () => {
  const api = load();
  const container = element('section');
  api.render(container, api.project(sample), documentStub());
  assert.doesNotMatch(textOf(container), /Optional opportunities/);
});

const replacingOpportunity = Object.assign({}, sample, {
  opportunities: [{
    id: 'tragic-replacement',
    title: 'The compact fails and hope was naive',
    why_it_matters: 'A tragic frame may sharpen institutional pressure.',
    scope: 'series',
    relationship: 'replaces',
    requires_author_decision: true,
  }],
});

const deepeningOpportunity = Object.assign({}, sample, {
  opportunities: [{
    id: 'darker-middle',
    title: 'A devastating middle Book',
    why_it_matters: 'Cost can make the eventual hope load-bearing.',
    scope: 'series',
    relationship: 'deepens',
    requires_author_decision: false,
  }],
});

test('reader marks an alternative that would replace the expressed purpose', () => {
  const api = load();
  const p = api.project(replacingOpportunity);
  assert.equal(p.opportunities[0].relationship, 'replaces');
  assert.equal(p.opportunities[0].requiresAuthorDecision, true);
  const container = element('section');
  api.render(container, p, documentStub());
  const text = textOf(container);
  assert.match(text, /would replace your purpose: your decision required/);
  assert.match(text, /\(series, replaces\)/);
});

test('reader does not demand a decision for a deepening alternative', () => {
  const api = load();
  const container = element('section');
  api.render(container, api.project(deepeningOpportunity), documentStub());
  const text = textOf(container);
  assert.match(text, /\(series, deepens\)/);
  assert.doesNotMatch(text, /would replace your purpose/);
});

const provisionalOpportunity = Object.assign({}, sample, {
  opportunities: [{
    id: 'consent-tragedy',
    title: 'The vote is a tragedy',
    why_it_matters: 'A different answer to what the voyage is for.',
    scope: 'series',
    relationship: 'replaces',
    provisional_primary: true,
  }],
});

test('reader marks a provisional primary as a working selection only', () => {
  const api = load();
  const p = api.project(provisionalOpportunity);
  assert.equal(p.opportunities[0].provisionalPrimary, true);
  const container = element('section');
  api.render(container, p, documentStub());
  const text = textOf(container);
  assert.match(text, /the agent provisional primary under your delegated goal discovery/);
  assert.doesNotMatch(text, /Accepted Story Identity/);
});

test('reader states that an agent-assigned emotion label came from the agent', () => {
  const api = load();
  const declaredId = api.project(sample).emotions.filter(e => e.provenance === 'author_declared').map(e => e.id)[0];
  const status = {authorEmotionGrounding: [{id: declaredId, emotion: 'joy', emotion_named_by_author: false}]};
  const p = api.project(sample, status);
  const container = element('section');
  api.render(container, p, documentStub());
  const text = textOf(container);
  assert.match(text, /experience described by the author; emotion label assigned by the agent/);
  assert.doesNotMatch(text, /\[author declared\]/);
});

test('reader keeps the author-declared label when the author named the emotion', () => {
  const api = load();
  const declaredId = api.project(sample).emotions.filter(e => e.provenance === 'author_declared').map(e => e.id)[0];
  const status = {authorEmotionGrounding: [{id: declaredId, emotion: 'joy', emotion_named_by_author: true}]};
  const container = element('section');
  api.render(container, api.project(sample, status), documentStub());
  assert.match(textOf(container), /\[author declared\]/);
});
