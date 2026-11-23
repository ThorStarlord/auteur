// Atelier Series context helpers: a concept is joined to a Book plan only by the node id that Book
// records; freshness is said as each owner records it; a hypothesis draft asserts no link.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const browser = new URL('../src/auteur/beginner/browser/', import.meta.url);
function load() {
  const sandbox = {window: {}};
  runInNewContext(readFileSync(new URL('studio_atelier_series.js', browser), 'utf8'), sandbox);
  return sandbox.window.AuteurAtelierSeries;
}
const X = load();
// Values built inside the vm sandbox carry its prototypes; compare them as plain data.
const plain = (value) => JSON.parse(JSON.stringify(value));
const ref = (node_id, extra = {}) => ({node_id, present: true, title: node_id, changed_since_book: false,
  elements: [{id: 'e1', collection: 'engines', text: 'Ledger engine words', commitment_authority: 'agent_working'}], edges: [], ...extra});
const ctx = (books, plan = {state: 'absent'}, direction = {state: 'absent'}) => ({version: 'v',
  sources: {working_books: {state: books.length ? 'available' : 'absent', books}, series_plan: plan, series_direction: direction}});

test('a concept is joined to a Book only by its recorded node id', () => {
  const book = {state: 'working', book_number: 24, title: 'B', freshness: 'ready', semantic_impact: 'clear',
    references: [ref('eng_ledger'), ref('eng_source')]};
  const c = ctx([book, {state: 'unreadable', book_number: 3}]);
  assert.deepEqual(plain(X.forNode(c, 'eng_ledger').map((h) => h.book.book_number)), [24]);
  // Matching words in a title or element text never join anything.
  assert.equal(X.forNode(c, 'Ledger engine').length, 0);
  assert.equal(X.forNode(c, 'eng_led').length, 0);
  assert.equal(X.forNode(c, null).length, 0);
  assert.equal(X.workingBooks(c).length, 1);
});

test('freshness is said as the owner records it', () => {
  assert.deepEqual(plain(X.bookFreshness({freshness: 'ready', semantic_impact: 'clear'}).map((l) => l.tone)), ['ok']);
  const stale = X.bookFreshness({freshness: 'stale', series_changed: true, source_changed: false, semantic_impact: 'contradictory'});
  assert.deepEqual(plain(stale.map((l) => l.tone)), ['warn', 'bad']);
  assert.equal(X.refStanding(ref('x', {present: false})).tone, 'bad');
  assert.equal(X.refStanding(ref('x', {changed_since_book: true})).tone, 'warn');
  assert.equal(X.refStanding(ref('x', {changed_since_book: null})), null);
  assert.match(X.directionBookFreshness({freshness: 'series_direction_revised', accepted_against_series_revision: 1,
    current_series_revision: 2}).text, /revision 1; the Series Direction is now revision 2/);
  assert.match(X.directionBookFreshness({freshness: 'unknown', accepted_against_series_revision: 1}).text, /cannot be told/);
});

test('project plans are summarised by owner and never as linked', () => {
  const plan = {state: 'available', title: 'Ash', path: 'series_identity.yaml', books: [1, 2, 3], setups: [1, 2], payoffs: [1]};
  const direction = {state: 'accepted', series: {state: 'accepted', title: 'Archive', revision: 2},
    books: [{state: 'accepted'}], other_proposals: {series_direction: 1, book_direction: 0}};
  const lines = X.projectSummary(ctx([], plan, direction)).map((l) => l.text);
  assert.match(lines[0], /3 Book plans, 2 setups, 1 payoff · author-declared/);
  assert.match(lines[1], /accepted, revision 2 · 1 accepted Book Direction$/);
  assert.equal(X.projectSummary(ctx([], {state: 'invalid', path: 'series_identity.yaml'})).at(0).tone, 'bad');
  assert.equal(X.projectSummary(ctx([])).length, 0);
});

test('a hypothesis draft names the source and asserts no link', () => {
  const text = X.hypothesisDraft('The First Crosser', 'the setup “ledger”', {path: 'series_identity.yaml', ref: 'narrative_setups[0]'});
  assert.match(text, /not a recorded link/);
  assert.match(text, /series_identity\.yaml · narrative_setups\[0\]/);
  assert.match(text, /change nothing/);
  assert.equal(X.sourceLine({path: 'p', ref: null, revision: 2, content_hash: 'sha256:abcdef0123456789'}), 'p · revision 2 · sha256:abcdef0123');
});

test('an unreadable Book is reported, never treated as absent', () => {
  const c = ctx([{state: 'unreadable', book_number: 24, reason: 'cut short'}]);
  assert.equal(X.workingBooks(c).length, 0);
  assert.match(X.unreadableBooks(c)[0], /Book 24’s working architecture could not be read/);
  const all = {version: 'v', sources: {working_books: {state: 'unreadable', books: []}, series_plan: {state: 'absent'}, series_direction: {state: 'absent'}}};
  assert.equal(X.unreadableBooks(all).length, 1);
});

test('proposal files are said only as far as the owner records allow', () => {
  const base = {proposal_files: {series_direction: 2, book_direction: 1}, other_proposals: {series_direction: 1, book_direction: 0}};
  assert.match(X.proposalNote({...base, proposals_accounted: true, series: {state: 'accepted'}, books: []}), /also keeps 1 proposal file besides those behind the accepted records/);
  assert.match(X.proposalNote({...base, proposals_accounted: false, series: {state: 'unverified'}, books: [{state: 'accepted'}]}), /does not verify, so which proposal is behind it cannot be told/);
  assert.match(X.proposalNote({...base, proposals_accounted: true, series: {state: 'absent'}, books: []}), /3 proposal files and no accepted record/);
});
