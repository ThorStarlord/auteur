import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalizeEvidence, entriesForPerspective, connectionsForSelection } from './model.mjs';
const load = name => JSON.parse(readFileSync(new URL(`./fixtures/${name}`, import.meta.url), 'utf8'));
const story = load('paladin.json');
const evidence = load('genre-evidence.json');

test('retains separate source-relative classifications for the same trope', () => {
  const m = normalizeEvidence(story, evidence);
  const rows = m.items.find(n => n.id === 'earn').genre_links;
  assert.equal(rows.length, 2);
  assert.deepEqual(rows.map(x => x.genre_id), ['progression_fantasy', 'heroic_fantasy']);
  assert.equal(rows[0].rule_strength, null);
  assert.equal(rows[0].coverage, 'inference_only');
  assert.equal(m.authority_status, 'DERIVED / NOT CANON');
});

test('missing genre pack is unknown, never hard constraint or incompatibility', () => {
  const m = normalizeEvidence(story, evidence);
  assert.equal(m.genres.find(g => g.id === 'progression_fantasy').coverage, 'inference_only');
  assert.equal(m.items.find(n => n.id === 'generosity').genre_links[0].rule_strength, null);
  assert.equal(m.items.find(n => n.id === 'commitment').story_treatment, 'proposed_story_specific');
});

test('preserves literal legacy category rather than rewriting it as universal law', () => {
  const m = normalizeEvidence(story, evidence);
  const epic = m.genres.find(g => g.id === 'epic_fantasy');
  assert.equal(epic.legacy_rule_field, 'required_tropes');
  assert.equal(epic.pack_version, null);
  assert.equal(epic.coverage, 'legacy_contract');
});

test('only explicit proposal edges become navigable arrows and retain their warrant', () => {
  const m = normalizeEvidence(story, evidence);
  const edges = connectionsForSelection(m, 'growth');
  assert.equal(edges.length, 2);
  assert(edges.every(e => e.support_status === 'hypothesis'));
  assert.equal(connectionsForSelection(m, 'world').length, 0);
  assert.deepEqual(connectionsForSelection(m, 'unknown'), []);
});

test('perspectives project the same IDs with no canonical acceptance', () => {
  const m = normalizeEvidence(story, evidence);
  assert(entriesForPerspective(m, 'overview').length === m.items.length);
  assert(entriesForPerspective(m, 'comparison').every(i => i.type === 'trope'));
  assert(entriesForPerspective(m, 'mechanism').some(i => i.id === 'growth'));
  assert.throws(() => entriesForPerspective(m, 'invalid'), /Unknown perspective/);
});

test('fails closed for dangling source link IDs and duplicate nodes', () => {
  const bad = structuredClone(story);
  bad.proposal_edges[0].target = 'ghost';
  assert.throws(() => normalizeEvidence(bad, evidence), /Unknown edge endpoint ghost/);
  const dup = structuredClone(story);
  dup.nodes.push(dup.nodes[0]);
  assert.throws(() => normalizeEvidence(dup, evidence), /Duplicate node/);
});

test('does not mutate the incoming story or evidence', () => {
  const s = structuredClone(story), e = structuredClone(evidence);
  normalizeEvidence(s, e);
  assert.deepEqual(s, story); assert.deepEqual(e, evidence);
});

test('rejects invented curated provenance and legacy rule strengths', () => {
  const falseSource = structuredClone(story);
  falseSource.genre_links[0].source_kind = 'legacy_contract';
  assert.throws(() => normalizeEvidence(falseSource, evidence), /Provenance coverage mismatch/);
  const falseStrength = structuredClone(story);
  falseStrength.genre_links.find(l=>l.source_kind==='legacy_contract').rule_strength = 'HARD_CONSTRAINT';
  assert.throws(() => normalizeEvidence(falseStrength, evidence), /Legacy contracts do not confer Genre Pack rule strengths/);
});
