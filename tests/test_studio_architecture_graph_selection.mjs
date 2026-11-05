import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/auteur/beginner/browser/studio_architecture_graph_selection.js',import.meta.url),'utf8');
function element(tag,document){
  return {
    tag,ownerDocument:document,children:[],listeners:{},attrs:{},dataset:{},
    textContent:'',value:'',title:'',style:{},
    append(...items){this.children.push(...items)},
    appendChild(item){this.children.push(item);return item},
    replaceChildren(...items){this.children=items},
    setAttribute(key,value){this.attrs[key]=value},
    addEventListener(key,fn){(this.listeners[key]||=[]).push(fn)},
    removeEventListener(key,fn){this.listeners[key]=(this.listeners[key]||[]).filter(x=>x!==fn)},
    dispatch(name,event={}){for(const fn of this.listeners[name]||[])fn(event)},
    focus(){document.activeElement=this},
  };
}
function setup(){
  const document={activeElement:null,createElement(tag){return element(tag,this)}},window={};
  runInNewContext(source,{window,document});
  let sha='a'.repeat(64),selected=[];
  const candidate={schema_version:2,nodes:[
    {id:'engine',title:'Memory Economy',category:'engine',summary:'Discovery costs memories',parent_id:null},
    {id:'genre',title:'Mystery',category:'genre',summary:'Questions',parent_id:'engine'}],
    links:[{id:'recorded_link',source:'engine',target:'genre',function:'raises tension'}],
    genre_interactions:[],emotion_targets:[],complex_emotions:[],
    genre_contracts:[],phases:[]};
  const graphRoot=document.createElement('svg'),indexRoot=document.createElement('section'),inspectorRoot=document.createElement('section');
  const controller=window.AuteurStudioGraphSelection.createGraphSelectionController({
    getCandidate:()=>candidate,getRequestSha:()=>sha,graphRoot,indexRoot,inspectorRoot,
    onSelect:next=>{selected=next},
  });
  return{document,candidate,graphRoot,indexRoot,inspectorRoot,controller,selected:()=>selected,setSha:value=>sha=value};
}
test('recorded edge is selected by typed source ID, not title',()=>{
  const s=setup();s.controller.select({kind:'link',id:'recorded_link'});
  assert.equal(s.selected()[0].kind,'link');assert.equal(s.selected()[0].id,'recorded_link');
});
test('graph SVG hit target routes to the same typed link selection',()=>{
  const s=setup();let stopped=false;
  const edge={getAttribute:k=>k==='data-architecture-link-id'?'recorded_link':null,
    hasAttribute:k=>k==='data-architecture-link-id'};
  s.graphRoot.dispatch('click',{target:{closest:()=>edge},stopPropagation(){stopped=true}});
  assert.equal(s.selected()[0].id,'recorded_link');assert.equal(stopped,true);
});
test('keyboard-operable linear relationship index is available independent of SVG',()=>{
  const s=setup();const list=s.indexRoot.children[1];const link=list.children.find(x=>x.tag==='button');
  assert(link);link.dispatch('click');assert.equal(s.selected()[0].id,'recorded_link');
});
test('top-level component selection has the same source owner ID',()=>{
  const s=setup();s.controller.select({kind:'node',id:'engine'});
  const component=s.inspectorRoot.children.find(x=>x.dataset.componentField==='summary');
  assert(component);component.dispatch('click');
  assert.equal(s.selected()[0].kind,'node');assert.equal(s.selected()[0].id,'engine');
  assert.equal(s.selected()[0].field,'summary');
});
test('search retains focus during multiple typed filtering edits',()=>{
  const s=setup();const filter=s.indexRoot.children[0];filter.focus();
  for(const value of ['r','re','rec','record']){filter.value=value;filter.dispatch('input');assert.equal(s.document.activeElement,filter)}
  assert(s.indexRoot.children[1].children.some(x=>x.tag==='button'));
});
test('source request SHA change clears selected anchors',()=>{
  const s=setup();s.controller.select({kind:'node',id:'engine'});
  s.setSha('b'.repeat(64));s.controller.onCandidateChange();
  assert.equal(s.selected().length,0);
});
test('stale or fabricated relationship cannot be selected',()=>{
  const s=setup();assert.throws(()=>s.controller.select({kind:'link',id:'not_present'}),/not recorded/);
});
test('selection limit of three independent anchors is enforced',()=>{
  const s=setup();s.controller.select({kind:'node',id:'engine'});
  s.controller.select({kind:'node',id:'genre'},{append:true});
  s.controller.select({kind:'link',id:'recorded_link'},{append:true});
  assert.equal(s.selected().length,3);
  assert.throws(()=>s.controller.select({kind:'node',id:'engine',field:'summary'},{append:true}),/at most three/);
});
test('controller destroy detaches graph listener and clears visual index',()=>{
  const s=setup();s.controller.destroy();assert.equal(s.indexRoot.children.length,0);
});
