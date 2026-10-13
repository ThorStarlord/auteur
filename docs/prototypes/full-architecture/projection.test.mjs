import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {projectFullArchitecture,sourceFingerprint} from './projection.mjs';
const fixture=JSON.parse(readFileSync(new URL('./fixtures/paladin.json',import.meta.url),'utf8'));
const clone=x=>structuredClone(x);

test('missing pack coverage is unknown while genre trope functions remain candidate interpretations',()=>{
 const p=projectFullArchitecture(fixture);
 assert.equal(p.genreViews.length,3);
 const progression=p.genreViews.find(g=>g.genreId==='genre-progress');
 assert.equal(progression.packCoverage.status,'unknown');
 assert.equal(progression.morphology.length,0);
 assert.equal(progression.candidateInterpretations.find(v=>v.kind==='trope').title,'Earned breakthrough');
 assert.equal(progression.candidateInterpretations[0].authority,'candidate_genre_interpretation');
});

test('a supplied versioned pack displays exact version, content hash and convention strength',()=>{
 const data=clone(fixture);
 data.genreEvidence=[{genreId:'genre-progress',applicability:'applicable',verified:true,contentHash:'c'.repeat(64),
    pack:{pack_id:'progression-fantasy',version:'1.3',audience_promises:[{id:'p',description:'Earned change',strength:'STRONG_DEFAULT'}],
    core_conventions:[{id:'conv',description:'Training effort',strength:'COMMON_PATTERN'}],emotional_targets:[{id:'em',name:'joy',description:'Delight in growth',default_weight:0.8}],narrative_engines:[],escalation_patterns:[],resolution_patterns:[]}}];
 const genre=projectFullArchitecture(data).genreViews.find(g=>g.genreId==='genre-progress');
 assert.deepEqual(genre.packCoverage,{status:'verified_pack',packId:'progression-fantasy',version:'1.3',contentHash:'c'.repeat(64)});
 assert.equal(genre.morphology.find(x=>x.kind==='trope').ruleStrength,'COMMON_PATTERN');
 assert.ok(genre.morphology.every(x=>x.sourceKind==='versioned_pack'));
});

test('bad or missing hash never becomes a verified versioned rule',()=>{
 const d=clone(fixture);
 d.genreEvidence=[{genreId:'genre-progress',applicability:'applicable',pack:{pack_id:'progression',version:'1',core_conventions:[{id:'x',description:'fake mandatory rule',strength:'HARD_CONSTRAINT'}]}}];
 assert.equal(projectFullArchitecture(d).genreViews[0].packCoverage.status,'unverified');
 assert.equal(projectFullArchitecture(d).genreViews[0].morphology.length,0);
});

test('legacy contracts remain legacy, not verified pack rules',()=>{
 const d=clone(fixture);d.legacyEvidence=[{genreId:'genre-hero',sourceRef:'legacy/heroic.yaml',contract:{audience_product:'Justice',required_tropes:['moral choice']}}];
 const genre=projectFullArchitecture(d).genreViews.find(x=>x.genreId==='genre-hero');
 assert.equal(genre.packCoverage.status,'unknown');
 assert.ok(genre.morphology.every(x=>x.sourceKind==='legacy_contract'));
 assert.ok(genre.morphology.some(x=>x.kind==='trope'));
});

test('one phrase repeated in two genres retains distinct source refs and roles',()=>{
 const p=projectFullArchitecture(fixture);
 const a=p.genreViews.find(x=>x.genreId==='genre-progress');
 const b=p.genreViews.find(x=>x.genreId==='genre-hero');
 const e=a.candidateInterpretations.find(x=>x.title==='Earned breakthrough');
 const f=b.candidateInterpretations.find(x=>x.title==='Earned breakthrough');
 assert.ok(e&&f);assert.notEqual(e.sourceRef,f.sourceRef);assert.notEqual(a.role,b.role);
});

test('unattributed author addition stays working and is not claimed globally original',()=>{
 const p=projectFullArchitecture(fixture);
 const addition=p.storySpecific.find(x=>x.itemId==='author-trope');
 assert.equal(addition.classification,'unattributed_or_unknown');
 assert.equal(addition.authority,'author_working');
 assert.equal(addition.linkedRefs.length,0);
 assert.equal(addition.canonical,false);
});

test('adopted source pointer is historical and never marks accepted Identity',()=>{
 const p=projectFullArchitecture(fixture);
 const item=p.storySpecific.find(x=>x.itemId==='author-struct');
 assert.equal(item.sourceRef,'links/2');assert.equal(item.classification,'candidate_derived_working');
 assert.equal(p.identity.accepted.status,'unavailable_source');
});

test('basic emotion target keeps author origin; genre-level target is not a trope causal edge',()=>{
 const p=projectFullArchitecture(fixture);
 assert.equal(p.emotionalDesign.basicTargets[0].emotion,'joy');
 assert.equal(p.emotionalDesign.basicTargets[0].role,'primary');
 assert.equal(p.emotionalDesign.basicTargets[0].provenance,'author_declared');
 assert.ok(!p.typedLinks.some(l=>l.from==='trope-breakthrough'&&l.to==='joy-goal'));
});

test('Book phase ordering and structural links preserve declared origins',()=>{
 const d=clone(fixture);d.candidate.phases.reverse();
 const p=projectFullArchitecture(d);
 assert.deepEqual(p.structure.phases.map(x=>x.id),['beginning','continuing']);
 assert.equal(p.structure.phases[1].genreActivations[0].genreId,'genre-hero');
 assert.equal(p.typedLinks.length,3);assert.equal(p.typedLinks[2].verb,'illustrates');
 assert.equal(p.typedLinks[2].sourceRef,'links/2');
});

test('accepted narrative and rich hope remain separate from basic candidate emotions',()=>{
 const d=clone(fixture);d.acceptedIdentity={revision:5,target_experience:'Hope and heroic awe'};d.acceptedStructure={revision:3,title:'Four arcs'};
 const p=projectFullArchitecture(d);
 assert.equal(p.identity.accepted.status,'available');
 assert.equal(p.emotionalDesign.richExperiences[0],'Hope and heroic awe');
 assert.equal(p.structure.accepted.title,'Four arcs');
 assert.deepEqual(p.emotionalDesign.basicTargets.map(t=>t.emotion),['joy']);
});

test('projection never mutates input or invents genre rules on empty story',()=>{
 const d=clone(fixture);const before=JSON.stringify(d);projectFullArchitecture(d);
 assert.equal(JSON.stringify(d),before);
 const empty=projectFullArchitecture({candidate:null,workingItems:[],genreEvidence:[]});
 assert.equal(empty.genreViews.length,0);assert.equal(empty.storySpecific.length,0);
 assert.equal(empty.identity.accepted.status,'unavailable_source');
});

test('fingerprint is source-specific and changes on canvas revision or proposal SHA',()=>{
 const a=sourceFingerprint(fixture),b=sourceFingerprint({...fixture,canvasRevision:4});
 assert.notDeepEqual(a,b);
 const c=sourceFingerprint({...fixture,requestSha:'b'.repeat(64)});
 assert.notDeepEqual(a,c);
});

test('a pack cannot claim verified morphology without authenticated validity and 64-digit hash',()=>{
 const d=clone(fixture);
 d.genreEvidence=[{genreId:'genre-progress',applicability:'applicable',contentHash:'pretend-hash',
   verified:true,pack:{pack_id:'p',version:'1.0',core_conventions:[{id:'c',description:'Must be this',strength:'HARD_CONSTRAINT'}]}}];
 const genre=projectFullArchitecture(d).genreViews.find(g=>g.genreId==='genre-progress');
 assert.equal(genre.packCoverage.status,'unverified');
 assert.equal(genre.morphology.length,0);
});

test('adopted working origin becomes visibly stale on changed proposal SHA but never disappears',()=>{
 const d=clone(fixture);d.requestSha='b'.repeat(64);
 const p=projectFullArchitecture(d),item=p.storySpecific.find(x=>x.itemId==='author-struct');
 assert.equal(item.needsReview,true);
 assert.equal(item.sourceRef,'links/2');
 assert.equal(item.authority,'author_working');
});

test('source-domain revision is checked against the correct origin, not a different candidate SHA',()=>{
 const d=clone(fixture);d.workingItems.push({id:'from-demo',title:'Shared hope',architecture_role:'trope',
   proposal_origin:{request_sha:'demo-paladin-v1',source_ref:'demo-fixture/paladin/hope',source_kind:'illustrative_model_hypothesis'}});
 d.workingSourceRevision='demo-paladin-v1';
 assert.equal(projectFullArchitecture(d).storySpecific.find(i=>i.itemId==='from-demo').needsReview,false);
 d.workingSourceRevision='demo-paladin-v2';
 assert.equal(projectFullArchitecture(d).storySpecific.find(i=>i.itemId==='from-demo').needsReview,true);
});
