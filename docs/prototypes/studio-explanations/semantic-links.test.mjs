import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {normalizeEvidence} from './model.mjs';
import {deriveSemanticLinks, linksForFocus, preferredPerspective} from './semantic-links.mjs';

const load = p => JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const evidence = load('./fixtures/genre-evidence.json');
const model = normalizeEvidence(load('./fixtures/paladin.json'),evidence);
const links = deriveSemanticLinks(model);

test('keeps each genre relationship distinct even for the same trope',()=>{
  const earned=linksForFocus(links,{kind:'item',id:'earn'}).filter(l=>l.target.kind==='genre');
  assert.equal(earned.length,2);
  assert.deepEqual(new Set(earned.map(l=>l.target.id)),new Set(['heroic_fantasy','progression_fantasy']));
  assert.deepEqual(new Set(earned.map(l=>l.sourceRef)),new Set(['illustrative:heroic-cost','illustrative:progression-cycle']));
  assert.ok(earned.every(l=>l.originalFrom.kind==='genre'&&l.supportStatus==='hypothesis'));
});

test('does not invent trope to emotion from a genre-level promise or a multi-hop inference',()=>{
  const earned=linksForFocus(links,{kind:'item',id:'earn'});
  assert.ok(!earned.some(l=>l.target.id==='joy'));
  assert.ok(linksForFocus(links,{kind:'item',id:'growth'}).some(l=>l.target.id==='joy'&&l.supportStatus==='hypothesis'));
});

test('missing a versioned pack keeps inferred genres explicitly hypothetical',()=>{
  const inferred=linksForFocus(links,{kind:'genre',id:'progression_fantasy'});
  assert.ok(inferred.length>0);
  assert.ok(inferred.every(l=>l.sourceKind==='model_inference'&&l.supportStatus==='hypothesis'&&l.ruleStrength===null));
});

test('preserves declared proposal edge direction and source on forward and reverse exploration',()=>{
  const forward=linksForFocus(links,{kind:'item',id:'earn'}).find(l=>l.target.id==='growth');
  const reverse=linksForFocus(links,{kind:'item',id:'growth'}).find(l=>l.target.id==='earn');
  assert.equal(forward.sourceRef,'illustrative:link-earned-cycle');
  assert.equal(reverse.id,forward.id);
  assert.equal(forward.verb,'illustrates');
  assert.match(reverse.verb,/illustrates/);
  assert.equal(reverse.direction,'reverse');
});

test('prefers the right explanatory perspective and refuses unknown targets',()=>{
  assert.equal(preferredPerspective(model,{kind:'genre',id:'progression_fantasy'}),'anatomy');
  assert.equal(preferredPerspective(model,{kind:'item',id:'earn'}),'comparison');
  assert.equal(preferredPerspective(model,{kind:'item',id:'growth'}),'mechanism');
  assert.equal(preferredPerspective(model,{kind:'item',id:'joy'}),'overview');
  assert.equal(preferredPerspective(model,{kind:'item',id:'missing'}),null);
  assert.equal(preferredPerspective(model,{kind:'phase',id:'anticipation'}),null);
});

test('the normalized model is not modified when links are projected',()=>{
  const before=JSON.stringify(model);
  deriveSemanticLinks(model);
  assert.equal(JSON.stringify(model),before);
});

test('reverse genre traversal describes the existing relationship without inventing causation',()=>{
 const reverse=linksForFocus(links,{kind:'item',id:'earn'});
 assert.equal(reverse.find(l=>l.target.id==='progression_fantasy').verb,'is used by');
 assert.equal(reverse.find(l=>l.target.id==='heroic_fantasy').verb,'is supported by');
 assert.equal(reverse.filter(l=>l.target.kind==='genre').length,2);
});
