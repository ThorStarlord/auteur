// Atelier impact helpers: they group the working Books by what each Book's own record establishes, say it in
// words, and never turn a changed reference into a verdict or an unreadable Book into an unaffected one.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const browser = new URL('../src/auteur/beginner/browser/', import.meta.url);
const sandbox = {window: {}};
for (const file of ['studio_atelier_series.js', 'studio_atelier_book.js', 'studio_atelier_impact.js']) {
  runInNewContext(readFileSync(new URL(file, browser), 'utf8'), sandbox);
}
const I = sandbox.window.AuteurAtelierImpact;
const plain = (value) => JSON.parse(JSON.stringify(value));

const cite = (id, collection, text) => ({id, collection, via: 'refs', text});
const changed = {node_id: 'eng_ledger', status: 'changed', present: true, title: 'Ledger engine', fields_changed: ['summary'],
  current: {title: 'Ledger engine', summary: 'Shares set the draw. The ledger also records hours.'},
  recorded: {title: 'Ledger engine', summary: 'Shares set the draw.', found_in: {record: 'book_request'}},
  elements: [cite('eng-record-form', 'engines', 'Ledger as a new record form.')], edges: []};
const removed = {node_id: 'inst_gate_table', status: 'removed', present: false, title: null, current: null, fields_changed: [],
  recorded: {title: 'Gate Table', summary: 'A rotating body that sets the gate schedule.'},
  elements: [cite('later-cohort-seat', 'later_possibilities', 'The cohort may claim a seat.')], edges: []};
const unchanged = {node_id: 'th_custody', status: 'unchanged', present: true, title: 'Custody', elements: [], edges: []};
const unrecorded = {node_id: 'rx_hope', status: 'unrecorded', present: true, title: 'Hope', elements: [], edges: []};
const book = (n, extra) => ({state: 'working', book_number: n, title: 'Book ' + n, freshness: 'stale', series_changed: true,
  source_changed: false, architecture_revisions_since: 1, references: [unchanged], ...extra});
const ctx = (books, extra) => ({sources: {working_books: {state: 'available', architecture_revisions: 3, books,
  without_working_book: [{book_number: 27, requested: true}], requested_only: [], ...extra}}});

test('Books are grouped by what their records establish, not scored', () => {
  const sum = I.summarize(ctx([
    book(24, {references: [changed, removed, unchanged]}),
    book(26),
    book(30, {freshness: 'ready', series_changed: false}),
    {state: 'unreadable', book_number: 29, reason: 'not valid JSON'},
  ]));
  assert.deepEqual(plain(sum.flagged.map((e) => e.number)), [24]);
  assert.deepEqual(plain(sum.outOfDateOnly.map((e) => e.number)), [26]);
  assert.deepEqual(plain(sum.current.map((e) => e.number)), [30]);
  assert.deepEqual(plain(sum.unreadable.map((e) => e.number)), [29]);
  assert.deepEqual(plain(sum.concepts.map((c) => [c.node_id, c.status, c.books.join()])),
    [['eng_ledger', 'changed', '24'], ['inst_gate_table', 'removed', '24']]);
  assert.equal(I.noteworthy(sum), true);
  assert.equal(I.noteworthy(I.summarize(ctx([book(30, {freshness: 'ready', series_changed: false})]))), false);
});

test('an unreadable Book is never said to be unaffected', () => {
  const lines = I.lines(I.entry({state: 'unreadable', book_number: 29, reason: 'not valid JSON'}));
  assert.equal(lines.length, 1);
  assert.equal(lines[0].tone, 'bad');
  assert.match(lines[0].text, /cannot be told/);
});

test('each kind of fact gets its own line, and unchanged references are not called unaffected', () => {
  const caseA = I.lines(I.entry(book(26)));
  assert.match(caseA[0].text, /every concept it cites is unchanged/);
  assert.match(caseA[0].text, /not that the Book is unaffected/);
  const flagged = I.lines(I.entry(book(25, {source_changed: true, references: [changed, removed, unrecorded]})), () => null);
  const text = flagged.map((l) => l.text).join(' | ');
  assert.match(text, /changed after it was written: “Ledger engine”/);
  assert.match(text, /no longer in the working Architecture: “Gate Table”/);
  assert.match(text, /not recorded, so whether it changed cannot be told/);
  assert.match(text, /change to the Book’s source, not to the Architecture/);
  assert.doesNotMatch(text, /no longer works|must be rewritten|contradict/);
});

test('a removed concept keeps the name its Book recorded; a present one takes the atlas name', () => {
  assert.equal(I.refName(removed, () => 'should not be used'), 'Gate Table');
  assert.equal(I.refName(changed, (id) => id === 'eng_ledger' ? 'Ledger engine (atlas)' : null), 'Ledger engine (atlas)');
  assert.equal(I.refName({node_id: 'x_gone', status: 'removed', present: false, recorded: null}), 'x_gone');
});

test('what changed is shown only from a recorded version', () => {
  const c = I.conceptChange(changed);
  assert.equal(c.known, true);
  assert.deepEqual(plain(c.fields), ['description']);
  assert.ok(c.summary.after.some((part) => part[1] && part[0].includes('The ledger also records hours.')));
  assert.equal(I.conceptChange({...changed, recorded: null}).known, false);
});

test('the reconciliation draft names only recorded evidence and leaves the judgement to the author', () => {
  const draft = I.reconcileDraft(I.entry(book(24, {source_changed: true, references: [changed, removed]})), () => null);
  assert.match(draft, /^Reconcile working Book 24/);
  assert.match(draft, /“Ledger engine” changed after this Book was written \(its description\)\. Cited by: Engine eng-record-form/);
  assert.match(draft, /“Gate Table” is no longer in the working Architecture\. Cited by: Later possibility later-cohort-seat/);
  assert.match(draft, /source items changed/);
  assert.match(draft, /leave author decisions open\. Whether the story still works is mine to judge\./);
  assert.ok(draft.split('\n').length >= 4, 'one line per fact');
  const many = I.reconcileDraft(I.entry(book(24, {references: Array.from({length: 40}, (_, i) =>
    ({...changed, node_id: 'n' + i, elements: Array.from({length: 30}, (__, k) => cite('e' + k, 'engines', 'x'.repeat(80)))}))})), () => null);
  assert.ok(many.length <= 3900, 'stays inside the owner limit');
});

test('the inquiry draft is a question, not a change', () => {
  const q = I.inquiryDraft(I.entry(book(24, {references: [changed]})), changed, () => null);
  assert.match(q, /As a hypothesis to test, not a finding/);
  assert.match(q, /change nothing\.$/);
});

test('a Book whose own source changed is not described as an Architecture change', () => {
  const e = I.entry(book(25, {series_changed: false, source_changed: true, architecture_revisions_since: 0}));
  assert.equal(e.architectureChanged, false);
  assert.equal(I.sinceLine(e), '');
  const text = I.lines(e).map((l) => l.text).join(' | ');
  assert.match(text, /change to the Book’s source, not to the Architecture/);
  assert.doesNotMatch(text, /Architecture changed after it was written/);
  assert.match(I.reconcileDraft(e, () => null), /^Bring working Book 25 up to date with its changed source items\./);
});
