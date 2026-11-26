// Atelier open-question helpers: the owner's projection said in words. Each statement must keep the distinctions the
// owner keeps: a continuing identity is not an unchanged wording, a removal is not an answer, a reason is only what a
// revision recorded, and a Book relationship is said only as the Book's recorded reference states it.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const browser = new URL('../src/auteur/beginner/browser/', import.meta.url);
function load() {
  const sandbox = {window: {}};
  runInNewContext(readFileSync(new URL('studio_atelier_questions.js', browser), 'utf8'), sandbox);
  return sandbox.window.AuteurAtelierQuestions;
}
const Q = load();
const plain = (value) => JSON.parse(JSON.stringify(value));
const sha = (c) => c.repeat(64).slice(0, 64);
const v = (revision, c) => ({revision_number: revision, request_sha256: sha(c)});

const complete = {complete: true, gaps: [], introduced_in_recorded_history: true, first_recorded_in: v(3, 'a'),
  legacy_versions_before: 2, unreadable_versions: 0};

test('a continuing question says when its identity was first recorded, and shows no gap it does not have', () => {
  const q = {id: 'q-gate', standing: 'continuing', history: complete, spans: [], books: []};
  const lines = plain(Q.standing(q, {current: {numbered: true}}));
  assert.equal(lines.length, 1);
  assert.equal(lines[0].tone, 'ok');
  assert.match(lines[0].text, /first recorded in revision 3/);
});

test('a gap in the history is said, and the claim of introduction is withheld', () => {
  const q = {id: 'q-gate', standing: 'continuing', spans: [], books: [],
    history: {complete: false, gaps: ['unreadable_before_first_recorded'], introduced_in_recorded_history: false,
      first_recorded_in: v(4, 'b')}};
  const lines = plain(Q.standing(q, {current: {numbered: true}}));
  assert.equal(lines[0].tone, 'warn');
  assert.match(lines[0].text, /recorded from revision 4 on; what came before cannot be read in full/);
  assert.match(lines[1].text, /cannot be read, so whether the question was open then is not shown/);
});

test('a question with no identity is wording only, and cannot be asked about as continuing', () => {
  const q = {id: null, index: 2, standing: 'wording_only', spans: [], books: [], history: {complete: false, gaps: ['no_identity']}};
  const lines = plain(Q.standing(q, {current: {numbered: true}}));
  assert.match(lines[0].text, /Wording only\. This question has no recorded identity yet/);
  assert.equal(Q.isAskable(q, {current: {}}), false);
  assert.match(Q.askNote(q, {current: {}}), /needs a recorded identity/);
});

test('a question no longer open is said to be not answered, and cannot be asked about', () => {
  const q = {id: 'q-gate', standing: 'no_longer_open', text: 'Gate?', spans: [
    {kind: 'absent', change: 'removed', from_revision: 5, to_revision: 5, versions: [v(5, 'c')],
      previous: {index: 14, text: 'Gate?'}, reason: null}], books: [], history: complete};
  const lines = plain(Q.standing(q, {current: {numbered: true}}));
  assert.equal(lines[0].tone, 'warn');
  assert.match(lines[0].text, /No longer open in the working Architecture since revision 5\. Removing it is not an answer/);
  assert.equal(Q.isAskable(q, {current: {}}), false);
  assert.match(Q.askNote(q, {current: {}}), /no longer open cannot be asked about/);
});

test('an asked-about continuing question needs its identity and a current Architecture', () => {
  const continuing = {id: 'q-gate', standing: 'continuing'};
  assert.equal(Q.isAskable(continuing, {current: {numbered: true}}), true);
  assert.equal(Q.isAskable(continuing, {}), false);
  assert.equal(Q.isAskable({id: null, standing: 'continuing'}, {current: {}}), false);
});

test('a span says what changed against the span before it, and keeps the wording it covers', () => {
  const reworded = {kind: 'present', change: 'reworded', from_revision: 6, to_revision: 7,
    versions: [v(6, 'd'), v(7, 'e')], previous: {index: 14, text: 'Old?'}, index: 14, text: 'New?'};
  assert.equal(Q.spanHead(reworded).text, 'Revision 6 · reworded, same position; kept through revision 7');
  const introduced = {kind: 'present', change: 'introduced', from_revision: 3, to_revision: 3, versions: [v(3, 'a')]};
  assert.equal(Q.spanHead(introduced).text, 'First recorded in revision 3');
  const unchanged = {kind: 'present', change: null, from_revision: 4, to_revision: 6, versions: [v(4, 'f'), v(5, 'g'), v(6, 'h')]};
  assert.match(Q.spanHead(unchanged).text, /Wording unchanged/);
  const unverified = {kind: 'present', change: 'unverified', from_revision: 4, to_revision: 4, versions: [v(4, 'l')]};
  assert.match(Q.spanHead(unverified).text, /Revision 4 · recorded; the version before it cannot be read, so whether it changed is not shown/);
  assert.deepEqual(plain(Q.chipsFor({id: 'q-u', standing: 'continuing', spans: [unverified], books: []})), []);
  const unreadable = {kind: 'unreadable', from_revision: 2, to_revision: 2, versions: [v(2, 'i')]};
  assert.match(Q.spanHead(unreadable).text, /Cannot be read · revision 2/);
  const legacy = {kind: 'no_identity', from_revision: 1, to_revision: 2, versions: [v(1, 'j'), v(2, 'k')]};
  assert.match(Q.spanHead(legacy).text, /Wording only · revisions 1–2 · no identity recorded/);
});

test('a reason is only what the revision recorded; none is invented', () => {
  assert.deepEqual(plain(Q.reasonLines(null)), ['The record gives no reason for this change.']);
  assert.deepEqual(plain(Q.reasonLines({readable: true, instruction: null, selected_alternative: null})),
    ['The record gives no reason for this change.']);
  assert.deepEqual(plain(Q.reasonLines({readable: false})), ['The request that made this revision cannot be read, so no reason is shown.']);
  const both = plain(Q.reasonLines({readable: true, instruction: 'Reword it.', selected_alternative: {title: 'A mechanism question'}}));
  assert.deepEqual(both, ['Your revision request: “Reword it.”',
    'The alternative you chose in the coding-agent desk: “A mechanism question”']);
});

test('a Book relationship is said as the Book records it, and a changed question may warrant reconsideration only', () => {
  const reworded = Q.bookRelation({state: 'reworded'});
  assert.equal(reworded.tone, 'warn');
  assert.match(reworded.text, /may warrant reconsideration/);
  assert.match(reworded.text, /not declared inconsistent/);
  assert.match(Q.bookRelation({state: 'removed'}).text, /Removing it is not an answer/);
  assert.equal(Q.bookRelation({state: 'identity_not_established'}), null);
  assert.equal(Q.bookRelation({state: 'some_unknown_state'}), null);
  assert.equal(Q.bookRelation({state: 'current_wording'}).tone, 'ok');
});

test('book reference is passed to the existing inquiry in the shape it takes', () => {
  const ask = plain(Q.bookAskRef({question_id: 'q-gate', decision_id: 'dec-gate', state: 'reworded',
    recorded: {text: 'Old?', index: 14}, current: {text: 'New?', index: 14}}));
  assert.deepEqual(ask, {question_id: 'q-gate', decision_id: 'dec-gate', state: 'reworded', recorded_text: 'Old?',
    recorded_index: 14, current_text: 'New?', current_index: 14});
});

test('find names a question by identity, or by position when it has none', () => {
  const data = {questions: [{id: 'q-a', index: 0, text: 'A'}, {id: null, index: 1, text: 'B'}],
    no_longer_open: [{id: 'q-z', index: 4, text: 'Z'}]};
  assert.equal(Q.find(data, {id: 'q-a'}).text, 'A');
  assert.equal(Q.find(data, {id: 'q-z'}).text, 'Z');
  assert.equal(Q.find(data, {index: 1}).text, 'B');
  assert.equal(Q.find(data, {id: 'q-missing'}), null);
});

test('the list keeps continuing, wording-only and no-longer-open questions in separate groups', () => {
  const data = {questions: [{id: 'q-a', standing: 'continuing'}, {id: null, standing: 'wording_only'}],
    no_longer_open: [{id: 'q-z', standing: 'no_longer_open'}]};
  const g = Q.groups(data);
  assert.deepEqual(g.continuing.map((q) => q.id), ['q-a']);
  assert.deepEqual(g.wording.map((q) => q.id), [null]);
  assert.deepEqual(g.gone.map((q) => q.id), ['q-z']);
});

test('chips say continuing identity, its changes, an incomplete history and its Book decisions, and nothing more', () => {
  const q = {id: 'q-gate', standing: 'continuing', history: {complete: false, gaps: ['chain_incomplete']},
    spans: [{kind: 'present', change: 'introduced'}, {kind: 'present', change: 'reworded'}],
    books: [{}, {}]};
  assert.deepEqual(plain(Q.chipsFor(q)).map((c) => c.text),
    ['1 change', 'History incomplete', '2 Book decisions']);
  assert.deepEqual(plain(Q.chipsFor({id: 'q-plain', standing: 'continuing', spans: [], books: []})), []);
  const wording = {id: null, standing: 'wording_only', spans: [], books: []};
  assert.deepEqual(plain(Q.chipsFor(wording)).map((c) => c.text), ['Wording only']);
});

test('suggested words exist for every offered operation, and are offered, never sent', () => {
  assert.deepEqual(plain(Q.OPERATIONS.map((o) => o[0]).sort()), plain(Object.keys(Q.SUGGEST).sort()));
});

test('a formulation keeps its wording whole and gives its version an honest label', () => {
  assert.equal(Q.label({revision_number: 3, request_sha256: sha('a')}), 'revision 3');
  assert.equal(Q.label({revision_number: null, request_sha256: 'abcdef0123456789'}), 'version abcdef01');
  assert.equal(Q.rangeOf({from_revision: 2, to_revision: 4, versions: [v(2, 'a'), v(3, 'b'), v(4, 'c')]}), 'revisions 2–4');
});
