import test from 'node:test';
import assert from 'node:assert/strict';
import {renderFullArchitecture} from '../focused-unfolding/full-view.mjs';
import {renderReviewArchitecture} from '../focused-unfolding/review-view.mjs';
import {projectFullArchitecture} from './projection.mjs';

const element=(tag='div')=>({tagName:tag,className:'',textContent:'',children:[],attributes:{},
  append(...items){this.children.push(...items)},
  appendChild(item){this.children.push(item)},
  replaceChildren(...items){this.children=[...items]},
  setAttribute(k,v){this.attributes[k]=v},addEventListener(){}});
const flat=x=>[x,...x.children.flatMap(flat)];

test('native imports work and legacy genre morphology does not duplicate alongside a Pack',()=>{
 const prior=globalThis.document;globalThis.document={createElement:element};
 try{
  const sample={candidate:{nodes:[{id:'g',title:'Epic Fantasy',category:'genre'}],genre_contracts:[]},
   genreEvidence:[{genreId:'g',verified:true,applicability:'applicable',contentHash:'b'.repeat(64),
    pack:{pack_id:'epic',version:'1',audience_promises:[],emotional_targets:[],
      core_conventions:[],narrative_engines:[],escalation_patterns:[],resolution_patterns:[]}}],
   legacyEvidence:[{genreId:'g',sourceRef:'genres/data/epic_fantasy.yaml',
     contract:{genre_id:'epic_fantasy',audience_product:'Awe'}}]};
  const root=element();
  renderFullArchitecture(root,projectFullArchitecture(sample),
    {expandedGenre:'g',onToggleGenre(){},onFocusRef(){},onReview(){}});
  const texts=flat(root).map(x=>x.textContent).filter(Boolean);
  assert.equal(texts.filter(x=>x.includes('reader_promise: Awe')).length,1);
  assert.ok(texts.some(x=>x.includes('Epic Fantasy')&&x.includes('Verified Pack')));
 }finally{globalThis.document=prior;}
});

test('legacy morphology is named available even without versioned Pack',()=>{
 const prior=globalThis.document;globalThis.document={createElement:element};
 try{
   const projection=projectFullArchitecture({candidate:{nodes:[{id:'g',title:'Epic Fantasy',category:'genre'}]},
     legacyEvidence:[{genreId:'g',sourceRef:'genres/data/epic_fantasy.yaml',
       contract:{genre_id:'epic_fantasy',required_tropes:['found family']}}]});
   const root=element();renderFullArchitecture(root,projection,{expandedGenre:'g',
     onToggleGenre(){},onFocusRef(){},onReview(){}});
   assert.match(flat(root).map(x=>x.textContent).join(' '),/Legacy genre reference available/);
 }finally{globalThis.document=prior;}
});
