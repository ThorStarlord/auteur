import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// The scenario executes the source-loaded Studio action, but not the served UI,
// Quick Draft generation backend, or browser persistence owner.
const source = readFileSync(new URL('../src/auteur/beginner/browser/studio.js', import.meta.url), 'utf8');
const begin = source.indexOf('  function useGenerated() {');
const end = source.indexOf('  function concealScene() {', begin + 1);
assert.ok(begin !== -1 && end > begin, 'Studio source action boundary must exist');
const action = source.slice(begin, end);

function authorScenario({ working = '', candidate = 'A revised scene.', confirm = false,
                          ready = true, failed = false } = {}) {
  const item = { id: 'working-scene', kind: 'scene', content: working };
  const fields = {
    'generated-prose': { value: candidate },
    'scene-text': { value: working },
    'generation-status': { textContent: '' },
  };
  const confirmations = [], notices = [];
  let saves = 0;
  const selected = () => item;
  const $ = id => fields[id];
  const remote = { ready, failed };
  const window = { confirm(message) { confirmations.push(message); return confirm; } };
  const queueSave = () => { saves += 1; };
  const status = message => { notices.push(message); };
  const useGenerated = new Function(
    'selected', '$', 'remote', 'window', 'queueSave', 'status',
    action + '\nreturn useGenerated;',
  )(selected, $, remote, window, queueSave, status);
  return { item, fields, confirmations, notices, get saves() { return saves; }, useGenerated };
}

test('declining a destructive copy preserves authored prose and causes no save', () => {
  const author = authorScenario({ working: 'Carefully edited author text.' });
  author.useGenerated();
  assert.equal(author.item.content, 'Carefully edited author text.');
  assert.equal(author.fields['scene-text'].value, 'Carefully edited author text.');
  assert.equal(author.saves, 0);
  assert.equal(author.confirmations.length, 1);
  assert.match(author.confirmations[0], /Replace your existing working scene prose/);
  assert.match(author.fields['generation-status'].textContent, /kept/);
  assert.equal(author.fields['generated-prose'].value, 'A revised scene.');
});

test('author-confirmed replacement copies candidate once without accepting canon', () => {
  const author = authorScenario({ working: 'Author original.', confirm: true });
  author.useGenerated();
  assert.equal(author.item.content, 'A revised scene.');
  assert.equal(author.fields['scene-text'].value, 'A revised scene.');
  assert.equal(author.saves, 1);
  assert.equal(author.confirmations.length, 1);
  assert.match(author.notices.at(-1), /Nothing accepted/);
});

test('empty working scene accepts candidate without destructive confirmation', () => {
  const author = authorScenario({ working: '' });
  author.useGenerated();
  assert.equal(author.item.content, 'A revised scene.');
  assert.equal(author.saves, 1);
  assert.equal(author.confirmations.length, 0);
});

test('same prose does not trigger a redundant destructive warning', () => {
  const author = authorScenario({ working: 'Same candidate.', candidate: 'Same candidate.' });
  author.useGenerated();
  assert.equal(author.item.content, 'Same candidate.');
  assert.equal(author.confirmations.length, 0);
});

test('overlength candidate is refused without editor mutation or persistence', () => {
  const author = authorScenario({ working: 'Keep this.', candidate: 'x'.repeat(20001) });
  author.useGenerated();
  assert.equal(author.item.content, 'Keep this.');
  assert.equal(author.saves, 0);
  assert.equal(author.confirmations.length, 0);
  assert.match(author.fields['generation-status'].textContent, /20,000-character scene limit/);
});

test('an unavailable persistence owner cannot silently mutate working prose', () => {
  const author = authorScenario({ working: 'Keep this.', failed: true });
  author.useGenerated();
  assert.equal(author.item.content, 'Keep this.');
  assert.equal(author.saves, 0);
  assert.match(author.fields['generation-status'].textContent, /unavailable/);
});
