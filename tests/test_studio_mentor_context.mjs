import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentor_context.js',import.meta.url),'utf8');
const modelSource=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentorship.js',import.meta.url),'utf8');
function model(){const win={};new Function('window',source)(win);new Function('window',modelSource)(win);return win;}
const sha='a'.repeat(64);
function state(){return {architectureRequestSha:sha,items:[
 {id:'story-vision',title:'Story Vision',content:'Earned hope and generous power'},
 {id:'friend',title:'Independent companion',kind:'note',content:'The companion can leave'}
],architecture:{nodes:[{id:'g',title:'Generosity',category:'theme',summary:'Power through service'},
 {id:'c',title:'Agency',category:'theme',summary:'Freedom'}],
 links:[{source:'g',target:'c',function:'supports'}],
 open_questions:['How do companions become independent?']}};}
test('author intent is quoted as working, never accepted authority',()=>{
 const m=model();const p=m.AuteurStudioMentorContext.project(state(),state().architecture.nodes[0],'candidate');
 assert.equal(p.storyVision.text,'Earned hope and generous power');
 assert.equal(p.storyVision.authority,'author_working');
 assert.equal(p.acceptedIdentity.status,'not_bound');
 assert.equal(p.genreEvidence.status,'not_evaluated');
 assert.equal(p.declaredEdges[0].sourceRef,'links/0');
 assert.equal(p.declaredEdges[0].authority,'agent_candidate');
 assert.equal(p.questions[0].authority,'agent_candidate');
});
test('author working focus does not inherit candidate edges as accepted facts',()=>{
 const m=model(),s=state(),p=m.AuteurStudioMentorContext.project(s,s.items[1],'working');
 assert.equal(p.selected.authority,'author_working');
 assert.equal(p.selected.sourceRef,'canvas/items/friend');
 assert.deepEqual(p.declaredEdges,[]);
});
test('missing vision stays unknown rather than fabricated',()=>{
 const m=model(),s=state();s.items=s.items.filter(x=>x.id!=='story-vision');
 const p=m.AuteurStudioMentorContext.project(s,s.architecture.nodes[0],'candidate');
 assert.equal(p.storyVision.authority,'not_supplied');
 assert.equal(p.storyVision.text,'');
});
test('stale or missing SHA cannot attribute candidate relationships to a request',()=>{
 const m=model(),s=state();s.architectureRequestSha='broken';
 const p=m.AuteurStudioMentorContext.project(s,s.architecture.nodes[0],'candidate');
 assert.equal(p.sourceSha,null);assert.deepEqual(p.declaredEdges,[]);assert.deepEqual(p.questions,[]);
});
test('host instruction includes context with origin labels and preserves no-auto-canon',()=>{
 const m=model(),s=state(),focus=s.architecture.nodes[0];
 const ctx=m.AuteurStudioMentorContext.project(s,focus,'candidate');
 const mentor=m.AuteurStudioMentorship.project({focus,focusKind:'candidate',
   requestSha:sha,candidate:s.architecture,authorContext:ctx});
 const prompt=m.AuteurStudioMentorship.hostInstruction(mentor,s.items[0].content);
 assert.match(prompt,/author_working/);
 assert.match(prompt,/agent_candidate/);
 assert.match(prompt,/not_bound/);
 assert.match(prompt,/No story acceptance/);
 assert.match(prompt,/Do not automatically accept/);
 assert.ok(prompt.length<=4000);
});
test('context construction is read-only',()=>{
 const m=model(),s=state(),before=structuredClone(s);
 m.AuteurStudioMentorContext.project(s,s.architecture.nodes[0],'candidate');
 assert.deepEqual(s,before);
 assert.equal(m.AuteurStudioMentorContext.project(s,null,'candidate'),null);
});

test('stale and pending architecture cannot supply source-bound mentor evidence',()=>{
 const m=model(),s=state();
 for(const status of ['stale','awaiting_host_agent','review_ready']){
   s.architectureSourceStatus=status;
   const p=m.AuteurStudioMentorContext.project(s,s.architecture.nodes[0],'candidate');
   assert.equal(p.sourceSha,null);
   assert.deepEqual(p.declaredEdges,[]);
   assert.deepEqual(p.questions,[]);
   assert.equal(p.selected.sourceRef,null);
 }
 s.architectureSourceStatus='ready';
 const p=m.AuteurStudioMentorContext.project(s,s.architecture.nodes[0],'candidate');
 assert.equal(p.sourceSha,sha);
 assert.equal(p.declaredEdges.length,1);
});
