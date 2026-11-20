// Recorded genre interactions, phase activations and reader-experience links are navigable (#620).
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

class Element {
  constructor(tag = 'div') { this.tag = tag; this.children = []; this.textContent = ''; this.events = {}; this.className = ''; this.attributes = {}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener(name, fn) { this.events[name] = fn; }
  setAttribute(name, value) { this.attributes[name] = value; }
}
const document = {createElement: tag => new Element(tag)};
const window = {};
for (const path of ['studio_explanations.js', 'studio_explanation_views.js']) {
  vm.runInNewContext(readFileSync(new URL('../src/auteur/beginner/browser/' + path, import.meta.url), 'utf8'), {window, document});
}
const api = window.AuteurStudioExplanations, views = window.AuteurStudioExplanationViews;
const contract = (id, role, targets) => ({genre_node_id: id, role, emotion_target_ids: targets, trope_functions: ['f ' + id],
  narrative_engine: 'engine ' + id, structural_pattern: 'pattern ' + id, payoff_expectations: ['payoff']});
const candidate = {
  nodes: [
    {id: 'mystery', title: 'Records mystery', category: 'genre'}, {id: 'thriller', title: 'Succession thriller', category: 'genre'},
    {id: 'pyrrhic', title: 'Pyrrhic victory', category: 'trope'}, {id: 'grief', title: 'Grief with defiant hope', category: 'reader_experience'},
  ],
  links: [{id: 'pyrrhic-evokes', source: 'pyrrhic', target: 'grief', function: 'aims to evoke'}],
  emotion_targets: [{id: 'curious', emotion: 'joy', role: 'primary', intended_effect: 'Delight.'},
                    {id: 'dread', emotion: 'fear', role: 'supporting', intended_effect: 'Dread.'}],
  genre_contracts: [contract('mystery', 'governing', ['curious']), contract('thriller', 'supporting', ['dread'])],
  genre_interactions: [{id: 'squeeze', source_genre_id: 'thriller', target_genre_id: 'mystery', kind: 'constrains',
    mechanism: 'Deadlines stop verification.', risk: 'Fairness erodes too early.'}],
  phases: [
    {id: 'late', title: 'Book 2 · War', order: 2, narrative_function: 'War.',
     genre_activations: [{genre_node_id: 'thriller', basic_emotions: ['fear', 'surprise'], structural_function: 'The race.'}]},
    {id: 'early', title: 'Book 1 · Inquiry', order: 1, narrative_function: 'Inquiry.',
     genre_activations: [{genre_node_id: 'thriller', basic_emotions: ['fear'], structural_function: 'First weaponised truth.'},
                         {genre_node_id: 'mystery', basic_emotions: ['joy'], structural_function: 'Fair clues.'}]},
  ],
};
const packet = api.project(candidate, 'sha', null);
const linksOf = (facet, key) => JSON.parse(JSON.stringify(api.linksFor(packet, {facet, key})));

test('a typed genre interaction is a navigable relationship carrying its mechanism and risk, in both directions', () => {
  const forward = linksOf('genres', 'genre:thriller').find(l => l.targetKey === 'genre:mystery');
  assert.equal(forward.relationVerb, 'constrains');
  assert.equal(forward.sourceRef, 'genre_interactions/squeeze');
  assert.match(forward.explanation, /Deadlines stop verification\. Risk: Fairness erodes too early\./);
  const reverse = linksOf('genres', 'genre:mystery').find(l => l.targetKey === 'genre:thriller');
  assert.equal(reverse.direction, 'reverse');
  assert.equal(reverse.relationVerb, 'constrained by');
});

test('a genre lists the phases that activate it, in story order, with its local function', () => {
  const phases = linksOf('genres', 'genre:thriller').filter(l => l.targetFacet === 'timeline');
  assert.deepEqual(phases.map(l => l.targetKey), ['phase:early', 'phase:late']);
  assert.equal(phases[0].relationVerb, 'active in');
  assert.equal(phases[0].explanation, 'fear · First weaponised truth.');
  assert.equal(phases[1].explanation, 'fear, surprise · The race.');
  assert.equal(phases[0].sourceRef, 'phases/early/genre_activations/thriller');
  assert.ok(api.resolve(packet, 'timeline', 'phase:early', 'sha'));
});

test('a declared trope-to-reader-experience link is navigable; genre targets still never become trope edges', () => {
  const evokes = linksOf('tropes', 'trope-node:pyrrhic');
  assert.deepEqual(evokes.map(l => [l.relationVerb, l.targetFacet, l.targetKey]),
    [['aims to evoke', 'emotions', 'emotion-node:grief']]);
  assert.equal(api.resolve(packet, 'emotions', 'emotion-node:grief', 'sha').title, 'Grief with defiant hope');
  assert.equal(linksOf('tropes', 'trope:thriller:0').filter(l => l.targetFacet === 'emotions').length, 0);
});

test('a phase reads its genres as "activates"; a repeated activation stays one link; unknown kinds stay generic', () => {
  const fromPhase = linksOf('timeline', 'phase:early');
  assert.ok(fromPhase.some(l => l.targetKey === 'genre:thriller' && l.relationVerb === 'activates'));
  const twice = JSON.parse(JSON.stringify(candidate));
  twice.phases[0].genre_activations.push({genre_node_id: 'thriller', basic_emotions: ['joy'], structural_function: 'Again.'});
  twice.genre_interactions.push({id: 'odd', source_genre_id: 'mystery', target_genre_id: 'thriller', kind: 'mirrors',
    mechanism: 'Unknown kind.'});
  const p = api.project(twice, 'sha', null);
  const active = p.links.filter(l => l.relationVerb === 'active in');
  assert.equal(active.filter(l => l.targetKey === 'phase:late' && l.fromKey === 'genre:thriller').length, 1);
  assert.equal(new Set(active.map(l => l.id)).size, active.length);
  const odd = JSON.parse(JSON.stringify(api.linksFor(p, {facet: 'genres', key: 'genre:thriller'})))
    .find(l => l.sourceRef === 'genre_interactions/odd');
  assert.equal(odd.relationVerb, 'related through “mirrors”');
});

test('a candidate without genre contracts yields no genre or phase links', () => {
  const bare = {nodes: [{id: 'g', title: 'G', category: 'genre'}], phases: [{id: 'p', title: 'P', order: 1,
    narrative_function: 'x', genre_activations: [{genre_node_id: 'g', basic_emotions: [], structural_function: 's'}]}]};
  const links = JSON.parse(JSON.stringify(api.project(bare, 'sha', null).links));
  assert.deepEqual(links.filter(l => l.fromFacet === 'genres' || l.targetFacet === 'genres'), []);
});

test('the genre explanation groups relationships by perspective and shows why each holds', () => {
  const root = new Element();
  views.renderGenre(root, packet, 'genre:thriller', () => {}, () => {});
  const headings = [], notes = [];
  (function visit(node) {
    if (node.tag === 'h4') headings.push(node.textContent);
    if (node.className === 'studio-semantic-why') notes.push(node.textContent);
    node.children.forEach(visit);
  })(root);
  assert.deepEqual(headings, ['Genres', 'Reader emotions', 'Tropes', 'Structure and engines',
    'Across the story']);
  assert.ok(notes.includes('Deadlines stop verification. Risk: Fairness erodes too early.'));
  assert.ok(notes.includes('fear · First weaponised truth.'));
  // Each reason is announced with its button.
  const described = [];
  (function visit(node) { if (node.attributes['aria-describedby']) described.push(node.attributes['aria-describedby']);
    node.children.forEach(visit); })(root);
  assert.ok(described.length >= notes.length);
});
