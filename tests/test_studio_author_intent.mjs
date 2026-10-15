import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const window = {};
const path = new URL('../src/auteur/beginner/browser/studio_author_intent.js', import.meta.url);
vm.runInNewContext(readFileSync(path, 'utf8'), { window });
const project = window.AuteurStudioAuthorIntent.project;
const items = [{ id: 'story-vision', content: 'Joy through generous heroism. The paladin is extraordinarily kind.' }];
const suggestion = { candidate: { summary: 'A solitary protector must learn to empower others.' },
  candidate_request_sha256: 'e'.repeat(64), status: 'ready' };
test('the exact author vision is separate from an invented flaw', () => {
  const result = project(items, suggestion);
  assert.equal(result.authorVision.text, items[0].content);
  assert.equal(result.authorVision.authority, 'author_working');
  assert.equal(result.authorVision.sourceRef, 'canvas/items/story-vision');
  assert.equal(result.proposal.text, suggestion.candidate.summary);
  assert.equal(result.proposal.authority, 'agent_proposal');
  assert.ok(!result.authorVision.text.includes('solitary protector'));
});
test('a stale result never looks like fresh author intent', () => {
  const result = project(items, {...suggestion, status: 'stale'});
  assert.equal(result.sourceStatus, 'stale');
  assert.equal(result.proposal.freshness, 'stale');
  assert.equal(result.proposal.requestSha, 'e'.repeat(64));
});
test('missing author vision and missing candidate do not create false claims', () => {
  const result = project([], {status: 'awaiting_host_agent', request: {request_sha256: 'f'.repeat(64)}});
  assert.equal(result.authorVision, null);
  assert.equal(result.proposal, null);
  assert.equal(result.sourceStatus, 'awaiting_host_agent');
});
test('current authored text is not reclassified by agent self-labels', () => {
  const result = project(items, {...suggestion,candidate: {...suggestion.candidate,
    emotion_targets: [{provenance:'author_declared', intended_effect:'must overcome selfishness'}]}});
  assert.equal(result.authorVision.text, items[0].content);
  assert.equal(result.proposal.text, suggestion.candidate.summary);
});

test('AI self-described author provenance is explicitly unverified', () => {
  assert.match(window.AuteurStudioAuthorIntent.provenanceLabel('author_declared'),/AI claimed.*verify/i);
  assert.equal(window.AuteurStudioAuthorIntent.provenanceLabel('agent_proposed'), 'AI proposal · not accepted');
  assert.match(window.AuteurStudioAuthorIntent.provenanceLabel('unknown'),/unverified/i);
});
