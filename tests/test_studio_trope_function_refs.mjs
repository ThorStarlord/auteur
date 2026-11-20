// Source-qualified trope-function references: one trope node reached from each genre-specific function (#622 follow-up).
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
vm.runInNewContext(readFileSync(new URL('../src/auteur/beginner/browser/studio_explanations.js', import.meta.url), 'utf8'), {window, document});
const api = window.AuteurStudioExplanations;
const plain = value => JSON.parse(JSON.stringify(value));

function candidate() {
  return {
    nodes: [
      {id: 'mystery', title: 'Records mystery', category: 'genre'},
      {id: 'thriller', title: 'Succession thriller', category: 'genre'},
      {id: 'pyrrhic', title: 'Pyrrhic victory', category: 'trope', summary: 'Winning is the cost.'},
    ],
    links: [],
    genre_contracts: [
      {genre_node_id: 'mystery', role: 'governing', trope_functions: ['The altered record gives clues a second meaning.'],
       trope_function_refs: [{function_index: 0, trope_node_id: 'pyrrhic'}], narrative_engine: 'e', structural_pattern: 's', payoff_expectations: ['p']},
      {genre_node_id: 'thriller', role: 'supporting', trope_functions: ['Winning costs the heir.'],
       trope_function_refs: [{function_index: 0, trope_node_id: 'pyrrhic'}], narrative_engine: 'e', structural_pattern: 's', payoff_expectations: ['p']},
    ],
    phases: [],
  };
}

test('one trope node is reached from each genre-specific function that realises it, and never merged with them', () => {
  const p = api.project(candidate(), 'sha', null);
  const reached = plain(api.linksFor(p, {facet: 'tropes', key: 'trope-node:pyrrhic'}));
  assert.deepEqual(reached.map(l => l.sourceRef).sort(),
    ['genre_contracts/mystery/trope_function_refs/0', 'genre_contracts/thriller/trope_function_refs/0']);
  assert.ok(reached.every(l => l.direction === 'reverse' && l.relationVerb === 'performed as a function here'));
  const forward = plain(api.linksFor(p, {facet: 'tropes', key: 'trope:thriller:0'})).find(l => l.targetKey === 'trope-node:pyrrhic');
  assert.equal(forward.relationVerb, 'realises trope');
  assert.equal(p.tropes.filter(t => t.key === 'trope-node:pyrrhic').length, 1);
  assert.notEqual(api.resolve(p, 'tropes', 'trope:mystery:0', 'sha').title,
    api.resolve(p, 'tropes', 'trope:thriller:0', 'sha').title);
});

test('a reference that names no recorded function or node creates no link', () => {
  const c = candidate();
  c.genre_contracts[0].trope_function_refs = [{function_index: 9, trope_node_id: 'pyrrhic'}];
  c.genre_contracts[1].trope_function_refs = [{function_index: 0, trope_node_id: 'missing'}];
  const p = plain(api.project(c, 'sha', null));
  assert.equal(p.links.filter(l => l.sourceRef.includes('trope_function_refs')).length, 0);
});

test('a phase activation reference resolves to the phase function entry and reaches the same trope node', () => {
  const c = candidate();
  c.phases = [{id: 'war', title: 'The war', order: 1, narrative_function: 'War.',
    genre_activations: [{genre_node_id: 'thriller', basic_emotions: ['fear'],
      trope_functions: ['Winning costs the heir.'],
      trope_function_refs: [{function_index: 0, trope_node_id: 'pyrrhic'}], structural_function: 'Race.'}]}];
  const p = plain(api.project(c, 'sha', null));
  const phaseLink = p.links.find(l => l.sourceRef === 'phases/war/genre_activations/thriller#0/trope_function_refs/0');
  assert.equal(phaseLink && phaseLink.sourceKind, 'phase');
  assert.ok(phaseLink, 'phase reference must produce a link, not be dropped');
  assert.equal(phaseLink.fromKey, 'phase-trope:war:thriller:0');
  assert.equal(phaseLink.targetKey, 'trope-node:pyrrhic');
  const reached = plain(api.linksFor(p, {facet: 'tropes', key: 'trope-node:pyrrhic'}));
  assert.equal(reached.length, 3);
});
