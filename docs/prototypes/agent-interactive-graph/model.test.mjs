import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolveAnchor, recordedRelations, listSelectableAnchors} from './model.mjs';

const RICH_SHA = 'c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66';
const candidate = JSON.parse(readFileSync(
  new URL('../../qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json', import.meta.url),
  'utf8',
));
const sparse = JSON.parse(readFileSync(
  new URL('../../qualification-evidence/agent-first-ontology-20261103/sparse-vision-candidate.json', import.meta.url),
  'utf8',
));

const anchor = (kind, id) => ({kind, id});

test('node and link anchors remain distinct and source-bound', () => {
  const engine = resolveAnchor(candidate, RICH_SHA, anchor('node', 'memory_economy'));
  const link = resolveAnchor(candidate, RICH_SHA, anchor('link', 'engine_drives_cost'));
  assert.equal(engine.sourceRef, 'nodes/3');
  assert.equal(link.sourceRef, 'links/3');
  assert.equal(engine.authority, 'working_proposal');
  assert.equal(link.authority, 'working_proposal');
  assert.equal(engine.request_sha256, RICH_SHA);
  assert.equal(link.request_sha256, RICH_SHA);
  assert.equal(engine.id, 'memory_economy');
  assert.equal(link.id, 'engine_drives_cost');
  assert.notEqual(engine.kind, link.kind);
  assert.equal(engine.title, 'Memory economy');
  assert.match(engine.meaning, /transfers a memory/i);
  assert.match(link.meaning, /personal loss/i);
});

test('missing relation stays unknown without inferred edges', () => {
  const engine = anchor('node', 'memory_economy');
  const wonder = anchor('emotion_target', 'wonder');
  assert.deepEqual(recordedRelations(candidate, [engine, wonder]), []);
  assert.match(
    JSON.stringify(resolveAnchor(candidate, RICH_SHA, engine)),
    /engine_drives_cost/,
  );
  assert.doesNotMatch(
    JSON.stringify(resolveAnchor(candidate, RICH_SHA, engine)),
    /"to":\{"kind":"emotion_target","id":"wonder"/,
  );
});

test('one node exposes only directed incident links and explicit references', () => {
  const relations = recordedRelations(candidate, [anchor('node', 'memory_economy')]);
  const linkIds = relations.filter(item => item.kind === 'link').map(item => item.id);
  assert.deepEqual(linkIds.sort(), ['engine_drives_cost', 'engine_feeds_archive', 'magical_map_instantiates']);
  assert.ok(relations.every(item => item.authority === 'working_proposal'));
  assert.ok(relations.every(item => /^(nodes|links|genre_contracts|genre_interactions|phases)\/\d+/.test(item.sourceRef)));
  assert.ok(relations.some(item => item.direction === 'incoming'));
  assert.ok(relations.some(item => item.direction === 'outgoing'));
});

test('two node anchors return only relations recorded between them', () => {
  const relations = recordedRelations(candidate, [
    anchor('node', 'memory_economy'),
    anchor('node', 'cost_escalation'),
  ]);
  assert.deepEqual(relations.map(item => item.id), ['engine_drives_cost']);
  assert.equal(relations[0].from.id, 'memory_economy');
  assert.equal(relations[0].to.id, 'cost_escalation');
  const reversed = recordedRelations(candidate, [
    anchor('node', 'cost_escalation'),
    anchor('node', 'memory_economy'),
  ]);
  assert.deepEqual(reversed.map(item => item.id), ['engine_drives_cost']);
  assert.equal(reversed[0].direction, 'incoming');
});

test('no transitive edge is created between indirectly connected nodes', () => {
  const relations = recordedRelations(candidate, [
    anchor('node', 'memory_economy'),
    anchor('node', 'earned_hope'),
  ]);
  assert.deepEqual(relations, []);
});

test('genre identity and genre contract key remain explicit and inspectable', () => {
  const contract = resolveAnchor(candidate, RICH_SHA, anchor('genre_contract', 'literary_mystery'));
  assert.equal(contract.sourceRef, 'genre_contracts/0');
  assert.equal(contract.id, 'literary_mystery');
  assert.match(contract.meaning, /archive/i);
  const emotionRelations = recordedRelations(candidate, [
    anchor('genre_contract', 'literary_mystery'),
    anchor('emotion_target', 'wonder'),
  ]);
  assert.equal(emotionRelations.length, 1);
  assert.equal(emotionRelations[0].kind, 'emotion_target_reference');
  assert.equal(emotionRelations[0].from.id, 'literary_mystery');
  assert.equal(emotionRelations[0].to.id, 'wonder');
  assert.match(emotionRelations[0].detail, /Wonder at the coast/i);
});

test('phase and genre activation references are source-bound', () => {
  const phaseRelations = recordedRelations(candidate, [
    anchor('phase', 'strange_coast'),
    anchor('genre_contract', 'literary_mystery'),
  ]);
  assert.equal(phaseRelations.length, 1);
  assert.equal(phaseRelations[0].kind, 'phase_activation');
  assert.equal(phaseRelations[0].from.id, 'strange_coast');
  assert.equal(phaseRelations[0].to.id, 'literary_mystery');
  assert.equal(phaseRelations[0].sourceRef, 'phases/0');
  assert.match(phaseRelations[0].detail, /inquiry/i);
});

test('genre interactions preserve direction and kind without hiding the recorded link', () => {
  const relations = recordedRelations(candidate, [
    anchor('node', 'horror'),
    anchor('node', 'literary_mystery'),
  ]);
  assert.equal(relations.length, 3);
  const interactions = relations.filter(item => item.kind === 'genre_interaction');
  assert.equal(interactions.length, 2);
  const outgoing = interactions.find(item => item.direction === 'outgoing');
  const incoming = interactions.find(item => item.direction === 'incoming');
  assert.ok(outgoing);
  assert.ok(incoming);
  assert.equal(outgoing.id, 'horror_pressures_mystery');
  assert.equal(outgoing.from.id, 'horror');
  assert.equal(outgoing.to.id, 'literary_mystery');
  assert.match(outgoing.detail, /clean triumph/i);
  assert.equal(incoming.id, 'mystery_horror_converge');
  assert.equal(incoming.from.id, 'literary_mystery');
  assert.equal(incoming.to.id, 'horror');
  const link = relations.find(item => item.kind === 'link');
  assert.ok(link);
  assert.equal(link.id, 'horror_pressures_mystery');
  assert.equal(link.from.id, 'horror');
  assert.equal(link.to.id, 'literary_mystery');
});

test('same-name trope text does not unify two genre contracts', () => {
  const synthetic = {
    schema_version: 2,
    summary: 'Synthetic duplicate phrase case.',
    nodes: [
      {id: 'genre_a', title: 'Genre A', category: 'genre', summary: 'A'},
      {id: 'genre_b', title: 'Genre B', category: 'genre', summary: 'B'},
    ],
    links: [],
    phases: [],
    emotion_targets: [],
    complex_emotions: [],
    genre_contracts: [
      {genre_node_id: 'genre_a', role: 'governing', emotion_target_ids: [], complex_emotion_ids: [],
       trope_functions: ['Shared phrase'], narrative_engine: 'A engine', structural_pattern: 'A pattern',
       aesthetic_strategies: [], payoff_expectations: ['A payoff']},
      {genre_node_id: 'genre_b', role: 'supporting', emotion_target_ids: [], complex_emotion_ids: [],
       trope_functions: ['Shared phrase'], narrative_engine: 'B engine', structural_pattern: 'B pattern',
       aesthetic_strategies: [], payoff_expectations: ['B payoff']},
    ],
    genre_interactions: [],
    open_questions: [],
  };
  assert.deepEqual(recordedRelations(synthetic, [
    anchor('genre_contract', 'genre_a'),
    anchor('genre_contract', 'genre_b'),
  ]), []);
});

test('identical titles with distinct IDs do not rebind by title', () => {
  const synthetic = {
    schema_version: 2,
    summary: 'Titles can collide; IDs are the identity.',
    nodes: [
      {id: 'engine_one', title: 'Discovery engine', category: 'engine', summary: 'First meaning.'},
      {id: 'engine_two', title: 'Discovery engine', category: 'engine', summary: 'Second meaning.'},
    ],
    links: [],
    phases: [],
    emotion_targets: [],
    complex_emotions: [],
    genre_contracts: [],
    genre_interactions: [],
    open_questions: [],
  };
  const first = resolveAnchor(synthetic, 'a'.repeat(64), anchor('node', 'engine_one'));
  const second = resolveAnchor(synthetic, 'a'.repeat(64), anchor('node', 'engine_two'));
  assert.equal(first.sourceRef, 'nodes/0');
  assert.equal(second.sourceRef, 'nodes/1');
  assert.equal(first.meaning, 'First meaning.');
  assert.equal(second.meaning, 'Second meaning.');
  assert.equal(resolveAnchor(synthetic, 'a'.repeat(64), anchor('node', 'missing')), null);
});

test('sparse candidate has no invented genre or relationship', () => {
  const anchors = listSelectableAnchors(sparse);
  assert.equal(anchors.some(item => item.kind === 'genre_contract'), false);
  assert.equal(anchors.some(item => item.kind === 'genre_interaction'), false);
  assert.equal(anchors.some(item => item.kind === 'node' && item.category === 'genre'), false);
  assert.deepEqual(recordedRelations(sparse, [
    anchor('node', 'repair_engine'),
    anchor('emotion_target', 'trust'),
  ]), []);
});

test('invalid anchor shapes and SHA values fail closed', () => {
  assert.equal(resolveAnchor(candidate, 'not-a-sha', anchor('node', 'memory_economy')), null);
  assert.equal(resolveAnchor(candidate, RICH_SHA, anchor('unknown', 'memory_economy')), null);
  assert.equal(resolveAnchor(candidate, RICH_SHA, {kind: 'node'}), null);
  assert.equal(resolveAnchor(candidate, RICH_SHA, null), null);
});

test('selectable anchors expose stable kinds and IDs without inferred fields', () => {
  const anchors = listSelectableAnchors(candidate, RICH_SHA);
  assert.ok(anchors.some(item => item.kind === 'node' && item.id === 'memory_economy'));
  assert.ok(anchors.some(item => item.kind === 'link' && item.id === 'engine_drives_cost'));
  assert.ok(anchors.some(item => item.kind === 'emotion_target' && item.id === 'wonder'));
  assert.ok(anchors.some(item => item.kind === 'genre_contract' && item.id === 'literary_mystery'));
  assert.ok(anchors.some(item => item.kind === 'genre_interaction' && item.id === 'mystery_enables_fantasy'));
  assert.ok(anchors.some(item => item.kind === 'phase' && item.id === 'strange_coast'));
  for (const item of anchors) {
    assert.match(item.sourceRef, /^(nodes|links|genre_interactions|emotion_targets|genre_contracts|phases)\/\d+$/);
    assert.equal(item.authority, 'working_proposal');
    assert.equal(item.request_sha256, RICH_SHA);
  }
});
