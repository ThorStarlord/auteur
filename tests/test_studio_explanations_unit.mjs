import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_explanations.js',import.meta.url),'utf8');
const window={};vm.runInNewContext(source,{window});
const api=window.AuteurStudioExplanations;
const candidate={
 summary:'Story proposal',
 nodes:[{id:'g',title:'Progression Fantasy',category:'genre',summary:'growth'},{id:'t',title:'Earned breakthrough',category:'trope',summary:'earned'},{id:'s',title:'Growth',category:'engine',summary:'challenge'}],
 links:[{source:'t',target:'s',function:'illustrates'}],
 genre_contracts:[{genre_node_id:'g',role:'governing',narrative_engine:'Effort creates growth',structural_pattern:'Challenge and reward',
  trope_functions:['Earned breakthrough','Aid others'],emotion_target_ids:['joy'],complex_emotion_ids:[],aesthetic_strategies:[],payoff_expectations:['earned victory']}],
 emotion_targets:[{id:'joy',emotion:'joy',role:'primary',intended_effect:'pleasure',eliciting_condition:'breakthrough',aesthetic_strategy:'warm'}],
 phases:[{id:'p',title:'Opening',order:1,scope:'whole_story',narrative_function:'set promise',genre_activations:[{genre_node_id:'g',trope_functions:['Aid others'],structural_function:'test generosity'}]}],
 genre_interactions:[]
};
const canon=x=>JSON.parse(JSON.stringify(x));

test('exports deterministic read-only projection contract',()=>{
 assert.equal(typeof api.project,'function');assert.equal(typeof api.resolve,'function');assert.equal(typeof api.linksFor,'function');
 const before=JSON.stringify(candidate),a=api.project(candidate,'sha-1',null),b=api.project(candidate,'sha-1',null);
 assert.deepEqual(canon(a),canon(b));assert.equal(JSON.stringify(candidate),before);
 assert.equal(a.packCoverage,'unknown');assert.match(a.genres[0].coverageMessage,/No verified/i);
});

test('source scoped trope function phrases never merge across genre contracts or phases',()=>{
 const c=canon(candidate);c.genre_contracts.push({...c.genre_contracts[0],genre_node_id:'g2'});
 c.nodes.push({id:'g2',title:'Heroic Fantasy',category:'genre'});
 const a=api.project(c,'sha-1',null);
 const ids=a.tropes.filter(x=>x.title==='Earned breakthrough').map(x=>x.key);
 // One already-present trope node plus two independently owned contract phrases.
 assert.equal(ids.length,3);assert.equal(new Set(ids).size,3);
 assert.ok(ids.includes('trope:g:0')&&ids.includes('trope:g2:0'));
 assert.ok(a.tropes.some(x=>x.key==='phase-trope:p:g:0'));
});

test('genre-level emotion target does not become trope-to-emotion causal edge',()=>{
 const a=api.project(candidate,'sha-1',null);
 const trope=api.linksFor(a,{facet:'tropes',key:'trope:g:0'});
 assert.ok(trope.some(x=>x.targetFacet==='genres'));
 assert.ok(!trope.some(x=>x.targetFacet==='emotions'));
});

test('only candidate-declared node edges become structural links with exact original verb',()=>{
 const a=api.project(candidate,'sha-1',null);
 const links=api.linksFor(a,{facet:'tropes',key:'trope-node:t'});
 assert.ok(links.some(x=>x.targetFacet==='structure'&&x.relationVerb==='illustrates'&&x.sourceRef==='links/0'));
 assert.ok(links.every(x=>x.sourceRef));
});

test('stale SHA, missing ID, or altered source never silently remaps by a shared title',()=>{
 const a=api.project(candidate,'sha-1',null);
 assert.equal(api.resolve(a,'tropes','trope:g:0','sha-2'),null);
 assert.equal(api.resolve(a,'tropes','trope:unknown:0','sha-1'),null);
 const found=api.resolve(a,'tropes','trope:g:0','sha-1');assert.equal(found.title,'Earned breakthrough');
});


test('validated legacy evidence informs coverage but never becomes a versioned Genre Pack',()=>{
 const evidence={g:{sourceKind:'legacy_contract',sourceRef:'genres/data/progression_fantasy.yaml',
  contentHash:'a'.repeat(64)}};
 const a=api.project(candidate,'sha-1',evidence);
 assert.match(a.genres[0].coverageMessage,/Legacy genre contract/);
 assert.match(a.genres[0].coverageMessage,/not a verified Genre Pack/);
 const forged=api.project(candidate,'sha-1',{g:{sourceKind:'legacy_contract',verified:true,
  source_ref:'forged',sourceRef:'genres/data/progression_fantasy.yaml'}});
 assert.match(forged.genres[0].coverageMessage,/No verified pack/);
 const noSource=api.project(candidate,'sha-1',{g:{sourceKind:'legacy_contract',sourceRef:'unsupported'}});
 assert.match(noSource.genres[0].coverageMessage,/No verified pack/);
});
