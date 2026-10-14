import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_mentorship.js',import.meta.url),'utf8');
function mentor(){
  const browser={};new Function('window',source)(browser);
  return browser.AuteurStudioMentorship;
}
const sha='a'.repeat(64);
const suggestion=(id,role,verb,ref)=>({
  id,title:id,targetRole:role,relationshipVerb:verb,sourceRef:ref,
  sourceKind:'proposal_edge',supportStatus:'source_backed_proposal',
  requestSha:sha,description:id+' changes the plot',canonical:false
});

test('teaches actual narrative role without mislabelling genre evidence',()=>{
  const p=mentor().project({focus:{id:'g',title:'Epic Fantasy',category:'genre'},focusKind:'candidate'});
  assert.match(p.definition,/not a verified genre convention/);
  assert.match(p.evidenceNote,/proposals/);
  assert.equal(p.options.length,0);
  assert.equal(p.recommended,'learn');
});

test('divergence preserves source identity and chooses different mechanisms',()=>{
  const items=[suggestion('One','trope','uses','links/0'),suggestion('Copy','trope','uses','links/1'),
    suggestion('Two','structure','supports','links/2'),suggestion('Three','emotion','contrasts','links/3')];
  const before=structuredClone(items);
  const p=mentor().project({focus:{id:'g',title:'Hero',category:'character'},requestSha:sha,
    suggestions:items});
  assert.deepEqual(items,before);
  assert.deepEqual(p.options.map(x=>x.title),['One','Two','Three']);
  assert.deepEqual(p.options.map(x=>x.sourceRef),['links/0','links/2','links/3']);
  assert.equal(p.recommended,'explore');
});

test('only one same-mechanism option remains when no divergent evidence exists',()=>{
  const p=mentor().project({focus:{id:'g',title:'Growth',category:'engine'},requestSha:sha,
    suggestions:[suggestion('A','trope','uses','links/0'),suggestion('B','trope','uses','links/1')]});
  assert.equal(p.options.length,1);
  assert.equal(p.recommended,'explore');
});

test('mismatched, fabricated or unproven suggestions cannot appear as grounded alternatives',()=>{
  const ideas=[suggestion('A','trope','uses','links/0'),
    {...suggestion('B','character','supports','links/1'),requestSha:'b'.repeat(64)},
    {...suggestion('C','engine','supports','links/2'),supportStatus:'model_hypothesis'},
    {...suggestion('D','structure','uses','invented/3'),sourceRef:'invented/3'}];
  const p=mentor().project({focus:{id:'g',title:'Idea'},requestSha:sha,suggestions:ideas});
  assert.deepEqual(p.options.map(x=>x.title),['A']);
  assert.deepEqual(mentor().project({focus:{id:'g',title:'Idea'},requestSha:'broken',suggestions:ideas}).options,[]);
});

test('challenge is proactive only for an explicit, source-bound tension',()=>{
  const p=mentor().project({focus:{id:'g',title:'Generosity',category:'theme'},focusKind:'candidate',
    requestSha:sha,candidate:{nodes:[{id:'g',title:'Generosity'},{id:'x',title:'Personal independence'}],
      links:[{source:'g',target:'x',function:'contrasts'}]}});
  assert.equal(p.recommended,'challenge');
  assert.equal(p.challengeStatus,'declared_proposal_tension');
  assert.equal(p.challengeSourceRef,'links/0');
  assert.match(p.challenge,/Personal independence/);
});

test('working idea does not inherit candidate tension as established truth',()=>{
  const p=mentor().project({focus:{id:'g',title:'Generosity',architecture_role:'theme'},focusKind:'working',
    requestSha:sha,candidate:{nodes:[{id:'g',title:'Generosity'},{id:'x',title:'Independence'}],
      links:[{source:'g',target:'x',function:'contradicts'}]}});
  assert.equal(p.challengeStatus,'conditional_hypothesis');
  assert.notEqual(p.recommended,'challenge');
});

test('deep prompt protects author purpose and requests real divergence',()=>{
  const p=mentor().project({focus:{id:'hero',title:'Kind hero',category:'character'},requestSha:sha});
  const prompt=mentor().hostInstruction(p,'Keep the hero generous and hopeful.');
  assert.match(prompt,/NONCANONICAL/);
  assert.match(prompt,/genuinely DIFFERENT/);
  assert.match(prompt,/Keep the hero generous and hopeful/);
  assert.match(prompt,/Do not automatically accept/);
  assert.match(prompt,/a{64}/);
  assert.ok(prompt.length<=4000);
});

test('missing focus fails closed; arbitrary input is rendered as text, not HTML',()=>{
  assert.equal(mentor().project({}),null);
  const p=mentor().project({focus:{id:'x',title:'<img src=x onerror=alert(1)>',category:'other',
    content:'<script>alert(1)</script>'}});
  assert.match(p.title,/^<img/);
  assert.match(p.inStory,/^<script/);
  assert.equal(p.recommended,'learn');
});

test('question follows a declared graph relation without claiming cause',()=>{
 const p=mentor().project({focus:{id:'g',title:'Generosity',category:'theme'},
   focusKind:'candidate',requestSha:sha,
   candidate:{nodes:[{id:'g',title:'Generosity'},{id:'e',title:'Hope'}],
     links:[{source:'g',target:'e',function:'supports'}]}});
 assert.equal(p.questionStatus,'source_bound_prompt');
 assert.equal(p.questionSourceRef,'links/0');
 assert.match(p.question,/Generosity/);
 assert.match(p.question,/Hope/);
 assert.match(p.question,/current proposal/);
});
