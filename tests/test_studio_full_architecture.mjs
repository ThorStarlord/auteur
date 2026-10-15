import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {projectFullArchitecture} from '../docs/prototypes/full-architecture/projection.mjs';
import {reviewFullArchitecture} from '../docs/prototypes/full-architecture/review.mjs';
const root=new URL('../src/auteur/beginner/browser/',import.meta.url);
const file=n=>readFileSync(new URL(n,root),'utf8');
const sample=JSON.parse(readFileSync(new URL('../docs/prototypes/full-architecture/fixtures/paladin.json',import.meta.url),'utf8'));
function loadCore(){const sandbox={window:{},structuredClone};runInNewContext(file('studio_full_architecture.js'),sandbox);return sandbox.window.AuteurStudioFullArchitecture;}

test('Studio browser adapter exactly matches tested pure projector on genre/source authority',()=>{
 const api=loadCore();assert.deepEqual(JSON.parse(JSON.stringify(api.project(sample))),projectFullArchitecture(sample));
});

test('Studio browser adapter exactly matches tested author-decision review',()=>{
 const api=loadCore(),p=projectFullArchitecture(sample);
 assert.deepEqual(JSON.parse(JSON.stringify(api.review(p))),reviewFullArchitecture(p));
});

test('candidate genre contracts do not become verified pack rules in Studio mode',()=>{
 const api=loadCore(),p=api.project(sample);
 assert.equal(p.genreViews[0].packCoverage.status,'unknown');
 assert.equal(p.genreViews[0].morphology.length,0);
 assert.equal(p.genreViews[0].candidateInterpretations[0].authority,'candidate_genre_interpretation');
});

test('source bundle never contains provider, HTTP or acceptance side effects',()=>{
 const s=file('studio_full_architecture.js');
 assert.doesNotMatch(s,/\bfetch\s*\(|XMLHttpRequest|axios|\.post\s*\(|accept_story|acceptStoryIdentity/);
});

test('source bundle fingerprint changes with canvas revision and proposal SHA',()=>{
 const api=loadCore(),p=api.project(sample);
 const changed=api.project({...sample,canvasRevision:4,requestSha:'b'.repeat(64)});
 assert.notDeepEqual(JSON.parse(JSON.stringify(p.fingerprint)),JSON.parse(JSON.stringify(changed.fingerprint)));
});

test('controller can render Full and Review without a working-document mutation',()=>{
 let renderCount=0,reviewCount=0,mutations=0;
 const sandbox={window:{AuteurStudioFullArchitecture:{project(){return projectFullArchitecture(sample)},review(){return reviewFullArchitecture(projectFullArchitecture(sample))},
   renderFull(){renderCount++},renderReview(){reviewCount++}}}};
 runInNewContext(file('studio_full_architecture_controller.js'),sandbox);
 const api=sandbox.window.AuteurStudioFullArchitectureController;
 const root={hidden:true,replaceChildren(){}},review={hidden:true,replaceChildren(){}},nav={hidden:true};
 const nodes={focus:{attrs:{},setAttribute(k,v){this.attrs[k]=v}},full:{attrs:{},setAttribute(k,v){this.attrs[k]=v}}};
 const ctrl=api.create({getState:()=>({workspace:'architecture',view:'architecture',architectureFacet:'overview',architecture:sample.candidate,
   architectureRequestSha:sample.requestSha,items:sample.workingItems,connections:[],fullArchitectureDisplay:'full'}),
   getRemote:()=>({revision:3}),root,reviewRoot:review,nav,focusButton:nodes.focus,fullButton:nodes.full,
   onFocus(){},onMode(){mutations++}});
 ctrl.render();assert.equal(renderCount,1);assert.equal(reviewCount,0);assert.equal(root.hidden,false);
 // A separate review-state instance shares the same source and makes no writes.
 const ctrl2=api.create({getState:()=>({workspace:'architecture',view:'architecture',architectureFacet:'overview',architecture:sample.candidate,
   architectureRequestSha:sample.requestSha,items:sample.workingItems,connections:[],fullArchitectureDisplay:'review'}),
   getRemote:()=>({revision:3}),root,reviewRoot:review,nav,focusButton:nodes.focus,fullButton:nodes.full,
   onFocus(){},onMode(){mutations++}});
 ctrl2.render();assert.equal(reviewCount,1);assert.equal(review.hidden,false);
 assert.equal(mutations,0);
});

test('Review from Studio remains a read-only derivation with missing pack explicit',()=>{
 const api=loadCore(),p=api.project(sample),r=api.review(p);
 assert.ok(r.items.some(x=>x.kind==='source_coverage'&&x.state==='not_established'));
 assert.ok(!('accepted' in r));
});


test('controller only attaches legacy evidence from matching canvas and source request',()=>{
 const calls=[];
 const sandbox={window:{AuteurStudioFullArchitecture:{
   project(payload){calls.push(payload);return projectFullArchitecture(payload)},
   review(){return {items:[]}},renderFull(){},renderReview(){}
 }}};
 runInNewContext(file('studio_full_architecture_controller.js'),sandbox);
 const make=sandbox.window.AuteurStudioFullArchitectureController.create;
 let canvasId='author-canvas';
 const state={workspace:'architecture',view:'architecture',architectureFacet:'overview',
   architecture:sample.candidate,architectureRequestSha:'a'.repeat(64),
   items:sample.workingItems,connections:[],fullArchitectureDisplay:'full',
   fullArchitectureEvidence:{canvasId,requestSha:'a'.repeat(64),
      legacyEvidence:[{genreId:'epic',sourceRef:'genres/data/epic_fantasy.yaml',
        contract:{genre_id:'epic_fantasy',audience_product:'Awe'}}]}};
 const node=()=>({hidden:true,setAttribute(){}});
 const controller=make({getState:()=>state,getRemote:()=>({canvasId,revision:1}),
   nav:node(),root:node(),reviewRoot:node(),focusButton:node(),fullButton:node(),
   onFocus(){},onMode(){}});
 controller.render();
 assert.equal(calls.at(-1).legacyEvidence.length,1);
 state.architectureRequestSha='b'.repeat(64);
 controller.render();
 assert.equal(calls.at(-1).legacyEvidence.length,0);
 state.architectureRequestSha='a'.repeat(64);canvasId='new-canvas';
 controller.render();
 assert.equal(calls.at(-1).legacyEvidence.length,0);
});
