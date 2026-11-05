import test from 'node:test';
import assert from 'node:assert/strict';
import {compareArchitectureRevision} from './compare.mjs';
import {mountRevisionReview} from './view.mjs';
class FakeNode {
  constructor(tag,doc){this.tagName=tag;this.doc=doc;this.children=[];this._text='';this.id='';this.className='';this.style={};this.dataset={};this.attrs={};this.listeners={};this.classList={add:name=>{this.className+=' '+name}}}
  set textContent(value){this._text=String(value);this.children=[]}
  get textContent(){return this._text+this.children.map(n=>typeof n==='string'?n:n.textContent).join('')}
  append(...items){this.children.push(...items)}
  appendChild(item){this.children.push(item);return item}
  replaceChildren(...items){this.children=[...items];this._text=''}
  addEventListener(name,callback){this.listeners[name]=callback}
  setAttribute(name,value){this.attrs[name]=String(value)}
  focus(){this.doc.activeElement=this}
}
class FakeDocument {
  constructor(){this.activeElement=null;this.root=new FakeNode('main',this)}
  createElement(tag){return new FakeNode(tag,this)}
  createElementNS(_ns,tag){return this.createElement(tag)}
  getElementById(id){return walk(this.root).find(n=>n.id===id)||null}
}
function walk(node){return [node,...node.children.flatMap(child=>typeof child==='string'?[]:walk(child))]}
const SHA='a'.repeat(64),NEXT='b'.repeat(64);
function candidate(){return{schema_version:2,summary:'Original',nodes:[
{id:'engine',title:'Engine',category:'engine',summary:'Original cost'},
{id:'wonder',title:'Wonder',category:'theme',summary:'Awe'}],
links:[{id:'cost',source:'engine',target:'wonder',function:'pressures'}],
emotion_targets:[],complex_emotions:[],genre_contracts:[],genre_interactions:[],phases:[],open_questions:[]}}
function setup(){const before=candidate(),after=structuredClone(before);after.nodes[0].summary='Discovery inspires wonder';after.links[0].function='enables';const comparison=compareArchitectureRevision({before,after,beforeRequestSha:SHA,afterRequestSha:NEXT,expectedPriorSha:SHA,requestedChange:'More wonder'});const doc=new FakeDocument();const view=mountRevisionReview(doc.root,{comparison,document:doc});return{doc,view,comparison}}
test('summary is text first and never claims canon acceptance',()=>{const {doc}=setup();assert.match(doc.getElementById('revision-summary').textContent,/working architecture/i);assert.match(doc.getElementById('revision-summary').textContent,/Requirements to check \(not verified\)/);assert.match(doc.root.textContent,/No story canon accepted/i)});
test('explicit compare has separate before and after graph surfaces',()=>{const {doc,view}=setup();view.setMode('compare');assert.ok(doc.getElementById('side-before'));assert.ok(doc.getElementById('side-after'));assert.match(doc.getElementById('side-after').textContent,/un-applied/i)});
test('focused semantic field difference shows before and after meaning',()=>{const {doc,view}=setup();view.selectFocus({kind:'node',id:'engine'});const fields=doc.getElementById('field-comparison').textContent;assert.match(fields,/Original cost/);assert.match(fields,/Discovery inspires wonder/)});
test('link focus exposes exact relationship function differences without inferred causality',()=>{const {doc,view}=setup();view.selectFocus({kind:'link',id:'cost'});assert.match(doc.getElementById('field-comparison').textContent,/pressures/);assert.match(doc.getElementById('field-comparison').textContent,/enables/);assert.match(doc.getElementById('focused-overlay').textContent,/recorded local links/i)});
test('review selection does not mutate either immutable input candidate',()=>{const {view,comparison}=setup();const a=JSON.stringify(comparison.beforeCandidate),b=JSON.stringify(comparison.afterCandidate);view.setMode('compare');view.selectFocus({kind:'node',id:'engine'});view.reset();assert.equal(JSON.stringify(comparison.beforeCandidate),a);assert.equal(JSON.stringify(comparison.afterCandidate),b)});
test('paired graph paths have a visible directional marker for recorded relationships',()=>{const {doc,view}=setup();view.setMode('compare');const paths=walk(doc.root).filter(n=>n.tagName==='path'&&String(n.attrs.class||'').startsWith('edge '));assert.ok(paths.length>=2);assert.ok(paths.every(p=>String(p.attrs['marker-end']||'').startsWith('url(')))});
