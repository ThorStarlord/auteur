// Atelier Book development helpers: they say the Working Book owner's review in words without deciding
// anything. A mechanical link stays a link to inspect; an author decision stays the author's.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const browser = new URL('../src/auteur/beginner/browser/', import.meta.url);
const sandbox = {window: {}};
runInNewContext(readFileSync(new URL('studio_atelier_series.js', browser), 'utf8'), sandbox);
runInNewContext(readFileSync(new URL('studio_atelier_book.js', browser), 'utf8'), sandbox);
const B = sandbox.window.AuteurAtelierBook;
const plain = (value) => JSON.parse(JSON.stringify(value));

const elements = [
  {id: 'eng-record-form', collection: 'engines', text: 'Ledger as a new record form: the lineage needs proof of training.'},
  {id: 'edge-hands', collection: 'typed_edges', text: 'The craft-mark shows who can give return labour.'},
  {id: 'dec-settlement', collection: 'open_author_decisions', text: 'Whether the conversion settles.'},
];
const review = {
  request_sha256: 'a'.repeat(64), revision_number: 2, mode: 'targeted', applicable: true, instruction: 'Make the cost visible.',
  baseline: {request_sha256: 'b'.repeat(64), content_sha256: 'c'.repeat(64), revision_number: 1},
  permitted_ids: ['edge-hands', 'eng-record-form'],
  changes: {added: [], removed: [], changed: [{id: 'eng-record-form', classification: 'interpretive', fields_changed: ['text', 'attribution'],
    before_text: 'old', after_text: 'new'}]},
  preserved: {count: 86}, unexpected_changes: [],
  consequence_candidates: [{id: 'edge-hands', via: ['eng-record-form'], classification: 'mechanical_link'}],
  dependency_implications: [],
  series_consequences: [{series_node_id: 'eng_ledger', cited_by: ['eng-record-form'], exists_in_series: true, series_state: 'unchanged'},
    {series_node_id: 'gone_node', cited_by: ['edge-hands'], exists_in_series: false, series_state: 'unchanged'}],
  author_decisions: [{decision_id: 'dec-settlement', touched_by: ['eng-record-form'], status: 'remains_author_reserved'}],
  authority_changes: [], unresolved_effects: [{id: 'eng-record-form'}], note: 'owner note',
};

test('elements are named by their kind and words, never by bare ids alone', () => {
  assert.equal(B.elementLabel(elements, 'eng-record-form'), 'Engine · “Ledger as a new record form: the lineage needs proof of training.”');
  assert.equal(B.elementLabel(elements, 'missing-id'), 'missing-id');
  assert.deepEqual(plain(B.labels(elements, ['edge-hands'])), ['Typed edge · “The craft-mark shows who can give return labour.”']);
});

test('a review keeps mechanical links as links and author decisions as the author’s', () => {
  const g = B.reviewDigest(review, elements, (id) => (id === 'eng_ledger' ? 'Ledger engine' : id));
  assert.equal(g.fromRevision, 1);
  assert.equal(g.toRevision, 2);
  assert.equal(g.changed[0].kind, 'Its wording or interpretation changed');
  assert.deepEqual(plain(g.changed[0].fields), ['wording', 'what supports it']);
  assert.match(g.reread[0], /Re-read it: the reference is recorded, whether it still holds is not\./);
  assert.doesNotMatch(g.reread.join(' '), /causes|because of/);
  assert.match(g.series[0].text, /“Ledger engine” is cited by .* The Architecture is unchanged/);
  assert.equal(g.series[1].tone, 'bad');
  assert.match(g.decisions[0], /stays yours to decide; this revision does not decide it\./);
  assert.match(g.unresolved[0], /not established/);
  assert.equal(g.preserved, 86);
  assert.equal(g.identity[0][1], 'a'.repeat(64));
});

test('a blocked review offers to widen only to elements the Book still has, never to edges alone', () => {
  const blocked = {...review, applicable: false, permitted_ids: ['eng-record-form', 'edge-hands'],
    unexpected_changes: [{id: 'dec-settlement', change: 'changed', reason: 'not a permitted element'},
      {id: 'new-thing', change: 'added', reason: 'adds an element that references no permitted element'}]};
  assert.deepEqual(plain(B.widenedTargets(blocked, elements)), ['eng-record-form', 'dec-settlement']);
  const g = B.reviewDigest(blocked, elements);
  assert.equal(g.applicable, false);
  assert.match(g.unexpected[1].text, /new-thing — added: adds an element/);
});

test('phases and scope are said as the owner reports them', () => {
  assert.equal(B.phaseLine('none', 24), null);
  assert.match(B.phaseLine('awaiting_coding_agent', 24).text, /Nothing in the Book has changed/);
  assert.match(B.phaseLine('review_ready', 24).text, /unchanged until you apply it/);
  assert.equal(B.phaseLine('stale', 24).tone, 'bad');
  assert.equal(B.staleReason({book_changed: true, context_changed: false}), 'the working Book changed after it was prepared');
  assert.match(B.scopeSentence({targets: ['a'], dependents: ['b', 'c']}), /this element and the 2 elements that refer to it/);
  assert.match(B.scopeSentence({targets: ['a'], dependents: []}), /may change only this element/);
});

test('the message for the coding agent names the owner’s commands and promises no change', () => {
  const message = B.agentMessage({show: 'python -m x book-show --book 24', complete: 'python -m x book-complete-file --book 24 --candidate <f>',
    guide: 'docs/agents/studio-architecture-bridge.md'}, 24, 'spring-ledger', {instruction: 'Make the cost visible.'});
  assert.match(message, /book-show --book 24/);
  assert.match(message, /book-complete-file/);
  assert.match(message, /does not change the working Book/);
  assert.equal(B.agentMessage(null, 24, 'x'), '');
});

test('a reworded link and an added element are shown in their own words', () => {
  const before = [{id: 'edge-hands', collection: 'typed_edges', text: 'Old function.', fields: {function: 'Old function.', dependency: 'pressures', source: 'eng'}}];
  const after = [{id: 'edge-hands', collection: 'typed_edges', text: 'New function.', fields: {function: 'New function.', dependency: 'pressures', source: 'eng'}},
    {id: 'assume-new', collection: 'assumptions', text: 'A mark carries no hours.', fields: {text: 'A mark carries no hours.', reversal: 'It does.'}}];
  const r = {...review, changes: {changed: [{id: 'edge-hands', classification: 'mechanical', fields_changed: ['function']}],
    added: [{id: 'assume-new', collection: 'assumptions', references: ['edge-hands']}], removed: []}};
  const g = B.reviewDigest(r, before, null, after);
  assert.equal(g.changed[0].kind, 'The wording of this link changed');
  assert.deepEqual(plain(g.changed[0].worded), [{field: 'stated function', key: 'function', before: 'Old function.', after: 'New function.'}]);
  assert.equal(g.added[0].label, 'Assumption · “A mark carries no hours.”');
  assert.equal(g.added[0].text, 'A mark carries no hours.');
  // A link whose words did not change is still only a change of references.
  const mech = B.reviewDigest({...r, changes: {changed: [{id: 'edge-hands', classification: 'mechanical', fields_changed: ['target']}], added: [], removed: []}},
    before, null, [{...before[0]}]);
  assert.equal(mech.changed[0].kind, 'Only its references changed');
});
