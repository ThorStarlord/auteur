import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/auteur/beginner/browser/studio_unfolding.js',import.meta.url),'utf8');
const win={};new Function('window',src)(win);
const {projectLocalSuggestions,buildAdoptionCommand,buildManualAnchorCommand}=win.AuteurStudioUnfolding;
const sha='a'.repeat(64);
const candidate={nodes:[
 {id:'g',category:'genre',title:'Progression Fantasy',summary:'A genre proposal'},
 {id:'t',category:'trope',title:'Earned breakthrough',summary:'Capability through effort'},
 {id:'e',category:'engine',title:'Challenge and growth',summary:'A repeatable pressure'},
 {id:'p',category:'reader_experience',title:'Joy',summary:'Intended emotional effect'},
 {id:'orphan',category:'trope',title:'No related edge',summary:'Disconnected'}],
 links:[{source:'g',target:'t',function:'uses'},{source:'t',target:'e',function:'illustrates'},
 {source:'g',target:'p',function:'targets reader emotion'},
 {source:'t',target:'p',function:'potentially supports'}]};

const from=(id='g',opts={})=>projectLocalSuggestions(candidate,sha,{kind:'candidate',id},
 opts.items||[],opts.dismissed||[],opts.limit===undefined?3:opts.limit,opts.offset||0);

test('focus-local candidates derive solely from actual declared edges',()=>{
 const ghosts=from();assert.equal(ghosts.length,2);
 assert.ok(ghosts.every(g=>g.sourceRef.startsWith('links/')&&g.sourceKind==='proposal_edge'));
 assert.ok(!ghosts.some(g=>g.title.includes('No related edge')));
 assert.ok(ghosts.every(g=>g.supportStatus==='source_backed_proposal'&&g.canonical===false));
});

test('trope focus gives declared structure/emotion links, never genre target causal jump',()=>{
 const ghosts=from('t');
 assert.equal(ghosts.length,3);
 assert.ok(ghosts.some(x=>x.title==='Challenge and growth'&&x.targetRole==='structure'));
 assert.ok(ghosts.every(x=>x.relationshipVerb));
 assert.ok(!ghosts.some(x=>x.sourceRef==='genre_contracts/g/emotion_target_ids/0'));
});

test('local ghost count is bounded and unrelated nodes cannot acquire a fabricated link',()=>{
 assert.equal(from('t',{limit:2}).length,2);
 assert.equal(from('orphan').length,0);
 assert.equal(from('t',{limit:3,offset:2}).length,1);
});

test('reversed edge traversal says related through rather than inventing causality',()=>{
 const ghosts=from('e');assert.equal(ghosts.length,1);
 assert.equal(ghosts[0].title,'Earned breakthrough');
 assert.match(ghosts[0].relationshipVerb,/related through/i);
});

test('already adopted and dismissed local evidence is suppressed by exact origin',()=>{
 const gs=from('g'),g=gs[0];
 const item={id:'adopted',proposal_origin:{request_sha:sha,source_ref:g.sourceRef,focus_id:'g'}};
 assert.equal(from('g',{items:[item]}).length,1);
 assert.equal(from('g',{dismissed:[gs[0].id]}).length,1);
});

test('working adopted idea can unfold the matching candidate without a global trope ID',()=>{
 const working={id:'working',proposal_origin:{request_sha:sha,source_ref:'links/0',focus_id:'g'}};
 const gs=projectLocalSuggestions(candidate,sha,{kind:'working',id:'working'},[working],[],3,0);
 assert.ok(gs.some(g=>g.title==='Challenge and growth'));
 assert.ok(!gs.some(g=>g.sourceRef==='links/0'));
});

test('stale working attribution and unknown focus never show unrelated ghost',()=>{
 const old={id:'working',proposal_origin:{request_sha:'b'.repeat(64),source_ref:'links/0',focus_id:'g'}};
 assert.deepEqual(projectLocalSuggestions(candidate,sha,{kind:'working',id:'working'},[old],[],3,0),[]);
 assert.deepEqual(from('missing'),[]);
});

test('adoption command is deterministic, atomic-request-shaped and strictly noncanonical',()=>{
 const g=from('g')[0],a=buildAdoptionCommand(g,{x:450,y:350}),b=buildAdoptionCommand(g,{x:450,y:350});
 assert.deepEqual(a,b);
 assert.match(a.commandId,/^[a-z0-9-]+$/);
 assert.match(a.payload.item.id,/^[a-z0-9-]+$/);
 assert.equal(a.payload.item.proposal_origin.request_sha,sha);
 assert.equal(a.payload.item.proposal_origin.source_ref,'links/0');
 assert.equal(a.payload.item.architecture_role,'trope');
 assert.equal(a.payload.item.kind,'note');
 assert.ok(!('canonical' in a.payload.item));
 assert.deepEqual(Object.keys(a.payload).sort(),['item','position']);
});

test('invalid source sha or coordinates cannot form an adoption payload',()=>{
 const g=from('g')[0];
 assert.throws(()=>buildAdoptionCommand({...g,requestSha:'wrong'},{x:1,y:1}),/sha|source/i);
 assert.throws(()=>buildAdoptionCommand(g,{x:-4,y:1}),/position/i);
});

test('manual first anchor is an explicit working item with no inferred source',()=>{
 const c=buildManualAnchorCommand('emotion','Joy through generous heroism','author-1',{x:50,y:50});
 assert.equal(c.payload.item.architecture_role,'emotion');
 assert.equal(c.payload.item.proposal_origin,null);
 assert.equal(c.payload.item.title,'Joy through generous heroism');
 assert.ok(!('canonical' in c.payload.item));
 assert.throws(()=>buildManualAnchorCommand('canon','bad','id',{x:1,y:1}),/role/i);
});

test('author can start from a character without falsely classifying it as an emotion',()=>{
 const cmd=buildManualAnchorCommand('character','Eira the healer','manual-character',{x:25,y:40});
 assert.equal(cmd.payload.item.kind,'character');
 assert.equal(cmd.payload.item.architecture_role,'other');
 assert.equal(cmd.payload.item.proposal_origin,null);
});
