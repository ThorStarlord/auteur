import {test} from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import vm from 'node:vm';
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.events={};this.className='';this.type='';this.attributes={};}
 append(...children){this.children.push(...children);}replaceChildren(...children){this.children=children;}
 addEventListener(name,fn){this.events[name]=fn;}
 setAttribute(name,value){this.attributes[name]=value;}
}
const document={createElement:(tag)=>new Element(tag)};const window={};
const sources=['../src/auteur/beginner/browser/studio_explanations.js','../src/auteur/beginner/browser/studio_explanation_views.js'];
for(const path of sources)vm.runInNewContext(readFileSync(new URL(path,import.meta.url),'utf8'),{window,document});
const c={nodes:[{id:'g',title:'Heroic Fantasy',category:'genre'},{id:'t',title:'Earned victory',category:'trope'},{id:'s',title:'Costs of heroism',category:'structure'}],
 links:[{source:'t',target:'s',function:'creates pressure for'}],genre_contracts:[{genre_node_id:'g',role:'governing',trope_functions:['earned victory'],narrative_engine:'Heroic choice',structural_pattern:'Costly choice',payoff_expectations:['hope'],aesthetic_strategies:['warmth'],emotion_target_ids:[]}],phases:[],emotion_targets:[]};
const model=window.AuteurStudioExplanations.project(c,'sha-demo',null),views=window.AuteurStudioExplanationViews;
function contents(root){let output=[];function visit(node){if(node.textContent)output.push(node.textContent);node.children.forEach(visit);}visit(root);return output.join(' | ');}

test('genre renderer explains proposed promise/engine and missing curated source',()=>{
 const root=new Element();views.renderGenre(root,model,'genre:g',()=>{},()=>{});
 assert.match(contents(root),/Heroic Fantasy/);assert.match(contents(root),/Heroic choice/);
 assert.match(contents(root),/No verified pack/);
 assert.match(contents(root),/hope/);
});

test('trope renderer distinguishes source-scoped story variation from genre-wide rules',()=>{
 const root=new Element();views.renderTrope(root,model,'trope:g:0',()=>{},()=>{});
 assert.match(contents(root),/earned victory/);assert.match(contents(root),/No verified pack/);
 assert.match(contents(root),/genre_contracts\/g\/trope_functions\/0/);
});

test('mechanism renderer gives real relationship verbs without a fabricated chain',()=>{
 const root=new Element();views.renderStructure(root,model,'structure-node:s',()=>{},()=>{});
 assert.match(contents(root),/Costs of heroism/);assert.match(contents(root),/creates pressure for/);
 assert.match(contents(root),/links\/0/);
});

test('buttons call navigation only on explicit click, not render',()=>{
 let navigations=0,inspections=0;const root=new Element();
 views.renderGenre(root,model,'genre:g',()=>navigations++,()=>inspections++);
 assert.equal(navigations,0);assert.equal(inspections,0);
 const buttons=[];function visit(node){if(node.tag==='button'&&node.events.click)buttons.push(node);node.children.forEach(visit);}visit(root);
 assert.ok(buttons.length>1);
 buttons[0].events.click();assert.equal(navigations,1);
});
